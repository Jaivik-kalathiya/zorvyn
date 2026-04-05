from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, oauth2_scheme
from app.core.rate_limit import limiter
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    BootstrapAdminRequest,
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/bootstrap-admin", response_model=UserRead)
@limiter.limit("30/minute")
def bootstrap_admin(
    request: Request,
    payload: BootstrapAdminRequest,
    db: Annotated[Session, Depends(get_db)],
) -> UserRead:
    service = AuthService(db)
    created = service.bootstrap_admin(payload)
    return UserRead.model_validate(created)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("60/minute")
def login(
    request: Request,
    payload: LoginRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    return AuthService(db).login(payload)


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("120/minute")
def refresh_token(
    request: Request,
    payload: RefreshTokenRequest,
    db: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    return AuthService(db).refresh(payload.refresh_token)


@router.get("/me", response_model=UserRead)
def me(current_user: Annotated[User, Depends(get_current_active_user)]) -> UserRead:
    return UserRead.model_validate(current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("120/minute")
def logout(
    request: Request,
    payload: LogoutRequest,
    db: Annotated[Session, Depends(get_db)],
    access_token: Annotated[str, Depends(oauth2_scheme)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Response:
    AuthService(db).logout(
        access_token=access_token,
        refresh_token=payload.refresh_token,
        actor_id=current_user.id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
