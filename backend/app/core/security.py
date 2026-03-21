from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.models import AdminUser
from app.db.session import get_db


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")


def authenticate_user(db: Session, email: str, password: str) -> AdminUser | None:
    user = db.scalar(select(AdminUser).where(AdminUser.email == email))
    if not user or not user.is_active or not verify_password(password, user.password_hash):
        return None
    return user


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    access_token: Annotated[str | None, Cookie(alias="access_token")] = None,
) -> AdminUser:
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    settings = get_settings()
    try:
        payload = jwt.decode(access_token, settings.secret_key, algorithms=["HS256"])
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session") from exc
    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    user = db.scalar(select(AdminUser).where(AdminUser.email == subject))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user

