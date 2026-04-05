from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.scheduled_report import ScheduledReport


class ReportRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, report: ScheduledReport) -> ScheduledReport:
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_by_id(self, report_id: int) -> ScheduledReport | None:
        return self.db.get(ScheduledReport, report_id)

    def list_reports(self, page: int, page_size: int) -> list[ScheduledReport]:
        stmt: Select[tuple[ScheduledReport]] = (
            select(ScheduledReport)
            .order_by(ScheduledReport.generated_at.desc(), ScheduledReport.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.execute(stmt).scalars().all())

    def count_reports(self) -> int:
        stmt = select(func.count(ScheduledReport.id))
        return int(self.db.execute(stmt).scalar_one() or 0)
