from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    token_type: Mapped[str] = mapped_column(String(20), nullable=False)
    subject_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        index=True,
        nullable=False,
    )
    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
