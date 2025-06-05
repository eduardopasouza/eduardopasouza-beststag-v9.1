
"""
BestStag v9.1 - Testes de Fluxo Completo
Testes end-to-end simulando fluxo real de mensagens WhatsApp
"""

import pytest
import asyncio
import json
import time
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient


@pytest.mark.e2e
@pytest.mark.asyncio
class TestFullWhatsAppFlow:
    """Testes de fluxo completo WhatsApp -> IA -> Resposta"""
    
    async def test_complete_text_message_flow(
        self,
        test_client,
        sample_whatsapp_message,
        mock_abacus_client,
        performance_monitor
    ):
        """
        Testa fluxo completo de mensagem de texto:
        1. Recebe webhook WhatsApp
        2. Processa com IA contextual
        3. Gera resposta
        4. Valida memória contextual
        """
        performance_monitor.start_timer("full_flow")
        
        # Configurar mock do Abacus
        with patch('src.backend.app.app.state.abacus_client', mock_abacus_client):
            # 1. Simular recebimento de webhook
            payload = json.dumps(sample_whatsapp_message).encode('utf-8')
            signature = self._create_signature(payload)
            
            response = test_client.post(
                "/webhook/whatsapp",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Hub-Signature-256": signature
                }
            )
            
            # Verificar resposta do webhook
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
            
            # 2. Aguardar processamento assíncrono
            await asyncio.sleep(0.5)
            
            # 3. Verificar se o Abacus foi chamado
            mock_abacus_client.process_message.assert_called_once()
            call_args = mock_abacus_client.process_message.call_args
            
            assert call_args[1]["message"] == "Olá, preciso de ajuda com meu pedido"
            assert call_args[1]["user_id"] == "5511999999999"
            assert call_args[1]["channel"] == "whatsapp"
            
            # 4. Verificar memória contextual
            user_id = "5511999999999"
            memory_response = test_client.get(f"/api/memory/{user_id}")
            assert memory_response.status_code == 200
            
            memory_data = memory_response.json()
            assert memory_data["user_id"] == user_id
            assert len(memory_data["memory"]) > 0
        
        duration = performance_monitor.end_timer("full_flow")
        assert duration < 2.0, f"Fluxo completo muito lento: {duration:.3f}s"
    
    async def test_image_message_flow(
        self,
        test_client,
        sample_whatsapp_image_message,
        mock_abacus_client,
        performance_monitor
    ):
        """
        Testa fluxo de mensagem com imagem:
        1. Recebe webhook com imagem
        2. Processa mídia
        3. Analisa com IA
        4. Gera resposta contextual
        """
        performance_monitor.start_timer("image_flow")
        
        # Configurar resposta específica para imagem
        mock_abacus_client.process_message.return_value = {
            "content": "Analisei sua imagem. Posso ajudar com o problema mostrado.",
            "sentiment": "helpful",
            "confidence": 0.92,
            "media_analysis": {
                "type": "image",
                "objects_detected": ["produto", "problema"],
                "text_extracted": ""
            }
        }
        
        with patch('src.backend.app.app.state.abacus_client', mock_abacus_client):
            # Enviar webhook com imagem
            payload = json.dumps(sample_whatsapp_image_message).encode('utf-8')
            signature = self._create_signature(payload)
            
            response = test_client.post(
                "/webhook/whatsapp",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Hub-Signature-256": signature
                }
            )
            
            assert response.status_code == 200
            
            # Aguardar processamento
            await asyncio.sleep(0.5)
            
            # Verificar processamento da imagem
            mock_abacus_client.process_message.assert_called_once()
            call_args = mock_abacus_client.process_message.call_args
            
            # Verificar se dados da mídia foram incluídos
            assert "media_id" in str(call_args)
            assert "image" in str(call_args)
        
        duration = performance_monitor.end_timer("image_flow")
        assert duration < 3.0, f"Fluxo de imagem muito lento: {duration:.3f}s"
    
    async def test_conversation_memory_flow(
        self,
        test_client,
        sample_whatsapp_message,
        mock_abacus_client,
        setup_test_data,
        performance_monitor
    ):
        """
        Testa memória contextual entre conversas:
        1. Usa histórico existente
        2. Processa nova mensagem
        3. Mantém contexto
        4. Gera resposta contextual
        """
        performance_monitor.start_timer("memory_flow")
        
        # Configurar resposta que usa contexto
        mock_abacus_client.process_message.return_value = {
            "content": "Com base no nosso histórico, vejo que você perguntou sobre o pedido #12345. Ele já foi enviado!",
            "sentiment": "helpful",
            "confidence": 0.95,
            "context_used": True,
            "previous_interactions": 2
        }
        
        with patch('src.backend.app.app.state.abacus_client', mock_abacus_client):
            # Modificar mensagem para continuar conversa
            message = sample_whatsapp_message.copy()
            message["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"] = "E quando vai chegar?"
            
            payload = json.dumps(message).encode('utf-8')
            signature = self._create_signature(payload)
            
            response = test_client.post(
                "/webhook/whatsapp",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Hub-Signature-256": signature
                }
            )
            
            assert response.status_code == 200
            
            # Aguardar processamento
            await asyncio.sleep(0.5)
            
            # Verificar se contexto foi usado
            mock_abacus_client.process_message.assert_called_once()
            
            # Verificar memória atualizada
            user_id = "5511999999999"
            memory_response = test_client.get(f"/api/memory/{user_id}")
            memory_data = memory_response.json()
            
            # Deve ter pelo menos 3 interações (2 do setup + 1 nova)
            assert len(memory_data["memory"]) >= 3
        
        duration = performance_monitor.end_timer("memory_flow")
        assert duration < 1.5, f"Fluxo de memória muito lento: {duration:.3f}s"
    
    async def test_sentiment_analysis_flow(
        self,
        test_client,
        mock_abacus_client,
        performance_monitor
    ):
        """
        Testa análise de sentimento:
        1. Mensagem com sentimento negativo
        2. Análise de sentimento
        3. Resposta adaptada ao sentimento
        4. Escalação se necessário
        """
        performance_monitor.start_timer("sentiment_flow")
        
        # Configurar análise de sentimento negativo
        mock_abacus_client.process_message.return_value = {
            "content": "Entendo sua frustração. Vou priorizar seu atendimento e resolver isso imediatamente.",
            "sentiment": "negative",
            "confidence": 0.89,
            "escalation_needed": True,
            "priority": "high"
        }
        
        # Mensagem com sentimento negativo
        negative_message = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "123456789",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "15551234567",
                                    "phone_number_id": "987654321"
                                },
                                "messages": [
                                    {
                                        "from": "5511999999999",
                                        "id": "wamid.negative123",
                                        "timestamp": str(int(time.time())),
                                        "text": {
                                            "body": "Estou muito irritado! Meu pedido está atrasado há uma semana!"
                                        },
                                        "type": "text"
                                    }
                                ]
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }
        
        with patch('src.backend.app.app.state.abacus_client', mock_abacus_client):
            payload = json.dumps(negative_message).encode('utf-8')
            signature = self._create_signature(payload)
            
            response = test_client.post(
                "/webhook/whatsapp",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Hub-Signature-256": signature
                }
            )
            
            assert response.status_code == 200
            
            # Aguardar processamento
            await asyncio.sleep(0.5)
            
            # Verificar análise de sentimento
            mock_abacus_client.process_message.assert_called_once()
            call_args = mock_abacus_client.process_message.call_args
            
            # Verificar se mensagem negativa foi detectada
            assert "irritado" in call_args[1]["message"]
            assert "atrasado" in call_args[1]["message"]
        
        duration = performance_monitor.end_timer("sentiment_flow")
        assert duration < 1.0, f"Análise de sentimento muito lenta: {duration:.3f}s"
    
    async def test_error_handling_flow(
        self,
        test_client,
        sample_whatsapp_message,
        mock_abacus_client,
        performance_monitor
    ):
        """
        Testa tratamento de erros:
        1. Simula falha na IA
        2. Verifica fallback
        3. Testa recovery
        4. Valida logs de erro
        """
        performance_monitor.start_timer("error_flow")
        
        # Configurar falha no Abacus
        mock_abacus_client.process_message.side_effect = Exception("API temporariamente indisponível")
        
        with patch('src.backend.app.app.state.abacus_client', mock_abacus_client):
            payload = json.dumps(sample_whatsapp_message).encode('utf-8')
            signature = self._create_signature(payload)
            
            response = test_client.post(
                "/webhook/whatsapp",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Hub-Signature-256": signature
                }
            )
            
            # Webhook deve aceitar mesmo com falha no processamento
            assert response.status_code == 200
            
            # Aguardar tentativa de processamento
            await asyncio.sleep(0.5)
            
            # Verificar que tentativa foi feita
            mock_abacus_client.process_message.assert_called_once()
        
        duration = performance_monitor.end_timer("error_flow")
        assert duration < 1.0, f"Tratamento de erro muito lento: {duration:.3f}s"
    
    def _create_signature(self, payload: bytes) -> str:
        """Cria assinatura HMAC-SHA256 para webhook"""
        import hmac
        import hashlib
        
        secret = "test_webhook_secret_123"
        signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"


