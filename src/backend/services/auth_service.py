import os
from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, Request


def create_access_token(user_id: str) -> str:
    """Generate JWT token with 24h expiration."""
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    secret = os.getenv("JWT_SECRET")
    return jwt.encode(payload, secret, algorithm="HS256")


def verify_access_token(token: str) -> str:
    """Validate token and return user_id."""
    secret = os.getenv("JWT_SECRET")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado") from exc
    return payload.get("sub")


async def get_current_user(request: Request) -> str:
    """Retrieve logged in user from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    token = auth_header.split(" ", 1)[1]
    return verify_access_token(token)
