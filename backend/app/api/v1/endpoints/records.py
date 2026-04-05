from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_minimum_role
from app.core.rbac import UserRole
from app.models.finance_record import FinanceEntryType
from app.models.user import User
from app.schemas.common import PaginatedResponse
from app.schemas.finance_record import FinanceRecordCreate, FinanceRecordRead, FinanceRecordUpdate
from app.services.finance_service import FinanceService

router = APIRouter()


@router.post("", response_model=FinanceRecordRead, status_code=status.HTTP_201_CREATED)
def create_record(
    payload: FinanceRecordCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_minimum_role(UserRole.ADMIN))],
) -> FinanceRecordRead:
    created = FinanceService(db).create_record(payload=payload, owner_id=current_user.id)
    return FinanceRecordRead.model_validate(created)


@router.get("", response_model=PaginatedResponse[FinanceRecordRead])
def list_records(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_minimum_role(UserRole.ANALYST))],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    entry_type: FinanceEntryType | None = Query(default=None),
    category: str | None = Query(default=None, max_length=80),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    search: str | None = Query(default=None, max_length=120),
) -> PaginatedResponse[FinanceRecordRead]:
    return FinanceService(db).list_records(
        page=page,
        page_size=page_size,
        entry_type=entry_type,
        category=category,
        from_date=from_date,
        to_date=to_date,
        search=search,
    )


@router.get("/export/csv")
def export_records_csv(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_minimum_role(UserRole.ANALYST))],
    entry_type: FinanceEntryType | None = Query(default=None),
    category: str | None = Query(default=None, max_length=80),
    from_date: date | None = Query(default=None),
    to_date: date | None = Query(default=None),
    search: str | None = Query(default=None, max_length=120),
) -> Response:
    csv_content = FinanceService(db).export_records_csv(
        entry_type=entry_type,
        category=category,
        from_date=from_date,
        to_date=to_date,
        search=search,
    )
    filename = f"finance-records-{date.today().isoformat()}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{record_id}", response_model=FinanceRecordRead)
def get_record(
    record_id: int,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_minimum_role(UserRole.ANALYST))],
) -> FinanceRecordRead:
    record = FinanceService(db).get_record(record_id)
    return FinanceRecordRead.model_validate(record)


@router.patch("/{record_id}", response_model=FinanceRecordRead)
def update_record(
    record_id: int,
    payload: FinanceRecordUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_minimum_role(UserRole.ADMIN))],
) -> FinanceRecordRead:
    updated = FinanceService(db).update_record(
        record_id=record_id,
        payload=payload,
        actor_id=current_user.id,
    )
    return FinanceRecordRead.model_validate(updated)


@router.delete("/{record_id}", response_model=FinanceRecordRead)
def delete_record(
    record_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_minimum_role(UserRole.ADMIN))],
) -> FinanceRecordRead:
    deleted = FinanceService(db).delete_record(record_id=record_id, actor_id=current_user.id)
    return FinanceRecordRead.model_validate(deleted)
