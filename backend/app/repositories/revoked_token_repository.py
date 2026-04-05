from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.revoked_token import RevokedToken


class RevokedTokenRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def is_revoked(self, jti: str) -> bool:
        stmt = select(RevokedToken.id).where(RevokedToken.jti == jti).limit(1)
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def revoke_token(
        self,
        *,
        jti: str,
        token_type: str,
        subject_id: int,
        expires_at: datetime,
    ) -> None:
        if self.is_revoked(jti):
            return

        token = RevokedToken(
            jti=jti,
            token_type=token_type,
            subject_id=subject_id,
            expires_at=expires_at,
        )
        self.db.add(token)
        self.db.commit()

    def cleanup_expired(self) -> int:
        stmt = delete(RevokedToken).where(RevokedToken.expires_at < datetime.now(UTC))
        result = self.db.execute(stmt)
        self.db.commit()
        return int(result.rowcount or 0)
