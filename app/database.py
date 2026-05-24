from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from app import models  # noqa: F401
from app.config import Environment, settings

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


def db_context():
    return Session(engine)


def get_db() -> Generator[Session, None, None]:
    with db_context() as session:
        yield session
