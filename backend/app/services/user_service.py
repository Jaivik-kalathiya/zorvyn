from sqlalchemy.orm import Session

from app.core.exceptions import APIError
from app.core.security import hash_password
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.utils.pagination import build_page_meta


class UserService:
    def __init__(self, db: Session) -> None:
        self.users = UserRepository(db)
        self.audit = AuditRepository(db)

    def create_user(self, payload: UserCreate, actor_id: int | None = None) -> User:
        if self.users.get_by_email(payload.email):
            raise APIError(status_code=409, message="Email is already in use.", code="conflict")

        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
            role=payload.role,
            is_active=True,
        )
        created = self.users.create(user)
        self.audit.create_log(
            actor_id=actor_id,
            action="create_user",
            entity_type="user",
            entity_id=str(created.id),
            details={"role": created.role.value},
        )
        return created

    def get_user(self, user_id: int) -> User:
        user = self.users.get_by_id(user_id)
        if not user:
            raise APIError(status_code=404, message="User not found.", code="not_found")
        return user

    def list_users(
        self,
        page: int,
        page_size: int,
        search: str | None = None,
    ) -> PaginatedResponse[UserRead]:
        total = self.users.count_users(search=search)
        rows = self.users.list_users(page=page, page_size=page_size, search=search)
        return PaginatedResponse[UserRead](
            items=[UserRead.model_validate(user) for user in rows],
            meta=build_page_meta(total_items=total, page=page, page_size=page_size),
        )

    def update_user(self, user_id: int, payload: UserUpdate, actor_id: int | None = None) -> User:
        user = self.get_user(user_id)
        updates = payload.model_dump(exclude_none=True)
        for field, value in updates.items():
            setattr(user, field, value)
        saved = self.users.save(user)
        self.audit.create_log(
            actor_id=actor_id,
            action="update_user",
            entity_type="user",
            entity_id=str(saved.id),
            details={"fields": ",".join(sorted(updates.keys())) or "none"},
        )
        return saved
