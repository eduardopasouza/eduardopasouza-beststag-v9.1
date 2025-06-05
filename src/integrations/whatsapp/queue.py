
"""
BestStag v9.1 - Sistema de Queue para WhatsApp
Processamento assíncrono de mensagens com retry e dead letter queue
"""

import asyncio
import json
import time
import uuid
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
import redis.asyncio as redis
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger('beststag.integrations.whatsapp.queue')


class MessageStatus(Enum):
    """Status das mensagens na queue"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class QueueMessage:
    """Mensagem na queue"""
    id: str
    payload: Dict[str, Any]
    status: MessageStatus = MessageStatus.PENDING
    attempts: int = 0
    max_attempts: int = 3
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    scheduled_at: Optional[float] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'id': self.id,
            'payload': self.payload,
            'status': self.status.value,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'scheduled_at': self.scheduled_at,
            'error_message': self.error_message,
            'processing_time': self.processing_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueueMessage':
        """Cria instância a partir de dicionário"""
        return cls(
            id=data['id'],
            payload=data['payload'],
            status=MessageStatus(data['status']),
            attempts=data['attempts'],
            max_attempts=data['max_attempts'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            scheduled_at=data.get('scheduled_at'),
            error_message=data.get('error_message'),
            processing_time=data.get('processing_time')
        )


class WhatsAppQueue:
    """
    Sistema de queue assíncrono para processamento de mensagens WhatsApp
    
    Features:
    - Processamento assíncrono com workers
    - Retry automático com backoff exponencial
    - Dead letter queue para mensagens falhadas
    - Monitoramento e métricas
    - Persistência Redis
    - Rate limiting
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        queue_name: str = "whatsapp_messages",
        max_workers: int = 5,
        max_attempts: int = 3,
        retry_delay: int = 60,
        rate_limit: int = 100  # mensagens por minuto
    ):
        self.redis_url = redis_url
        self.queue_name = queue_name
        self.max_workers = max_workers
        self.max_attempts = max_attempts
        self.retry_delay = retry_delay
        self.rate_limit = rate_limit
        
        # Chaves Redis
        self.pending_key = f"{queue_name}:pending"
        self.processing_key = f"{queue_name}:processing"
        self.completed_key = f"{queue_name}:completed"
        self.failed_key = f"{queue_name}:failed"
        self.dead_letter_key = f"{queue_name}:dead_letter"
        self.stats_key = f"{queue_name}:stats"
        self.rate_limit_key = f"{queue_name}:rate_limit"
        
        # Estado interno
        self._redis: Optional[redis.Redis] = None
        self._workers: List[asyncio.Task] = []
        self._running = False
        self._message_handlers: Dict[str, Callable] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        
        # Métricas
        self.stats = {
            'messages_received': 0,
            'messages_processed': 0,
            'messages_failed': 0,
            'messages_dead_letter': 0,
            'processing_time_total': 0.0,
            'rate_limit_hits': 0
        }
        
        logger.info(f"WhatsApp Queue inicializada - Workers: {max_workers}, Rate Limit: {rate_limit}/min")
    
    async def connect(self):
        """Conecta ao Redis"""
        try:
            self._redis = redis.from_url(self.redis_url)
            await self._redis.ping()
            logger.info(f"Conectado ao Redis: {self.redis_url}")
        except Exception as e:
            logger.error(f"Erro ao conectar Redis: {e}")
            raise
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self._redis:
            await self._redis.close()
            logger.info("Desconectado do Redis")
    
    def register_handler(self, message_type: str, handler: Callable):
        """
        Registra handler para tipo de mensagem
        
        Args:
            message_type: Tipo da mensagem (text, image, audio, etc.)
            handler: Função async para processar a mensagem
        """
        self._message_handlers[message_type] = handler
        logger.info(f"Handler registrado para tipo: {message_type}")
    
    async def _check_rate_limit(self) -> bool:
        """Verifica se está dentro do rate limit"""
        current_minute = int(time.time() // 60)
        key = f"{self.rate_limit_key}:{current_minute}"
        
        current_count = await self._redis.get(key)
        current_count = int(current_count) if current_count else 0
        
        if current_count >= self.rate_limit:
            self.stats['rate_limit_hits'] += 1
            return False
        
        # Incrementar contador
        pipe = self._redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)  # Expira em 1 minuto
        await pipe.execute()
        
        return True
    
    async def enqueue(
        self,
        payload: Dict[str, Any],
        priority: int = 0,
        delay: Optional[int] = None
    ) -> str:
        """
        Adiciona mensagem à queue
        
        Args:
            payload: Dados da mensagem
            priority: Prioridade (maior = mais prioritário)
            delay: Atraso em segundos (opcional)
            
        Returns:
            ID da mensagem
        """
        if not self._redis:
            await self.connect()
        
        # Verificar rate limit
        if not await self._check_rate_limit():
            logger.warning("Rate limit atingido, mensagem rejeitada")
            raise Exception("Rate limit exceeded")
        
        # Criar mensagem
        message_id = str(uuid.uuid4())
        scheduled_at = time.time() + delay if delay else None
        
        message = QueueMessage(
            id=message_id,
            payload=payload,
            max_attempts=self.max_attempts,
            scheduled_at=scheduled_at
        )
        
        # Adicionar à queue
        score = priority * 1000000 + time.time()  # Prioridade + timestamp
        await self._redis.zadd(
            self.pending_key,
            {json.dumps(message.to_dict()): score}
        )
        
        self.stats['messages_received'] += 1
        logger.debug(f"Mensagem enfileirada: {message_id}")
        
        return message_id
    
    async def _get_next_message(self) -> Optional[QueueMessage]:
        """Obtém próxima mensagem da queue"""
        current_time = time.time()
        
        # Buscar mensagem com maior prioridade que está pronta para processamento
        result = await self._redis.zrange(
            self.pending_key,
            0, 0,
            withscores=True
        )
        
        if not result:
            return None
        
        message_data, score = result[0]
        message_dict = json.loads(message_data)
        message = QueueMessage.from_dict(message_dict)
        
        # Verificar se está agendada para o futuro
        if message.scheduled_at and message.scheduled_at > current_time:
            return None
        
        # Remover da queue pending e adicionar à processing
        pipe = self._redis.pipeline()
        pipe.zrem(self.pending_key, message_data)
        pipe.hset(self.processing_key, message.id, message_data)
        await pipe.execute()
        
        return message
    
    async def _process_message(self, message: QueueMessage) -> bool:
        """
        Processa uma mensagem
        
        Args:
            message: Mensagem para processar
            
        Returns:
            True se processada com sucesso, False caso contrário
        """
        start_time = time.time()
        
        try:
            # Atualizar status
            message.status = MessageStatus.PROCESSING
            message.attempts += 1
            message.updated_at = time.time()
            
            # Determinar tipo da mensagem
            message_type = message.payload.get('type', 'text')
            
            # Buscar handler
            handler = self._message_handlers.get(message_type)
            if not handler:
                logger.warning(f"Nenhum handler encontrado para tipo: {message_type}")
                handler = self._message_handlers.get('default')
            
            if not handler:
                raise Exception(f"Nenhum handler disponível para tipo: {message_type}")
            
            # Processar mensagem
            if asyncio.iscoroutinefunction(handler):
                await handler(message.payload)
            else:
                # Executar handler síncrono em thread pool
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(self._executor, handler, message.payload)
            
            # Sucesso
            processing_time = time.time() - start_time
            message.status = MessageStatus.COMPLETED
            message.processing_time = processing_time
            message.updated_at = time.time()
            
            # Mover para completed
            await self._redis.hset(
                self.completed_key,
                message.id,
                json.dumps(message.to_dict())
            )
            await self._redis.hdel(self.processing_key, message.id)
            
            self.stats['messages_processed'] += 1
            self.stats['processing_time_total'] += processing_time
            
            logger.debug(f"Mensagem processada com sucesso: {message.id} ({processing_time:.2f}s)")
            return True
            
        except Exception as e:
            # Falha no processamento
            processing_time = time.time() - start_time
            message.status = MessageStatus.FAILED
            message.error_message = str(e)
            message.processing_time = processing_time
            message.updated_at = time.time()
            
            logger.error(f"Erro ao processar mensagem {message.id}: {e}")
            
            # Verificar se deve tentar novamente
            if message.attempts < message.max_attempts:
                # Reagendar com backoff exponencial
                delay = self.retry_delay * (2 ** (message.attempts - 1))
                message.scheduled_at = time.time() + delay
                message.status = MessageStatus.PENDING
                
                # Voltar para pending queue
                score = time.time() + delay
                await self._redis.zadd(
                    self.pending_key,
                    {json.dumps(message.to_dict()): score}
                )
                await self._redis.hdel(self.processing_key, message.id)
                
                logger.info(f"Mensagem reagendada: {message.id} (tentativa {message.attempts}/{message.max_attempts})")
            else:
                # Mover para dead letter queue
                message.status = MessageStatus.DEAD_LETTER
                await self._redis.hset(
                    self.dead_letter_key,
                    message.id,
                    json.dumps(message.to_dict())
                )
                await self._redis.hdel(self.processing_key, message.id)
                
                self.stats['messages_dead_letter'] += 1
                logger.error(f"Mensagem movida para dead letter queue: {message.id}")
            
            self.stats['messages_failed'] += 1
            return False
    
    async def _worker(self, worker_id: int):
        """Worker para processar mensagens"""
        logger.info(f"Worker {worker_id} iniciado")
        
        while self._running:
            try:
                message = await self._get_next_message()
                
                if message:
                    await self._process_message(message)
                else:
                    # Nenhuma mensagem disponível, aguardar
                    await asyncio.sleep(1)
                    
            except Exception as e:
                logger.error(f"Erro no worker {worker_id}: {e}")
                await asyncio.sleep(5)  # Aguardar antes de tentar novamente
        
        logger.info(f"Worker {worker_id} finalizado")
    
    async def start(self):
        """Inicia o processamento da queue"""
        if self._running:
            logger.warning("Queue já está rodando")
            return
        
        if not self._redis:
            await self.connect()
        
        self._running = True
        
        # Iniciar workers
        for i in range(self.max_workers):
            worker = asyncio.create_task(self._worker(i))
            self._workers.append(worker)
        
        logger.info(f"Queue iniciada com {self.max_workers} workers")
    
    async def stop(self):
        """Para o processamento da queue"""
        if not self._running:
            return
        
        self._running = False
        
        # Aguardar workers finalizarem
        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)
            self._workers.clear()
        
        # Fechar thread pool
        self._executor.shutdown(wait=True)
        
        logger.info("Queue parada")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da queue"""
        if not self._redis:
            return self.stats
        
        # Contar mensagens em cada estado
        pending_count = await self._redis.zcard(self.pending_key)
        processing_count = await self._redis.hlen(self.processing_key)
        completed_count = await self._redis.hlen(self.completed_key)
        failed_count = await self._redis.hlen(self.failed_key)
        dead_letter_count = await self._redis.hlen(self.dead_letter_key)
        
        avg_processing_time = (
            self.stats['processing_time_total'] / max(self.stats['messages_processed'], 1)
        )
        
        return {
            **self.stats,
            'queue_sizes': {
                'pending': pending_count,
                'processing': processing_count,
                'completed': completed_count,
                'failed': failed_count,
                'dead_letter': dead_letter_count
            },
            'avg_processing_time': round(avg_processing_time, 3),
            'workers_active': len(self._workers),
            'is_running': self._running
        }
    
    async def clear_completed(self, older_than_hours: int = 24):
        """Remove mensagens completadas antigas"""
        if not self._redis:
            return
        
        cutoff_time = time.time() - (older_than_hours * 3600)
        
        # Buscar mensagens antigas
        completed_messages = await self._redis.hgetall(self.completed_key)
        old_keys = []
        
        for key, data in completed_messages.items():
            message_dict = json.loads(data)
            if message_dict['updated_at'] < cutoff_time:
                old_keys.append(key)
        
        # Remover mensagens antigas
        if old_keys:
            await self._redis.hdel(self.completed_key, *old_keys)
            logger.info(f"Removidas {len(old_keys)} mensagens completadas antigas")
    
    async def requeue_dead_letters(self, message_ids: Optional[List[str]] = None):
        """Recoloca mensagens da dead letter queue de volta na queue principal"""
        if not self._redis:
            return
        
        if message_ids:
            # Recolocar mensagens específicas
            for msg_id in message_ids:
                data = await self._redis.hget(self.dead_letter_key, msg_id)
                if data:
                    message_dict = json.loads(data)
                    message = QueueMessage.from_dict(message_dict)
                    message.status = MessageStatus.PENDING
                    message.attempts = 0
                    message.error_message = None
                    message.updated_at = time.time()
                    
                    # Adicionar de volta à pending queue
                    await self._redis.zadd(
                        self.pending_key,
                        {json.dumps(message.to_dict()): time.time()}
                    )
                    await self._redis.hdel(self.dead_letter_key, msg_id)
                    
            logger.info(f"Recolocadas {len(message_ids)} mensagens da dead letter queue")
        else:
            # Recolocar todas as mensagens
            dead_letters = await self._redis.hgetall(self.dead_letter_key)
            
            for msg_id, data in dead_letters.items():
                message_dict = json.loads(data)
                message = QueueMessage.from_dict(message_dict)
                message.status = MessageStatus.PENDING
                message.attempts = 0
                message.error_message = None
                message.updated_at = time.time()
                
                await self._redis.zadd(
                    self.pending_key,
                    {json.dumps(message.to_dict()): time.time()}
                )
            
            if dead_letters:
                await self._redis.delete(self.dead_letter_key)
                logger.info(f"Recolocadas {len(dead_letters)} mensagens da dead letter queue")


# Instância global da queue
_queue_instance: Optional[WhatsAppQueue] = None


def get_queue() -> WhatsAppQueue:
    """Retorna instância singleton da queue"""
    global _queue_instance
    if _queue_instance is None:
        _queue_instance = WhatsAppQueue()
    return _queue_instance


async def initialize_queue(
    redis_url: str = "redis://localhost:6379",
    max_workers: int = 5,
    rate_limit: int = 100
) -> WhatsAppQueue:
    """
    Inicializa a queue global
    
    Args:
        redis_url: URL do Redis
        max_workers: Número máximo de workers
        rate_limit: Limite de mensagens por minuto
        
    Returns:
        Instância da queue configurada
    """
    global _queue_instance
    
    _queue_instance = WhatsAppQueue(
        redis_url=redis_url,
        max_workers=max_workers,
        rate_limit=rate_limit
    )
    
    await _queue_instance.connect()
    return _queue_instance
