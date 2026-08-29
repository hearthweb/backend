from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.auth.models import *
from app.config import Environment, settings
from app.finance.models import *
from app.registry.models import *

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


def get_db() -> Generator[Session]:
    with db_context() as session:
        yield session
