import env
from log import logger
from pathlib import Path
from datetime import datetime
from dateutil.tz import tzlocal
from PIL import Image
import imagehash
import h5py
import io
import numpy as np
from . import models
from fast_image_viewer import settings


# 定数
API_THUMBNAIL_GROUP = 'ThumbnailGroup'


# HDF5ファイル管理
class Hdf5File:
    h5 = None
    group = None

    def __init__(self, folder_path: Path, mode='r'):
        path = folder_path / settings.API_THUMBNAIL_FILENAME
        self.h5 = h5py.File(path, mode)
        self.group = self.h5[API_THUMBNAIL_GROUP] if API_THUMBNAIL_GROUP in self.h5 else self.h5.create_group(API_THUMBNAIL_GROUP)

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
        except:
            pass

    def set_data(self, id: int, data: bytes) -> None:
        if not self.group:
            raise Exception(f'{settings.API_THUMBNAIL_FILENAME} is not prepared.')
        name = str(id)
        if name in self.group:
            raise Exception(f'{id=} already exists in {settings.API_THUMBNAIL_FILENAME}')
        self.group.create_dataset(name, data=np.asarray(data))
    
    def get_data(self, id: int) -> bytes:
        if not self.group:
            raise Exception(f'{settings.API_THUMBNAIL_FILENAME} is not prepared.')
        name = str(id)
        if name not in self.group:
            raise Exception(f'{id=} not found in {settings.API_THUMBNAIL_FILENAME}')
        return np.asarray(self.group[name]).tobytes()
    
    def has_data(self, id: int) -> bool:
        if not self.group:
            raise Exception(f'{settings.API_THUMBNAIL_FILENAME} is not prepared.')
        name = str(id)
        return name in self.group


# 画像ファイルのサムネイルとデータの作成
def _create_image_data(hdf5file: Hdf5File, path: Path, parent: models.Folder|None) -> None:
    try:
        q = models.Image.objects.filter(name=path.name, parent=parent)
        if q.first():
            return

        img = Image.open(path)
        w, h = img.size
        if w < h:
            img = img.crop((0, (h-w)//2, w, (h+w)//2))
        else:
            img = img.crop(((w-h)//2, 0, (w+h)//2, h))
        img = img.resize((env.FIV_THUMBNAIL_SIZE, env.FIV_THUMBNAIL_SIZE), Image.LANCZOS)
        with io.BytesIO() as output:
            img.save(output, format="JPEG", quality=env.FIV_THUMBNAIL_QUALITY)
            jpeg_data = output.getvalue()
        image = models.Image(
            name=path.name,
            parent=parent,
            hash=imagehash.average_hash(img),
            timestamp=datetime.fromtimestamp(path.stat().st_mtime, tz=tzlocal()),
        )
        image.save()
        hdf5file.set_data(image.id, jpeg_data)
    except Exception as excep:
        logger.error(f'Error at dataset.create_image_data: {str(excep)}')


# データセット(サブ)フォルダー内のスキャン
def _scan_dataset_folder(hdf5file: Hdf5File, parent_path: Path, root_path: Path, parent: models.Folder|None) -> None:
    for i in parent_path.glob('*'):
        if i.is_dir():
            try:
                pathname = str(i.relative_to(root_path))
                q = models.Folder.objects.filter(pathname=pathname)
                folder = q.first()
                if not folder:
                    folder = models.Folder(
                        name=i.name,
                        pathname=pathname, 
                        parent=parent
                    )
                    folder.save()
                _scan_dataset_folder(hdf5file, i, root_path, folder)
            except Exception as excep:
                logger.error(f'Error at dataset._scan_dataset_folder: {str(excep)}')
        elif i.is_file():
            if i.name.startswith('.'):
                continue
            _create_image_data(hdf5file, i, parent)


# データベースのクリーンアップ
def _cleanup_database(root_path: Path, parent: models.Folder|None) -> None:
    # フォルダーのクリーンアップ
    q = models.Folder.objects.filter(parent=parent)
    for i in q:
        try:
            path = root_path / i.pathname
            if path.exists():
                _cleanup_database(root_path, i)
            else:
                i.delete()
        except Exception as excep:
            logger.error(f'Error at dataset._cleanup_database: {str(excep)}')

    # 画像データのクリーンアップ
    # (HDF5のデータセットはdelしてもファイルサイズが減らないためDBのみクリーンアップする)
    q = models.Image.objects.filter(parent=parent)
    if parent:
        parent_path = root_path / parent.pathname
    else:
        parent_path = root_path
    for i in q:
        try:
            path = parent_path / i.name
            if not path.exists():
                i.delete()
        except Exception as excep:
            logger.error(f'Error at dataset._cleanup_database: {str(excep)}')

# データセットフォルダー内のスキャン(ルート直下)
def scan_dataset() -> None:
    root_path = Path(env.FIV_DATASET_FOLDER_PATH).resolve()
    appdata_path = Path(env.FIV_APPDATA_FOLDER_PATH).resolve()
    _cleanup_database(root_path, None)
    with Hdf5File(appdata_path, 'a') as hdf5file:
        _scan_dataset_folder(hdf5file, root_path, root_path, None)
