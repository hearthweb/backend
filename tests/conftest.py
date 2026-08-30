from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from app.auth.models.user import User
from app.database import get_db
from app.main import app
from app.upload import get_upload_path

from . import (
    USER_EMAIL,
    USER_PASSWORD,
)


@pytest.fixture(name="db")
def db_fixture() -> Generator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client", autouse=True)
def client_fixture(
    db: Session,
    tmp_path: str,
) -> Generator[TestClient]:
    def override_get_db() -> Generator[Session]:
        yield db

    def override_get_upload_path() -> Path:
        return Path(tmp_path)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_upload_path] = override_get_upload_path
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(name="user")
def user_fixture(db: Session) -> User:
    user = User(email=USER_EMAIL)
    user.set_password(USER_PASSWORD)
    db.add(user)
    db.commit()
    return user


@pytest.fixture(name="logged_in_user")
def logged_in_user_fixture(
    client: TestClient,
    user: User,
) -> User:
    response = client.post(
        "/auth/session/login",
        json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    return user
