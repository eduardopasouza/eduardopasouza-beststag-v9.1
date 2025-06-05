
"""
BestStag v9.1 - Testes de Latência
Testes específicos para medir tempos de resposta e throughput
"""

import pytest
import asyncio
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch, AsyncMock


@pytest.mark.performance
@pytest.mark.asyncio
class TestLatencyMetrics:
    """Testes de latência para diferentes componentes"""
    
    async def test_webhook_latency(
        self,
        test_client,
        sample_whatsapp_message,
        mock_abacus_client,
        performance_monitor
    ):
        """
        Testa latência do webhook WhatsApp
        Meta: < 100ms para aceitar webhook
        """
        import json
        
        latencies = []
        num_requests = 50
        
        with patch('src.backend.app.app.state.abacus_client', mock_abacus_client):
            for i in range(num_requests):
                # Criar mensagem única
                message = sample_whatsapp_message.copy()
                message["entry"][0]["changes"][0]["value"]["messages"][0]["id"] = f"wamid.test{i}"
                
                payload = json.dumps(message).encode('utf-8')
                signature = self._create_signature(payload)
                
                # Medir latência
                start_time = time.time()
                
                response = test_client.post(
                    "/webhook/whatsapp",
                    content=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Hub-Signature-256": signature
                    }
                )
                
                end_time = time.time()
                latency = (end_time - start_time) * 1000  # em ms
                latencies.append(latency)
                
                assert response.status_code == 200
        
        # Análise estatística
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]  # 95th percentile
        p99_latency = statistics.quantiles(latencies, n=100)[98]  # 99th percentile
        max_latency = max(latencies)
        
        print(f"\nWebhook Latency Stats:")
        print(f"Average: {avg_latency:.2f}ms")
        print(f"P95: {p95_latency:.2f}ms")
        print(f"P99: {p99_latency:.2f}ms")
        print(f"Max: {max_latency:.2f}ms")
        
        # Assertions
        assert avg_latency < 100, f"Latência média muito alta: {avg_latency:.2f}ms"
        assert p95_latency < 200, f"P95 muito alto: {p95_latency:.2f}ms"
        assert p99_latency < 500, f"P99 muito alto: {p99_latency:.2f}ms"
    
    async def test_chat_api_latency(
        self,
        test_client,
        mock_abacus_client,
        performance_monitor
    ):
        """
        Testa latência da API de chat
        Meta: < 500ms para resposta completa
        """
        latencies = []
        num_requests = 30
        
        messages = [
            "Olá, como posso ajudar?",
            "Qual o status do meu pedido?",
            "Preciso cancelar uma compra",
            "Como faço para trocar um produto?",
            "Gostaria de falar com atendente"
        ]
        
        with patch('src.backend.app.app.state.abacus_client', mock_abacus_client):
            for i in range(num_requests):
                message = messages[i % len(messages)]
                
                start_time = time.time()
                
                response = test_client.post(
                    "/api/chat",
                    params={
                        "message": message,
                        "user_id": f"user{i}",
                        "conversation_id": f"conv{i}",
                        "channel": "web"
                    }
                )
                
                end_time = time.time()
                latency = (end_time - start_time) * 1000
                latencies.append(latency)
                
                assert response.status_code == 200
        
        # Análise estatística
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]
        max_latency = max(latencies)
        
        print(f"\nChat API Latency Stats:")
        print(f"Average: {avg_latency:.2f}ms")
        print(f"P95: {p95_latency:.2f}ms")
        print(f"Max: {max_latency:.2f}ms")
        
        # Assertions
        assert avg_latency < 500, f"Latência média muito alta: {avg_latency:.2f}ms"
        assert p95_latency < 1000, f"P95 muito alto: {p95_latency:.2f}ms"
    
    async def test_memory_api_latency(
        self,
        test_client,
        setup_test_data,
        performance_monitor
    ):
        """
        Testa latência da API de memória
        Meta: < 100ms para consulta
        """
        latencies = []
        num_requests = 50
        
        for i in range(num_requests):
            start_time = time.time()
            
            response = test_client.get("/api/memory/5511999999999")
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            latencies.append(latency)
            
            assert response.status_code == 200
        
        # Análise estatística
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]
        
        print(f"\nMemory API Latency Stats:")
        print(f"Average: {avg_latency:.2f}ms")
        print(f"P95: {p95_latency:.2f}ms")
        
        # Assertions
        assert avg_latency < 100, f"Latência média muito alta: {avg_latency:.2f}ms"
        assert p95_latency < 200, f"P95 muito alto: {p95_latency:.2f}ms"
    
    async def test_concurrent_requests_latency(
        self,
        test_client,
        mock_abacus_client,
        performance_monitor
    ):
        """
        Testa latência sob carga concorrente
        Meta: Latência não deve degradar significativamente
        """
        import json
        
        def make_request(request_id):
            """Função para fazer requisição individual"""
            message_data = {
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
                                            "from": f"user{request_id}",
                                            "id": f"wamid.concurrent{request_id}",
                                            "timestamp": str(int(time.time())),
                                            "text": {
                                                "body": f"Concurrent test message {request_id}"
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
            
            payload = json.dumps(message_data).encode('utf-8')
            signature = self._create_signature(payload)
            
            start_time = time.time()
            
            response = test_client.post(
                "/webhook/whatsapp",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-Hub-Signature-256": signature
                }
            )
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            
            return {
                "request_id": request_id,
                "latency": latency,
                "status_code": response.status_code
            }
        
        with patch('src.backend.app.app.state.abacus_client', mock_abacus_client):
            # Executar requisições concorrentes
            num_concurrent = 20
            latencies = []
            
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request, i) for i in range(num_concurrent)]
                
                for future in as_completed(futures):
                    result = future.result()
                    latencies.append(result["latency"])
                    assert result["status_code"] == 200
        
        # Análise estatística
        avg_latency = statistics.mean(latencies)
        p95_latency = statistics.quantiles(latencies, n=20)[18]
        max_latency = max(latencies)
        
        print(f"\nConcurrent Requests Latency Stats:")
        print(f"Concurrent requests: {num_concurrent}")
        print(f"Average: {avg_latency:.2f}ms")
        print(f"P95: {p95_latency:.2f}ms")
        print(f"Max: {max_latency:.2f}ms")
        
        # Assertions - latência pode ser um pouco maior sob carga
        assert avg_latency < 300, f"Latência média sob carga muito alta: {avg_latency:.2f}ms"
        assert p95_latency < 1000, f"P95 sob carga muito alto: {p95_latency:.2f}ms"
    
    def _create_signature(self, payload: bytes) -> str:
        """Cria assinatura HMAC-SHA256"""
        import hmac
        import hashlib
        
        secret = "test_webhook_secret_123"
        signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"


