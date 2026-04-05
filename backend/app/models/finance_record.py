from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Numeric, String, Text, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class FinanceEntryType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"


class FinanceRecord(Base):
    __tablename__ = "finance_records"
    __table_args__ = (
        Index("ix_finance_records_entry_date", "entry_date"),
        Index("ix_finance_records_category", "category"),
        Index("ix_finance_records_entry_type", "entry_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    entry_type: Mapped[FinanceEntryType] = mapped_column(SqlEnum(FinanceEntryType), nullable=False)
    category: Mapped[str] = mapped_column(String(80), nullable=False)
    entry_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner = relationship("User", back_populates="records")
