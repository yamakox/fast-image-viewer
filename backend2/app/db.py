from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import env

db_path = Path(env.FIV_APPDATA_FOLDER_PATH).resolve() / 'dataset.sqlite3'
db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f'sqlite:///{db_path}',
    connect_args={'check_same_thread': False},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
