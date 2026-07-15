from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# SQLite は INTEGER PRIMARY KEY のみ autoincrement するため、BigInteger を variant で切り替える
BigIntPK = BigInteger().with_variant(Integer, 'sqlite')


class Base(DeclarativeBase):
    pass


class Folder(Base):
    __tablename__ = 'api_folder'

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    pathname: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        BigIntPK,
        ForeignKey('api_folder.id', ondelete='CASCADE'),
        nullable=True,
    )

    parent: Mapped[Folder | None] = relationship(
        'Folder',
        remote_side=[id],
        back_populates='children',
    )
    children: Mapped[list[Folder]] = relationship(
        'Folder',
        back_populates='parent',
    )
    images: Mapped[list[Image]] = relationship(
        'Image',
        back_populates='parent',
    )


class Image(Base):
    __tablename__ = 'api_image'

    id: Mapped[int] = mapped_column(BigIntPK, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[int | None] = mapped_column(
        BigIntPK,
        ForeignKey('api_folder.id', ondelete='CASCADE'),
        nullable=True,
    )
    hash_: Mapped[str] = mapped_column('hash', String(16), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    favorite: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    parent: Mapped[Folder | None] = relationship('Folder', back_populates='images')
