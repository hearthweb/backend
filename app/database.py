from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from . import models  # noqa: F401
from .config import Environment, settings

connect_args = (
    {"check_same_thread": False} if settings.ENVIRONMENT == Environment.DEV else {}
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=(settings.ENVIRONMENT == Environment.DEV),
)


def init_db() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        try:
            yield session
        except:
            session.rollback()
            raise
