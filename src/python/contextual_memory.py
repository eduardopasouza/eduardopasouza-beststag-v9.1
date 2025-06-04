"""
BestStag v9.1 + Abacus.AI - Sistema de Memória Contextual
Fase 2: IA Contextual e Front-end Inteligente
"""

import os
import json
import time
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from sentence_transformers import SentenceTransformer
    import faiss
except ImportError:
    logger.warning("sentence-transformers ou faiss não instalados. Instale com: pip install sentence-transformers faiss-cpu")

@dataclass
class MemoryItem:
    """Item de memória contextual"""
    id: str
    content: str
    user_id: str
    timestamp: datetime
    category: str
    importance: float
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None

class ContextualMemorySystem:
    """Sistema de Memória Contextual Avançado com Embeddings"""
    
    def __init__(self, 
                 model_name: str = 'all-MiniLM-L6-v2',
                 index_file: str = 'memory_index.faiss',
                 metadata_file: str = 'memory_metadata.json',
                 max_items: int = 10000):
        """
        Inicializa o sistema de memória contextual
        
        Args:
            model_name: Nome do modelo de embeddings
            index_file: Arquivo para salvar o índice FAISS
            metadata_file: Arquivo para salvar metadados
            max_items: Número máximo de itens na memória
        """
        self.model_name = model_name
        self.index_file = index_file
        self.metadata_file = metadata_file
        self.max_items = max_items
        
        # Inicializar modelo de embeddings
        try:
            self.model = SentenceTransformer(model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
        except Exception as e:
            logger.error(f"Erro ao carregar modelo de embeddings: {e}")
            self.model = None
            self.embedding_dim = 384  # Dimensão padrão
        
        # Inicializar índice FAISS
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.metadata_store = []
        
        # Carregar dados existentes
        self.load_memory()
    
    def _generate_embedding(self, text: str) -> List[float]:
        """Gera embedding para um texto"""
        if self.model is None:
            # Fallback: embedding aleatório (apenas para desenvolvimento)
            return np.random.random(self.embedding_dim).tolist()
        
        try:
            embedding = self.model.encode([text])[0]
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Erro ao gerar embedding: {e}")
            return np.random.random(self.embedding_dim).tolist()
    
    def add_memory(self, 
                   content: str, 
                   user_id: str, 
                   category: str = "general",
                   importance: float = 0.5,
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Adiciona um item à memória contextual
        
        Args:
            content: Conteúdo a ser armazenado
            user_id: ID do usuário
            category: Categoria do conteúdo
            importance: Importância (0.0 a 1.0)
            metadata: Metadados adicionais
            
        Returns:
            ID do item criado
        """
        # Gerar ID único
        item_id = f"{user_id}_{int(time.time())}_{hash(content) % 10000}"
        
        # Gerar embedding
        embedding = self._generate_embedding(content)
        
        # Criar item de memória
        memory_item = MemoryItem(
            id=item_id,
            content=content,
            user_id=user_id,
            timestamp=datetime.now(),
            category=category,
            importance=importance,
            metadata=metadata or {},
            embedding=embedding
        )
        
        # Adicionar ao índice FAISS
        embedding_array = np.array([embedding], dtype='float32')
        self.index.add(embedding_array)
        
        # Adicionar metadados
        self.metadata_store.append(memory_item)
        
        # Limpar memória se necessário
        self._cleanup_memory()
        
        logger.info(f"Memória adicionada: {item_id} para usuário {user_id}")
        return item_id
    
    def search_memory(self, 
                      query: str, 
                      user_id: Optional[str] = None,
                      category: Optional[str] = None,
                      top_k: int = 5,
                      min_importance: float = 0.0) -> List[MemoryItem]:
        """
        Busca na memória contextual
        
        Args:
            query: Texto de busca
            user_id: Filtrar por usuário
            category: Filtrar por categoria
            top_k: Número de resultados
            min_importance: Importância mínima
            
        Returns:
            Lista de itens de memória relevantes
        """
        if self.index.ntotal == 0:
            return []
        
        # Gerar embedding da query
        query_embedding = self._generate_embedding(query)
        query_array = np.array([query_embedding], dtype='float32')
        
        # Buscar no índice FAISS
        distances, indices = self.index.search(query_array, min(top_k * 2, self.index.ntotal))
        
        # Filtrar resultados
        results = []
        for i, idx in enumerate(indices[0]):
            if idx >= len(self.metadata_store):
                continue
                
            item = self.metadata_store[idx]
            
            # Aplicar filtros
            if user_id and item.user_id != user_id:
                continue
            if category and item.category != category:
                continue
            if item.importance < min_importance:
                continue
            
            # Adicionar score de similaridade
            item.metadata['similarity_score'] = float(1.0 / (1.0 + distances[0][i]))
            results.append(item)
            
            if len(results) >= top_k:
                break
        
        return results
    
    def get_user_context(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        Obtém contexto completo de um usuário
        
        Args:
            user_id: ID do usuário
            days: Número de dias para considerar
            
        Returns:
            Contexto do usuário
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filtrar itens do usuário
        user_items = [
            item for item in self.metadata_store
            if item.user_id == user_id and item.timestamp >= cutoff_date
        ]
        
        if not user_items:
            return {"user_id": user_id, "items": [], "summary": "Nenhum histórico recente"}
        
        # Organizar por categoria
        categories = {}
        for item in user_items:
            if item.category not in categories:
                categories[item.category] = []
            categories[item.category].append(item)
        
        # Calcular estatísticas
        total_items = len(user_items)
        avg_importance = sum(item.importance for item in user_items) / total_items
        most_recent = max(user_items, key=lambda x: x.timestamp)
        
        return {
            "user_id": user_id,
            "total_items": total_items,
            "categories": {cat: len(items) for cat, items in categories.items()},
            "avg_importance": avg_importance,
            "most_recent": most_recent.content,
            "most_recent_time": most_recent.timestamp.isoformat(),
            "items": [asdict(item) for item in user_items[-10:]]  # Últimos 10 itens
        }
    
    def _cleanup_memory(self):
        """Limpa memória antiga baseado em importância e idade"""
        if len(self.metadata_store) <= self.max_items:
            return
        
        # Calcular score de retenção (importância + recência)
        now = datetime.now()
        for item in self.metadata_store:
            days_old = (now - item.timestamp).days
            recency_score = max(0, 1.0 - (days_old / 365))  # Decai ao longo do ano
            item.metadata['retention_score'] = item.importance * 0.7 + recency_score * 0.3
        
        # Ordenar por score de retenção
        self.metadata_store.sort(key=lambda x: x.metadata.get('retention_score', 0), reverse=True)
        
        # Manter apenas os melhores itens
        items_to_keep = self.metadata_store[:self.max_items]
        items_to_remove = len(self.metadata_store) - self.max_items
        
        # Reconstruir índice FAISS
        if items_to_remove > 0:
            logger.info(f"Removendo {items_to_remove} itens antigos da memória")
            
            # Criar novo índice
            new_index = faiss.IndexFlatL2(self.embedding_dim)
            embeddings = []
            
            for item in items_to_keep:
                if item.embedding:
                    embeddings.append(item.embedding)
            
            if embeddings:
                embeddings_array = np.array(embeddings, dtype='float32')
                new_index.add(embeddings_array)
            
            self.index = new_index
            self.metadata_store = items_to_keep
    
    def save_memory(self):
        """Salva memória em disco"""
        try:
            # Salvar índice FAISS
            if self.index.ntotal > 0:
                faiss.write_index(self.index, self.index_file)
            
            # Salvar metadados
            metadata_dict = []
            for item in self.metadata_store:
                item_dict = asdict(item)
                item_dict['timestamp'] = item.timestamp.isoformat()
                metadata_dict.append(item_dict)
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata_dict, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Memória salva: {len(self.metadata_store)} itens")
            
        except Exception as e:
            logger.error(f"Erro ao salvar memória: {e}")
    
    def load_memory(self):
        """Carrega memória do disco"""
        try:
            # Carregar índice FAISS
            if os.path.exists(self.index_file):
                self.index = faiss.read_index(self.index_file)
                logger.info(f"Índice FAISS carregado: {self.index.ntotal} itens")
            
            # Carregar metadados
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata_dict = json.load(f)
                
                self.metadata_store = []
                for item_dict in metadata_dict:
                    item_dict['timestamp'] = datetime.fromisoformat(item_dict['timestamp'])
                    memory_item = MemoryItem(**item_dict)
                    self.metadata_store.append(memory_item)
                
                logger.info(f"Metadados carregados: {len(self.metadata_store)} itens")
            
        except Exception as e:
            logger.error(f"Erro ao carregar memória: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da memória"""
        if not self.metadata_store:
            return {"total_items": 0}
        
        categories = {}
        users = set()
        total_importance = 0
        
        for item in self.metadata_store:
            # Categorias
            if item.category not in categories:
                categories[item.category] = 0
            categories[item.category] += 1
            
            # Usuários
            users.add(item.user_id)
            
            # Importância
            total_importance += item.importance
        
        return {
            "total_items": len(self.metadata_store),
            "total_users": len(users),
            "categories": categories,
            "avg_importance": total_importance / len(self.metadata_store),
            "index_size": self.index.ntotal,
            "embedding_dim": self.embedding_dim,
            "model_name": self.model_name
        }

# Exemplo de uso
if __name__ == "__main__":
    # Inicializar sistema de memória
    memory = ContextualMemorySystem()
    
    # Adicionar algumas memórias de teste
    memory.add_memory(
        content="Usuário mencionou que tem reunião importante na sexta-feira",
        user_id="user123",
        category="agenda",
        importance=0.8,
        metadata={"type": "meeting", "day": "friday"}
    )
    
    memory.add_memory(
        content="Usuário está trabalhando no projeto BestStag v9.1",
        user_id="user123",
        category="projeto",
        importance=0.9,
        metadata={"project": "beststag", "version": "9.1"}
    )
    
    memory.add_memory(
        content="Usuário demonstrou interesse em automação de tarefas",
        user_id="user123",
        category="preferencias",
        importance=0.7,
        metadata={"interest": "automation"}
    )
    
    # Buscar memórias
    print("=== Busca por 'reunião' ===")
    results = memory.search_memory("reunião", user_id="user123", top_k=3)
    for result in results:
        print(f"- {result.content} (score: {result.metadata.get('similarity_score', 0):.3f})")
    
    print("\n=== Contexto do usuário ===")
    context = memory.get_user_context("user123")
    print(json.dumps(context, indent=2, ensure_ascii=False))
    
    print("\n=== Estatísticas ===")
    stats = memory.get_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # Salvar memória
    memory.save_memory()
    print("\n✅ Memória salva com sucesso!")

