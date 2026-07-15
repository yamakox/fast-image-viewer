from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

import h5py
import imagehash
import numpy as np
from dateutil.tz import tzlocal
from PIL import Image as PilImage
from PIL import ImageFile
from sqlalchemy import select
from sqlalchemy.orm import Session

import env
from app.db import SessionLocal
from app.models import Folder, Image
from log import logger

API_THUMBNAIL_FILENAME = 'thumbnail.hdf5'
API_THUMBNAIL_GROUP = 'ThumbnailGroup'


class Hdf5File:
    h5 = None
    group = None

    def __init__(self, folder_path: Path, mode: str = 'r'):
        path = folder_path / API_THUMBNAIL_FILENAME
        self.h5 = h5py.File(path, mode)
        self.group = (
            self.h5[API_THUMBNAIL_GROUP]
            if API_THUMBNAIL_GROUP in self.h5
            else self.h5.create_group(API_THUMBNAIL_GROUP)
        )

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.close()

    def close(self):
        try:
            if self.h5:
                self.h5.close()
                self.h5 = None
                self.group = None
        except Exception:
            pass

    def set_data(self, id: int, data: bytes) -> None:
        name = str(id)
        if name in self.group:
            raise Exception(f'{id=} already exists in {API_THUMBNAIL_FILENAME}')
        self.group.create_dataset(name, data=np.asarray(data))

    def get_data(self, id: int) -> bytes:
        name = str(id)
        if name not in self.group:
            raise Exception(f'{id=} not found in {API_THUMBNAIL_FILENAME}')
        return np.asarray(self.group[name]).tobytes()

    def has_data(self, id: int) -> bool:
        name = str(id)
        return name in self.group


def _to_rgb(img: ImageFile.ImageFile) -> ImageFile.ImageFile | PilImage.Image:
    if img.mode == 'RGB':
        return img
    buf = PilImage.new('RGBA', img.size, (0, 0, 0))
    buf.paste(img)
    frame = PilImage.new('RGB', img.size, (0, 0, 0))
    frame.paste(buf, mask=buf.split()[3])
    return frame


def _create_image_data(
    session: Session,
    hdf5file: Hdf5File,
    path: Path,
    parent: Folder | None,
) -> None:
    try:
        existing = session.scalar(
            select(Image).where(Image.name == path.name, Image.parent_id == (parent.id if parent else None))
        )
        if existing:
            return

        img = PilImage.open(path)
        w, h = img.size
        if w < h:
            img = img.crop((0, (h - w) // 2, w, (h + w) // 2))
        else:
            img = img.crop(((w - h) // 2, 0, (w + h) // 2, h))
        img = img.resize((env.FIV_THUMBNAIL_SIZE, env.FIV_THUMBNAIL_SIZE), PilImage.LANCZOS)
        with io.BytesIO() as output:
            _to_rgb(img).save(output, format='JPEG', quality=env.FIV_THUMBNAIL_QUALITY)
            jpeg_data = output.getvalue()

        image = Image(
            name=path.name,
            parent=parent,
            hash_=str(imagehash.average_hash(img)),
            timestamp=datetime.fromtimestamp(path.stat().st_mtime, tz=tzlocal()),
        )
        session.add(image)
        session.flush()
        hdf5file.set_data(image.id, jpeg_data)
        session.commit()
    except Exception as excep:
        session.rollback()
        logger.error(f'Error at dataset.create_image_data: {str(excep)}')


def _scan_dataset_folder(
    session: Session,
    hdf5file: Hdf5File,
    parent_path: Path,
    root_path: Path,
    parent: Folder | None,
) -> None:
    logger.info(f'scan {parent_path}...')

    for i in parent_path.glob('*'):
        if i.is_dir():
            try:
                pathname = str(i.relative_to(root_path))
                folder = session.scalar(select(Folder).where(Folder.pathname == pathname))
                if not folder:
                    folder = Folder(name=i.name, pathname=pathname, parent=parent)
                    session.add(folder)
                    session.commit()
                    session.refresh(folder)
                _scan_dataset_folder(session, hdf5file, i, root_path, folder)
            except Exception as excep:
                session.rollback()
                logger.error(f'Error at dataset._scan_dataset_folder: {str(excep)}')
        elif i.is_file():
            if i.name.startswith('.'):
                continue
            _create_image_data(session, hdf5file, i, parent)


def _cleanup_database(session: Session, root_path: Path, parent: Folder | None) -> None:
    parent_id = parent.id if parent else None
    folders = list(session.scalars(select(Folder).where(Folder.parent_id == parent_id)).all())
    for folder in folders:
        try:
            path = root_path / folder.pathname
            if path.exists():
                _cleanup_database(session, root_path, folder)
            else:
                session.delete(folder)
                session.commit()
        except Exception as excep:
            session.rollback()
            logger.error(f'Error at dataset._cleanup_database: {str(excep)}')

    if parent:
        parent_path = root_path / parent.pathname
    else:
        parent_path = root_path

    images = list(session.scalars(select(Image).where(Image.parent_id == parent_id)).all())
    for image in images:
        try:
            path = parent_path / image.name
            if not path.exists():
                session.delete(image)
                session.commit()
        except Exception as excep:
            session.rollback()
            logger.error(f'Error at dataset._cleanup_database: {str(excep)}')


def scan_dataset() -> None:
    root_path = Path(env.FIV_DATASET_FOLDER_PATH).resolve()
    appdata_path = Path(env.FIV_APPDATA_FOLDER_PATH).resolve()
    appdata_path.mkdir(parents=True, exist_ok=True)

    with SessionLocal() as session:
        _cleanup_database(session, root_path, None)
        with Hdf5File(appdata_path, 'a') as hdf5file:
            _scan_dataset_folder(session, hdf5file, root_path, root_path, None)
