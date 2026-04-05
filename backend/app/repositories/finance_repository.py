from datetime import UTC, date, datetime

from sqlalchemy import Select, and_, func, or_, select
from sqlalchemy.orm import Session

from app.models.finance_record import FinanceEntryType, FinanceRecord


class FinanceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, record_id: int, include_deleted: bool = False) -> FinanceRecord | None:
        stmt: Select[tuple[FinanceRecord]] = select(FinanceRecord).where(
            FinanceRecord.id == record_id
        )
        if not include_deleted:
            stmt = stmt.where(FinanceRecord.is_deleted.is_(False))
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, record: FinanceRecord) -> FinanceRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def save(self, record: FinanceRecord) -> FinanceRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def soft_delete(self, record: FinanceRecord) -> FinanceRecord:
        record.is_deleted = True
        record.deleted_at = datetime.now(UTC)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_records(
        self,
        page: int,
        page_size: int,
        entry_type: FinanceEntryType | None = None,
        category: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        search: str | None = None,
    ) -> list[FinanceRecord]:
        filters = self._build_filters(
            entry_type=entry_type,
            category=category,
            from_date=from_date,
            to_date=to_date,
            search=search,
        )

        stmt = (
            select(FinanceRecord)
            .where(and_(*filters))
            .order_by(FinanceRecord.entry_date.desc(), FinanceRecord.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.execute(stmt).scalars().all())

    def list_records_for_export(
        self,
        entry_type: FinanceEntryType | None = None,
        category: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        search: str | None = None,
    ) -> list[FinanceRecord]:
        filters = self._build_filters(
            entry_type=entry_type,
            category=category,
            from_date=from_date,
            to_date=to_date,
            search=search,
        )

        stmt = (
            select(FinanceRecord)
            .where(and_(*filters))
            .order_by(FinanceRecord.entry_date.desc(), FinanceRecord.id.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def count_records(
        self,
        entry_type: FinanceEntryType | None = None,
        category: str | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        search: str | None = None,
    ) -> int:
        filters = self._build_filters(
            entry_type=entry_type,
            category=category,
            from_date=from_date,
            to_date=to_date,
            search=search,
        )

        stmt = select(func.count(FinanceRecord.id)).where(and_(*filters))
        return int(self.db.execute(stmt).scalar_one() or 0)

    def _build_filters(
        self,
        entry_type: FinanceEntryType | None,
        category: str | None,
        from_date: date | None,
        to_date: date | None,
        search: str | None,
    ) -> list:
        filters = [FinanceRecord.is_deleted.is_(False)]
        if entry_type:
            filters.append(FinanceRecord.entry_type == entry_type)
        if category:
            filters.append(func.lower(FinanceRecord.category) == category.lower())
        if from_date:
            filters.append(FinanceRecord.entry_date >= from_date)
        if to_date:
            filters.append(FinanceRecord.entry_date <= to_date)
        if search:
            like_query = f"%{search.lower()}%"
            filters.append(
                or_(
                    func.lower(FinanceRecord.category).like(like_query),
                    func.lower(func.coalesce(FinanceRecord.notes, "")).like(like_query),
                )
            )
        return filters
