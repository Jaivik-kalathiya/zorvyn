import math

from app.schemas.common import PageMeta


def build_page_meta(total_items: int, page: int, page_size: int) -> PageMeta:
    total_pages = math.ceil(total_items / page_size) if total_items > 0 else 0
    return PageMeta(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
    )
