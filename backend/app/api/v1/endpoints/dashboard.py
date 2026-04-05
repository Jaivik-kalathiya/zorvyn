from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_minimum_role
from app.core.rbac import UserRole
from app.models.user import User
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard_service import DashboardService

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_minimum_role(UserRole.VIEWER))],
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
) -> DashboardSummary:
    return DashboardService(db).get_summary(from_date=from_date, to_date=to_date)
