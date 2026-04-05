from app.db.base import *  # noqa: F403
from app.db.session import Base, engine


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
