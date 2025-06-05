
"""
BestStag v9.1 - Configuração de Testes
Fixtures e configurações compartilhadas para todos os testes
"""

import pytest
import asyncio
import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch
import httpx
import redis.asyncio as redis
from fastapi.testclient import TestClient

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# Imports do projeto
from src.backend.app import app
from src.integrations.whatsapp.webhook import WhatsAppWebhook
from src.integrations.whatsapp.queue import WhatsAppQueue
from src.integrations.abacus.client import AbacusOptimizedClient
from src.python.contextual_memory import ContextualMemory
from src.python.intelligent_reports import IntelligentReports


# Configurações de teste
TEST_CONFIG = {
    "REDIS_URL": "redis://localhost:6379/1",  # DB 1 para testes
    "WHATSAPP_WEBHOOK_SECRET": "test_webhook_secret_123",
    "WHATSAPP_VERIFY_TOKEN": "test_verify_token_456",
    "ABACUS_API_KEY": "test_abacus_key",
    "ABACUS_DEPLOYMENT_ID": "test_deployment_123",
    "LOG_LEVEL": "DEBUG",
    "ENVIRONMENT": "test"
}

# Aplicar configurações de teste
for key, value in TEST_CONFIG.items():
    os.environ[key] = value


@pytest.fixture(scope="session")
def event_loop():
    """Cria um event loop para toda a sessão de testes"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def redis_client():
    """Cliente Redis para testes"""
    client = redis.from_url(TEST_CONFIG["REDIS_URL"])
    
    # Limpar dados de teste
    await client.flushdb()
    
    yield client
    
    # Cleanup
    await client.flushdb()
    await client.close()


@pytest.fixture
def test_client():
    """Cliente de teste FastAPI"""
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def mock_abacus_client():
    """Mock do cliente Abacus.AI"""
    mock_client = AsyncMock(spec=AbacusOptimizedClient)
    
    # Configurar respostas padrão
    mock_client.process_message.return_value = {
        "content": "Resposta de teste do assistente",
        "sentiment": "neutral",
        "confidence": 0.95,
        "processing_time": 0.5,
        "tokens_used": 150,
        "model_version": "test-model-v1"
    }
    
    mock_client.analyze_sentiment.return_value = {
        "sentiment": "positive",
        "confidence": 0.87,
        "emotions": {
            "joy": 0.6,
            "trust": 0.3,
            "anticipation": 0.1
        }
    }
    
    mock_client.get_health.return_value = {
        "status": "healthy",
        "latency": 0.1,
        "cache_hit_rate": 0.75
    }
    
    return mock_client


@pytest.fixture
async def mock_whatsapp_queue(redis_client):
    """Queue WhatsApp para testes"""
    queue = WhatsAppQueue(
        redis_client=redis_client,
        max_workers=2,
        rate_limit=100
    )
    
    await queue.start()
    yield queue
    await queue.stop()


@pytest.fixture
async def whatsapp_webhook(mock_whatsapp_queue):
    """Webhook WhatsApp para testes"""
    webhook = WhatsAppWebhook(
        webhook_secret=TEST_CONFIG["WHATSAPP_WEBHOOK_SECRET"],
        verify_token=TEST_CONFIG["WHATSAPP_VERIFY_TOKEN"],
        queue=mock_whatsapp_queue,
        rate_limit_per_minute=100
    )
    
    yield webhook
    
    # Cleanup
    webhook.clear_rate_limits()


@pytest.fixture
async def contextual_memory():
    """Memória contextual para testes"""
    memory = ContextualMemory()
    yield memory
    
    # Cleanup - limpar dados de teste
    await memory.clear_all_data()


@pytest.fixture
async def intelligent_reports():
    """Relatórios inteligentes para testes"""
    reports = IntelligentReports()
    yield reports


@pytest.fixture
def sample_whatsapp_message():
    """Mensagem WhatsApp de exemplo"""
    return {
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
                                    "id": "wamid.test123",
                                    "timestamp": str(int(time.time())),
                                    "text": {
                                        "body": "Olá, preciso de ajuda com meu pedido"
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


@pytest.fixture
def sample_whatsapp_image_message():
    """Mensagem WhatsApp com imagem de exemplo"""
    return {
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
                                    "id": "wamid.image123",
                                    "timestamp": str(int(time.time())),
                                    "image": {
                                        "id": "media123",
                                        "mime_type": "image/jpeg",
                                        "sha256": "abc123def456",
                                        "caption": "Foto do problema"
                                    },
                                    "type": "image"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def sample_conversation_history():
    """Histórico de conversa de exemplo"""
    return [
        {
            "user_id": "5511999999999",
            "conversation_id": "conv_123",
            "timestamp": time.time() - 3600,  # 1 hora atrás
            "user_message": "Qual o status do meu pedido?",
            "assistant_response": "Vou verificar o status do seu pedido. Qual o número?",
            "sentiment": "neutral",
            "metadata": {"channel": "whatsapp"}
        },
        {
            "user_id": "5511999999999",
            "conversation_id": "conv_123",
            "timestamp": time.time() - 3500,  # 58 minutos atrás
            "user_message": "Pedido #12345",
            "assistant_response": "Seu pedido #12345 está em preparação e será enviado hoje.",
            "sentiment": "positive",
            "metadata": {"channel": "whatsapp"}
        }
    ]


@pytest.fixture
async def setup_test_data(contextual_memory, sample_conversation_history):
    """Configura dados de teste no sistema"""
    # Inserir histórico de conversa
    for interaction in sample_conversation_history:
        await contextual_memory.save_interaction(**interaction)
    
    yield
    
    # Cleanup
    await contextual_memory.clear_all_data()


@pytest.fixture
def mock_external_apis():
    """Mock de APIs externas"""
    with patch('httpx.AsyncClient') as mock_client:
        # Mock do cliente HTTP
        mock_instance = AsyncMock()
        mock_client.return_value.__aenter__.return_value = mock_instance
        
        # Configurar respostas padrão
        mock_instance.post.return_value.status_code = 200
        mock_instance.post.return_value.json.return_value = {
            "success": True,
            "message_id": "test_msg_123"
        }
        
        mock_instance.get.return_value.status_code = 200
        mock_instance.get.return_value.json.return_value = {
            "status": "healthy"
        }
        
        yield mock_instance


@pytest.fixture
def performance_monitor():
    """Monitor de performance para testes"""
    class PerformanceMonitor:
        def __init__(self):
            self.metrics = {}
            self.start_times = {}
        
        def start_timer(self, operation: str):
            self.start_times[operation] = time.time()
        
        def end_timer(self, operation: str):
            if operation in self.start_times:
                duration = time.time() - self.start_times[operation]
                if operation not in self.metrics:
                    self.metrics[operation] = []
                self.metrics[operation].append(duration)
                del self.start_times[operation]
                return duration
            return None
        
        def get_average(self, operation: str) -> float:
            if operation in self.metrics and self.metrics[operation]:
                return sum(self.metrics[operation]) / len(self.metrics[operation])
            return 0.0
        
        def get_max(self, operation: str) -> float:
            if operation in self.metrics and self.metrics[operation]:
                return max(self.metrics[operation])
            return 0.0
        
        def get_min(self, operation: str) -> float:
            if operation in self.metrics and self.metrics[operation]:
                return min(self.metrics[operation])
            return 0.0
        
        def reset(self):
            self.metrics.clear()
            self.start_times.clear()
    
    return PerformanceMonitor()


# Helpers para testes
def create_signature(payload: bytes, secret: str) -> str:
    """Cria assinatura HMAC-SHA256 para testes"""
    import hmac
    import hashlib
    
    signature = hmac.new(
        secret.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return f"sha256={signature}"


def assert_response_time(duration: float, max_time: float = 1.0):
    """Verifica se o tempo de resposta está dentro do limite"""
    assert duration <= max_time, f"Tempo de resposta muito alto: {duration:.3f}s > {max_time}s"


def assert_memory_usage():
    """Verifica uso de memória (placeholder para implementação futura)"""
    # TODO: Implementar verificação de uso de memória
    pass


# Configurações pytest
def pytest_configure(config):
    """Configuração do pytest"""
    # Adicionar marcadores customizados
    config.addinivalue_line(
        "markers", "e2e: marca testes end-to-end"
    )
    config.addinivalue_line(
        "markers", "integration: marca testes de integração"
    )
    config.addinivalue_line(
        "markers", "performance: marca testes de performance"
    )
    config.addinivalue_line(
        "markers", "slow: marca testes lentos"
    )


def pytest_collection_modifyitems(config, items):
    """Modifica itens coletados pelo pytest"""
    # Adicionar marcador slow para testes que demoram mais de 5s
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.slow)
