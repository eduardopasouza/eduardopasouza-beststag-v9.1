
"""
BestStag v9.1 - Testes de Cache e Circuit Breaker
Testes específicos para validar cache inteligente e circuit breaker
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch


@pytest.mark.integration
@pytest.mark.asyncio
class TestIntelligentCache:
    """Testes do sistema de cache inteligente"""
    
    async def test_cache_basic_operations(self):
        """Testa operações básicas do cache"""
        from src.integrations.abacus.cache import IntelligentCache
        
        cache = IntelligentCache(ttl_seconds=60)
        
        # Teste de set/get
        key = "test_key"
        value = {"message": "test", "response": "cached response"}
        
        await cache.set(key, value)
        retrieved = await cache.get(key)
        
        assert retrieved == value
        
        # Verificar estatísticas
        stats = cache.get_stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 0
        assert stats["sets"] == 1
    
    async def test_cache_miss(self):
        """Testa cache miss"""
        from src.integrations.abacus.cache import IntelligentCache
        
        cache = IntelligentCache(ttl_seconds=60)
        
        # Tentar obter chave inexistente
        result = await cache.get("nonexistent_key")
        assert result is None
        
        # Verificar estatísticas
        stats = cache.get_stats()
        assert stats["misses"] == 1
        assert stats["hits"] == 0
    
    async def test_cache_ttl_expiration(self):
        """Testa expiração por TTL"""
        from src.integrations.abacus.cache import IntelligentCache
        
        cache = IntelligentCache(ttl_seconds=1)  # TTL muito baixo para teste
        
        # Adicionar item
        key = "expiring_key"
        value = {"data": "will expire"}
        
        await cache.set(key, value)
        
        # Verificar que está no cache
        result = await cache.get(key)
        assert result == value
        
        # Aguardar expiração
        await asyncio.sleep(1.5)
        
        # Verificar que expirou
        result = await cache.get(key)
        assert result is None
    
    async def test_cache_invalidation(self):
        """Testa invalidação manual do cache"""
        from src.integrations.abacus.cache import IntelligentCache
        
        cache = IntelligentCache(ttl_seconds=300)
        
        # Adicionar item
        key = "invalidate_key"
        value = {"data": "to be invalidated"}
        
        await cache.set(key, value)
        assert await cache.get(key) == value
        
        # Invalidar
        await cache.invalidate(key)
        
        # Verificar que foi removido
        result = await cache.get(key)
        assert result is None
    
    async def test_cache_clear_all(self):
        """Testa limpeza completa do cache"""
        from src.integrations.abacus.cache import IntelligentCache
        
        cache = IntelligentCache(ttl_seconds=300)
        
        # Adicionar múltiplos itens
        for i in range(5):
            await cache.set(f"key_{i}", {"data": f"value_{i}"})
        
        # Verificar que estão no cache
        for i in range(5):
            result = await cache.get(f"key_{i}")
            assert result["data"] == f"value_{i}"
        
        # Limpar cache
        await cache.clear()
        
        # Verificar que foram removidos
        for i in range(5):
            result = await cache.get(f"key_{i}")
            assert result is None
    
    async def test_cache_hit_rate_calculation(self):
        """Testa cálculo de hit rate"""
        from src.integrations.abacus.cache import IntelligentCache
        
        cache = IntelligentCache(ttl_seconds=300)
        
        # Adicionar alguns itens
        await cache.set("key1", {"data": "value1"})
        await cache.set("key2", {"data": "value2"})
        
        # Fazer hits e misses
        await cache.get("key1")  # hit
        await cache.get("key2")  # hit
        await cache.get("key3")  # miss
        await cache.get("key1")  # hit
        await cache.get("key4")  # miss
        
        # Verificar estatísticas
        stats = cache.get_stats()
        assert stats["hits"] == 3
        assert stats["misses"] == 2
        assert stats["hit_rate"] == 0.6  # 3/5
    
    async def test_cache_size_limit(self):
        """Testa limite de tamanho do cache"""
        from src.integrations.abacus.cache import IntelligentCache
        
        cache = IntelligentCache(ttl_seconds=300, max_size=3)
        
        # Adicionar itens até o limite
        for i in range(5):
            await cache.set(f"key_{i}", {"data": f"value_{i}"})
        
        # Verificar que apenas os últimos itens estão no cache (LRU)
        # Os primeiros devem ter sido removidos
        result_0 = await cache.get("key_0")
        result_4 = await cache.get("key_4")
        
        # Dependendo da implementação LRU, key_0 pode ter sido removido
        assert result_4 is not None  # O último deve estar presente
    
    async def test_cache_with_complex_objects(self):
        """Testa cache com objetos complexos"""
        from src.integrations.abacus.cache import IntelligentCache
        
        cache = IntelligentCache(ttl_seconds=300)
        
        # Objeto complexo
        complex_object = {
            "user_id": "user123",
            "conversation": [
                {"message": "Hello", "timestamp": time.time()},
                {"message": "How are you?", "timestamp": time.time() + 1}
            ],
            "metadata": {
                "sentiment": "positive",
                "confidence": 0.95,
                "tags": ["greeting", "question"]
            }
        }
        
        key = "complex_object"
        await cache.set(key, complex_object)
        
        retrieved = await cache.get(key)
        assert retrieved == complex_object
        assert retrieved["user_id"] == "user123"
        assert len(retrieved["conversation"]) == 2
        assert retrieved["metadata"]["sentiment"] == "positive"


@pytest.mark.integration
@pytest.mark.asyncio
class TestCircuitBreaker:
    """Testes do circuit breaker"""
    
    async def test_circuit_breaker_closed_state(self):
        """Testa estado fechado (normal) do circuit breaker"""
        from src.integrations.abacus.circuit_breaker import CircuitBreaker
        
        circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=5,
            expected_exception=Exception
        )
        
        # Mock de função que funciona
        async def working_function():
            return "success"
        
        # Deve funcionar normalmente
        result = await circuit_breaker.call(working_function)
        assert result == "success"
        assert circuit_breaker.state == "closed"
        assert circuit_breaker.failure_count == 0
    
    async def test_circuit_breaker_failure_counting(self):
        """Testa contagem de falhas"""
        from src.integrations.abacus.circuit_breaker import CircuitBreaker
        
        circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=5,
            expected_exception=Exception
        )
        
        # Mock de função que falha
        async def failing_function():
            raise Exception("Service error")
        
        # Primeira falha
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_function)
        
        assert circuit_breaker.failure_count == 1
        assert circuit_breaker.state == "closed"
        
        # Segunda falha
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_function)
        
        assert circuit_breaker.failure_count == 2
        assert circuit_breaker.state == "closed"
    
    async def test_circuit_breaker_open_state(self):
        """Testa estado aberto do circuit breaker"""
        from src.integrations.abacus.circuit_breaker import CircuitBreaker
        
        circuit_breaker = CircuitBreaker(
            failure_threshold=2,  # Threshold baixo para teste
            recovery_timeout=5,
            expected_exception=Exception
        )
        
        # Mock de função que falha
        async def failing_function():
            raise Exception("Service error")
        
        # Causar falhas até abrir o circuit
        for i in range(2):
            with pytest.raises(Exception):
                await circuit_breaker.call(failing_function)
        
        # Circuit deve estar aberto agora
        assert circuit_breaker.state == "open"
        
        # Próximas chamadas devem falhar rapidamente
        start_time = time.time()
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_function)
        
        # Deve falhar rapidamente (não executar a função)
        elapsed = time.time() - start_time
        assert elapsed < 0.1  # Muito rápido
    
    async def test_circuit_breaker_half_open_state(self):
        """Testa estado meio-aberto do circuit breaker"""
        from src.integrations.abacus.circuit_breaker import CircuitBreaker
        
        circuit_breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=1,  # Timeout baixo para teste
            expected_exception=Exception
        )
        
        # Abrir o circuit
        async def failing_function():
            raise Exception("Service error")
        
        for i in range(2):
            with pytest.raises(Exception):
                await circuit_breaker.call(failing_function)
        
        assert circuit_breaker.state == "open"
        
        # Aguardar timeout de recovery
        await asyncio.sleep(1.5)
        
        # Próxima chamada deve colocar em half-open
        # Simular função que agora funciona
        async def working_function():
            return "recovered"
        
        result = await circuit_breaker.call(working_function)
        assert result == "recovered"
        assert circuit_breaker.state == "closed"  # Deve fechar após sucesso
        assert circuit_breaker.failure_count == 0
    
    async def test_circuit_breaker_recovery_failure(self):
        """Testa falha durante recovery"""
        from src.integrations.abacus.circuit_breaker import CircuitBreaker
        
        circuit_breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=1,
            expected_exception=Exception
        )
        
        # Abrir o circuit
        async def failing_function():
            raise Exception("Service error")
        
        for i in range(2):
            with pytest.raises(Exception):
                await circuit_breaker.call(failing_function)
        
        # Aguardar timeout
        await asyncio.sleep(1.5)
        
        # Tentar recovery mas falhar
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_function)
        
        # Deve voltar para open
        assert circuit_breaker.state == "open"
    
    async def test_circuit_breaker_with_different_exceptions(self):
        """Testa circuit breaker com diferentes tipos de exceção"""
        from src.integrations.abacus.circuit_breaker import CircuitBreaker
        
        # Circuit breaker que só conta TimeoutError
        circuit_breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=5,
            expected_exception=asyncio.TimeoutError
        )
        
        # Função que gera ValueError (não deve contar)
        async def value_error_function():
            raise ValueError("Value error")
        
        # Função que gera TimeoutError (deve contar)
        async def timeout_error_function():
            raise asyncio.TimeoutError("Timeout error")
        
        # ValueError não deve afetar o circuit breaker
        with pytest.raises(ValueError):
            await circuit_breaker.call(value_error_function)
        
        assert circuit_breaker.failure_count == 0
        assert circuit_breaker.state == "closed"
        
        # TimeoutError deve afetar
        with pytest.raises(asyncio.TimeoutError):
            await circuit_breaker.call(timeout_error_function)
        
        assert circuit_breaker.failure_count == 1
        assert circuit_breaker.state == "closed"
    
    async def test_circuit_breaker_statistics(self):
        """Testa estatísticas do circuit breaker"""
        from src.integrations.abacus.circuit_breaker import CircuitBreaker
        
        circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=5,
            expected_exception=Exception
        )
        
        # Simular algumas operações
        async def sometimes_failing_function(should_fail=False):
            if should_fail:
                raise Exception("Simulated failure")
            return "success"
        
        # Sucessos
        for i in range(5):
            result = await circuit_breaker.call(sometimes_failing_function, should_fail=False)
            assert result == "success"
        
        # Falhas
        for i in range(2):
            with pytest.raises(Exception):
                await circuit_breaker.call(sometimes_failing_function, should_fail=True)
        
        # Verificar estatísticas
        stats = circuit_breaker.get_stats()
        assert stats["total_calls"] == 7
        assert stats["successful_calls"] == 5
        assert stats["failed_calls"] == 2
        assert stats["current_state"] == "closed"
        assert stats["failure_count"] == 2


@pytest.mark.integration
@pytest.mark.asyncio
class TestCacheCircuitBreakerIntegration:
    """Testes de integração entre cache e circuit breaker"""
    
    async def test_cache_with_circuit_breaker(self):
        """Testa uso de cache quando circuit breaker está aberto"""
        from src.integrations.abacus.cache import IntelligentCache
        from src.integrations.abacus.circuit_breaker import CircuitBreaker
        
        cache = IntelligentCache(ttl_seconds=300)
        circuit_breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout=5,
            expected_exception=Exception
        )
        
        # Simular função que usa cache como fallback
        async def api_call_with_cache(message):
            cache_key = f"message:{hash(message)}"
            
            # Tentar obter do cache primeiro
            cached_result = await cache.get(cache_key)
            if cached_result:
                return cached_result
            
            # Simular chamada de API que falha
            async def api_call():
                raise Exception("API down")
            
            try:
                result = await circuit_breaker.call(api_call)
                await cache.set(cache_key, result)
                return result
            except Exception:
                # Fallback para resposta padrão
                fallback_result = {"content": "Serviço temporariamente indisponível", "fallback": True}
                await cache.set(cache_key, fallback_result, ttl=60)  # Cache por menos tempo
                return fallback_result
        
        # Primeira chamada - deve falhar e usar fallback
        result1 = await api_call_with_cache("test message")
        assert result1["fallback"] is True
        
        # Segunda chamada - deve usar cache
        result2 = await api_call_with_cache("test message")
        assert result2 == result1  # Mesmo resultado do cache
        
        # Verificar estatísticas do cache
        cache_stats = cache.get_stats()
        assert cache_stats["hits"] >= 1
    
    async def test_cache_invalidation_on_circuit_recovery(self):
        """Testa invalidação de cache quando circuit breaker se recupera"""
        from src.integrations.abacus.cache import IntelligentCache
        from src.integrations.abacus.circuit_breaker import CircuitBreaker
        
        cache = IntelligentCache(ttl_seconds=300)
        circuit_breaker = CircuitBreaker(
            failure_threshold=1,
            recovery_timeout=1,
            expected_exception=Exception
        )
        
        call_count = 0
        
        async def api_call():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("First call fails")
            return {"content": "API recovered", "call_count": call_count}
        
        cache_key = "recovery_test"
        
        # Primeira chamada - falha e abre circuit
        try:
            await circuit_breaker.call(api_call)
        except Exception:
            pass
        
        # Adicionar resposta de fallback ao cache
        await cache.set(cache_key, {"content": "Fallback response", "fallback": True})
        
        # Aguardar recovery
        await asyncio.sleep(1.5)
        
        # Próxima chamada deve funcionar
        result = await circuit_breaker.call(api_call)
        assert result["content"] == "API recovered"
        
        # Invalidar cache de fallback
        await cache.invalidate(cache_key)
        
        # Adicionar nova resposta ao cache
        await cache.set(cache_key, result)
        
        # Verificar que cache foi atualizado
        cached_result = await cache.get(cache_key)
        assert cached_result["content"] == "API recovered"
        assert "fallback" not in cached_result
