from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_log(
        self,
        actor_id: int | None,
        action: str,
        entity_type: str,
        entity_id: str | None = None,
        details: dict[str, str] | None = None,
    ) -> AuditLog:
        log = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log
