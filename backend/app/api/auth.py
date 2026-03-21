from typing import Annotated

from fastapi import APIRouter, Depends, Response

from app.core.config import get_settings
from app.core.security import authenticate_user, create_access_token, get_current_user
from app.db.models import AdminUser
from app.db.session import get_db
from app.schemas.auth import AuthUser, LoginRequest, LoginResponse


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, db=Depends(get_db)) -> LoginResponse:
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        from fastapi import HTTPException, status

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.email)
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=get_settings().access_token_expire_minutes * 60,
    )
    return LoginResponse(user=AuthUser.model_validate(user, from_attributes=True))


@router.post("/logout")
def logout(response: Response) -> dict[str, str]:
    response.delete_cookie("access_token")
    return {"message": "Logged out"}


@router.get("/me", response_model=AuthUser)
def me(user: Annotated[AdminUser, Depends(get_current_user)]) -> AuthUser:
    return AuthUser.model_validate(user, from_attributes=True)

