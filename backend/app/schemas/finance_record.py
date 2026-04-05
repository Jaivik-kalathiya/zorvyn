from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.models.finance_record import FinanceEntryType


class FinanceRecordCreate(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    entry_type: FinanceEntryType
    category: str = Field(min_length=2, max_length=80)
    entry_date: date
    notes: str | None = Field(default=None, max_length=2000)


class FinanceRecordUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    entry_type: FinanceEntryType | None = None
    category: str | None = Field(default=None, min_length=2, max_length=80)
    entry_date: date | None = None
    notes: str | None = Field(default=None, max_length=2000)


class FinanceRecordRead(BaseModel):
    id: int
    amount: Decimal
    entry_type: FinanceEntryType
    category: str
    entry_date: date
    notes: str | None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
