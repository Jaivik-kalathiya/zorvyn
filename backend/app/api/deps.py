from collections.abc import Callable
from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.exceptions import APIError
from app.core.rbac import UserRole, has_minimum_role
from app.core.security import decode_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.revoked_token_repository import RevokedTokenRepository
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
DBSession = Annotated[Session, Depends(get_db)]


def get_current_user(db: DBSession, token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    payload = decode_token(token)
    if payload.token_type != "access":
        raise APIError(status_code=401, message="Invalid access token.", code="auth_error")

    if RevokedTokenRepository(db).is_revoked(payload.jti):
        raise APIError(status_code=401, message="Token has been revoked.", code="auth_error")

    user = UserRepository(db).get_by_id(int(payload.sub))
    if not user:
        raise APIError(status_code=401, message="User no longer exists.", code="auth_error")

    return user


def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if not current_user.is_active:
        raise APIError(status_code=403, message="User account is inactive.", code="forbidden")
    return current_user


def require_minimum_role(required_role: UserRole) -> Callable[[User], User]:
    def dependency(current_user: Annotated[User, Depends(get_current_active_user)]) -> User:
        if not has_minimum_role(current_user.role, required_role):
            raise APIError(status_code=403, message="Insufficient privileges.", code="forbidden")
        return current_user

    return dependency
