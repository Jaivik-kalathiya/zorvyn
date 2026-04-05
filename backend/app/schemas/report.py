from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class RunReportRequest(BaseModel):
    report_name: str = Field(default="manual_snapshot", min_length=3, max_length=80)
    lookback_days: int = Field(default=7, ge=1, le=365)


class ScheduledReportRead(BaseModel):
    id: int
    report_name: str
    period_start: date
    period_end: date
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    record_count: int
    payload: dict[str, Any] | None
    generated_at: datetime

    model_config = {"from_attributes": True}
