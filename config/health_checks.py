
"""
BestStag v9.1 - Health Checks e Monitoramento
Implementa verificações de saúde para todos os componentes do sistema
"""

import asyncio
import time
import psutil
import redis
import psycopg2
from typing import Dict, Any, Optional
import requests
from datetime import datetime
import os
from .logging_config import get_logger, log_health_check


class HealthChecker:
    """Classe principal para verificações de saúde do sistema"""
    
    def __init__(self):
        self.logger = get_logger('beststag.health')
        self.start_time = time.time()
    
    async def check_all(self) -> Dict[str, Any]:
        """
        Executa todas as verificações de saúde
        
        Returns:
            Dict com status de todos os componentes
        """
        checks = {
            'system': await self.check_system(),
            'database': await self.check_database(),
            'redis': await self.check_redis(),
            'abacus_api': await self.check_abacus_api(),
            'n8n': await self.check_n8n(),
            'disk_space': await self.check_disk_space(),
            'memory': await self.check_memory(),
        }
        
        # Status geral
        overall_status = 'healthy'
        for component, status in checks.items():
            if status['status'] != 'healthy':
                overall_status = 'degraded' if overall_status == 'healthy' else 'unhealthy'
        
        result = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'overall_status': overall_status,
            'uptime_seconds': time.time() - self.start_time,
            'checks': checks
        }
        
        self.logger.info(
            f"Health check completo - Status: {overall_status}",
            extra={'overall_status': overall_status, 'checks_count': len(checks)}
        )
        
        return result
    
    async def check_system(self) -> Dict[str, Any]:
        """Verifica saúde geral do sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            status = 'healthy'
            if cpu_percent > 90 or memory.percent > 90:
                status = 'degraded'
            if cpu_percent > 95 or memory.percent > 95:
                status = 'unhealthy'
            
            result = {
                'status': status,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else None,
            }
            
            log_health_check('system', status, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no health check do sistema: {e}", exc_info=True)
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def check_database(self) -> Dict[str, Any]:
        """Verifica conexão com PostgreSQL"""
        try:
            database_url = os.getenv('DATABASE_URL', 'postgresql://beststag:beststag123@localhost:5432/beststag')
            
            start_time = time.time()
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.fetchone()
            cursor.close()
            conn.close()
            response_time = time.time() - start_time
            
            status = 'healthy'
            if response_time > 1.0:
                status = 'degraded'
            if response_time > 5.0:
                status = 'unhealthy'
            
            result = {
                'status': status,
                'response_time': response_time,
                'connection': 'ok'
            }
            
            log_health_check('database', status, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no health check do database: {e}", exc_info=True)
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def check_redis(self) -> Dict[str, Any]:
        """Verifica conexão com Redis"""
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            
            start_time = time.time()
            r = redis.from_url(redis_url)
            r.ping()
            response_time = time.time() - start_time
            
            # Verificar memória do Redis
            info = r.info('memory')
            memory_usage = info.get('used_memory', 0)
            max_memory = info.get('maxmemory', 0)
            
            status = 'healthy'
            if response_time > 0.5:
                status = 'degraded'
            if response_time > 2.0 or (max_memory > 0 and memory_usage / max_memory > 0.9):
                status = 'unhealthy'
            
            result = {
                'status': status,
                'response_time': response_time,
                'memory_usage_bytes': memory_usage,
                'connection': 'ok'
            }
            
            log_health_check('redis', status, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no health check do Redis: {e}", exc_info=True)
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def check_abacus_api(self) -> Dict[str, Any]:
        """Verifica conectividade com Abacus.AI API"""
        try:
            api_key = os.getenv('ABACUS_API_KEY')
            if not api_key or api_key == 'your_abacus_api_key_here':
                return {
                    'status': 'degraded',
                    'message': 'API key não configurada'
                }
            
            base_url = os.getenv('ABACUS_BASE_URL', 'https://api.abacus.ai')
            
            start_time = time.time()
            response = requests.get(
                f"{base_url}/health",
                headers={'Authorization': f'Bearer {api_key}'},
                timeout=10
            )
            response_time = time.time() - start_time
            
            status = 'healthy' if response.status_code == 200 else 'unhealthy'
            if response_time > 2.0:
                status = 'degraded'
            
            result = {
                'status': status,
                'response_time': response_time,
                'status_code': response.status_code
            }
            
            log_health_check('abacus_api', status, result)
            return result
            
        except requests.exceptions.Timeout:
            return {'status': 'unhealthy', 'error': 'Timeout na API'}
        except Exception as e:
            self.logger.error(f"Erro no health check da Abacus API: {e}", exc_info=True)
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def check_n8n(self) -> Dict[str, Any]:
        """Verifica status do N8N"""
        try:
            n8n_url = os.getenv('N8N_WEBHOOK_URL', 'http://localhost:5678')
            
            start_time = time.time()
            response = requests.get(f"{n8n_url}/healthz", timeout=5)
            response_time = time.time() - start_time
            
            status = 'healthy' if response.status_code == 200 else 'unhealthy'
            if response_time > 1.0:
                status = 'degraded'
            
            result = {
                'status': status,
                'response_time': response_time,
                'status_code': response.status_code
            }
            
            log_health_check('n8n', status, result)
            return result
            
        except requests.exceptions.ConnectionError:
            return {'status': 'degraded', 'message': 'N8N não disponível (opcional)'}
        except Exception as e:
            self.logger.error(f"Erro no health check do N8N: {e}", exc_info=True)
            return {'status': 'degraded', 'error': str(e)}
    
    async def check_disk_space(self) -> Dict[str, Any]:
        """Verifica espaço em disco"""
        try:
            disk_usage = psutil.disk_usage('/')
            percent_used = (disk_usage.used / disk_usage.total) * 100
            
            status = 'healthy'
            if percent_used > 80:
                status = 'degraded'
            if percent_used > 90:
                status = 'unhealthy'
            
            result = {
                'status': status,
                'percent_used': percent_used,
                'free_bytes': disk_usage.free,
                'total_bytes': disk_usage.total
            }
            
            log_health_check('disk_space', status, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no health check do disco: {e}", exc_info=True)
            return {'status': 'unhealthy', 'error': str(e)}
    
    async def check_memory(self) -> Dict[str, Any]:
        """Verifica uso de memória"""
        try:
            memory = psutil.virtual_memory()
            
            status = 'healthy'
            if memory.percent > 80:
                status = 'degraded'
            if memory.percent > 90:
                status = 'unhealthy'
            
            result = {
                'status': status,
                'percent_used': memory.percent,
                'available_bytes': memory.available,
                'total_bytes': memory.total
            }
            
            log_health_check('memory', status, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Erro no health check da memória: {e}", exc_info=True)
            return {'status': 'unhealthy', 'error': str(e)}


# Instância global do health checker
health_checker = HealthChecker()


async def get_health_status() -> Dict[str, Any]:
    """Função conveniente para obter status de saúde"""
    return await health_checker.check_all()


def get_simple_health() -> Dict[str, str]:
    """Health check simples e rápido para endpoints básicos"""
    try:
        # Verificações básicas rápidas
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        if cpu_percent > 95 or memory_percent > 95:
            return {'status': 'unhealthy'}
        elif cpu_percent > 80 or memory_percent > 80:
            return {'status': 'degraded'}
        else:
            return {'status': 'healthy'}
            
    except Exception:
        return {'status': 'unhealthy'}


if __name__ == "__main__":
    # Teste dos health checks
    async def test_health_checks():
        checker = HealthChecker()
        result = await checker.check_all()
        print(f"Health check result: {result}")
    
    asyncio.run(test_health_checks())
