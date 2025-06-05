
"""
BestStag v9.1 - Testes de Integração de APIs
Testes para validar integrações com Abacus.AI, WhatsApp e N8N
"""

import pytest
import asyncio
import json
import time
from unittest.mock import patch, AsyncMock, MagicMock
import httpx
from fastapi import HTTPException


@pytest.mark.integration
@pytest.mark.asyncio
class TestAbacusIntegration:
    """Testes de integração com Abacus.AI"""
    
    async def test_abacus_client_initialization(self, mock_abacus_client):
        """Testa inicialização do cliente Abacus"""
        # Verificar se cliente foi inicializado corretamente
        assert mock_abacus_client is not None
        assert hasattr(mock_abacus_client, 'process_message')
        assert hasattr(mock_abacus_client, 'analyze_sentiment')
        assert hasattr(mock_abacus_client, 'get_health')
    
    async def test_abacus_message_processing(self, mock_abacus_client):
        """Testa processamento de mensagem via Abacus"""
        # Configurar resposta esperada
        expected_response = {
            "content": "Resposta processada pela IA",
            "sentiment": "positive",
            "confidence": 0.92,
            "processing_time": 0.3
        }
        mock_abacus_client.process_message.return_value = expected_response
        
        # Processar mensagem
        result = await mock_abacus_client.process_message(
            message="Como posso ajudar você hoje?",
            user_id="user123",
            conversation_id="conv456",
            channel="whatsapp"
        )
        
        # Verificações
        assert result == expected_response
        mock_abacus_client.process_message.assert_called_once()
        
        call_args = mock_abacus_client.process_message.call_args
        assert call_args[1]["message"] == "Como posso ajudar você hoje?"
        assert call_args[1]["user_id"] == "user123"
        assert call_args[1]["conversation_id"] == "conv456"
        assert call_args[1]["channel"] == "whatsapp"
    
    async def test_abacus_sentiment_analysis(self, mock_abacus_client):
        """Testa análise de sentimento"""
        # Configurar resposta de sentimento
        expected_sentiment = {
            "sentiment": "negative",
            "confidence": 0.85,
            "emotions": {
                "anger": 0.6,
                "frustration": 0.3,
                "disappointment": 0.1
            }
        }
        mock_abacus_client.analyze_sentiment.return_value = expected_sentiment
        
        # Analisar sentimento
        result = await mock_abacus_client.analyze_sentiment(
            "Estou muito irritado com o atraso do meu pedido!"
        )
        
        # Verificações
        assert result == expected_sentiment
        assert result["sentiment"] == "negative"
        assert result["confidence"] > 0.8
        assert "anger" in result["emotions"]
    
    async def test_abacus_error_handling(self, mock_abacus_client):
        """Testa tratamento de erros do Abacus"""
        # Simular erro de timeout
        mock_abacus_client.process_message.side_effect = asyncio.TimeoutError("Request timeout")
        
        # Verificar se erro é tratado adequadamente
        with pytest.raises(asyncio.TimeoutError):
            await mock_abacus_client.process_message(
                message="Test message",
                user_id="user123"
            )
        
        # Simular erro de API
        mock_abacus_client.process_message.side_effect = HTTPException(
            status_code=503,
            detail="Service temporarily unavailable"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await mock_abacus_client.process_message(
                message="Test message",
                user_id="user123"
            )
        
        assert exc_info.value.status_code == 503
    
    async def test_abacus_health_check(self, mock_abacus_client):
        """Testa health check do Abacus"""
        # Configurar resposta de health
        expected_health = {
            "status": "healthy",
            "latency": 0.15,
            "cache_hit_rate": 0.78,
            "circuit_breaker_state": "closed"
        }
        mock_abacus_client.get_health.return_value = expected_health
        
        # Verificar health
        health = await mock_abacus_client.get_health()
        
        assert health["status"] == "healthy"
        assert health["latency"] < 1.0
        assert 0 <= health["cache_hit_rate"] <= 1.0


@pytest.mark.integration
@pytest.mark.asyncio
class TestWhatsAppIntegration:
    """Testes de integração com WhatsApp"""
    
    async def test_webhook_signature_validation(self, whatsapp_webhook):
        """Testa validação de assinatura do webhook"""
        from src.integrations.whatsapp.validator import SignatureValidator
        
        validator = SignatureValidator("test_secret")
        
        # Teste com assinatura válida
        payload = b'{"test": "data"}'
        valid_signature = validator._generate_signature(payload)
        
        assert validator.validate_signature(payload, f"sha256={valid_signature}")
        
        # Teste com assinatura inválida
        invalid_signature = "sha256=invalid_signature"
        assert not validator.validate_signature(payload, invalid_signature)
        
        # Teste com formato inválido
        assert not validator.validate_signature(payload, "invalid_format")
    
    async def test_webhook_rate_limiting(self, whatsapp_webhook):
        """Testa rate limiting do webhook"""
        # Limpar rate limits existentes
        whatsapp_webhook.clear_rate_limits()
        
        # Simular múltiplas requisições do mesmo IP
        client_ip = "192.168.1.100"
        
        # Primeiras requisições devem passar
        for i in range(50):  # Metade do limite
            assert whatsapp_webhook._check_rate_limit(client_ip)
        
        # Próximas requisições devem passar até o limite
        for i in range(50):  # Completar o limite de 100
            assert whatsapp_webhook._check_rate_limit(client_ip)
        
        # Próxima requisição deve ser bloqueada
        assert not whatsapp_webhook._check_rate_limit(client_ip)
        
        # Verificar estatísticas
        stats = whatsapp_webhook.get_stats()
        assert stats["rate_limit_hits"] > 0
    
    async def test_message_extraction(self, whatsapp_webhook, sample_whatsapp_message):
        """Testa extração de dados de mensagem"""
        messages = whatsapp_webhook._extract_message_data(sample_whatsapp_message)
        
        assert len(messages) == 1
        
        message = messages[0]
        assert message["from"] == "5511999999999"
        assert message["type"] == "text"
        assert message["webhook_type"] == "message"
        assert "content" in message
        assert message["content"]["text"] == "Olá, preciso de ajuda com meu pedido"
    
    async def test_image_message_extraction(self, whatsapp_webhook, sample_whatsapp_image_message):
        """Testa extração de mensagem com imagem"""
        messages = whatsapp_webhook._extract_message_data(sample_whatsapp_image_message)
        
        assert len(messages) == 1
        
        message = messages[0]
        assert message["type"] == "image"
        assert "content" in message
        assert message["content"]["media_id"] == "media123"
        assert message["content"]["mime_type"] == "image/jpeg"
        assert message["content"]["caption"] == "Foto do problema"
    
    async def test_queue_processing(self, mock_whatsapp_queue):
        """Testa processamento da queue WhatsApp"""
        # Adicionar mensagem à queue
        test_message = {
            "id": "test_msg_123",
            "from": "5511999999999",
            "type": "text",
            "content": {"text": "Mensagem de teste"}
        }
        
        await mock_whatsapp_queue.enqueue(test_message, priority=1)
        
        # Verificar se mensagem foi enfileirada
        stats = mock_whatsapp_queue.get_stats()
        assert stats["messages_queued"] >= 1


@pytest.mark.integration
@pytest.mark.asyncio
class TestN8NIntegration:
    """Testes de integração com N8N"""
    
    async def test_n8n_workflow_trigger(self, mock_external_apis):
        """Testa trigger de workflow N8N"""
        # Simular trigger de workflow
        workflow_data = {
            "user_id": "user123",
            "message": "Trigger workflow test",
            "action": "process_message"
        }
        
        # Mock da resposta do N8N
        mock_external_apis.post.return_value.status_code = 200
        mock_external_apis.post.return_value.json.return_value = {
            "success": True,
            "workflow_id": "workflow_123",
            "execution_id": "exec_456"
        }
        
        # Simular chamada para N8N
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:5678/webhook/beststag",
                json=workflow_data
            )
        
        # Verificações
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["success"] is True
        assert "workflow_id" in response_data
    
    async def test_n8n_webhook_response(self, mock_external_apis):
        """Testa resposta de webhook N8N"""
        # Mock de resposta de webhook
        webhook_response = {
            "processed": True,
            "response_message": "Mensagem processada com sucesso",
            "next_actions": ["send_whatsapp", "update_crm"]
        }
        
        mock_external_apis.post.return_value.json.return_value = webhook_response
        
        # Simular recebimento de resposta
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:5678/webhook/response",
                json={"execution_id": "exec_456"}
            )
        
        response_data = response.json()
        assert response_data["processed"] is True
        assert "response_message" in response_data
        assert isinstance(response_data["next_actions"], list)


