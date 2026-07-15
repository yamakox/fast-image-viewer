import math
from typing import TypeVar

from fastapi import HTTPException, Query
from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session

import env

T = TypeVar('T')


def parse_ordering(ordering: str | None, allowed: set[str], default: list[str]) -> list[tuple[str, bool]]:
    """Return list of (field, descending)."""
    if not ordering:
        fields = default
    else:
        fields = [part.strip() for part in ordering.split(',') if part.strip()]
    result: list[tuple[str, bool]] = []
    for field in fields:
        descending = field.startswith('-')
        name = field[1:] if descending else field
        if name not in allowed:
            raise HTTPException(status_code=400, detail=f'Unknown ordering field: {name}')
        result.append((name, descending))
    return result


def apply_ordering(stmt: Select, model, ordering: list[tuple[str, bool]]) -> Select:
    order_by = []
    for name, descending in ordering:
        # parent maps to parent_id column
        col = getattr(model, 'parent_id' if name == 'parent' else name)
        if name == 'hash':
            col = model.hash_
        order_by.append(desc(col) if descending else asc(col))
    return stmt.order_by(*order_by)


def paginate(
    session: Session,
    stmt: Select,
    *,
    page: int,
    page_size: int | None,
) -> tuple[list, int, int, int, int]:
    """Return (items, count, page, num_pages, page_size)."""
    if page < 1:
        raise HTTPException(status_code=400, detail='page must be >= 1')
    per_page = page_size if page_size is not None else env.PAGINATION_SIZE
    if per_page < 1:
        raise HTTPException(status_code=400, detail='page_size must be >= 1')

    count = session.scalar(select(func.count()).select_from(stmt.order_by(None).subquery())) or 0
    num_pages = max(1, math.ceil(count / per_page)) if count else 1
    if page > num_pages and count:
        raise HTTPException(status_code=404, detail='Invalid page.')

    items = list(session.scalars(stmt.offset((page - 1) * per_page).limit(per_page)).all())
    return items, count, page, num_pages, per_page


def page_query(page: int = Query(1, ge=1), page_size: int | None = Query(None, ge=1)) -> tuple[int, int | None]:
    return page, page_size
