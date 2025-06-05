
"""
BestStag v9.1 - Circuit Breaker Pattern para Abacus.AI
Implementa circuit breaker com estados, métricas e recovery automático
"""

import time
import threading
from enum import Enum
from typing import Callable, Any, Optional, Dict, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging

logger = logging.getLogger('beststag.integrations.circuit_breaker')


class CircuitState(Enum):
    """Estados do Circuit Breaker"""
    CLOSED = "closed"      # Funcionamento normal
    OPEN = "open"          # Circuito aberto, rejeitando requisições
    HALF_OPEN = "half_open"  # Testando se o serviço se recuperou


@dataclass
class CircuitBreakerConfig:
    """Configuração do Circuit Breaker"""
    failure_threshold: int = 5          # Número de falhas para abrir o circuito
    recovery_timeout: int = 60          # Tempo em segundos para tentar recovery
    success_threshold: int = 3          # Sucessos necessários para fechar o circuito
    timeout: float = 30.0               # Timeout para requisições
    expected_exceptions: tuple = (Exception,)  # Exceções que contam como falha
    
    # Configurações avançadas
    sliding_window_size: int = 10       # Tamanho da janela deslizante
    minimum_requests: int = 5           # Mínimo de requisições para avaliar
    failure_rate_threshold: float = 50.0  # Taxa de falha em % para abrir


@dataclass
class CircuitBreakerMetrics:
    """Métricas do Circuit Breaker"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    rejected_requests: int = 0
    state_changes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    
    # Janela deslizante para cálculo de taxa de falha
    recent_results: List[bool] = field(default_factory=list)
    
    def add_result(self, success: bool, window_size: int):
        """Adiciona resultado à janela deslizante"""
        self.recent_results.append(success)
        if len(self.recent_results) > window_size:
            self.recent_results.pop(0)
        
        if success:
            self.successful_requests += 1
            self.last_success_time = time.time()
        else:
            self.failed_requests += 1
            self.last_failure_time = time.time()
        
        self.total_requests += 1
    
    def get_failure_rate(self) -> float:
        """Calcula taxa de falha atual"""
        if not self.recent_results:
            return 0.0
        
        failures = sum(1 for result in self.recent_results if not result)
        return (failures / len(self.recent_results)) * 100.0
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas completas"""
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'rejected_requests': self.rejected_requests,
            'state_changes': self.state_changes,
            'success_rate': (self.successful_requests / max(self.total_requests, 1)) * 100,
            'failure_rate': self.get_failure_rate(),
            'last_failure': datetime.fromtimestamp(self.last_failure_time) if self.last_failure_time else None,
            'last_success': datetime.fromtimestamp(self.last_success_time) if self.last_success_time else None
        }


class CircuitBreakerOpenException(Exception):
    """Exceção lançada quando o circuit breaker está aberto"""
    pass