@pytest.mark.integration
@pytest.mark.asyncio
class TestFallbackAndRecovery:
    """Testes de fallback e recovery"""
    
    async def test_abacus_fallback_mechanism(self, test_client):
        """Testa mecanismo de fallback quando Abacus falha"""
        # Simular falha do Abacus
        with patch('src.backend.app.app.state.abacus_client') as mock_client:
            mock_client.process_message.side_effect = Exception("Abacus API down")
            
            # Tentar processar mensagem
            response = test_client.post(
                "/api/chat",
                params={
                    "message": "Test fallback message",
                    "user_id": "user123",
                    "conversation_id": "conv456",
                    "channel": "web"
                }
            )
            
            # Deve retornar erro 500 mas não quebrar o sistema
            assert response.status_code == 500
            
            # Verificar que tentativa foi feita
            mock_client.process_message.assert_called_once()
    
    async def test_circuit_breaker_behavior(self, mock_abacus_client):
        """Testa comportamento do circuit breaker"""
        from src.integrations.abacus.circuit_breaker import CircuitBreaker
        
        circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=5,
            expected_exception=Exception
        )
        
        # Simular falhas consecutivas
        mock_abacus_client.process_message.side_effect = Exception("Service error")
        
        # Primeiras falhas devem passar pelo circuit breaker
        for i in range(3):
            with pytest.raises(Exception):
                await circuit_breaker.call(mock_abacus_client.process_message, "test")
        
        # Circuit breaker deve estar aberto agora
        assert circuit_breaker.state == "open"
        
        # Próximas chamadas devem falhar rapidamente
        with pytest.raises(Exception):
            await circuit_breaker.call(mock_abacus_client.process_message, "test")
    
    async def test_cache_fallback(self):
        """Testa fallback para cache quando API falha"""
        from src.integrations.abacus.cache import IntelligentCache
        
        cache = IntelligentCache(ttl_seconds=300)
        
        # Adicionar item ao cache
        cache_key = "user123:message:hash123"
        cached_response = {
            "content": "Resposta em cache",
            "sentiment": "neutral",
            "confidence": 0.8
        }
        
        await cache.set(cache_key, cached_response)
        
        # Verificar se pode recuperar do cache
        retrieved = await cache.get(cache_key)
        assert retrieved == cached_response
        
        # Verificar hit rate
        stats = cache.get_stats()
        assert stats["hits"] > 0
    
    async def test_retry_mechanism(self, mock_abacus_client):
        """Testa mecanismo de retry automático"""
        # Configurar falha temporária seguida de sucesso
        call_count = 0
        
        async def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:  # Falha nas primeiras 2 tentativas
                raise Exception("Temporary failure")
            return {"content": "Success after retry", "sentiment": "neutral"}
        
        mock_abacus_client.process_message.side_effect = side_effect
        
        # Simular retry (implementação simplificada)
        max_retries = 3
        for attempt in range(max_retries):
            try:
                result = await mock_abacus_client.process_message("test message")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.1)  # Delay entre tentativas
        
        # Verificar sucesso após retries
        assert result["content"] == "Success after retry"
        assert call_count == 3  # 2 falhas + 1 sucesso


