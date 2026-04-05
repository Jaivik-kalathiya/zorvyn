from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class PageMeta(BaseModel):
    page: int = Field(ge=1)
    page_size: int = Field(ge=1)
    total_items: int = Field(ge=0)
    total_pages: int = Field(ge=0)


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    meta: PageMeta
