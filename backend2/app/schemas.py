from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FolderListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class FolderDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    pathname: str
    parent: int | None = None


class ImageListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    favorite: datetime | None


class ImageDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    parent: int | None = None
    hash: str = Field(validation_alias='hash_', serialization_alias='hash')
    timestamp: datetime
    favorite: datetime | None


class ImageFavoriteUpdate(BaseModel):
    favorite: datetime | None


class ImageFavoriteResponse(BaseModel):
    id: int
    favorite: datetime | None


class PaginatedImages(BaseModel):
    count: int
    page: int
    num_pages: int
    page_size: int
    results: list[ImageListItem]
