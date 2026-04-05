from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def exists_any(self) -> bool:
        stmt = select(func.count(User.id))
        return (self.db.execute(stmt).scalar_one() or 0) > 0

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt: Select[tuple[User]] = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_users(self, page: int, page_size: int, search: str | None = None) -> list[User]:
        stmt: Select[tuple[User]] = select(User)
        if search:
            like_query = f"%{search.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(User.full_name).like(like_query),
                    func.lower(User.email).like(like_query),
                )
            )
        stmt = stmt.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size)
        return list(self.db.execute(stmt).scalars().all())

    def count_users(self, search: str | None = None) -> int:
        stmt = select(func.count(User.id))
        if search:
            like_query = f"%{search.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(User.full_name).like(like_query),
                    func.lower(User.email).like(like_query),
                )
            )
        return int(self.db.execute(stmt).scalar_one() or 0)

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
