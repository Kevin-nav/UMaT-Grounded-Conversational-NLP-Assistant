from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.db.models import AdminUser


def require_roles(*roles: str):
    def dependency(user: Annotated[AdminUser, Depends(get_current_user)]) -> AdminUser:
        if user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return dependency

