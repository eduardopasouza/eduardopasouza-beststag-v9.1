
"""
BestStag v9.1 - Sistema de Métricas para Integrações
Coleta e exposição de métricas para monitoramento
"""

import time
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
import logging

logger = logging.getLogger('beststag.integrations.metrics')


@dataclass
class MetricPoint:
    """Ponto de métrica com timestamp"""
    value: float
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    """
    Coletor de métricas para integrações
    
    Coleta métricas de performance, erros, latência e throughput
    para todas as integrações do sistema.
    """
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.retention_seconds = retention_hours * 3600
        
        # Armazenamento de métricas
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = defaultdict(float)
        self._histograms: Dict[str, List[MetricPoint]] = defaultdict(list)
        self._timeseries: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # Lock para thread safety
        self._lock = threading.RLock()
        
        # Métricas automáticas
        self._start_time = time.time()
        
        logger.info(f"Metrics Collector inicializado - Retenção: {retention_hours}h")
    
    def _cleanup_old_metrics(self):
        """Remove métricas antigas baseado na retenção"""
        cutoff_time = time.time() - self.retention_seconds
        
        with self._lock:
            # Limpar histogramas
            for metric_name, points in self._histograms.items():
                self._histograms[metric_name] = [
                    point for point in points
                    if point.timestamp > cutoff_time
                ]
            
            # Limpar timeseries
            for metric_name, series in self._timeseries.items():
                while series and series[0]['timestamp'] < cutoff_time:
                    series.popleft()
    
    def increment_counter(
        self,
        name: str,
        value: float = 1.0,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Incrementa um contador
        
        Args:
            name: Nome da métrica
            value: Valor para incrementar
            labels: Labels adicionais
        """
        with self._lock:
            key = self._build_key(name, labels)
            self._counters[key] += value
            
            # Adicionar à timeseries
            self._timeseries[key].append({
                'value': self._counters[key],
                'timestamp': time.time(),
                'type': 'counter'
            })
        
        logger.debug(f"Counter incrementado: {name} += {value}")
    
    def set_gauge(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Define valor de um gauge
        
        Args:
            name: Nome da métrica
            value: Valor do gauge
            labels: Labels adicionais
        """
        with self._lock:
            key = self._build_key(name, labels)
            self._gauges[key] = value
            
            # Adicionar à timeseries
            self._timeseries[key].append({
                'value': value,
                'timestamp': time.time(),
                'type': 'gauge'
            })
        
        logger.debug(f"Gauge definido: {name} = {value}")
    
    def record_histogram(
        self,
        name: str,
        value: float,
        labels: Optional[Dict[str, str]] = None
    ):
        """
        Registra valor em histograma
        
        Args:
            name: Nome da métrica
            value: Valor para registrar
            labels: Labels adicionais
        """
        with self._lock:
            key = self._build_key(name, labels)
            point = MetricPoint(
                value=value,
                timestamp=time.time(),
                labels=labels or {}
            )
            self._histograms[key].append(point)
            
            # Adicionar à timeseries
            self._timeseries[key].append({
                'value': value,
                'timestamp': time.time(),
                'type': 'histogram'
            })
        
        logger.debug(f"Histograma registrado: {name} = {value}")
    
    def time_function(self, name: str, labels: Optional[Dict[str, str]] = None):
        """
        Decorador para medir tempo de execução de funções
        
        Args:
            name: Nome da métrica
            labels: Labels adicionais
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    success = True
                    return result
                except Exception as e:
                    success = False
                    raise
                finally:
                    duration = time.time() - start_time
                    
                    # Registrar tempo de execução
                    exec_labels = (labels or {}).copy()
                    exec_labels['function'] = func.__name__
                    exec_labels['success'] = str(success)
                    
                    self.record_histogram(f"{name}_duration_seconds", duration, exec_labels)
                    self.increment_counter(f"{name}_total", 1.0, exec_labels)
            
            return wrapper
        return decorator
    
    def _build_key(self, name: str, labels: Optional[Dict[str, str]]) -> str:
        """Constrói chave única para métrica com labels"""
        if not labels:
            return name
        
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"
    
    def get_counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Obtém valor de contador"""
        key = self._build_key(name, labels)
        return self._counters.get(key, 0.0)
    
    def get_gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> float:
        """Obtém valor de gauge"""
        key = self._build_key(name, labels)
        return self._gauges.get(key, 0.0)
    
    def get_histogram_stats(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict[str, float]:
        """
        Obtém estatísticas de histograma
        
        Returns:
            Dicionário com count, sum, avg, min, max, p50, p95, p99
        """
        key = self._build_key(name, labels)
        points = self._histograms.get(key, [])
        
        if not points:
            return {
                'count': 0,
                'sum': 0.0,
                'avg': 0.0,
                'min': 0.0,
                'max': 0.0,
                'p50': 0.0,
                'p95': 0.0,
                'p99': 0.0
            }
        
        values = [point.value for point in points]
        values.sort()
        
        count = len(values)
        total = sum(values)
        avg = total / count
        
        def percentile(p):
            index = int(count * p / 100)
            return values[min(index, count - 1)]
        
        return {
            'count': count,
            'sum': total,
            'avg': avg,
            'min': min(values),
            'max': max(values),
            'p50': percentile(50),
            'p95': percentile(95),
            'p99': percentile(99)
        }
    
    def get_timeseries(
        self,
        name: str,
        labels: Optional[Dict[str, str]] = None,
        duration_minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Obtém série temporal de uma métrica
        
        Args:
            name: Nome da métrica
            labels: Labels para filtrar
            duration_minutes: Duração em minutos
            
        Returns:
            Lista de pontos da série temporal
        """
        key = self._build_key(name, labels)
        series = self._timeseries.get(key, deque())
        
        cutoff_time = time.time() - (duration_minutes * 60)
        
        return [
            point for point in series
            if point['timestamp'] > cutoff_time
        ]
    
    def get_all_metrics(self) -> Dict[str, Any]:
        """Retorna todas as métricas coletadas"""
        self._cleanup_old_metrics()
        
        with self._lock:
            return {
                'counters': dict(self._counters),
                'gauges': dict(self._gauges),
                'histograms': {
                    name: self.get_histogram_stats(name.split('{')[0], 
                                                 self._parse_labels(name))
                    for name in self._histograms.keys()
                },
                'system': {
                    'uptime_seconds': time.time() - self._start_time,
                    'metrics_count': len(self._counters) + len(self._gauges) + len(self._histograms),
                    'collection_time': time.time()
                }
            }
    
    def _parse_labels(self, key: str) -> Optional[Dict[str, str]]:
        """Parse labels de uma chave de métrica"""
        if '{' not in key:
            return None
        
        label_part = key.split('{')[1].rstrip('}')
        if not label_part:
            return None
        
        labels = {}
        for pair in label_part.split(','):
            if '=' in pair:
                k, v = pair.split('=', 1)
                labels[k] = v
        
        return labels
    
    def export_prometheus(self) -> str:
        """
        Exporta métricas no formato Prometheus
        
        Returns:
            String no formato Prometheus
        """
        self._cleanup_old_metrics()
        
        lines = []
        
        # Exportar counters
        for key, value in self._counters.items():
            name = key.split('{')[0]
            labels = self._parse_labels(key)
            
            if labels:
                label_str = ','.join(f'{k}="{v}"' for k, v in labels.items())
                lines.append(f'{name}{{{label_str}}} {value}')
            else:
                lines.append(f'{name} {value}')
        
        # Exportar gauges
        for key, value in self._gauges.items():
            name = key.split('{')[0]
            labels = self._parse_labels(key)
            
            if labels:
                label_str = ','.join(f'{k}="{v}"' for k, v in labels.items())
                lines.append(f'{name}{{{label_str}}} {value}')
            else:
                lines.append(f'{name} {value}')
        
        # Exportar histogramas
        for key, points in self._histograms.items():
            if not points:
                continue
                
            name = key.split('{')[0]
            labels = self._parse_labels(key)
            stats = self.get_histogram_stats(name, labels)
            
            label_str = ''
            if labels:
                label_str = ','.join(f'{k}="{v}"' for k, v in labels.items())
                label_str = f'{{{label_str}}}'
            
            lines.append(f'{name}_count{label_str} {stats["count"]}')
            lines.append(f'{name}_sum{label_str} {stats["sum"]}')
        
        return '\n'.join(lines)
    
    def reset_metrics(self):
        """Reseta todas as métricas"""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._timeseries.clear()
            self._start_time = time.time()
        
        logger.info("Todas as métricas foram resetadas")


# Instância global do coletor de métricas
_metrics_instance: Optional[MetricsCollector] = None


def get_metrics() -> MetricsCollector:
    """Retorna instância singleton do coletor de métricas"""
    global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = MetricsCollector()
    return _metrics_instance


def initialize_metrics(retention_hours: int = 24) -> MetricsCollector:
    """
    Inicializa o coletor de métricas global
    
    Args:
        retention_hours: Horas de retenção das métricas
        
    Returns:
        Instância do coletor configurada
    """
    global _metrics_instance
    _metrics_instance = MetricsCollector(retention_hours=retention_hours)
    return _metrics_instance


# Métricas específicas para integrações
class IntegrationMetrics:
    """Métricas específicas para integrações"""
    
    def __init__(self, integration_name: str):
        self.integration_name = integration_name
        self.metrics = get_metrics()
    
    def record_request(self, endpoint: str, success: bool, duration: float):
        """Registra uma requisição"""
        labels = {
            'integration': self.integration_name,
            'endpoint': endpoint,
            'success': str(success)
        }
        
        self.metrics.increment_counter('integration_requests_total', 1.0, labels)
        self.metrics.record_histogram('integration_request_duration_seconds', duration, labels)
    
    def record_error(self, error_type: str, endpoint: str = None):
        """Registra um erro"""
        labels = {
            'integration': self.integration_name,
            'error_type': error_type
        }
        
        if endpoint:
            labels['endpoint'] = endpoint
        
        self.metrics.increment_counter('integration_errors_total', 1.0, labels)
    
    def set_connection_status(self, connected: bool):
        """Define status da conexão"""
        labels = {'integration': self.integration_name}
        self.metrics.set_gauge('integration_connected', 1.0 if connected else 0.0, labels)
    
    def record_cache_hit(self, hit: bool):
        """Registra hit/miss do cache"""
        labels = {
            'integration': self.integration_name,
            'result': 'hit' if hit else 'miss'
        }
        self.metrics.increment_counter('integration_cache_requests_total', 1.0, labels)
    
    def record_rate_limit(self):
        """Registra hit de rate limit"""
        labels = {'integration': self.integration_name}
        self.metrics.increment_counter('integration_rate_limit_hits_total', 1.0, labels)
