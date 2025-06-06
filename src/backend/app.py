"""
BestStag v9.1 - Aplicação Principal Backend
FastAPI application com integração Abacus.AI, logging estruturado e health checks
"""

import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path para imports
root_dir = Path(__file__).parent.parent.parent
sys.path.append(str(root_dir))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, Optional

# Imports locais
from config.logging_config import setup_logging, get_logger, log_execution
from config.health_checks import get_health_status, get_simple_health
from src.python.abacus_client import create_abacus_client
from src.python.contextual_memory import ContextualMemorySystem
from src.python.intelligent_reports import IntelligentReportGenerator

# Imports das integrações otimizadas
try:
    from src.integrations.abacus import initialize_client as init_abacus_client
    from src.integrations.whatsapp import initialize_webhook, initialize_queue, send_whatsapp_message_via_twilio
    from src.integrations.common import initialize_metrics
    OPTIMIZED_INTEGRATIONS_AVAILABLE = True
except ImportError:
    OPTIMIZED_INTEGRATIONS_AVAILABLE = False

setup_logging(
    log_level=os.getenv('LOG_LEVEL', 'INFO'),
    log_dir=os.getenv('LOG_DIR', 'logs'),
    app_name='beststag-backend'
)

logger = get_logger('beststag.app')


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando BestStag v9.1 Backend")

    try:
        if OPTIMIZED_INTEGRATIONS_AVAILABLE:
            logger.info("Inicializando integrações otimizadas...")
            app.state.metrics = initialize_metrics(retention_hours=24)
            app.state.abacus_client = await init_abacus_client()

            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            app.state.whatsapp_queue = await initialize_queue(
                redis_url=redis_url,
                max_workers=int(os.getenv('WHATSAPP_WORKERS', '5')),
                rate_limit=int(os.getenv('WHATSAPP_RATE_LIMIT', '100'))
            )

            async def process_incoming_text(message_payload: Dict[str, Any]):
                user_number = message_payload.get("from")
                text = message_payload.get("content", {}).get("text") or message_payload.get("text", "")
                response_text = "Desculpe, não entendi."
                try:
                    abacus = app.state.abacus_client
                    result = await abacus.process_message(message=text, user_id=user_number, conversation_id=None, channel="whatsapp")
                    if isinstance(result, dict):
                        response_text = result.get("content") or result.get("response") or response_text
                except Exception as e:
                    logger.error(f"Erro ao gerar resposta de IA: {e}")
                try:
                    await send_whatsapp_message_via_twilio(user_number, response_text)
                    logger.info(f"Resposta enviada para {user_number}: {response_text}")
                except Exception as e:
                    logger.error(f"Falha ao enviar mensagem via Twilio: {e}")

            app.state.whatsapp_queue.register_handler('text', process_incoming_text)
            app.state.whatsapp_queue.register_handler('default', process_incoming_text)

            webhook_secret = os.getenv('WHATSAPP_WEBHOOK_SECRET')
            verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN')
            if webhook_secret and verify_token:
                app.state.whatsapp_webhook = initialize_webhook(
                    webhook_secret=webhook_secret,
                    verify_token=verify_token,
                    queue=app.state.whatsapp_queue,
                    enable_signature_validation=False
                )
                app.state.whatsapp_webhook.setup_routes(app, webhook_path="/webhook/whatsapp")
                logger.info("Webhook WhatsApp configurado")
            else:
                logger.warning("Credenciais WhatsApp não configuradas")

            await app.state.whatsapp_queue.start()
        else:
            logger.info("Usando integrações padrão...")
            app.state.abacus_client = create_abacus_client(use_optimized=False)

        app.state.contextual_memory = ContextualMemorySystem()
        app.state.intelligent_reports = IntelligentReportGenerator(
            abacus_client=app.state.abacus_client,
            memory_system=app.state.contextual_memory
        )

        logger.info("Todos os componentes inicializados com sucesso")

    except Exception as e:
        logger.error(f"Erro na inicialização: {e}", exc_info=True)
        raise

    yield
    logger.info("Finalizando BestStag Backend")


app = FastAPI(
    title="BestStag v9.1 API",
    description="Assistente Virtual Inteligente com IA Contextual",
    version="9.1.1",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Import endpoints that register routes
from . import whatsapp  # noqa: F401

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv('CORS_ORIGINS', '*').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=os.getenv('ALLOWED_HOSTS', '*').split(',')
)


