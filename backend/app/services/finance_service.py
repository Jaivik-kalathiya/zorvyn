import csv
import io
from datetime import date

from sqlalchemy.orm import Session

from app.core.exceptions import APIError
from app.models.finance_record import FinanceEntryType, FinanceRecord
from app.repositories.audit_repository import AuditRepository
from app.repositories.finance_repository import FinanceRepository
from app.schemas.common import PaginatedResponse
from app.schemas.finance_record import FinanceRecordCreate, FinanceRecordRead, FinanceRecordUpdate
from app.utils.pagination import build_page_meta


class FinanceService:
    def __init__(self, db: Session) -> None:
        self.records = FinanceRepository(db)
        self.audit = AuditRepository(db)

    def create_record(self, payload: FinanceRecordCreate, owner_id: int) -> FinanceRecord:
        record = FinanceRecord(**payload.model_dump(), owner_id=owner_id)
        created = self.records.create(record)
        self.audit.create_log(
            actor_id=owner_id,
            action="create_finance_record",
            entity_type="finance_record",
            entity_id=str(created.id),
        )
        return created

    def get_record(self, record_id: int) -> FinanceRecord:
        record = self.records.get_by_id(record_id)
        if not record:
            raise APIError(status_code=404, message="Finance record not found.", code="not_found")
        return record

    def list_records(
        self,
        page: int,
        page_size: int,
        entry_type: FinanceEntryType | None,
        category: str | None,
        from_date: date | None,
        to_date: date | None,
        search: str | None,
    ) -> PaginatedResponse[FinanceRecordRead]:
        total = self.records.count_records(
            entry_type=entry_type,
            category=category,
            from_date=from_date,
            to_date=to_date,
            search=search,
        )
        rows = self.records.list_records(
            page=page,
            page_size=page_size,
            entry_type=entry_type,
            category=category,
            from_date=from_date,
            to_date=to_date,
            search=search,
        )
        return PaginatedResponse[FinanceRecordRead](
            items=[FinanceRecordRead.model_validate(record) for record in rows],
            meta=build_page_meta(total_items=total, page=page, page_size=page_size),
        )

    def export_records_csv(
        self,
        entry_type: FinanceEntryType | None,
        category: str | None,
        from_date: date | None,
        to_date: date | None,
        search: str | None,
    ) -> str:
        rows = self.records.list_records_for_export(
            entry_type=entry_type,
            category=category,
            from_date=from_date,
            to_date=to_date,
            search=search,
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "id",
                "entry_date",
                "entry_type",
                "category",
                "amount",
                "notes",
                "owner_id",
                "created_at",
                "updated_at",
            ]
        )

        for record in rows:
            writer.writerow(
                [
                    record.id,
                    record.entry_date.isoformat(),
                    record.entry_type.value,
                    record.category,
                    str(record.amount),
                    record.notes or "",
                    record.owner_id,
                    record.created_at.isoformat(),
                    record.updated_at.isoformat(),
                ]
            )

        return output.getvalue()

    def update_record(
        self,
        record_id: int,
        payload: FinanceRecordUpdate,
        actor_id: int,
    ) -> FinanceRecord:
        record = self.get_record(record_id)
        updates = payload.model_dump(exclude_none=True)
        if not updates:
            return record

        for field, value in updates.items():
            setattr(record, field, value)

        saved = self.records.save(record)
        self.audit.create_log(
            actor_id=actor_id,
            action="update_finance_record",
            entity_type="finance_record",
            entity_id=str(saved.id),
            details={"fields": ",".join(sorted(updates.keys()))},
        )
        return saved

    def delete_record(self, record_id: int, actor_id: int) -> FinanceRecord:
        record = self.get_record(record_id)
        deleted = self.records.soft_delete(record)
        self.audit.create_log(
            actor_id=actor_id,
            action="soft_delete_finance_record",
            entity_type="finance_record",
            entity_id=str(deleted.id),
        )
        return deleted
