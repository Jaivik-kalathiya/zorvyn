from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_minimum_role
from app.core.rbac import UserRole
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_minimum_role(UserRole.ADMIN))],
) -> UserRead:
    created = UserService(db).create_user(payload, actor_id=current_user.id)
    return UserRead.model_validate(created)


@router.get("", response_model=PaginatedResponse[UserRead])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_minimum_role(UserRole.ADMIN))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None, max_length=120),
) -> PaginatedResponse[UserRead]:
    return UserService(db).list_users(page=page, page_size=page_size, search=search)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_minimum_role(UserRole.ADMIN))],
) -> UserRead:
    updated = UserService(db).update_user(
        user_id=user_id,
        payload=payload,
        actor_id=current_user.id,
    )
    return UserRead.model_validate(updated)
