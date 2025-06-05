
"""
BestStag v9.1 - Testes de Carga com Locust
Load testing e stress testing para validar performance do sistema
"""

import json
import time
import random
from locust import HttpUser, task, between, events
from locust.env import Environment
import hmac
import hashlib


class BestStagUser(HttpUser):
    """
    Usuário simulado para testes de carga
    Simula comportamento real de usuários interagindo com o sistema
    """
    
    wait_time = between(1, 5)  # Tempo entre requisições
    
    def on_start(self):
        """Configuração inicial do usuário"""
        self.user_id = f"user_{random.randint(1000, 9999)}"
        self.conversation_id = f"conv_{random.randint(1000, 9999)}"
        self.webhook_secret = "test_webhook_secret_123"
        
        # Mensagens de exemplo para variação
        self.sample_messages = [
            "Olá, preciso de ajuda",
            "Qual o status do meu pedido?",
            "Como posso cancelar minha compra?",
            "Gostaria de falar com um atendente",
            "Obrigado pela ajuda!",
            "Não entendi a resposta anterior",
            "Pode me explicar melhor?",
            "Estou com problemas no app",
            "Como faço para trocar minha senha?",
            "Onde encontro meus pedidos?"
        ]
    
    def _create_signature(self, payload: bytes) -> str:
        """Cria assinatura HMAC-SHA256 para webhook"""
        signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    def _create_whatsapp_message(self, message_text: str) -> dict:
        """Cria estrutura de mensagem WhatsApp"""
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
                                        "from": self.user_id,
                                        "id": f"wamid.{random.randint(100000, 999999)}",
                                        "timestamp": str(int(time.time())),
                                        "text": {
                                            "body": message_text
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
    
    @task(3)
    def send_whatsapp_message(self):
        """
        Simula envio de mensagem via webhook WhatsApp
        Peso 3 - tarefa mais comum
        """
        message_text = random.choice(self.sample_messages)
        webhook_data = self._create_whatsapp_message(message_text)
        
        payload = json.dumps(webhook_data).encode('utf-8')
        signature = self._create_signature(payload)
        
        with self.client.post(
            "/webhook/whatsapp",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": signature
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(2)
    def chat_api_request(self):
        """
        Simula requisição via API de chat
        Peso 2 - tarefa comum
        """
        message_text = random.choice(self.sample_messages)
        
        with self.client.post(
            "/api/chat",
            params={
                "message": message_text,
                "user_id": self.user_id,
                "conversation_id": self.conversation_id,
                "channel": "web"
            },
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def check_memory(self):
        """
        Consulta memória do usuário
        Peso 1 - tarefa menos frequente
        """
        with self.client.get(
            f"/api/memory/{self.user_id}",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def health_check(self):
        """
        Verifica health do sistema
        Peso 1 - monitoramento
        """
        with self.client.get(
            "/health",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")
    
    @task(1)
    def generate_report(self):
        """
        Solicita geração de relatório
        Peso 1 - tarefa ocasional
        """
        with self.client.post(
            "/api/reports/generate",
            params={
                "report_type": "conversation_summary",
                "user_id": self.user_id
            },
            json={"period": "last_day"},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Status code: {response.status_code}")


class StressTestUser(HttpUser):
    """
    Usuário para testes de stress
    Comportamento mais agressivo para testar limites
    """
    
    wait_time = between(0.1, 0.5)  # Requisições mais frequentes
    
    def on_start(self):
        """Configuração inicial"""
        self.user_id = f"stress_user_{random.randint(1000, 9999)}"
        self.webhook_secret = "test_webhook_secret_123"
    
    def _create_signature(self, payload: bytes) -> str:
        """Cria assinatura HMAC-SHA256"""
        signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    @task
    def rapid_fire_requests(self):
        """Requisições rápidas para testar rate limiting"""
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
                                        "from": self.user_id,
                                        "id": f"wamid.stress_{random.randint(100000, 999999)}",
                                        "timestamp": str(int(time.time())),
                                        "text": {
                                            "body": f"Stress test message {random.randint(1, 1000)}"
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
        
        with self.client.post(
            "/webhook/whatsapp",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "X-Hub-Signature-256": signature
            },
            catch_response=True
        ) as response:
            if response.status_code in [200, 429]:  # 429 = rate limited
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")


# Event listeners para métricas customizadas
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
    """Listener para todas as requisições"""
    if exception:
        print(f"Request failed: {name} - {exception}")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Início dos testes"""
    print("=== Iniciando testes de performance BestStag v9.1 ===")
    print(f"Target host: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Fim dos testes"""
    print("=== Testes de performance finalizados ===")
    
    # Estatísticas finais
    stats = environment.stats
    print(f"Total requests: {stats.total.num_requests}")
    print(f"Total failures: {stats.total.num_failures}")
    print(f"Average response time: {stats.total.avg_response_time:.2f}ms")
    print(f"Max response time: {stats.total.max_response_time:.2f}ms")
    print(f"Requests per second: {stats.total.current_rps:.2f}")
    
    # Salvar métricas em arquivo
    with open("performance_results.txt", "w") as f:
        f.write("BestStag v9.1 - Resultados de Performance\n")
        f.write("=" * 50 + "\n")
        f.write(f"Total requests: {stats.total.num_requests}\n")
        f.write(f"Total failures: {stats.total.num_failures}\n")
        f.write(f"Failure rate: {(stats.total.num_failures / stats.total.num_requests * 100):.2f}%\n")
        f.write(f"Average response time: {stats.total.avg_response_time:.2f}ms\n")
        f.write(f"50th percentile: {stats.total.get_response_time_percentile(0.5):.2f}ms\n")
        f.write(f"95th percentile: {stats.total.get_response_time_percentile(0.95):.2f}ms\n")
        f.write(f"99th percentile: {stats.total.get_response_time_percentile(0.99):.2f}ms\n")
        f.write(f"Max response time: {stats.total.max_response_time:.2f}ms\n")
        f.write(f"Requests per second: {stats.total.current_rps:.2f}\n")
        
        # Detalhes por endpoint
        f.write("\nDetalhes por endpoint:\n")
        f.write("-" * 30 + "\n")
        for name, stat in stats.entries.items():
            if stat.num_requests > 0:
                f.write(f"{name}:\n")
                f.write(f"  Requests: {stat.num_requests}\n")
                f.write(f"  Failures: {stat.num_failures}\n")
                f.write(f"  Avg time: {stat.avg_response_time:.2f}ms\n")
                f.write(f"  Max time: {stat.max_response_time:.2f}ms\n")
                f.write("\n")


# Configurações para diferentes tipos de teste
if __name__ == "__main__":
    # Exemplo de como executar diferentes cenários
    print("Cenários de teste disponíveis:")
    print("1. Load Test Normal: locust -f locustfile.py --host=http://localhost:8000")
    print("2. Stress Test: locust -f locustfile.py --host=http://localhost:8000 -u 100 -r 10")
    print("3. Spike Test: locust -f locustfile.py --host=http://localhost:8000 -u 200 -r 50 -t 60s")
    print("4. Endurance Test: locust -f locustfile.py --host=http://localhost:8000 -u 50 -r 5 -t 30m")
