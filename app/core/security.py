#REVIEW LATER
# app/core/security.py
from passlib.context import CryptContext
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(subject: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    # Move import here to avoid circular import
    from app.core.config import get_settings
    settings = get_settings()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    payload = {"sub": subject, "role": role, "exp": expire, "type": "access"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

def create_refresh_token(subject: str) -> str:
    from app.core.config import get_settings
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    payload = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)

def decode_token(token: str) -> dict:
    """Decode and verify JWT. Raises ValueError on any failure."""
    from app.core.config import get_settings
    settings = get_settings()
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid or expired token.") from exc