class CircuitBreaker:
    """
    Implementação do padrão Circuit Breaker para proteção de serviços
    
    O Circuit Breaker monitora falhas e automaticamente "abre" o circuito
    quando muitas falhas ocorrem, prevenindo cascata de erros.
    """
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        fallback_function: Optional[Callable] = None
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.fallback_function = fallback_function
        
        self._state = CircuitState.CLOSED
        self._last_failure_time = 0
        self._failure_count = 0
        self._success_count = 0
        self._lock = threading.RLock()
        
        # Métricas
        self.metrics = CircuitBreakerMetrics()
        
        # Callbacks para eventos
        self._on_state_change: List[Callable] = []
        self._on_failure: List[Callable] = []
        self._on_success: List[Callable] = []
        
        logger.info(f"Circuit Breaker '{name}' inicializado - Threshold: {self.config.failure_threshold}")
    
    @property
    def state(self) -> CircuitState:
        """Estado atual do circuit breaker"""
        return self._state
    
    @property
    def is_closed(self) -> bool:
        """Verifica se o circuito está fechado (funcionando normalmente)"""
        return self._state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Verifica se o circuito está aberto (rejeitando requisições)"""
        return self._state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Verifica se o circuito está meio-aberto (testando recovery)"""
        return self._state == CircuitState.HALF_OPEN
    
    def add_state_change_listener(self, callback: Callable[[CircuitState, CircuitState], None]):
        """Adiciona callback para mudanças de estado"""
        self._on_state_change.append(callback)
    
    def add_failure_listener(self, callback: Callable[[Exception], None]):
        """Adiciona callback para falhas"""
        self._on_failure.append(callback)
    
    def add_success_listener(self, callback: Callable[[], None]):
        """Adiciona callback para sucessos"""
        self._on_success.append(callback)
    
    def _change_state(self, new_state: CircuitState):
        """Muda o estado do circuit breaker"""
        if new_state != self._state:
            old_state = self._state
            self._state = new_state
            self.metrics.state_changes += 1
            
            logger.info(f"Circuit Breaker '{self.name}': {old_state.value} -> {new_state.value}")
            
            # Notificar listeners
            for callback in self._on_state_change:
                try:
                    callback(old_state, new_state)
                except Exception as e:
                    logger.error(f"Erro em callback de mudança de estado: {e}")
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar resetar o circuit breaker"""
        return (
            self._state == CircuitState.OPEN and
            time.time() - self._last_failure_time >= self.config.recovery_timeout
        )
    
    def _evaluate_state(self):
        """Avalia e atualiza o estado do circuit breaker"""
        current_time = time.time()
        
        if self._state == CircuitState.CLOSED:
            # Verificar se deve abrir por número de falhas
            if self._failure_count >= self.config.failure_threshold:
                self._change_state(CircuitState.OPEN)
                return
            
            # Verificar se deve abrir por taxa de falha
            if (len(self.metrics.recent_results) >= self.config.minimum_requests and
                self.metrics.get_failure_rate() >= self.config.failure_rate_threshold):
                self._change_state(CircuitState.OPEN)
                return
                
        elif self._state == CircuitState.OPEN:
            # Verificar se deve tentar recovery
            if self._should_attempt_reset():
                self._change_state(CircuitState.HALF_OPEN)
                self._success_count = 0
                return
                
        elif self._state == CircuitState.HALF_OPEN:
            # Verificar se deve fechar (recovery bem-sucedido)
            if self._success_count >= self.config.success_threshold:
                self._change_state(CircuitState.CLOSED)
                self._failure_count = 0
                return
            
            # Verificar se deve abrir novamente (falha durante recovery)
            if self._failure_count > 0:
                self._change_state(CircuitState.OPEN)
                return
    
    def _record_success(self):
        """Registra uma operação bem-sucedida"""
        with self._lock:
            self._success_count += 1
            self._failure_count = max(0, self._failure_count - 1)  # Reduz falhas gradualmente
            
            self.metrics.add_result(True, self.config.sliding_window_size)
            
            # Notificar listeners
            for callback in self._on_success:
                try:
                    callback()
                except Exception as e:
                    logger.error(f"Erro em callback de sucesso: {e}")
            
            self._evaluate_state()
    
    def _record_failure(self, exception: Exception):
        """Registra uma falha"""
        with self._lock:
            self._failure_count += 1
            self._success_count = 0
            self._last_failure_time = time.time()
            
            self.metrics.add_result(False, self.config.sliding_window_size)
            
            # Notificar listeners
            for callback in self._on_failure:
                try:
                    callback(exception)
                except Exception as e:
                    logger.error(f"Erro em callback de falha: {e}")
            
            self._evaluate_state()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa uma função protegida pelo circuit breaker
        
        Args:
            func: Função a ser executada
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Resultado da função
            
        Raises:
            CircuitBreakerOpenException: Se o circuito estiver aberto
            Exception: Qualquer exceção da função original
        """
        with self._lock:
            self._evaluate_state()
            
            if self._state == CircuitState.OPEN:
                self.metrics.rejected_requests += 1
                
                if self.fallback_function:
                    logger.debug(f"Circuit Breaker '{self.name}' aberto, usando fallback")
                    return self.fallback_function(*args, **kwargs)
                else:
                    raise CircuitBreakerOpenException(
                        f"Circuit Breaker '{self.name}' está aberto. "
                        f"Próxima tentativa em {self.config.recovery_timeout}s"
                    )
        
        # Executar função
        try:
            result = func(*args, **kwargs)
            self._record_success()
            return result
            
        except self.config.expected_exceptions as e:
            self._record_failure(e)
            raise
        except Exception as e:
            # Exceções não esperadas não contam como falha
            logger.warning(f"Exceção não esperada no Circuit Breaker '{self.name}': {e}")
            raise
    
    def __call__(self, func: Callable) -> Callable:
        """Permite usar como decorador"""
        def wrapper(*args, **kwargs):
            return self.call(func, *args, **kwargs)
        
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    
    def reset(self):
        """Reseta o circuit breaker para estado inicial"""
        with self._lock:
            self._change_state(CircuitState.CLOSED)
            self._failure_count = 0
            self._success_count = 0
            self._last_failure_time = 0
            self.metrics = CircuitBreakerMetrics()
            
        logger.info(f"Circuit Breaker '{self.name}' resetado")
    
    def force_open(self):
        """Força o circuit breaker a abrir"""
        with self._lock:
            self._change_state(CircuitState.OPEN)
            self._last_failure_time = time.time()
            
        logger.warning(f"Circuit Breaker '{self.name}' forçado a abrir")
    
    def force_close(self):
        """Força o circuit breaker a fechar"""
        with self._lock:
            self._change_state(CircuitState.CLOSED)
            self._failure_count = 0
            
        logger.info(f"Circuit Breaker '{self.name}' forçado a fechar")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas completas do circuit breaker"""
        return {
            'name': self.name,
            'state': self._state.value,
            'failure_count': self._failure_count,
            'success_count': self._success_count,
            'config': {
                'failure_threshold': self.config.failure_threshold,
                'recovery_timeout': self.config.recovery_timeout,
                'success_threshold': self.config.success_threshold,
                'timeout': self.config.timeout
            },
            **self.metrics.get_stats()
        }


# Registry global de circuit breakers
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str,
    config: Optional[CircuitBreakerConfig] = None,
    fallback_function: Optional[Callable] = None
) -> CircuitBreaker:
    """
    Obtém ou cria um circuit breaker
    
    Args:
        name: Nome único do circuit breaker
        config: Configuração (opcional)
        fallback_function: Função de fallback (opcional)
        
    Returns:
        Instância do circuit breaker
    """
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name, config, fallback_function)
    
    return _circuit_breakers[name]


def get_all_circuit_breakers() -> Dict[str, CircuitBreaker]:
    """Retorna todos os circuit breakers registrados"""
    return _circuit_breakers.copy()


def reset_all_circuit_breakers():
    """Reseta todos os circuit breakers"""
    for cb in _circuit_breakers.values():
        cb.reset()
    logger.info("Todos os circuit breakers foram resetados")
