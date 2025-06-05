
"""
BestStag v9.1 - Configuração de Logging Estruturado
Implementa logs estruturados com diferentes níveis e formatação JSON
"""

import logging
import logging.config
import json
import sys
from datetime import datetime
from pathlib import Path
import os


class JSONFormatter(logging.Formatter):
    """Formatter personalizado para logs em formato JSON"""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'process_id': os.getpid(),
            'thread_id': record.thread,
        }
        
        # Adicionar informações extras se disponíveis
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'execution_time'):
            log_entry['execution_time'] = record.execution_time
        
        # Adicionar stack trace para erros
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(
    log_level: str = "INFO",
    log_dir: str = "logs",
    app_name: str = "beststag"
):
    """
    Configura o sistema de logging estruturado
    
    Args:
        log_level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Diretório para arquivos de log
        app_name: Nome da aplicação para identificação nos logs
    """
    
    # Criar diretório de logs se não existir
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Configuração do logging
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'json': {
                '()': JSONFormatter,
            },
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': log_level,
                'formatter': 'standard',
                'stream': sys.stdout,
            },
            'file_json': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': log_level,
                'formatter': 'json',
                'filename': log_path / f'{app_name}.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8',
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'json',
                'filename': log_path / f'{app_name}_errors.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 5,
                'encoding': 'utf8',
            },
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['console', 'file_json', 'error_file'],
                'level': log_level,
                'propagate': False,
            },
            'beststag': {
                'handlers': ['console', 'file_json', 'error_file'],
                'level': log_level,
                'propagate': False,
            },
            'abacus_client': {
                'handlers': ['console', 'file_json'],
                'level': log_level,
                'propagate': False,
            },
            'uvicorn': {
                'handlers': ['console', 'file_json'],
                'level': 'INFO',
                'propagate': False,
            },
        },
    }
    
    logging.config.dictConfig(logging_config)
    
    # Log inicial
    logger = logging.getLogger('beststag.setup')
    logger.info(
        f"Sistema de logging configurado - Nível: {log_level}, Diretório: {log_dir}",
        extra={'component': 'logging_setup', 'app_name': app_name}
    )


def get_logger(name: str = None):
    """
    Retorna um logger configurado
    
    Args:
        name: Nome do logger (opcional)
    
    Returns:
        logging.Logger: Logger configurado
    """
    if name is None:
        name = 'beststag'
    
    return logging.getLogger(name)


# Decorador para logging automático de funções
def log_execution(logger_name: str = 'beststag'):
    """
    Decorador para logging automático de execução de funções
    
    Args:
        logger_name: Nome do logger a ser usado
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger(logger_name)
            start_time = datetime.utcnow()
            
            logger.info(
                f"Iniciando execução: {func.__name__}",
                extra={
                    'function': func.__name__,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs),
                    'start_time': start_time.isoformat()
                }
            )
            
            try:
                result = func(*args, **kwargs)
                end_time = datetime.utcnow()
                execution_time = (end_time - start_time).total_seconds()
                
                logger.info(
                    f"Execução concluída: {func.__name__}",
                    extra={
                        'function': func.__name__,
                        'execution_time': execution_time,
                        'success': True
                    }
                )
                
                return result
                
            except Exception as e:
                end_time = datetime.utcnow()
                execution_time = (end_time - start_time).total_seconds()
                
                logger.error(
                    f"Erro na execução: {func.__name__} - {str(e)}",
                    extra={
                        'function': func.__name__,
                        'execution_time': execution_time,
                        'success': False,
                        'error_type': type(e).__name__
                    },
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


# Health check logger
def log_health_check(component: str, status: str, details: dict = None):
    """
    Log específico para health checks
    
    Args:
        component: Nome do componente
        status: Status (healthy, unhealthy, degraded)
        details: Detalhes adicionais
    """
    logger = get_logger('beststag.health')
    
    log_data = {
        'component': component,
        'status': status,
        'check_time': datetime.utcnow().isoformat()
    }
    
    if details:
        log_data.update(details)
    
    if status == 'healthy':
        logger.info(f"Health check OK: {component}", extra=log_data)
    else:
        logger.warning(f"Health check FAIL: {component}", extra=log_data)


if __name__ == "__main__":
    # Teste da configuração de logging
    setup_logging(log_level="DEBUG")
    
    logger = get_logger('test')
    logger.debug("Teste de log DEBUG")
    logger.info("Teste de log INFO")
    logger.warning("Teste de log WARNING")
    logger.error("Teste de log ERROR")
    
    # Teste do decorador
    @log_execution('test')
    def test_function():
        return "Função de teste executada"
    
    test_function()
    
    # Teste do health check
    log_health_check('database', 'healthy', {'response_time': 0.05})
    log_health_check('redis', 'unhealthy', {'error': 'Connection timeout'})
