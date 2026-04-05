import csv
import io
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.exceptions import APIError
from app.models.scheduled_report import ScheduledReport
from app.repositories.audit_repository import AuditRepository
from app.repositories.finance_repository import FinanceRepository
from app.repositories.report_repository import ReportRepository
from app.schemas.common import PaginatedResponse
from app.schemas.report import ScheduledReportRead
from app.services.dashboard_service import DashboardService
from app.utils.pagination import build_page_meta


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.reports = ReportRepository(db)
        self.finance = FinanceRepository(db)
        self.audit = AuditRepository(db)

    def generate_report(
        self,
        *,
        report_name: str,
        period_start: date,
        period_end: date,
        actor_id: int | None = None,
    ) -> ScheduledReport:
        summary = DashboardService(self.db).get_summary(from_date=period_start, to_date=period_end)
        record_count = self.finance.count_records(from_date=period_start, to_date=period_end)

        payload = {
            "category_totals": [
                {"category": item.category, "total": str(item.total)}
                for item in summary.category_totals
            ],
            "trends": [
                {
                    "period": str(item.period),
                    "income": str(item.income),
                    "expense": str(item.expense),
                }
                for item in summary.trends
            ],
            "recent_activity": [
                {
                    "id": item.id,
                    "amount": str(item.amount),
                    "entry_type": item.entry_type.value,
                    "category": item.category,
                    "entry_date": str(item.entry_date),
                }
                for item in summary.recent_activity
            ],
        }

        report = ScheduledReport(
            report_name=report_name,
            period_start=period_start,
            period_end=period_end,
            total_income=summary.total_income,
            total_expenses=summary.total_expenses,
            net_balance=summary.net_balance,
            record_count=record_count,
            payload=payload,
        )
        created = self.reports.create(report)
        self.audit.create_log(
            actor_id=actor_id,
            action="generate_report",
            entity_type="scheduled_report",
            entity_id=str(created.id),
            details={"report_name": report_name},
        )
        return created

    def generate_scheduled_snapshot(
        self,
        *,
        lookback_days: int,
        report_name: str = "scheduled_snapshot",
    ) -> ScheduledReport:
        period_end = date.today()
        period_start = period_end - timedelta(days=lookback_days)
        return self.generate_report(
            report_name=report_name,
            period_start=period_start,
            period_end=period_end,
            actor_id=None,
        )

    def get_report(self, report_id: int) -> ScheduledReport:
        report = self.reports.get_by_id(report_id)
        if not report:
            raise APIError(status_code=404, message="Report not found.", code="not_found")
        return report

    def list_reports(self, *, page: int, page_size: int) -> PaginatedResponse[ScheduledReportRead]:
        total = self.reports.count_reports()
        rows = self.reports.list_reports(page=page, page_size=page_size)
        return PaginatedResponse[ScheduledReportRead](
            items=[ScheduledReportRead.model_validate(row) for row in rows],
            meta=build_page_meta(total_items=total, page=page, page_size=page_size),
        )

    def export_report_csv(self, report_id: int) -> str:
        report = self.get_report(report_id)
        payload = report.payload or {}

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(
            [
                "report_id",
                "report_name",
                "period_start",
                "period_end",
                "generated_at",
                "total_income",
                "total_expenses",
                "net_balance",
                "record_count",
            ]
        )
        writer.writerow(
            [
                report.id,
                report.report_name,
                report.period_start.isoformat(),
                report.period_end.isoformat(),
                report.generated_at.isoformat(),
                str(Decimal(report.total_income)),
                str(Decimal(report.total_expenses)),
                str(Decimal(report.net_balance)),
                report.record_count,
            ]
        )

        category_totals = payload.get("category_totals", [])
        if category_totals:
            writer.writerow([])
            writer.writerow(["category", "total"])
            for item in category_totals:
                writer.writerow([item.get("category", ""), item.get("total", "0")])

        return output.getvalue()
