
"""
BestStag v9.1 - Sistema de Cache Inteligente para Abacus.AI
Implementa cache com TTL dinâmico, invalidação inteligente e compressão
"""

import json
import time
import hashlib
import pickle
import gzip
from typing import Dict, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
import redis
import logging
from dataclasses import dataclass

logger = logging.getLogger('beststag.integrations.cache')


@dataclass
class CacheEntry:
    """Entrada do cache com metadados"""
    data: Any
    timestamp: float
    ttl: int
    access_count: int = 0
    last_access: float = 0
    compressed: bool = False
    size_bytes: int = 0


class IntelligentCache:
    """
    Sistema de cache inteligente com TTL dinâmico e otimizações avançadas
    
    Features:
    - TTL dinâmico baseado em padrões de acesso
    - Compressão automática para dados grandes
    - Invalidação inteligente
    - Métricas detalhadas
    - Suporte Redis para persistência
    """
    
    def __init__(
        self,
        default_ttl: int = 300,
        max_size: int = 1000,
        compression_threshold: int = 1024,
        redis_client: Optional[redis.Redis] = None,
        key_prefix: str = "beststag:cache:"
    ):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self.compression_threshold = compression_threshold
        self.redis_client = redis_client
        self.key_prefix = key_prefix
        
        # Cache local (fallback se Redis não disponível)
        self._local_cache: Dict[str, CacheEntry] = {}
        
        # Métricas
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0,
            'compressions': 0,
            'redis_errors': 0
        }
        
        logger.info(f"Cache inicializado - TTL: {default_ttl}s, Max Size: {max_size}")
    
    def _generate_key(self, endpoint: str, payload: Dict[str, Any]) -> str:
        """Gera chave única para cache baseada no endpoint e payload"""
        payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        hash_obj = hashlib.sha256(f"{endpoint}:{payload_str}".encode('utf-8'))
        return f"{self.key_prefix}{hash_obj.hexdigest()[:16]}"
    
    def _compress_data(self, data: Any) -> Tuple[bytes, bool]:
        """Comprime dados se necessário"""
        serialized = pickle.dumps(data)
        
        if len(serialized) > self.compression_threshold:
            compressed = gzip.compress(serialized)
            self.stats['compressions'] += 1
            logger.debug(f"Dados comprimidos: {len(serialized)} -> {len(compressed)} bytes")
            return compressed, True
        
        return serialized, False
    
    def _decompress_data(self, data: bytes, compressed: bool) -> Any:
        """Descomprime dados se necessário"""
        if compressed:
            data = gzip.decompress(data)
        return pickle.loads(data)
    
    def _calculate_dynamic_ttl(self, access_count: int, base_ttl: int) -> int:
        """Calcula TTL dinâmico baseado no padrão de acesso"""
        if access_count > 10:
            # Dados muito acessados ficam mais tempo no cache
            return min(base_ttl * 2, 3600)  # Max 1 hora
        elif access_count > 5:
            return int(base_ttl * 1.5)
        else:
            return base_ttl
    
    def _evict_lru(self):
        """Remove entradas menos recentemente usadas do cache local"""
        if len(self._local_cache) >= self.max_size:
            # Encontrar entrada menos recentemente acessada
            lru_key = min(
                self._local_cache.keys(),
                key=lambda k: self._local_cache[k].last_access
            )
            del self._local_cache[lru_key]
            self.stats['evictions'] += 1
            logger.debug(f"Cache LRU eviction: {lru_key}")
    
    def get(self, endpoint: str, payload: Dict[str, Any]) -> Optional[Any]:
        """
        Recupera dados do cache
        
        Args:
            endpoint: Endpoint da API
            payload: Payload da requisição
            
        Returns:
            Dados do cache ou None se não encontrado/expirado
        """
        key = self._generate_key(endpoint, payload)
        current_time = time.time()
        
        # Tentar Redis primeiro
        if self.redis_client:
            try:
                redis_data = self.redis_client.hgetall(key)
                if redis_data:
                    entry_data = json.loads(redis_data[b'data'].decode('utf-8'))
                    timestamp = float(redis_data[b'timestamp'])
                    ttl = int(redis_data[b'ttl'])
                    access_count = int(redis_data.get(b'access_count', 0))
                    compressed = redis_data.get(b'compressed', b'false') == b'true'
                    
                    # Verificar se ainda é válido
                    if current_time - timestamp < ttl:
                        # Atualizar contadores
                        access_count += 1
                        self.redis_client.hset(key, mapping={
                            'access_count': access_count,
                            'last_access': current_time
                        })
                        
                        # Atualizar TTL dinâmico
                        new_ttl = self._calculate_dynamic_ttl(access_count, ttl)
                        if new_ttl != ttl:
                            self.redis_client.expire(key, new_ttl)
                        
                        self.stats['hits'] += 1
                        logger.debug(f"Cache hit (Redis): {key}")
                        
                        if compressed:
                            return self._decompress_data(entry_data.encode('latin1'), True)
                        return entry_data
                    else:
                        # Expirado, remover
                        self.redis_client.delete(key)
                        
            except Exception as e:
                logger.warning(f"Erro ao acessar Redis: {e}")
                self.stats['redis_errors'] += 1
        
        # Fallback para cache local
        if key in self._local_cache:
            entry = self._local_cache[key]
            
            if current_time - entry.timestamp < entry.ttl:
                # Atualizar estatísticas de acesso
                entry.access_count += 1
                entry.last_access = current_time
                
                # Recalcular TTL dinâmico
                new_ttl = self._calculate_dynamic_ttl(entry.access_count, self.default_ttl)
                entry.ttl = new_ttl
                
                self.stats['hits'] += 1
                logger.debug(f"Cache hit (local): {key}")
                return entry.data
            else:
                # Expirado, remover
                del self._local_cache[key]
        
        self.stats['misses'] += 1
        logger.debug(f"Cache miss: {key}")
        return None
    
    def set(
        self,
        endpoint: str,
        payload: Dict[str, Any],
        data: Any,
        ttl: Optional[int] = None
    ):
        """
        Armazena dados no cache
        
        Args:
            endpoint: Endpoint da API
            payload: Payload da requisição
            data: Dados para armazenar
            ttl: TTL customizado (opcional)
        """
        key = self._generate_key(endpoint, payload)
        current_time = time.time()
        cache_ttl = ttl or self.default_ttl
        
        # Preparar dados para armazenamento
        compressed_data, is_compressed = self._compress_data(data)
        
        # Tentar Redis primeiro
        if self.redis_client:
            try:
                cache_entry = {
                    'data': compressed_data.decode('latin1') if is_compressed else json.dumps(data),
                    'timestamp': current_time,
                    'ttl': cache_ttl,
                    'access_count': 0,
                    'last_access': current_time,
                    'compressed': str(is_compressed).lower(),
                    'size_bytes': len(compressed_data)
                }
                
                self.redis_client.hset(key, mapping=cache_entry)
                self.redis_client.expire(key, cache_ttl)
                
                self.stats['sets'] += 1
                logger.debug(f"Cache set (Redis): {key}, TTL: {cache_ttl}s")
                return
                
            except Exception as e:
                logger.warning(f"Erro ao salvar no Redis: {e}")
                self.stats['redis_errors'] += 1
        
        # Fallback para cache local
        self._evict_lru()  # Garantir espaço
        
        entry = CacheEntry(
            data=data,
            timestamp=current_time,
            ttl=cache_ttl,
            access_count=0,
            last_access=current_time,
            compressed=is_compressed,
            size_bytes=len(compressed_data)
        )
        
        self._local_cache[key] = entry
        self.stats['sets'] += 1
        logger.debug(f"Cache set (local): {key}, TTL: {cache_ttl}s")
    
    def invalidate(self, pattern: str = None):
        """
        Invalida entradas do cache
        
        Args:
            pattern: Padrão para invalidação (opcional, invalida tudo se None)
        """
        if pattern:
            # Invalidação por padrão
            keys_to_remove = [
                key for key in self._local_cache.keys()
                if pattern in key
            ]
            
            for key in keys_to_remove:
                del self._local_cache[key]
                
            if self.redis_client:
                try:
                    redis_keys = self.redis_client.keys(f"{self.key_prefix}*{pattern}*")
                    if redis_keys:
                        self.redis_client.delete(*redis_keys)
                except Exception as e:
                    logger.warning(f"Erro ao invalidar Redis: {e}")
                    
            logger.info(f"Cache invalidado por padrão: {pattern}")
        else:
            # Invalidar tudo
            self._local_cache.clear()
            
            if self.redis_client:
                try:
                    redis_keys = self.redis_client.keys(f"{self.key_prefix}*")
                    if redis_keys:
                        self.redis_client.delete(*redis_keys)
                except Exception as e:
                    logger.warning(f"Erro ao limpar Redis: {e}")
                    
            logger.info("Cache completamente invalidado")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        total_requests = self.stats['hits'] + self.stats['misses']
        hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            'hit_rate_percent': round(hit_rate, 2),
            'local_cache_size': len(self._local_cache),
            'total_requests': total_requests
        }
    
    def cleanup_expired(self):
        """Remove entradas expiradas do cache local"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._local_cache.items()
            if current_time - entry.timestamp >= entry.ttl
        ]
        
        for key in expired_keys:
            del self._local_cache[key]
            
        if expired_keys:
            logger.debug(f"Removidas {len(expired_keys)} entradas expiradas do cache")


# Instância global do cache (singleton)
_cache_instance: Optional[IntelligentCache] = None


def get_cache() -> IntelligentCache:
    """Retorna instância singleton do cache"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = IntelligentCache()
    return _cache_instance


def initialize_cache(
    default_ttl: int = 300,
    max_size: int = 1000,
    redis_url: Optional[str] = None
) -> IntelligentCache:
    """
    Inicializa o cache global
    
    Args:
        default_ttl: TTL padrão em segundos
        max_size: Tamanho máximo do cache local
        redis_url: URL do Redis (opcional)
        
    Returns:
        Instância do cache configurada
    """
    global _cache_instance
    
    redis_client = None
    if redis_url:
        try:
            redis_client = redis.from_url(redis_url)
            redis_client.ping()  # Testar conexão
            logger.info(f"Redis conectado: {redis_url}")
        except Exception as e:
            logger.warning(f"Falha ao conectar Redis: {e}")
    
    _cache_instance = IntelligentCache(
        default_ttl=default_ttl,
        max_size=max_size,
        redis_client=redis_client
    )
    
    return _cache_instance