@pytest.mark.performance
@pytest.mark.asyncio
class TestThroughputMetrics:
    """Testes de throughput (requisições por segundo)"""
    
    async def test_webhook_throughput(
        self,
        test_client,
        sample_whatsapp_message,
        mock_abacus_client
    ):
        """
        Testa throughput do webhook
        Meta: > 100 req/s
        """
        import json
        
        num_requests = 100
        duration_seconds = 10
        
        with patch('src.backend.app.app.state.abacus_client', mock_abacus_client):
            start_time = time.time()
            successful_requests = 0
            
            # Fazer requisições por período determinado
            while time.time() - start_time < duration_seconds:
                message = sample_whatsapp_message.copy()
                message["entry"][0]["changes"][0]["value"]["messages"][0]["id"] = f"wamid.throughput{successful_requests}"
                
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
                
                if response.status_code == 200:
                    successful_requests += 1
            
            actual_duration = time.time() - start_time
            throughput = successful_requests / actual_duration
            
            print(f"\nWebhook Throughput:")
            print(f"Successful requests: {successful_requests}")
            print(f"Duration: {actual_duration:.2f}s")
            print(f"Throughput: {throughput:.2f} req/s")
            
            # Assertion
            assert throughput > 50, f"Throughput muito baixo: {throughput:.2f} req/s"
    
    def _create_signature(self, payload: bytes) -> str:
        """Cria assinatura HMAC-SHA256"""
        import hmac
        import hashlib
        
        secret = "test_webhook_secret_123"
        signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return f"sha256={signature}"


@pytest.mark.performance
@pytest.mark.slow
class TestEnduranceMetrics:
    """Testes de resistência (endurance)"""
    
    def test_memory_leak_detection(self, test_client, mock_abacus_client):
        """
        Testa vazamentos de memória durante execução prolongada
        """
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        with patch('src.backend.app.app.state.abacus_client', mock_abacus_client):
            # Executar muitas requisições
            for i in range(1000):
                response = test_client.post(
                    "/api/chat",
                    params={
                        "message": f"Test message {i}",
                        "user_id": f"user{i % 10}",  # Reutilizar alguns usuários
                        "conversation_id": f"conv{i % 10}",
                        "channel": "test"
                    }
                )
                assert response.status_code == 200
                
                # Verificar memória a cada 100 requisições
                if i % 100 == 0:
                    current_memory = process.memory_info().rss / 1024 / 1024
                    memory_growth = current_memory - initial_memory
                    
                    print(f"Requisição {i}: Memória atual: {current_memory:.2f}MB, Crescimento: {memory_growth:.2f}MB")
                    
                    # Não deve crescer mais que 100MB
                    assert memory_growth < 100, f"Possível vazamento de memória: {memory_growth:.2f}MB"
        
        final_memory = process.memory_info().rss / 1024 / 1024
        total_growth = final_memory - initial_memory
        
        print(f"\nMemory Usage:")
        print(f"Initial: {initial_memory:.2f}MB")
        print(f"Final: {final_memory:.2f}MB")
        print(f"Growth: {total_growth:.2f}MB")
        
        # Crescimento total não deve exceder 50MB para 1000 requisições
        assert total_growth < 50, f"Crescimento de memória excessivo: {total_growth:.2f}MB"
