from fastapi import HTTPException
from sqlalchemy import Select
from sqlalchemy.orm import Session

from app.models import Folder


def require_parent_exists(session: Session, parent_id: int) -> Folder:
    folder = session.get(Folder, parent_id)
    if folder is None:
        raise HTTPException(
            status_code=400,
            detail={'parent': ['正しく選択してください。選択したものは候補にありません。']},
        )
    return folder


def apply_parent_filter(stmt: Select, model, parent: int | None, rootonly: str | None) -> Select:
    if rootonly:
        return stmt.where(model.parent_id.is_(None))
    if parent is not None:
        return stmt.where(model.parent_id == parent)
    return stmt


def get_folder_or_404(session: Session, folder_id: int) -> Folder:
    folder = session.get(Folder, folder_id)
    if folder is None:
        raise HTTPException(status_code=404, detail='No Folder matches the given query.')
    return folder
