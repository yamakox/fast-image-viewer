from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Folder
from app.pagination import apply_ordering, parse_ordering
from app.query import apply_parent_filter, get_folder_or_404, require_parent_exists
from app.schemas import FolderDetail, FolderListItem

router = APIRouter(tags=['folders'])

FOLDER_ORDERING = {'name', 'parent'}


@router.get('/folders', response_model=list[FolderListItem])
def list_folders(
    parent: int | None = None,
    rootonly: str | None = None,
    ordering: str | None = None,
    db: Session = Depends(get_db),
) -> list[Folder]:
    if parent is not None:
        require_parent_exists(db, parent)

    stmt = select(Folder)
    stmt = apply_parent_filter(stmt, Folder, parent, rootonly)
    order = parse_ordering(ordering, FOLDER_ORDERING, default=['name'])
    stmt = apply_ordering(stmt, Folder, order)
    return list(db.scalars(stmt).all())


@router.get('/folders/{folder_id}', response_model=FolderDetail)
def get_folder(folder_id: int, db: Session = Depends(get_db)) -> FolderDetail:
    folder = get_folder_or_404(db, folder_id)
    return FolderDetail(
        id=folder.id,
        name=folder.name,
        pathname=folder.pathname,
        parent=folder.parent_id,
    )
