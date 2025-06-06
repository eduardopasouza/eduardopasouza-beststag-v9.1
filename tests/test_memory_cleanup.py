import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict

import pytest

from src.backend.services.memory_service import ContextualMemorySystem, MemoryCleanupError
from config.memory_policies import MEMORY_POLICIES


class FakeRedis:
    def __init__(self, store: Dict[str, Any]):
        self.store = store

    async def keys(self, pattern: str):
        return list(self.store.keys())

    async def get(self, key: str):
        value = self.store[key]
        if isinstance(value, Exception):
            raise value
        return json.dumps(value)

    async def delete(self, key: str):
        self.store.pop(key, None)


class FakeFaiss:
    def __init__(self):
        self.removed = []

    def remove_ids(self, ids):
        self.removed.extend(ids.tolist())


@pytest.mark.asyncio
async def test_no_memories_to_cleanup(monkeypatch):
    now = datetime.utcnow().isoformat()
    store = {
        "memories:user1:1": {
            "id": 1,
            "user_id": "user1",
            "importance": 0.5,
            "created_at": now,
        },
        "memories:user1:2": {
            "id": 2,
            "user_id": "user1",
            "importance": 0.9,
            "created_at": now,
        },
    }
    fake_redis = FakeRedis(store)
    fake_faiss = FakeFaiss()
    monkeypatch.setattr("aioredis.from_url", lambda *a, **k: fake_redis)
    monkeypatch.setattr("faiss.IndexIDMap", lambda x: fake_faiss)
    monkeypatch.setattr("faiss.IndexFlatL2", lambda x: None)
    memory = ContextualMemorySystem()
    removed = await memory.cleanup_expired_memories("user1")
    assert removed == 0
    assert len(fake_faiss.removed) == 0
    assert len(store) == 2


@pytest.mark.asyncio
async def test_cleanup_low_importance_and_old(monkeypatch):
    past_date = (datetime.utcnow() - timedelta(days=10)).isoformat()
    store = {
        "memories:user1:1": {
            "id": 1,
            "user_id": "user1",
            "importance": 0.1,
            "created_at": past_date,
        }
    }
    fake_redis = FakeRedis(store)
    fake_faiss = FakeFaiss()
    monkeypatch.setattr("aioredis.from_url", lambda *a, **k: fake_redis)
    monkeypatch.setattr("faiss.IndexIDMap", lambda x: fake_faiss)
    monkeypatch.setattr("faiss.IndexFlatL2", lambda x: None)
    memory = ContextualMemorySystem()
    removed = await memory.cleanup_expired_memories("user1")
    assert removed == 1
    assert fake_faiss.removed == [1]
    assert store == {}


@pytest.mark.asyncio
async def test_cleanup_redis_offline(monkeypatch):
    store = {"memories:user1:1": ConnectionError("offline")}
    fake_redis = FakeRedis(store)
    monkeypatch.setattr("aioredis.from_url", lambda *a, **k: fake_redis)
    monkeypatch.setattr("faiss.IndexIDMap", lambda x: FakeFaiss())
    monkeypatch.setattr("faiss.IndexFlatL2", lambda x: None)
    memory = ContextualMemorySystem()
    with pytest.raises(MemoryCleanupError):
        await memory.cleanup_expired_memories("user1")
