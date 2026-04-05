from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import get_settings
from app.core.exceptions import APIError

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class TokenPayload(BaseModel):
    sub: str
    role: str
    token_type: str
    jti: str
    exp: int


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _create_token(subject: str, role: str, token_type: str, expires_delta: timedelta) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + expires_delta
    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "token_type": token_type,
        "jti": uuid4().hex,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str, role: str) -> str:
    settings = get_settings()
    return _create_token(
        subject=subject,
        role=role,
        token_type="access",
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(subject: str, role: str) -> str:
    settings = get_settings()
    return _create_token(
        subject=subject,
        role=role,
        token_type="refresh",
        expires_delta=timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES),
    )


def decode_token(token: str) -> TokenPayload:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return TokenPayload.model_validate(payload)
    except JWTError as exc:
        raise APIError(
            status_code=401,
            message="Could not validate credentials",
            code="auth_error",
        ) from exc


def token_expiry_to_datetime(exp: int) -> datetime:
    return datetime.fromtimestamp(exp, UTC)