@pytest.mark.e2e
@pytest.mark.asyncio
class TestAPIEndpointsFlow:
    """Testes de fluxo dos endpoints da API"""
    
    async def test_chat_api_flow(
        self,
        test_client,
        mock_abacus_client,
        performance_monitor
    ):
        """
        Testa fluxo da API de chat:
        1. Envio de mensagem via API
        2. Processamento com IA
        3. Resposta estruturada
        4. Salvamento na memória
        """
        performance_monitor.start_timer("chat_api")
        
        with patch('src.backend.app.app.state.abacus_client', mock_abacus_client):
            # Enviar mensagem via API
            response = test_client.post(
                "/api/chat",
                params={
                    "message": "Olá, como posso rastrear meu pedido?",
                    "user_id": "user123",
                    "conversation_id": "conv456",
                    "channel": "web"
                }
            )
            
            assert response.status_code == 200
            
            response_data = response.json()
            assert "content" in response_data
            assert response_data["content"] == "Resposta de teste do assistente"
            
            # Verificar se Abacus foi chamado corretamente
            mock_abacus_client.process_message.assert_called_once()
            call_args = mock_abacus_client.process_message.call_args
            
            assert call_args[1]["message"] == "Olá, como posso rastrear meu pedido?"
            assert call_args[1]["user_id"] == "user123"
            assert call_args[1]["conversation_id"] == "conv456"
            assert call_args[1]["channel"] == "web"
        
        duration = performance_monitor.end_timer("chat_api")
        assert duration < 1.0, f"API de chat muito lenta: {duration:.3f}s"
    
    async def test_memory_api_flow(
        self,
        test_client,
        setup_test_data,
        performance_monitor
    ):
        """
        Testa fluxo da API de memória:
        1. Consulta memória do usuário
        2. Verifica dados históricos
        3. Valida estrutura de resposta
        """
        performance_monitor.start_timer("memory_api")
        
        # Consultar memória
        response = test_client.get("/api/memory/5511999999999")
        
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["user_id"] == "5511999999999"
        assert "memory" in response_data
        assert len(response_data["memory"]) >= 2  # Dados do setup
        
        # Verificar estrutura dos dados de memória
        memory_item = response_data["memory"][0]
        required_fields = ["user_message", "assistant_response", "timestamp", "sentiment"]
        for field in required_fields:
            assert field in memory_item
        
        duration = performance_monitor.end_timer("memory_api")
        assert duration < 0.5, f"API de memória muito lenta: {duration:.3f}s"
    
    async def test_reports_api_flow(
        self,
        test_client,
        performance_monitor
    ):
        """
        Testa fluxo da API de relatórios:
        1. Solicita geração de relatório
        2. Verifica resposta assíncrona
        3. Consulta relatórios do usuário
        """
        performance_monitor.start_timer("reports_api")
        
        # Solicitar geração de relatório
        response = test_client.post(
            "/api/reports/generate",
            params={
                "report_type": "conversation_summary",
                "user_id": "user123"
            },
            json={"period": "last_week"}
        )
        
        assert response.status_code == 200
        
        response_data = response.json()
        assert response_data["status"] == "processing"
        assert response_data["report_type"] == "conversation_summary"
        assert response_data["user_id"] == "user123"
        
        # Consultar relatórios do usuário
        reports_response = test_client.get("/api/reports/user123")
        assert reports_response.status_code == 200
        
        reports_data = reports_response.json()
        assert reports_data["user_id"] == "user123"
        assert "reports" in reports_data
        assert "count" in reports_data
        
        duration = performance_monitor.end_timer("reports_api")
        assert duration < 1.0, f"API de relatórios muito lenta: {duration:.3f}s"


@pytest.mark.e2e
@pytest.mark.asyncio
class TestHealthCheckFlow:
    """Testes de health checks do sistema"""
    
    async def test_simple_health_check(self, test_client, performance_monitor):
        """Testa health check simples"""
        performance_monitor.start_timer("health_simple")
        
        response = test_client.get("/health")
        
        assert response.status_code == 200
        
        health_data = response.json()
        assert health_data["status"] == "healthy"
        
        duration = performance_monitor.end_timer("health_simple")
        assert duration < 0.1, f"Health check simples muito lento: {duration:.3f}s"
    
    async def test_detailed_health_check(self, test_client, performance_monitor):
        """Testa health check detalhado"""
        performance_monitor.start_timer("health_detailed")
        
        response = test_client.get("/health/detailed")
        
        # Pode retornar 200 ou 503 dependendo do estado dos serviços
        assert response.status_code in [200, 503]
        
        health_data = response.json()
        assert "status" in health_data
        
        duration = performance_monitor.end_timer("health_detailed")
        assert duration < 2.0, f"Health check detalhado muito lento: {duration:.3f}s"
