from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.auth.models.user import User, UserRead
from tests.utils import compare_sorted, dump

from . import (
    USER_EMAIL,
    USER_PASSWORD,
)


def test_users(
    client: TestClient,
    logged_in_user: User,
):
    response = client.get("/auth/users")
    assert response.status_code == status.HTTP_200_OK
    assert compare_sorted(
        response.json(),
        [
            dump(UserRead, logged_in_user),
        ],
        "id",
    )


def test_users_me(
    client: TestClient,
    logged_in_user: User,
):
    response = client.get("/auth/users/me")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == dump(UserRead, logged_in_user)


def test_users_user_id(
    client: TestClient,
    logged_in_user: User,
    user: User,
):
    response = client.get(f"/auth/users/{user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == dump(UserRead, user)


def test_users_create(
    client: TestClient,
    logged_in_user: User,
    db: Session,
):
    response = client.post(
        "/auth/users",
        json={
            "email": USER_EMAIL + "2",
            "password": USER_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == dump(UserRead, db.get(User, json["id"]))


def test_users_id_delete(
    client: TestClient,
    logged_in_user: User,
    user: User,
    db: Session,
):
    response = client.delete(f"/auth/users/{user.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db.get(User, user.id) is None