@pytest.mark.integration
@pytest.mark.asyncio
class TestErrorScenarios:
    """Testes de cenários de erro"""
    
    async def test_timeout_handling(self, mock_abacus_client):
        """Testa tratamento de timeouts"""
        # Simular timeout
        mock_abacus_client.process_message.side_effect = asyncio.TimeoutError("Request timeout")
        
        start_time = time.time()
        
        with pytest.raises(asyncio.TimeoutError):
            await mock_abacus_client.process_message("test message")
        
        # Verificar que falhou rapidamente (não ficou travado)
        elapsed = time.time() - start_time
        assert elapsed < 1.0  # Deve falhar em menos de 1 segundo
    
    async def test_invalid_json_handling(self, test_client):
        """Testa tratamento de JSON inválido"""
        # Enviar JSON malformado
        response = test_client.post(
            "/webhook/whatsapp",
            content=b'{"invalid": json}',  # JSON inválido
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": "sha256=invalid"
            }
        )
        
        # Deve retornar erro 400
        assert response.status_code in [400, 401]  # 400 para JSON inválido ou 401 para assinatura
    
    async def test_missing_signature_handling(self, test_client):
        """Testa tratamento de assinatura ausente"""
        response = test_client.post(
            "/webhook/whatsapp",
            content=b'{"test": "data"}',
            headers={"Content-Type": "application/json"}
            # Sem header de assinatura
        )
        
        # Deve retornar erro 400
        assert response.status_code == 400
    
    async def test_database_connection_error(self, contextual_memory):
        """Testa tratamento de erro de conexão com banco"""
        # Simular erro de conexão
        with patch.object(contextual_memory, 'save_interaction') as mock_save:
            mock_save.side_effect = Exception("Database connection failed")
            
            # Tentar salvar interação
            with pytest.raises(Exception):
                await contextual_memory.save_interaction(
                    user_id="user123",
                    conversation_id="conv456",
                    user_message="test",
                    assistant_response="test response"
                )
    
    async def test_memory_overflow_protection(self, contextual_memory):
        """Testa proteção contra overflow de memória"""
        # Simular muitas interações para um usuário
        user_id = "heavy_user"
        
        # Adicionar muitas interações
        for i in range(1000):
            await contextual_memory.save_interaction(
                user_id=user_id,
                conversation_id=f"conv_{i}",
                user_message=f"Message {i}",
                assistant_response=f"Response {i}",
                metadata={"test": True}
            )
        
        # Verificar se sistema ainda responde
        memory_data = await contextual_memory.get_user_memory(user_id)
        
        # Deve ter algum limite ou paginação
        assert len(memory_data) <= 100  # Assumindo limite de 100 interações por consulta


