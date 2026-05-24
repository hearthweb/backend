from typing import Generator

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from app.database import get_db
from app.main import app
from app.models.user import User
from tests.constants import USER_EMAIL, USER_PASSWORD


@pytest.fixture(name="db")
def db_fixture() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client", autouse=True)
def client_fixture(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture(name="user")
def user_fixture(db: Session) -> User:
    user = User(email=USER_EMAIL, is_admin=True)
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
        "/auth/login",
        json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    return user
