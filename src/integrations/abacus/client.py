
"""
BestStag v9.1 - Cliente Abacus.AI Otimizado
Cliente com circuit breaker, cache inteligente, retry automático e métricas
"""

import asyncio
import aiohttp
import backoff
from typing import Dict, Any, Optional, List, Union
import logging
import time
import os

from .cache import IntelligentCache, get_cache
from .circuit_breaker import CircuitBreaker, CircuitBreakerConfig, get_circuit_breaker
from ..common.metrics import IntegrationMetrics

logger = logging.getLogger('beststag.integrations.abacus.client')


class AbacusOptimizedClient:
    """
    Cliente Abacus.AI otimizado com todas as funcionalidades avançadas
    
    Features:
    - Cache inteligente com TTL dinâmico
    - Circuit breaker para proteção contra falhas
    - Retry automático com backoff exponencial
    - Rate limiting inteligente
    - Métricas detalhadas
    - Suporte assíncrono
    - Fallback automático
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.abacus.ai/v1",
        cache: Optional[IntelligentCache] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        session: Optional[aiohttp.ClientSession] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        rate_limit_per_minute: int = 60
    ):
        # Configuração básica
        self.api_key = api_key or os.getenv("ABACUS_API_KEY")
        if not self.api_key:
            raise ValueError("API key é obrigatória. Defina ABACUS_API_KEY ou passe como parâmetro.")
        
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_per_minute = rate_limit_per_minute
        
        # Componentes otimizados
        self.cache = cache or get_cache()
        
        # Configurar circuit breaker
        cb_config = circuit_breaker_config or CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=60,
            success_threshold=3,
            timeout=timeout,
            expected_exceptions=(aiohttp.ClientError, asyncio.TimeoutError)
        )
        self.circuit_breaker = get_circuit_breaker("abacus_api", cb_config, self._fallback_response)
        
        # Session HTTP
        self._session = session
        self._session_owned = session is None
        
        # Métricas
        self.metrics = IntegrationMetrics("abacus_ai")
        
        # Rate limiting
        self._rate_limit_tokens = rate_limit_per_minute
        self._rate_limit_last_refill = time.time()
        
        # Estatísticas
        self.stats = {
            "requests_made": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "circuit_breaker_opens": 0,
            "rate_limit_hits": 0,
            "total_tokens_used": 0,
            "avg_response_time": 0.0,
            "errors": 0
        }
        
        logger.info(f"Abacus Client otimizado inicializado - Rate Limit: {rate_limit_per_minute}/min")
    
    async def __aenter__(self):
        """Context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        await self.close()
    
    async def _ensure_session(self):
        """Garante que a sessão HTTP está disponível"""
        if self._session is None:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "BestStag-v9.1-OptimizedClient"
                }
            )
    
    async def close(self):
        """Fecha a sessão HTTP se foi criada pelo cliente"""
        if self._session and self._session_owned:
            await self._session.close()
            self._session = None
    
    def _check_rate_limit(self) -> bool:
        """Verifica e atualiza rate limiting usando token bucket"""
        current_time = time.time()
        time_passed = current_time - self._rate_limit_last_refill
        
        # Recarregar tokens baseado no tempo passado
        tokens_to_add = time_passed * (self.rate_limit_per_minute / 60.0)
        self._rate_limit_tokens = min(
            self.rate_limit_per_minute,
            self._rate_limit_tokens + tokens_to_add
        )
        self._rate_limit_last_refill = current_time
        
        # Verificar se há tokens disponíveis
        if self._rate_limit_tokens >= 1.0:
            self._rate_limit_tokens -= 1.0
            return True
        else:
            self.stats["rate_limit_hits"] += 1
            self.metrics.record_rate_limit()
            return False
    
    def _fallback_response(self, *args, **kwargs) -> Dict[str, Any]:
        """Resposta de fallback quando circuit breaker está aberto"""
        return {
            "error": "Service temporarily unavailable",
            "fallback": True,
            "message": "Circuit breaker is open. Please try again later.",
            "retry_after": 60
        }
    
    @backoff.on_exception(
        backoff.expo,
        (aiohttp.ClientError, asyncio.TimeoutError),
        max_tries=3,
        max_time=120,
        jitter=backoff.full_jitter
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        payload: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Faz requisição HTTP com todas as otimizações
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint da API
            payload: Dados para enviar
            use_cache: Se deve usar cache
            
        Returns:
            Resposta da API
        """
        start_time = time.time()
        
        # Verificar rate limit
        if not self._check_rate_limit():
            raise Exception("Rate limit exceeded. Please wait before making more requests.")
        
        # Verificar cache (apenas para GET e POST com payload)
        cache_key = None
        if use_cache and payload is not None:
            cached_response = self.cache.get(endpoint, payload)
            if cached_response is not None:
                self.stats["cache_hits"] += 1
                self.metrics.record_cache_hit(True)
                logger.debug(f"Cache hit para {endpoint}")
                return cached_response
            else:
                self.stats["cache_misses"] += 1
                self.metrics.record_cache_hit(False)
        
        await self._ensure_session()
        
        # Preparar URL
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        # Fazer requisição
        try:
            if method.upper() == "GET":
                async with self._session.get(url, params=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
            else:
                async with self._session.post(url, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
            
            # Atualizar estatísticas
            duration = time.time() - start_time
            self.stats["requests_made"] += 1
            self.stats["avg_response_time"] = (
                (self.stats["avg_response_time"] * (self.stats["requests_made"] - 1) + duration) /
                self.stats["requests_made"]
            )
            
            # Registrar métricas
            self.metrics.record_request(endpoint, True, duration)
            
            # Atualizar tokens usados se disponível
            if "usage" in data and "total_tokens" in data["usage"]:
                self.stats["total_tokens_used"] += data["usage"]["total_tokens"]
            
            # Salvar no cache
            if use_cache and payload is not None:
                # TTL dinâmico baseado no tipo de resposta
                ttl = self._calculate_cache_ttl(endpoint, data)
                self.cache.set(endpoint, payload, data, ttl)
            
            logger.debug(f"Requisição bem-sucedida: {method} {endpoint} ({duration:.2f}s)")
            return data
            
        except Exception as e:
            duration = time.time() - start_time
            self.stats["errors"] += 1
            
            # Registrar métricas de erro
            self.metrics.record_request(endpoint, False, duration)
            self.metrics.record_error(type(e).__name__, endpoint)
            
            logger.error(f"Erro na requisição: {method} {endpoint} - {e}")
            raise
    
    def _calculate_cache_ttl(self, endpoint: str, response: Dict[str, Any]) -> int:
        """Calcula TTL dinâmico baseado no endpoint e resposta"""
        # TTLs específicos por tipo de endpoint
        if "chat" in endpoint or "completion" in endpoint:
            return 300  # 5 minutos para chat
        elif "embedding" in endpoint:
            return 3600  # 1 hora para embeddings
        elif "sentiment" in endpoint:
            return 600  # 10 minutos para análise de sentimento
        elif "agent" in endpoint:
            return 180  # 3 minutos para agentes
        else:
            return 300  # Padrão 5 minutos
    
    async def generate_text(
        self,
        prompt: str,
        model: str = "chatglm",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Gera texto usando ChatLLM
        
        Args:
            prompt: Texto de entrada
            model: Modelo a ser usado
            max_tokens: Número máximo de tokens
            temperature: Temperatura para geração
            **kwargs: Parâmetros adicionais
            
        Returns:
            Resposta do modelo
        """
        payload = {
            "prompt": prompt,
            "model": model,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        return await self.circuit_breaker.call(
            self._make_request,
            "POST",
            "serve/chatllm",
            payload
        )
    
    async def run_agent(
        self,
        task: str,
        agent_id: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Executa tarefa usando DeepAgent
        
        Args:
            task: Descrição da tarefa
            agent_id: ID do agente
            context: Contexto adicional
            **kwargs: Parâmetros adicionais
            
        Returns:
            Resultado da execução
        """
        payload = {
            "task": task,
            "agentId": agent_id,
            **kwargs
        }
        
        if context:
            payload["context"] = context
        
        return await self.circuit_breaker.call(
            self._make_request,
            "POST",
            "serve/agent",
            payload
        )
    
    async def analyze_sentiment(
        self,
        text: str,
        language: str = "pt",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analisa sentimento do texto
        
        Args:
            text: Texto para análise
            language: Idioma do texto
            **kwargs: Parâmetros adicionais
            
        Returns:
            Análise de sentimento
        """
        payload = {
            "text": text,
            "language": language,
            **kwargs
        }
        
        return await self.circuit_breaker.call(
            self._make_request,
            "POST",
            "serve/sentiment",
            payload
        )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Chat completion com histórico de mensagens
        
        Args:
            messages: Lista de mensagens no formato [{"role": "user", "content": "..."}]
            model: Modelo a ser usado
            max_tokens: Número máximo de tokens
            temperature: Temperatura para geração
            stream: Se deve usar streaming
            **kwargs: Parâmetros adicionais
            
        Returns:
            Resposta do chat
        """
        payload = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        return await self.circuit_breaker.call(
            self._make_request,
            "POST",
            "chat/completions",
            payload
        )
    
    async def generate_embeddings(
        self,
        texts: Union[str, List[str]],
        model: str = "text-embedding-ada-002"
    ) -> Dict[str, Any]:
        """
        Gera embeddings para textos
        
        Args:
            texts: Texto ou lista de textos
            model: Modelo de embedding
            
        Returns:
            Embeddings gerados
        """
        if isinstance(texts, str):
            texts = [texts]
        
        payload = {
            "input": texts,
            "model": model
        }
        
        return await self.circuit_breaker.call(
            self._make_request,
            "POST",
            "embeddings",
            payload
        )
    
    async def process_message(
        self,
        message: str,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        channel: str = "web",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Processa mensagem completa com contexto
        
        Args:
            message: Mensagem do usuário
            user_id: ID do usuário
            conversation_id: ID da conversa
            channel: Canal de origem
            context: Contexto adicional
            
        Returns:
            Resposta processada
        """
        # Preparar contexto da conversa
        conversation_context = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "channel": channel,
            "timestamp": time.time()
        }
        
        if context:
            conversation_context.update(context)
        
        # Preparar mensagens para chat completion
        messages = [
            {
                "role": "system",
                "content": "Você é o BestStag, um assistente virtual inteligente especializado em atendimento ao cliente."
            },
            {
                "role": "user",
                "content": message
            }
        ]
        
        # Processar com chat completion
        response = await self.chat_completion(
            messages=messages,
            model="gpt-4",
            temperature=0.7,
            max_tokens=1000,
            context=conversation_context
        )
        
        return response
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verifica saúde da API
        
        Returns:
            Status de saúde
        """
        try:
            start_time = time.time()
            
            # Fazer requisição simples
            response = await self._make_request(
                "POST",
                "serve/chatllm",
                {"prompt": "Hello", "model": "chatglm", "max_tokens": 5},
                use_cache=False
            )
            
            duration = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": duration,
                "circuit_breaker_state": self.circuit_breaker.state.value,
                "cache_stats": self.cache.get_stats(),
                "timestamp": time.time()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "circuit_breaker_state": self.circuit_breaker.state.value,
                "timestamp": time.time()
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas completas do cliente"""
        return {
            **self.stats,
            "circuit_breaker": self.circuit_breaker.get_stats(),
            "cache": self.cache.get_stats(),
            "rate_limit": {
                "tokens_available": self._rate_limit_tokens,
                "limit_per_minute": self.rate_limit_per_minute
            }
        }
    
    def clear_cache(self):
        """Limpa o cache"""
        self.cache.invalidate()
        logger.info("Cache do Abacus Client limpo")
    
    def reset_circuit_breaker(self):
        """Reseta o circuit breaker"""
        self.circuit_breaker.reset()
        logger.info("Circuit breaker do Abacus Client resetado")


# Instância global do cliente (singleton)
_client_instance: Optional[AbacusOptimizedClient] = None


async def get_client() -> AbacusOptimizedClient:
    """Retorna instância singleton do cliente"""
    global _client_instance
    if _client_instance is None:
        _client_instance = AbacusOptimizedClient()
    return _client_instance


async def initialize_client(
    api_key: Optional[str] = None,
    cache: Optional[IntelligentCache] = None,
    circuit_breaker_config: Optional[CircuitBreakerConfig] = None
) -> AbacusOptimizedClient:
    """
    Inicializa o cliente global
    
    Args:
        api_key: Chave da API
        cache: Instância do cache
        circuit_breaker_config: Configuração do circuit breaker
        
    Returns:
        Instância do cliente configurada
    """
    global _client_instance
    
    _client_instance = AbacusOptimizedClient(
        api_key=api_key,
        cache=cache,
        circuit_breaker_config=circuit_breaker_config
    )
    
    return _client_instance