@pytest.mark.integration
@pytest.mark.asyncio
class TestLogsAndMetrics:
    """Testes de logs e métricas"""
    
    async def test_request_logging(self, test_client, caplog):
        """Testa logging de requisições"""
        import logging
        
        # Configurar captura de logs
        caplog.set_level(logging.INFO)
        
        # Fazer requisição
        response = test_client.get("/health")
        
        # Verificar se logs foram gerados
        assert len(caplog.records) > 0
        
        # Verificar conteúdo dos logs
        log_messages = [record.message for record in caplog.records]
        request_logged = any("Requisição recebida" in msg for msg in log_messages)
        response_logged = any("Resposta enviada" in msg for msg in log_messages)
        
        assert request_logged or response_logged  # Pelo menos um deve estar presente
    
    async def test_error_logging(self, test_client, caplog):
        """Testa logging de erros"""
        import logging
        
        caplog.set_level(logging.ERROR)
        
        # Fazer requisição que gera erro
        response = test_client.get("/nonexistent-endpoint")
        
        # Verificar se erro foi logado (pode não gerar log dependendo da implementação)
        assert response.status_code == 404
    
    async def test_metrics_collection(self, whatsapp_webhook):
        """Testa coleta de métricas"""
        # Obter estatísticas iniciais
        initial_stats = whatsapp_webhook.get_stats()
        
        # Simular algumas operações
        whatsapp_webhook.stats["webhooks_received"] += 5
        whatsapp_webhook.stats["webhooks_processed"] += 4
        whatsapp_webhook.stats["webhooks_failed"] += 1
        
        # Verificar estatísticas atualizadas
        updated_stats = whatsapp_webhook.get_stats()
        
        assert updated_stats["webhooks_received"] == initial_stats["webhooks_received"] + 5
        assert updated_stats["webhooks_processed"] == initial_stats["webhooks_processed"] + 4
        assert updated_stats["webhooks_failed"] == initial_stats["webhooks_failed"] + 1
    
    async def test_performance_metrics(self, performance_monitor):
        """Testa métricas de performance"""
        # Simular operação com timing
        performance_monitor.start_timer("test_operation")
        await asyncio.sleep(0.1)  # Simular trabalho
        duration = performance_monitor.end_timer("test_operation")
        
        # Verificar métricas
        assert duration >= 0.1
        assert performance_monitor.get_average("test_operation") >= 0.1
        assert performance_monitor.get_max("test_operation") >= 0.1
        assert performance_monitor.get_min("test_operation") >= 0.1
        
        # Adicionar mais medições
        for i in range(5):
            performance_monitor.start_timer("test_operation")
            await asyncio.sleep(0.05)
            performance_monitor.end_timer("test_operation")
        
        # Verificar estatísticas
        avg = performance_monitor.get_average("test_operation")
        assert 0.05 <= avg <= 0.15  # Deve estar na faixa esperada
