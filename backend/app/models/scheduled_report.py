from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Date, DateTime, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ScheduledReport(Base):
    __tablename__ = "scheduled_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    report_name: Mapped[str] = mapped_column(String(80), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    period_end: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    total_income: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    total_expenses: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    net_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    record_count: Mapped[int] = mapped_column(Integer, nullable=False)

    payload: Mapped[dict] = mapped_column(JSON, nullable=True)

    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
