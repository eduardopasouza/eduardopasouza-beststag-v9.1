from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import faiss
import numpy as np
import redis.asyncio as aioredis

from config.memory_policies import MEMORY_POLICIES


class MemoryCleanupError(Exception):
    """Raised when cleanup of expired memories fails."""


@dataclass
class MemoryItem:
    id: int
    user_id: str
    content: str
    importance: float
    created_at: str
    metadata: Dict[str, Any]


class ContextualMemorySystem:
    """Simple contextual memory service using Redis and FAISS."""

    def __init__(
        self,
        redis_url: Optional[str] = None,
        embedding_dim: int = 32,
    ) -> None:
        self.redis = aioredis.from_url(
            redis_url or os.getenv("REDIS_URL", "redis://localhost:6379"),
            decode_responses=True,
        )
        self.embedding_dim = embedding_dim
        self.faiss_index = faiss.IndexIDMap(faiss.IndexFlatL2(embedding_dim))

    async def add_memory(
        self,
        user_id: str,
        content: str,
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        mem_id = int(datetime.utcnow().timestamp() * 1000)
        embedding = np.random.random((self.embedding_dim,)).astype("float32")
        self.faiss_index.add_with_ids(
            np.expand_dims(embedding, axis=0),
            np.array([mem_id], dtype="int64"),
        )
        item = MemoryItem(
            id=mem_id,
            user_id=user_id,
            content=content,
            importance=importance,
            created_at=datetime.utcnow().isoformat(),
            metadata=metadata or {},
        )
        await self.redis.set(
            f"memories:{user_id}:{mem_id}",
            json.dumps(item.__dict__),
        )
        return str(mem_id)

    async def get_user_memory(self, user_id: str) -> List[Dict[str, Any]]:
        """Alias for get_all_memories for backward compatibility."""
        return await self.get_all_memories(user_id)

    async def save_interaction(
        self,
        user_id: str,
        conversation_id: str,
        user_message: str,
        assistant_response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Stores a conversation interaction as a memory item."""
        await self.add_memory(
            user_id=user_id,
            content=user_message,
            importance=0.5,
            metadata={"response": assistant_response, **(metadata or {})},
        )

    async def get_all_memories(self, user_id: str) -> List[Dict[str, Any]]:
        keys = await self.redis.keys(f"memories:{user_id}:*")
        memories: List[Dict[str, Any]] = []
        for key in keys:
            data = await self.redis.get(key)
            if data:
                memories.append(json.loads(data))
        return memories

    async def list_memories(
        self, user_id: str, limit: int = 50, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Return paginated memories ordered by creation date desc."""
        keys = await self.redis.keys(f"memories:{user_id}:*")
        ids = sorted((int(k.split(":")[-1]) for k in keys), reverse=True)
        selected = ids[offset : offset + limit]
        memories: List[Dict[str, Any]] = []
        for mem_id in selected:
            data = await self.redis.get(f"memories:{user_id}:{mem_id}")
            if data:
                memories.append(json.loads(data))
        return memories

    async def delete_all_memories(self, user_id: str) -> None:
        keys = await self.redis.keys(f"memories:{user_id}:*")
        for key in keys:
            data = await self.redis.get(key)
            if data:
                mem_id = json.loads(data).get("id")
                if mem_id is not None:
                    self.faiss_index.remove_ids(np.array([int(mem_id)], dtype="int64"))
            await self.redis.delete(key)

    async def cleanup_expired_memories(self, user_id: str) -> int:
        """Remove expired or low-importance memories for a user."""
        try:
            keys = await self.redis.keys(f"memories:{user_id}:*")
            removed = 0
            cutoff = datetime.utcnow() - timedelta(days=MEMORY_POLICIES["retention"]["short_term"])
            threshold = MEMORY_POLICIES["importance_thresholds"]["low"]
            for key in keys:
                data = await self.redis.get(key)
                if not data:
                    continue
                item = json.loads(data)
                importance = item.get("importance", 0.0)
                created_at = datetime.fromisoformat(item.get("created_at"))
                if importance < threshold or created_at < cutoff:
                    mem_id = int(item.get("id"))
                    self.faiss_index.remove_ids(np.array([mem_id], dtype="int64"))
                    await self.redis.delete(key)
                    removed += 1
            return removed
        except Exception as exc:  # pragma: no cover - error handling path
            raise MemoryCleanupError(str(exc)) from exc
