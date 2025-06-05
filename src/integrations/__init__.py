
"""
BestStag v9.1 - Módulo de Integrações Otimizadas
Contém todas as integrações críticas com sistemas externos
"""

__version__ = "9.1.1"
__author__ = "BestStag Team"

from .abacus import AbacusOptimizedClient, IntelligentCache, CircuitBreaker
from .whatsapp import WhatsAppWebhook, WhatsAppQueue
from .common import MetricsCollector

__all__ = [
    'AbacusOptimizedClient',
    'WhatsAppWebhook', 
    'WhatsAppQueue',
    'CircuitBreaker',
    'IntelligentCache',
    'MetricsCollector'
]
