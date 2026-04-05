from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.finance_record import FinanceEntryType, FinanceRecord
from app.schemas.dashboard import CategoryTotal, DashboardSummary, RecentActivityItem, TrendPoint


class DashboardService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_summary(
        self,
        from_date: date | None = None,
        to_date: date | None = None,
    ) -> DashboardSummary:
        filters = [FinanceRecord.is_deleted.is_(False)]
        if from_date:
            filters.append(FinanceRecord.entry_date >= from_date)
        if to_date:
            filters.append(FinanceRecord.entry_date <= to_date)

        total_income = self._sum_by_type(filters, FinanceEntryType.INCOME)
        total_expenses = self._sum_by_type(filters, FinanceEntryType.EXPENSE)
        net_balance = total_income - total_expenses

        category_totals = self._category_totals(filters)
        trends = self._monthly_trends(filters)
        recent_activity = self._recent_activity(filters)

        return DashboardSummary(
            total_income=total_income,
            total_expenses=total_expenses,
            net_balance=net_balance,
            category_totals=category_totals,
            trends=trends,
            recent_activity=recent_activity,
        )

    def _sum_by_type(self, filters: list, entry_type: FinanceEntryType) -> Decimal:
        stmt = select(func.coalesce(func.sum(FinanceRecord.amount), 0)).where(
            *filters, FinanceRecord.entry_type == entry_type
        )
        return Decimal(self.db.execute(stmt).scalar_one())

    def _category_totals(self, filters: list) -> list[CategoryTotal]:
        stmt = (
            select(
                FinanceRecord.category,
                func.coalesce(func.sum(FinanceRecord.amount), 0).label("total"),
            )
            .where(*filters)
            .group_by(FinanceRecord.category)
            .order_by(func.sum(FinanceRecord.amount).desc())
            .limit(8)
        )
        rows = self.db.execute(stmt).all()
        return [CategoryTotal(category=row.category, total=Decimal(row.total)) for row in rows]

    def _monthly_trends(self, filters: list) -> list[TrendPoint]:
        stmt = (
            select(FinanceRecord.entry_date, FinanceRecord.entry_type, FinanceRecord.amount)
            .where(*filters)
            .order_by(FinanceRecord.entry_date.asc())
        )
        rows = self.db.execute(stmt).all()

        grouped: dict[date, dict[str, Decimal]] = {}
        for row in rows:
            period = date(row.entry_date.year, row.entry_date.month, 1)
            if period not in grouped:
                grouped[period] = {"income": Decimal("0"), "expense": Decimal("0")}
            amount = Decimal(row.amount)
            if row.entry_type == FinanceEntryType.INCOME:
                grouped[period]["income"] += amount
            else:
                grouped[period]["expense"] += amount

        return [
            TrendPoint(period=period, income=values["income"], expense=values["expense"])
            for period, values in sorted(grouped.items(), key=lambda item: item[0])
        ]

    def _recent_activity(self, filters: list) -> list[RecentActivityItem]:
        stmt = (
            select(FinanceRecord)
            .where(*filters)
            .order_by(FinanceRecord.created_at.desc(), FinanceRecord.id.desc())
            .limit(8)
        )
        rows = self.db.execute(stmt).scalars().all()
        return [
            RecentActivityItem(
                id=row.id,
                amount=Decimal(row.amount),
                entry_type=row.entry_type,
                category=row.category,
                entry_date=row.entry_date,
            )
            for row in rows
        ]
