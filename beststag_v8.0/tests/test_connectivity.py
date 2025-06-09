"""Teste de conectividade com API externa (OpenAI)."""

import os

import httpx


def test_openai_connection():
    """Realiza uma requisição simples para verificar acesso externo."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        # Se a chave não estiver definida, o teste é pulado
        print("OPENAI_API_KEY não definido.")
        return
    headers = {"Authorization": f"Bearer {api_key}"}
    response = httpx.get("https://api.openai.com/v1/models", headers=headers)
    assert response.status_code in [200, 401]
