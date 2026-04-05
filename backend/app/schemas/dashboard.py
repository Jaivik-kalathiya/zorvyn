from datetime import date
from decimal import Decimal

from pydantic import BaseModel

from app.models.finance_record import FinanceEntryType


class CategoryTotal(BaseModel):
    category: str
    total: Decimal


class TrendPoint(BaseModel):
    period: date
    income: Decimal
    expense: Decimal


class RecentActivityItem(BaseModel):
    id: int
    amount: Decimal
    entry_type: FinanceEntryType
    category: str
    entry_date: date


class DashboardSummary(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal
    category_totals: list[CategoryTotal]
    trends: list[TrendPoint]
    recent_activity: list[RecentActivityItem]
