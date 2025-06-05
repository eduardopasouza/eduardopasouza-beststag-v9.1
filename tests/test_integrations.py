
"""
BestStag v9.1 - Testes das Integrações Otimizadas
Testes unitários e de integração para os novos módulos otimizados
"""

import pytest
import asyncio
import time
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

# Imports das integrações
from src.integrations.abacus.cache import IntelligentCache, initialize_cache
from src.integrations.abacus.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitState
from src.integrations.abacus.client import AbacusOptimizedClient
from src.integrations.whatsapp.validator import SignatureValidator
from src.integrations.whatsapp.queue import WhatsAppQueue, MessageStatus
from src.integrations.common.metrics import MetricsCollector, IntegrationMetrics


class TestIntelligentCache:
    """Testes para o sistema de cache inteligente"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.cache = IntelligentCache(default_ttl=60, max_size=10)
    
    def test_cache_basic_operations(self):
        """Testa operações básicas do cache"""
        # Set e get
        self.cache.set("test_endpoint", {"param": "value"}, "test_data")
        result = self.cache.get("test_endpoint", {"param": "value"})
        
        assert result == "test_data"
        
        # Cache miss
        result = self.cache.get("nonexistent", {"param": "value"})
        assert result is None
    
    def test_cache_ttl_expiration(self):
        """Testa expiração do cache por TTL"""
        # Set com TTL curto
        self.cache.set("test_endpoint", {"param": "value"}, "test_data", ttl=1)
        
        # Deve estar disponível imediatamente
        result = self.cache.get("test_endpoint", {"param": "value"})
        assert result == "test_data"
        
        # Aguardar expiração
        time.sleep(1.1)
        
        # Deve ter expirado
        result = self.cache.get("test_endpoint", {"param": "value"})
        assert result is None
    
    def test_cache_stats(self):
        """Testa estatísticas do cache"""
        # Operações para gerar estatísticas
        self.cache.set("endpoint1", {"param": "1"}, "data1")
        self.cache.get("endpoint1", {"param": "1"})  # Hit
        self.cache.get("endpoint2", {"param": "2"})  # Miss
        
        stats = self.cache.get_stats()
        
        assert stats['hits'] == 1
        assert stats['misses'] == 1
        assert stats['sets'] == 1
        assert stats['hit_rate_percent'] == 50.0
    
    def test_cache_invalidation(self):
        """Testa invalidação do cache"""
        # Adicionar dados
        self.cache.set("endpoint1", {"param": "1"}, "data1")
        self.cache.set("endpoint2", {"param": "2"}, "data2")
        
        # Verificar que estão lá
        assert self.cache.get("endpoint1", {"param": "1"}) == "data1"
        assert self.cache.get("endpoint2", {"param": "2"}) == "data2"
        
        # Invalidar por padrão
        self.cache.invalidate("endpoint1")
        
        # Verificar invalidação
        assert self.cache.get("endpoint1", {"param": "1"}) is None
        assert self.cache.get("endpoint2", {"param": "2"}) == "data2"


class TestCircuitBreaker:
    """Testes para o circuit breaker"""
    
    def setup_method(self):
        """Setup para cada teste"""
        config = CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=1,
            success_threshold=2
        )
        self.circuit_breaker = CircuitBreaker("test_cb", config)
    
    def test_circuit_breaker_closed_state(self):
        """Testa estado fechado do circuit breaker"""
        assert self.circuit_breaker.state == CircuitState.CLOSED
        assert self.circuit_breaker.is_closed
        assert not self.circuit_breaker.is_open
    
    def test_circuit_breaker_opens_on_failures(self):
        """Testa abertura do circuit breaker por falhas"""
        def failing_function():
            raise Exception("Test failure")
        
        # Executar falhas até abrir
        for i in range(3):
            with pytest.raises(Exception):
                self.circuit_breaker.call(failing_function)
        
        # Deve estar aberto agora
        assert self.circuit_breaker.state == CircuitState.OPEN
        assert self.circuit_breaker.is_open
    
    def test_circuit_breaker_recovery(self):
        """Testa recuperação do circuit breaker"""
        def failing_function():
            raise Exception("Test failure")
        
        def success_function():
            return "success"
        
        # Forçar abertura
        self.circuit_breaker.force_open()
        assert self.circuit_breaker.is_open
        
        # Aguardar timeout de recovery
        time.sleep(1.1)
        
        # Primeira chamada deve mudar para half-open
        result = self.circuit_breaker.call(success_function)
        assert result == "success"
        assert self.circuit_breaker.state == CircuitState.HALF_OPEN
        
        # Segunda chamada bem-sucedida deve fechar
        result = self.circuit_breaker.call(success_function)
        assert result == "success"
        assert self.circuit_breaker.is_closed
    
    def test_circuit_breaker_fallback(self):
        """Testa função de fallback"""
        def failing_function():
            raise Exception("Test failure")
        
        def fallback_function():
            return "fallback_result"
        
        # Criar circuit breaker com fallback
        config = CircuitBreakerConfig(failure_threshold=1)
        cb_with_fallback = CircuitBreaker("test_fallback", config, fallback_function)
        
        # Forçar abertura
        cb_with_fallback.force_open()
        
        # Deve retornar fallback
        result = cb_with_fallback.call(failing_function)
        assert result == "fallback_result"
    
    def test_circuit_breaker_stats(self):
        """Testa estatísticas do circuit breaker"""
        def success_function():
            return "success"
        
        # Executar algumas operações
        for i in range(5):
            self.circuit_breaker.call(success_function)
        
        stats = self.circuit_breaker.get_stats()
        
        assert stats['name'] == "test_cb"
        assert stats['state'] == CircuitState.CLOSED.value
        assert stats['successful_requests'] == 5
        assert stats['failed_requests'] == 0


class TestSignatureValidator:
    """Testes para validação de assinatura WhatsApp"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.validator = SignatureValidator("test_secret_key")
    
    def test_signature_generation(self):
        """Testa geração de assinatura"""
        payload = "test payload"
        signature = self.validator.generate_signature(payload)
        
        assert signature.startswith("sha256=")
        assert len(signature) == 71  # sha256= + 64 chars hex
    
    def test_signature_validation_success(self):
        """Testa validação bem-sucedida"""
        payload = "test payload"
        signature = self.validator.generate_signature(payload)
        
        is_valid = self.validator.validate_signature(payload, signature)
        assert is_valid
    
    def test_signature_validation_failure(self):
        """Testa validação com assinatura inválida"""
        payload = "test payload"
        invalid_signature = "sha256=invalid_signature_hash"
        
        is_valid = self.validator.validate_signature(payload, invalid_signature)
        assert not is_valid
    
    def test_signature_validation_different_payload(self):
        """Testa validação com payload diferente"""
        payload1 = "test payload 1"
        payload2 = "test payload 2"
        
        signature1 = self.validator.generate_signature(payload1)
        
        is_valid = self.validator.validate_signature(payload2, signature1)
        assert not is_valid
    
    def test_webhook_request_validation(self):
        """Testa validação de requisição completa"""
        body = b'{"test": "data"}'
        signature = self.validator.generate_signature(body)
        
        is_valid = self.validator.validate_webhook_request(body, signature)
        assert is_valid
        
        # Teste com header inválido
        is_valid = self.validator.validate_webhook_request(body, "invalid_header")
        assert not is_valid
        
        # Teste sem header
        is_valid = self.validator.validate_webhook_request(body, "")
        assert not is_valid


