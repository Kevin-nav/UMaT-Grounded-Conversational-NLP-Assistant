from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.dependencies import DbDep
from app.core.rbac import require_roles
from app.core.security import get_password_hash
from app.db.models import AdminUser
from app.schemas.user import AdminUserCreate, AdminUserRead, AdminUserUpdate


router = APIRouter(prefix="/admin/users", tags=["admin"])
SuperAdminDep = Annotated[AdminUser, Depends(require_roles("super_admin"))]


@router.get("", response_model=list[AdminUserRead])
def list_users(db: DbDep, _: SuperAdminDep) -> list[AdminUser]:
    return db.scalars(select(AdminUser).order_by(AdminUser.email)).all()


@router.post("", response_model=AdminUserRead)
def create_user(payload: AdminUserCreate, db: DbDep, _: SuperAdminDep) -> AdminUser:
    if db.scalar(select(AdminUser.id).where(AdminUser.email == payload.email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
    user = AdminUser(
        full_name=payload.full_name,
        email=str(payload.email),
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        is_active=payload.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=AdminUserRead)
def update_user(user_id: int, payload: AdminUserUpdate, db: DbDep, _: SuperAdminDep) -> AdminUser:
    user = db.get(AdminUser, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updates = payload.model_dump(exclude_unset=True)
    password = updates.pop("password", None)
    for key, value in updates.items():
        setattr(user, key, str(value) if key == "email" and value is not None else value)
    if password:
        user.password_hash = get_password_hash(password)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}")
def delete_user(user_id: int, db: DbDep, _: SuperAdminDep) -> dict[str, str]:
    user = db.get(AdminUser, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}
