import os
import time
import json
import logging
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AbacusClient:
    """Cliente Python para integração com Abacus.AI"""
    
    def __init__(self, api_key: Optional[str] = None, cache_ttl: int = 300, max_retries: int = 3):
        """
        Inicializa o cliente Abacus.AI
        
        Args:
            api_key: Chave da API (se não fornecida, usa variável de ambiente)
            cache_ttl: Tempo de vida do cache em segundos
            max_retries: Número máximo de tentativas em caso de erro
        """
        self.api_key = api_key or os.getenv("ABACUS_API_KEY")
        if not self.api_key:
            raise ValueError("API key é obrigatória. Defina ABACUS_API_KEY ou passe como parâmetro.")
        
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.max_retries = max_retries
        self.base_url = "https://api.abacus.ai/v1"
        
        # Estatísticas de uso
        self.stats = {
            "requests_made": 0,
            "cache_hits": 0,
            "errors": 0,
            "total_tokens": 0
        }
    
    def _cache_key(self, endpoint: str, payload: Dict[str, Any]) -> str:
        """Gera chave única para cache"""
        return f"{endpoint}:{hash(json.dumps(payload, sort_keys=True))}"
    
    def _is_cache_valid(self, timestamp: float) -> bool:
        """Verifica se o cache ainda é válido"""
        return time.time() - timestamp < self.cache_ttl
    
    def _post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Faz requisição POST com cache e retry
        
        Args:
            endpoint: URL do endpoint
            payload: Dados para enviar
            
        Returns:
            Resposta da API
        """
        # Verificar cache
        key = self._cache_key(endpoint, payload)
        if key in self.cache:
            data, timestamp = self.cache[key]
            if self._is_cache_valid(timestamp):
                self.stats["cache_hits"] += 1
                logger.info(f"Cache hit para {endpoint}")
                return data
        
        # Fazer requisição
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fazendo requisição para {endpoint} (tentativa {attempt + 1})")
                
                response = requests.post(
                    endpoint,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "User-Agent": "BestStag-v9.1-Client"
                    },
                    timeout=30
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Atualizar estatísticas
                self.stats["requests_made"] += 1
                if "usage" in data and "total_tokens" in data["usage"]:
                    self.stats["total_tokens"] += data["usage"]["total_tokens"]
                
                # Salvar no cache
                self.cache[key] = (data, time.time())
                
                logger.info(f"Requisição bem-sucedida para {endpoint}")
                return data
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Erro na tentativa {attempt + 1}: {e}")
                self.stats["errors"] += 1
                
                if attempt == self.max_retries - 1:
                    logger.error(f"Falha após {self.max_retries} tentativas")
                    raise
                
                # Backoff exponencial
                time.sleep(2 ** attempt)
        
        raise Exception(f"Falha após {self.max_retries} tentativas")
    
    def generate_text(self, prompt: str, model: str = "chatglm", **kwargs) -> Dict[str, Any]:
        """
        Gera texto usando ChatLLM
        
        Args:
            prompt: Texto de entrada
            model: Modelo a ser usado
            **kwargs: Parâmetros adicionais
            
        Returns:
            Resposta do modelo
        """
        payload = {
            "prompt": prompt,
            "model": model,
            **kwargs
        }
        
        return self._post(f"{self.base_url}/serve/chatllm", payload)
    
    def run_agent(self, task: str, agent_id: str, **kwargs) -> Dict[str, Any]:
        """
        Executa tarefa usando DeepAgent
        
        Args:
            task: Descrição da tarefa
            agent_id: ID do agente
            **kwargs: Parâmetros adicionais
            
        Returns:
            Resultado da execução
        """
        payload = {
            "task": task,
            "agentId": agent_id,
            **kwargs
        }
        
        return self._post(f"{self.base_url}/serve/agent", payload)
    
    def analyze_sentiment(self, text: str, **kwargs) -> Dict[str, Any]:
        """
        Analisa sentimento do texto
        
        Args:
            text: Texto para análise
            **kwargs: Parâmetros adicionais
            
        Returns:
            Análise de sentimento
        """
        payload = {
            "text": text,
            **kwargs
        }
        
        return self._post(f"{self.base_url}/serve/sentiment", payload)
    
    def chat_completion(self, messages: List[Dict[str, str]], model: str = "gpt-4", **kwargs) -> Dict[str, Any]:
        """
        Chat completion com histórico de mensagens
        
        Args:
            messages: Lista de mensagens no formato [{"role": "user", "content": "..."}]
            model: Modelo a ser usado
            **kwargs: Parâmetros adicionais
            
        Returns:
            Resposta do chat
        """
        payload = {
            "messages": messages,
            "model": model,
            **kwargs
        }
        
        return self._post(f"{self.base_url}/chat/completions", payload)
    
    def generate_embeddings(self, texts: List[str], model: str = "text-embedding-ada-002") -> Dict[str, Any]:
        """
        Gera embeddings para textos
        
        Args:
            texts: Lista de textos
            model: Modelo de embedding
            
        Returns:
            Embeddings gerados
        """
        payload = {
            "input": texts,
            "model": model
        }
        
        return self._post(f"{self.base_url}/embeddings", payload)
    
    def clear_cache(self):
        """Limpa o cache"""
        self.cache.clear()
        logger.info("Cache limpo")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de uso"""
        return {
            **self.stats,
            "cache_size": len(self.cache),
            "cache_hit_rate": self.stats["cache_hits"] / max(self.stats["requests_made"], 1) * 100
        }
    
    def health_check(self) -> bool:
        """Verifica se a API está funcionando"""
        try:
            response = self.generate_text("Hello", model="chatglm")
            return "response" in response or "choices" in response
        except Exception as e:
            logger.error(f"Health check falhou: {e}")
            return False

# Exemplo de uso
if __name__ == "__main__":
    # Configurar cliente
    client = AbacusClient()
    
    # Teste básico
    try:
        print("=== Teste de Geração de Texto ===")
        response = client.generate_text("Explique o que é o BestStag em uma frase.")
        print(f"Resposta: {response}")
        
        print("\n=== Teste de Análise de Sentimento ===")
        sentiment = client.analyze_sentiment("Estou muito feliz hoje!")
        print(f"Sentimento: {sentiment}")
        
        print("\n=== Teste de Chat Completion ===")
        chat_response = client.chat_completion([
            {"role": "system", "content": "Você é o assistente BestStag."},
            {"role": "user", "content": "Como você pode me ajudar?"}
        ])
        print(f"Chat: {chat_response}")
        
        print("\n=== Estatísticas ===")
        stats = client.get_stats()
        print(f"Stats: {stats}")
        
    except Exception as e:
        print(f"Erro: {e}")