class TestMetricsCollector:
    """Testes para coletor de métricas"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.metrics = MetricsCollector(retention_hours=1)
    
    def test_counter_operations(self):
        """Testa operações de contador"""
        # Incrementar contador
        self.metrics.increment_counter("test_counter", 5.0)
        self.metrics.increment_counter("test_counter", 3.0)
        
        # Verificar valor
        value = self.metrics.get_counter("test_counter")
        assert value == 8.0
    
    def test_gauge_operations(self):
        """Testa operações de gauge"""
        # Definir gauge
        self.metrics.set_gauge("test_gauge", 42.0)
        
        # Verificar valor
        value = self.metrics.get_gauge("test_gauge")
        assert value == 42.0
        
        # Atualizar gauge
        self.metrics.set_gauge("test_gauge", 100.0)
        value = self.metrics.get_gauge("test_gauge")
        assert value == 100.0
    
    def test_histogram_operations(self):
        """Testa operações de histograma"""
        # Registrar valores
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        for value in values:
            self.metrics.record_histogram("test_histogram", value)
        
        # Verificar estatísticas
        stats = self.metrics.get_histogram_stats("test_histogram")
        
        assert stats['count'] == 5
        assert stats['sum'] == 15.0
        assert stats['avg'] == 3.0
        assert stats['min'] == 1.0
        assert stats['max'] == 5.0
    
    def test_metrics_with_labels(self):
        """Testa métricas com labels"""
        labels1 = {"service": "api", "method": "GET"}
        labels2 = {"service": "api", "method": "POST"}
        
        # Incrementar contadores com labels diferentes
        self.metrics.increment_counter("requests", 10.0, labels1)
        self.metrics.increment_counter("requests", 5.0, labels2)
        
        # Verificar valores separados
        value1 = self.metrics.get_counter("requests", labels1)
        value2 = self.metrics.get_counter("requests", labels2)
        
        assert value1 == 10.0
        assert value2 == 5.0
    
    def test_time_function_decorator(self):
        """Testa decorador de tempo de função"""
        @self.metrics.time_function("test_function")
        def test_function():
            time.sleep(0.1)
            return "result"
        
        # Executar função
        result = test_function()
        assert result == "result"
        
        # Verificar métricas
        duration_stats = self.metrics.get_histogram_stats("test_function_duration_seconds")
        assert duration_stats['count'] == 1
        assert duration_stats['avg'] >= 0.1
        
        total_count = self.metrics.get_counter("test_function_total")
        assert total_count == 1.0
    
    def test_prometheus_export(self):
        """Testa exportação para formato Prometheus"""
        # Adicionar algumas métricas
        self.metrics.increment_counter("http_requests_total", 100.0, {"status": "200"})
        self.metrics.set_gauge("memory_usage_bytes", 1024.0)
        self.metrics.record_histogram("request_duration_seconds", 0.5)
        
        # Exportar
        prometheus_output = self.metrics.export_prometheus()
        
        # Verificar formato
        assert "http_requests_total{status=\"200\"} 100.0" in prometheus_output
        assert "memory_usage_bytes 1024.0" in prometheus_output
        assert "request_duration_seconds_count 1" in prometheus_output


@pytest.mark.asyncio
class TestWhatsAppQueue:
    """Testes para queue WhatsApp"""
    
    async def test_queue_basic_operations(self):
        """Testa operações básicas da queue"""
        # Mock Redis para testes
        with patch('redis.asyncio.from_url') as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis.return_value = mock_redis_instance
            
            queue = WhatsAppQueue(redis_url="redis://localhost:6379")
            await queue.connect()
            
            # Testar enqueue
            message_id = await queue.enqueue({"type": "text", "content": "test message"})
            assert message_id is not None
            
            # Verificar estatísticas
            stats = await queue.get_stats()
            assert stats['messages_received'] == 1


@pytest.mark.asyncio
class TestAbacusOptimizedClient:
    """Testes para cliente Abacus otimizado"""
    
    async def test_client_initialization(self):
        """Testa inicialização do cliente"""
        with patch.dict('os.environ', {'ABACUS_API_KEY': 'test_key'}):
            client = AbacusOptimizedClient()
            
            assert client.api_key == 'test_key'
            assert client.base_url == "https://api.abacus.ai/v1"
            assert client.timeout == 30.0
    
    async def test_rate_limiting(self):
        """Testa rate limiting do cliente"""
        with patch.dict('os.environ', {'ABACUS_API_KEY': 'test_key'}):
            client = AbacusOptimizedClient(rate_limit_per_minute=2)
            
            # Primeira requisição deve passar
            assert client._check_rate_limit() == True
            
            # Segunda requisição deve passar
            assert client._check_rate_limit() == True
            
            # Terceira requisição deve falhar
            assert client._check_rate_limit() == False
    
    async def test_health_check(self):
        """Testa health check do cliente"""
        with patch.dict('os.environ', {'ABACUS_API_KEY': 'test_key'}):
            client = AbacusOptimizedClient()
            
            # Mock da requisição
            with patch.object(client, '_make_request') as mock_request:
                mock_request.return_value = {"response": "ok"}
                
                health = await client.health_check()
                
                assert health['status'] == 'healthy'
                assert 'response_time' in health
                assert 'circuit_breaker_state' in health


class TestIntegrationMetrics:
    """Testes para métricas de integração"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.integration_metrics = IntegrationMetrics("test_integration")
    
    def test_record_request(self):
        """Testa registro de requisição"""
        # Registrar requisição bem-sucedida
        self.integration_metrics.record_request("test_endpoint", True, 0.5)
        
        # Verificar métricas
        metrics = self.integration_metrics.metrics
        
        requests_count = metrics.get_counter("integration_requests_total", {
            'integration': 'test_integration',
            'endpoint': 'test_endpoint',
            'success': 'True'
        })
        assert requests_count == 1.0
        
        duration_stats = metrics.get_histogram_stats("integration_request_duration_seconds", {
            'integration': 'test_integration',
            'endpoint': 'test_endpoint',
            'success': 'True'
        })
        assert duration_stats['count'] == 1
        assert duration_stats['avg'] == 0.5
    
    def test_record_error(self):
        """Testa registro de erro"""
        self.integration_metrics.record_error("ConnectionError", "test_endpoint")
        
        # Verificar métricas
        metrics = self.integration_metrics.metrics
        
        errors_count = metrics.get_counter("integration_errors_total", {
            'integration': 'test_integration',
            'error_type': 'ConnectionError',
            'endpoint': 'test_endpoint'
        })
        assert errors_count == 1.0
    
    def test_connection_status(self):
        """Testa status de conexão"""
        # Definir como conectado
        self.integration_metrics.set_connection_status(True)
        
        # Verificar métrica
        metrics = self.integration_metrics.metrics
        
        connected_status = metrics.get_gauge("integration_connected", {
            'integration': 'test_integration'
        })
        assert connected_status == 1.0
        
        # Definir como desconectado
        self.integration_metrics.set_connection_status(False)
        
        connected_status = metrics.get_gauge("integration_connected", {
            'integration': 'test_integration'
        })
        assert connected_status == 0.0


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v"])
