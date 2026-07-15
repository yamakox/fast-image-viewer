from pathlib import Path

from app.models import Image
import env

root_path = Path(env.FIV_DATASET_FOLDER_PATH).resolve()

IMAGE_MEDIA_TYPES = {
    '.avif': 'image/avif',
    '.gif': 'image/gif',
    '.heic': 'image/heic',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.webp': 'image/webp',
}


def resolve_image_path(image: Image) -> Path:
    if image.parent:
        return root_path / image.parent.pathname / image.name
    return root_path / image.name


def find_media_type(file_path: Path) -> str | None:
    return IMAGE_MEDIA_TYPES.get(file_path.suffix.lower())
