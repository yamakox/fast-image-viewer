from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

import env
from app.db import get_db
from app.models import Image
from app.pagination import apply_ordering, page_query, paginate, parse_ordering
from app.query import apply_parent_filter, require_parent_exists
from app.schemas import (
    ImageDetail,
    ImageFavoriteResponse,
    ImageFavoriteUpdate,
    ImageListItem,
    PaginatedImages,
)
from app.services import dataset
from app.services.paths import find_media_type, resolve_image_path

router = APIRouter(tags=['images'])

IMAGE_ORDERING = {'name', 'parent', 'timestamp', 'favorite'}
appdata_path = Path(env.FIV_APPDATA_FOLDER_PATH).resolve()


def _get_image_or_404(db: Session, image_id: int) -> Image:
    image = db.get(Image, image_id)
    if image is None:
        raise HTTPException(status_code=404, detail='Image data not found.')
    return image


@router.get('/images', response_model=PaginatedImages)
def list_images(
    parent: int | None = None,
    rootonly: str | None = None,
    favoriteonly: str | None = None,
    ordering: str | None = None,
    page_params: tuple[int, int | None] = Depends(page_query),
    db: Session = Depends(get_db),
) -> PaginatedImages:
    if parent is not None:
        require_parent_exists(db, parent)

    page, page_size = page_params
    stmt = select(Image)
    stmt = apply_parent_filter(stmt, Image, parent, rootonly)
    if favoriteonly:
        stmt = stmt.where(Image.favorite.is_not(None))

    order = parse_ordering(ordering, IMAGE_ORDERING, default=['-timestamp'])
    stmt = apply_ordering(stmt, Image, order)

    items, count, page_num, num_pages, per_page = paginate(db, stmt, page=page, page_size=page_size)
    return PaginatedImages(
        count=count,
        page=page_num,
        num_pages=num_pages,
        page_size=per_page,
        results=[ImageListItem.model_validate(i) for i in items],
    )


@router.get('/images/{image_id}', response_model=ImageDetail)
def get_image(image_id: int, db: Session = Depends(get_db)) -> ImageDetail:
    image = db.scalar(select(Image).where(Image.id == image_id).options(joinedload(Image.parent)))
    if image is None:
        raise HTTPException(status_code=404, detail='No Image matches the given query.')
    return ImageDetail(
        id=image.id,
        name=image.name,
        parent=image.parent_id,
        hash=image.hash_,
        timestamp=image.timestamp,
        favorite=image.favorite,
    )


@router.patch('/images/{image_id}', response_model=ImageFavoriteResponse)
def patch_image(
    image_id: int,
    body: ImageFavoriteUpdate,
    db: Session = Depends(get_db),
) -> ImageFavoriteResponse:
    image = _get_image_or_404(db, image_id)
    image.favorite = body.favorite
    db.commit()
    db.refresh(image)
    return ImageFavoriteResponse(id=image.id, favorite=image.favorite)


@router.get('/images/{image_id}/image')
def get_image_binary(image_id: int, db: Session = Depends(get_db)) -> Response:
    image = db.scalar(select(Image).where(Image.id == image_id).options(joinedload(Image.parent)))
    if image is None:
        raise HTTPException(status_code=404, detail='Image data not found.')

    image_filepath = resolve_image_path(image)
    if not image_filepath.exists():
        return JSONResponse(
            status_code=404,
            content={'detail': 'Image file not found.', 'file': str(image_filepath)},
        )

    media_type = find_media_type(image_filepath)
    if media_type is None:
        return JSONResponse(
            status_code=500,
            content={'detail': f'Unsupported image format: {image_filepath.name}'},
        )

    data = image_filepath.read_bytes()
    return Response(content=data, media_type=media_type, headers={'Content-Length': str(len(data))})


@router.get('/images/{image_id}/thumbnail')
def get_thumbnail_binary(image_id: int, db: Session = Depends(get_db)) -> Response:
    image = _get_image_or_404(db, image_id)
    try:
        with dataset.Hdf5File(appdata_path) as hdf5file:
            if not hdf5file.has_data(image.id):
                raise HTTPException(status_code=404, detail='Thumbnail image not found.')
            bindata = hdf5file.get_data(image.id)
    except HTTPException:
        raise
    except Exception as excep:
        return JSONResponse(status_code=500, content={'id': image_id, 'error': str(excep)})

    return Response(
        content=bindata,
        media_type='image/jpeg',
        headers={'Content-Length': str(len(bindata))},
    )
