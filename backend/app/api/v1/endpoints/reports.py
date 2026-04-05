from datetime import date, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_minimum_role
from app.core.rbac import UserRole
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.report import RunReportRequest, ScheduledReportRead
from app.services.report_service import ReportService

router = APIRouter()


@router.get("", response_model=PaginatedResponse[ScheduledReportRead])
def list_reports(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_minimum_role(UserRole.ANALYST))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
) -> PaginatedResponse[ScheduledReportRead]:
    return ReportService(db).list_reports(page=page, page_size=page_size)


@router.post("/run", response_model=ScheduledReportRead, status_code=status.HTTP_201_CREATED)
def run_report_now(
    payload: RunReportRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_minimum_role(UserRole.ADMIN))],
) -> ScheduledReportRead:
    period_end = date.today()
    period_start = period_end - timedelta(days=payload.lookback_days)
    report = ReportService(db).generate_report(
        report_name=payload.report_name,
        period_start=period_start,
        period_end=period_end,
        actor_id=current_user.id,
    )
    return ScheduledReportRead.model_validate(report)


@router.get("/{report_id}/csv")
def export_report_csv(
    report_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_minimum_role(UserRole.ANALYST))],
) -> Response:
    content = ReportService(db).export_report_csv(report_id)
    filename = f"report-{report_id}.csv"
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
