from __future__ import annotations

from pydantic import BaseModel, EmailStr

from app.schemas.common import ORMModel


class AdminUserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: str
    is_active: bool = True


class AdminUserRead(AdminUserBase, ORMModel):
    id: int


class AdminUserCreate(AdminUserBase):
    password: str


class AdminUserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None
    role: str | None = None
    is_active: bool | None = None
    password: str | None = None
