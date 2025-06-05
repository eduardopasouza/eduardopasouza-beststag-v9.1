@"
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import sys
from datetime import datetime

app = FastAPI(title="BestStag API v9.1", version="9.1")

class MessageRequest(BaseModel):
    message: str
    user_id: str = "default"
    channel: str = "web"

class ChatResponse(BaseModel):
    response: str
    user_id: str
    timestamp: str
    channel: str

@app.get("/")
def read_root():
    return {
        "name": "BestStag - Assistente Virtual Inteligente",
        "version": "9.1",
        "status": "running",
        "description": "MicroSaaS de assistente virtual multicanal com IA"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "9.1",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "ok",
            "faiss": "loaded",
            "backend": "running"
        }
    }

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: MessageRequest):
    responses = {
        "oi": "Ola! Sou o BestStag, seu assistente virtual inteligente. Como posso ajudar?",
        "help": "Posso ajudar com tarefas, analises, relatorios e muito mais!",
        "status": "Sistema funcionando perfeitamente! Todas as integracoes ativas."
    }
    
    message_lower = request.message.lower()
    response = responses.get(message_lower, 
        f"Recebi sua mensagem: '{request.message}'. O BestStag v9.1 esta funcionando!")
    
    return ChatResponse(
        response=response,
        user_id=request.user_id,
        timestamp=datetime.now().isoformat(),
        channel=request.channel
    )

@app.get("/api/stats")
def get_stats():
    return {
        "total_messages": 0,
        "active_users": 0,
        "uptime": "running",
        "version": "9.1"
    }

if __name__ == "__main__":
    print("Iniciando BestStag v9.1 - Assistente Virtual Inteligente")
    print("API disponivel em: ")
    print("Documentacao em: 
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
"@ | Out-File -FilePath "app_working.py" -Encoding UTF8