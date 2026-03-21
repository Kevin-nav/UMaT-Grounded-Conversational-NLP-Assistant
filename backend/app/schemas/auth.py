from __future__ import annotations

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthUser(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    role: str
    is_active: bool


class LoginResponse(BaseModel):
    user: AuthUser
