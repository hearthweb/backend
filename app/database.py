from typing import Generator

from sqlmodel import Session, SQLModel, create_engine, select

from app import models  # noqa: F401
from app.config import Environment, settings
from app.models import User

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
    with Session(engine) as session:
        if session.exec(select(User)).first() is None:
            user = User(
                email="admin@example.com",
                is_admin=True,
            )
            user.set_password("password")
            session.add(user)
            session.commit()


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        try:
            yield session
        except:
            session.rollback()
            raise
