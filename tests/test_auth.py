import pytest
from fastapi import HTTPException

from src.backend.services.auth_service import create_access_token, verify_access_token


def test_create_and_verify_token():
    token = create_access_token("user123")
    user_id = verify_access_token(token)
    assert user_id == "user123"


def test_invalid_token_raises():
    token = create_access_token("user123")
    with pytest.raises(HTTPException):
        verify_access_token(token + "x")
