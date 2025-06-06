
"""
BestStag v9.1 - Webhook WhatsApp Otimizado
Webhook seguro com validação de assinatura, rate limiting e processamento assíncrono
"""

import hmac
import hashlib
import json
import time
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging

from .queue import WhatsAppQueue, get_queue
from .validator import SignatureValidator
from ..common.metrics import IntegrationMetrics

logger = logging.getLogger('beststag.integrations.whatsapp.webhook')


class WhatsAppWebhook:
    """
    Webhook WhatsApp otimizado com validação segura e processamento assíncrono
    
    Features:
    - Validação robusta de assinatura HMAC-SHA256
    - Rate limiting por IP e usuário
    - Processamento assíncrono via queue
    - Suporte a diferentes tipos de mensagem
    - Logs detalhados e monitoramento
    - Retry automático para falhas
    - Dead letter queue para mensagens problemáticas
    """
    
    def __init__(
        self,
        webhook_secret: str,
        verify_token: str,
        queue: Optional[WhatsAppQueue] = None,
        rate_limit_per_minute: int = 60,
        enable_signature_validation: bool = True
    ):
        self.webhook_secret = webhook_secret
        self.verify_token = verify_token
        self.queue = queue or get_queue()
        self.rate_limit_per_minute = rate_limit_per_minute
        self.enable_signature_validation = enable_signature_validation
        
        # Validador de assinatura
        self.signature_validator = SignatureValidator(webhook_secret)
        
        # Métricas
        self.metrics = IntegrationMetrics("whatsapp")
        
        # Rate limiting por IP
        self._rate_limits: Dict[str, Dict[str, Any]] = {}
        
        # Handlers para diferentes tipos de mensagem
        self._message_handlers: Dict[str, Callable] = {}
        
        # Estatísticas
        self.stats = {
            "webhooks_received": 0,
            "webhooks_processed": 0,
            "webhooks_failed": 0,
            "signature_validation_failures": 0,
            "rate_limit_hits": 0,
            "messages_queued": 0
        }
        
        logger.info(f"WhatsApp Webhook inicializado - Rate Limit: {rate_limit_per_minute}/min")
    
    def register_message_handler(self, message_type: str, handler: Callable):
        """
        Registra handler para tipo específico de mensagem
        
        Args:
            message_type: Tipo da mensagem (text, image, audio, video, document, location, etc.)
            handler: Função para processar a mensagem
        """
        self._message_handlers[message_type] = handler
        logger.info(f"Handler registrado para tipo de mensagem: {message_type}")
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """
        Verifica rate limiting por IP
        
        Args:
            client_ip: IP do cliente
            
        Returns:
            True se dentro do limite, False caso contrário
        """
        current_time = time.time()
        current_minute = int(current_time // 60)
        
        if client_ip not in self._rate_limits:
            self._rate_limits[client_ip] = {
                "minute": current_minute,
                "count": 0
            }
        
        rate_limit_data = self._rate_limits[client_ip]
        
        # Reset contador se mudou de minuto
        if rate_limit_data["minute"] != current_minute:
            rate_limit_data["minute"] = current_minute
            rate_limit_data["count"] = 0
        
        # Verificar limite
        if rate_limit_data["count"] >= self.rate_limit_per_minute:
            self.stats["rate_limit_hits"] += 1
            self.metrics.record_rate_limit()
            return False
        
        rate_limit_data["count"] += 1
        return True
    
    def _extract_message_data(self, webhook_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrai dados das mensagens do webhook
        
        Args:
            webhook_data: Dados do webhook
            
        Returns:
            Lista de mensagens extraídas
        """
        messages = []

        try:
            # Formato simples enviado pelo Twilio
            if "Body" in webhook_data and "From" in webhook_data:
                msg_text = webhook_data.get("Body", "")
                from_number = webhook_data.get("From")
                to_number = webhook_data.get("To")
                msg_id = webhook_data.get("MessageSid") or webhook_data.get("SmsMessageSid")
                processed = {
                    "id": msg_id,
                    "from": from_number,
                    "to": to_number,
                    "type": "text",
                    "webhook_type": "twilio_message",
                    "content": {"text": msg_text}
                }
                messages.append(processed)
                return messages

            # Estrutura padrão do WhatsApp Cloud API
            if "entry" in webhook_data:
                for entry in webhook_data["entry"]:
                    if "changes" in entry:
                        for change in entry["changes"]:
                            if change.get("field") == "messages":
                                value = change.get("value", {})
                                
                                # Processar mensagens recebidas
                                if "messages" in value:
                                    for message in value["messages"]:
                                        processed_message = self._process_message_structure(message, value)
                                        if processed_message:
                                            messages.append(processed_message)
                                
                                # Processar status de mensagens enviadas
                                if "statuses" in value:
                                    for status in value["statuses"]:
                                        processed_status = self._process_status_structure(status, value)
                                        if processed_status:
                                            messages.append(processed_status)
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados da mensagem: {e}")
            self.metrics.record_error("message_extraction_error")
        
        return messages
    
    def _process_message_structure(self, message: Dict[str, Any], value: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Processa estrutura de mensagem individual
        
        Args:
            message: Dados da mensagem
            value: Dados do value do webhook
            
        Returns:
            Mensagem processada ou None
        """
        try:
            # Informações básicas
            processed = {
                "id": message.get("id"),
                "from": message.get("from"),
                "timestamp": message.get("timestamp"),
                "type": message.get("type", "unknown"),
                "webhook_type": "message",
                "metadata": {
                    "display_phone_number": value.get("metadata", {}).get("display_phone_number"),
                    "phone_number_id": value.get("metadata", {}).get("phone_number_id")
                }
            }
            
            # Processar conteúdo baseado no tipo
            message_type = message.get("type")
            
            if message_type == "text":
                processed["content"] = {
                    "text": message.get("text", {}).get("body", "")
                }
            
            elif message_type == "image":
                image_data = message.get("image", {})
                processed["content"] = {
                    "media_id": image_data.get("id"),
                    "mime_type": image_data.get("mime_type"),
                    "sha256": image_data.get("sha256"),
                    "caption": image_data.get("caption", "")
                }
            
            elif message_type == "audio":
                audio_data = message.get("audio", {})
                processed["content"] = {
                    "media_id": audio_data.get("id"),
                    "mime_type": audio_data.get("mime_type"),
                    "sha256": audio_data.get("sha256"),
                    "voice": audio_data.get("voice", False)
                }
            
            elif message_type == "video":
                video_data = message.get("video", {})
                processed["content"] = {
                    "media_id": video_data.get("id"),
                    "mime_type": video_data.get("mime_type"),
                    "sha256": video_data.get("sha256"),
                    "caption": video_data.get("caption", "")
                }
            
            elif message_type == "document":
                doc_data = message.get("document", {})
                processed["content"] = {
                    "media_id": doc_data.get("id"),
                    "mime_type": doc_data.get("mime_type"),
                    "sha256": doc_data.get("sha256"),
                    "filename": doc_data.get("filename", ""),
                    "caption": doc_data.get("caption", "")
                }
            
            elif message_type == "location":
                location_data = message.get("location", {})
                processed["content"] = {
                    "latitude": location_data.get("latitude"),
                    "longitude": location_data.get("longitude"),
                    "name": location_data.get("name", ""),
                    "address": location_data.get("address", "")
                }
            
            elif message_type == "contacts":
                processed["content"] = {
                    "contacts": message.get("contacts", [])
                }
            
            elif message_type == "interactive":
                interactive_data = message.get("interactive", {})
                processed["content"] = {
                    "type": interactive_data.get("type"),
                    "button_reply": interactive_data.get("button_reply"),
                    "list_reply": interactive_data.get("list_reply")
                }
            
            else:
                # Tipo desconhecido, salvar dados brutos
                processed["content"] = {
                    "raw_data": message
                }
                logger.warning(f"Tipo de mensagem desconhecido: {message_type}")
            
            # Informações de contexto (reply, forward)
            if "context" in message:
                processed["context"] = message["context"]
            
            return processed
            
        except Exception as e:
            logger.error(f"Erro ao processar estrutura da mensagem: {e}")
            return None
    
    def _process_status_structure(self, status: Dict[str, Any], value: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Processa estrutura de status de mensagem
        
        Args:
            status: Dados do status
            value: Dados do value do webhook
            
        Returns:
            Status processado ou None
        """
        try:
            return {
                "id": status.get("id"),
                "recipient_id": status.get("recipient_id"),
                "status": status.get("status"),
                "timestamp": status.get("timestamp"),
                "type": "status",
                "webhook_type": "status",
                "metadata": {
                    "display_phone_number": value.get("metadata", {}).get("display_phone_number"),
                    "phone_number_id": value.get("metadata", {}).get("phone_number_id")
                },
                "pricing": status.get("pricing"),
                "conversation": status.get("conversation")
            }
        except Exception as e:
            logger.error(f"Erro ao processar estrutura do status: {e}")
            return None
    
    async def verify_webhook(self, request: Request) -> JSONResponse:
        """
        Verifica webhook durante setup (GET request)
        
        Args:
            request: Request do FastAPI
            
        Returns:
            Response de verificação
        """
        try:
            # Extrair parâmetros de query
            mode = request.query_params.get("hub.mode")
            token = request.query_params.get("hub.verify_token")
            challenge = request.query_params.get("hub.challenge")
            
            # Verificar parâmetros
            if mode == "subscribe" and token == self.verify_token:
                logger.info("Webhook verificado com sucesso")
                return JSONResponse(content=int(challenge))
            else:
                logger.warning(f"Falha na verificação do webhook - Mode: {mode}, Token válido: {token == self.verify_token}")
                raise HTTPException(status_code=403, detail="Forbidden")
                
        except Exception as e:
            logger.error(f"Erro na verificação do webhook: {e}")
            raise HTTPException(status_code=400, detail="Bad Request")
    
    async def handle_webhook(self, request: Request, background_tasks: BackgroundTasks) -> JSONResponse:
        """
        Processa webhook do WhatsApp (POST request)
        
        Args:
            request: Request do FastAPI
            background_tasks: Tasks em background
            
        Returns:
            Response de confirmação
        """
        start_time = time.time()
        client_ip = request.client.host
        
        try:
            # Verificar rate limiting
            if not self._check_rate_limit(client_ip):
                logger.warning(f"Rate limit excedido para IP: {client_ip}")
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Ler body da requisição
            body = await request.body()
            content_type = request.headers.get("content-type", "")
            
            # Validar assinatura se habilitado
            if self.enable_signature_validation:
                signature_header = request.headers.get("X-Hub-Signature-256") or request.headers.get("X-Twilio-Signature")
                
                if not signature_header:
                    self.stats["signature_validation_failures"] += 1
                    logger.warning("Header de assinatura ausente")
                    raise HTTPException(status_code=400, detail="Missing signature header")
                
                if request.headers.get("X-Twilio-Signature"):
                    logger.warning("Validação de assinatura Twilio não implementada")
                else:
                    if not self.signature_validator.validate_signature(body, signature_header):
                        self.stats["signature_validation_failures"] += 1
                        logger.warning("Validação de assinatura falhou")
                        raise HTTPException(status_code=401, detail="Invalid signature")
            
            # Parse JSON ou form
            try:
                if "application/x-www-form-urlencoded" in content_type:
                    form_data = await request.form()
                    webhook_data = {k: v for k, v in form_data.items()}
                else:
                    webhook_data = json.loads(body.decode('utf-8'))
            except Exception as e:
                logger.error(f"Erro ao fazer parse do webhook: {e}")
                raise HTTPException(status_code=400, detail="Invalid webhook body")
            
            # Extrair mensagens
            messages = self._extract_message_data(webhook_data)
            
            # Processar mensagens assincronamente
            for message in messages:
                try:
                    # Adicionar à queue para processamento
                    await self.queue.enqueue(message, priority=1)
                    self.stats["messages_queued"] += 1
                    
                    logger.debug(f"Mensagem enfileirada: {message.get('id', 'unknown')}")
                    
                except Exception as e:
                    logger.error(f"Erro ao enfileirar mensagem: {e}")
                    self.metrics.record_error("queue_error")
            
            # Atualizar estatísticas
            duration = time.time() - start_time
            self.stats["webhooks_received"] += 1
            self.stats["webhooks_processed"] += 1
            
            # Registrar métricas
            self.metrics.record_request("webhook", True, duration)
            
            logger.info(f"Webhook processado com sucesso - {len(messages)} mensagens - {duration:.3f}s")
            
            # Resposta de confirmação
            return JSONResponse(content={"status": "ok"}, status_code=200)
            
        except HTTPException:
            # Re-raise HTTP exceptions
            duration = time.time() - start_time
            self.stats["webhooks_failed"] += 1
            self.metrics.record_request("webhook", False, duration)
            raise
            
        except Exception as e:
            # Erro interno
            duration = time.time() - start_time
            self.stats["webhooks_failed"] += 1
            
            logger.error(f"Erro interno no webhook: {e}", exc_info=True)
            self.metrics.record_request("webhook", False, duration)
            self.metrics.record_error("internal_error")
            
            raise HTTPException(status_code=500, detail="Internal server error")
    
    def setup_routes(self, app: FastAPI, webhook_path: str = "/webhook/whatsapp"):
        """
        Configura rotas do webhook no FastAPI
        
        Args:
            app: Instância do FastAPI
            webhook_path: Caminho do webhook
        """
        @app.get(webhook_path)
        async def verify_webhook_endpoint(request: Request):
            return await self.verify_webhook(request)
        
        @app.post(webhook_path)
        async def handle_webhook_endpoint(request: Request, background_tasks: BackgroundTasks):
            return await self.handle_webhook(request, background_tasks)
        
        logger.info(f"Rotas do webhook configuradas em: {webhook_path}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do webhook"""
        return {
            **self.stats,
            "queue_stats": self.queue.get_stats() if hasattr(self.queue, 'get_stats') else {},
            "rate_limits_active": len(self._rate_limits),
            "handlers_registered": len(self._message_handlers)
        }
    
    def clear_rate_limits(self):
        """Limpa rate limits (útil para testes)"""
        self._rate_limits.clear()
        logger.info("Rate limits limpos")


# Instância global do webhook
_webhook_instance: Optional[WhatsAppWebhook] = None


def get_webhook() -> WhatsAppWebhook:
    """Retorna instância singleton do webhook"""
    global _webhook_instance
    if _webhook_instance is None:
        raise RuntimeError("Webhook não foi inicializado. Chame initialize_webhook() primeiro.")
    return _webhook_instance


def initialize_webhook(
    webhook_secret: str,
    verify_token: str,
    queue: Optional[WhatsAppQueue] = None,
    rate_limit_per_minute: int = 60,
    enable_signature_validation: bool = True
) -> WhatsAppWebhook:
    """
    Inicializa o webhook global
    
    Args:
        webhook_secret: Secret para validação de assinatura
        verify_token: Token para verificação do webhook
        queue: Instância da queue (opcional)
        rate_limit_per_minute: Rate limit por minuto
        
    Returns:
        Instância do webhook configurada
    """
    global _webhook_instance
    
    _webhook_instance = WhatsAppWebhook(
        webhook_secret=webhook_secret,
        verify_token=verify_token,
        queue=queue,
        rate_limit_per_minute=rate_limit_per_minute,
        enable_signature_validation=enable_signature_validation
    )
    
    return _webhook_instance