@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.utcnow()
    logger.info(
        f"Requisição recebida: {request.method} {request.url.path}",
        extra={
            'method': request.method,
            'path': request.url.path,
            'query_params': str(request.query_params),
            'client_ip': request.client.host,
            'user_agent': request.headers.get('user-agent', ''),
            'request_id': id(request)
        }
    )
    try:
        response = await call_next(request)
        end_time = datetime.utcnow()
        logger.info(
            f"Resposta enviada: {response.status_code}",
            extra={
                'method': request.method,
                'path': request.url.path,
                'status_code': response.status_code,
                'processing_time': (end_time - start_time).total_seconds(),
                'request_id': id(request)
            }
        )
        return response
    except Exception as e:
        logger.error(
            f"Erro no processamento da requisição: {e}",
            extra={
                'method': request.method,
                'path': request.url.path,
                'processing_time': (datetime.utcnow() - start_time).total_seconds(),
                'request_id': id(request),
                'error_type': type(e).__name__
            },
            exc_info=True
        )
        raise


@app.get("/health")
async def health_check():
    return get_simple_health()


@app.get("/health/detailed")
async def detailed_health_check():
    try:
        return await get_health_status()
    except Exception as e:
        logger.error(f"Erro no health check detalhado: {e}", exc_info=True)
        return JSONResponse(status_code=503, content={"status": "unhealthy", "error": str(e)})


@app.get("/")
async def root():
    return {
        "message": "BestStag v9.1 API",
        "version": "9.1.1",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }


@app.get("/api/info")
async def api_info():
    return {
        "name": "BestStag",
        "version": "9.1.1",
        "description": "Assistente Virtual Inteligente com IA Contextual",
        "features": [
            "Integração Abacus.AI",
            "Memória Contextual",
            "Relatórios Inteligentes",
            "Análise de Sentimentos",
            "Suporte Multicanal"
        ],
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "chat": "/api/chat",
            "memory": "/api/memory",
            "reports": "/api/reports"
        }
    }


@app.post("/api/chat")
@log_execution('beststag.chat')
async def chat_endpoint(
    message: str,
    user_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    channel: str = "web"
):
    try:
        abacus_client = app.state.abacus_client
        contextual_memory = app.state.contextual_memory
        response = await abacus_client.process_message(
            message=message,
            user_id=user_id,
            conversation_id=conversation_id,
            channel=channel
        )
        if user_id and conversation_id:
            await contextual_memory.save_interaction(
                user_id=user_id,
                conversation_id=conversation_id,
                user_message=message,
                assistant_response=response.get('content', ''),
                metadata={'channel': channel}
            )
        return response
    except Exception as e:
        logger.error(f"Erro no processamento do chat: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


class SentimentPayload(BaseModel):
    text: str


@app.post("/api/sentiment")
async def analyze_sentiment(payload: SentimentPayload):
    text = payload.text.lower()
    if any(word in text for word in ["bom", "ótimo", "obrigado", "feliz"]):
        sentiment = "positive"; confidence = 0.9
    elif any(word in text for word in ["ruim", "triste", "ódio", "raiva"]):
        sentiment = "negative"; confidence = 0.9
    else:
        sentiment = "neutral"; confidence = 0.7
    return {"sentiment": sentiment, "confidence": confidence}


@app.get("/api/memory/{user_id}")
@log_execution('beststag.memory')
async def get_user_memory(user_id: str):
    try:
        contextual_memory = app.state.contextual_memory
        memory_data = await contextual_memory.get_user_memory(user_id)
        return {
            "user_id": user_id,
            "memory": memory_data,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
    except Exception as e:
        logger.error(f"Erro ao obter memória do usuário: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/reports/generate")
@log_execution('beststag.reports')
async def generate_report(
    background_tasks: BackgroundTasks,
    report_type: str,
    user_id: str,
    parameters: Dict[str, Any] = None
):
    try:
        intelligent_reports = app.state.intelligent_reports
        background_tasks.add_task(
            intelligent_reports.generate_report,
            report_type=report_type,
            user_id=user_id,
            parameters=parameters or {}
        )
        return {
            "message": "Relatório sendo gerado em background",
            "report_type": report_type,
            "user_id": user_id,
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports/{user_id}")
@log_execution('beststag.reports')
async def get_user_reports(user_id: str):
    try:
        intelligent_reports = app.state.intelligent_reports
        reports = await intelligent_reports.get_user_reports(user_id)
        return {
            "user_id": user_id,
            "reports": reports,
            "count": len(reports)
        }
    except Exception as e:
        logger.error(f"Erro ao obter relatórios: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Erro não tratado: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "message": "Entre em contato com o suporte",
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
    )


if __name__ == "__main__":
    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'false').lower() == 'true'

    logger.info(f"Iniciando servidor BestStag v9.1 em {host}:{port}", extra={'host': host, 'port': port, 'debug': debug})

    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info",
        access_log=True
    )
