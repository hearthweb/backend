from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.user import User, UserRead
from tests.constants import USER_EMAIL, USER_PASSWORD
from tests.utils import compare_sorted, dump


def test_users(
    client: TestClient,
    logged_in_admin: User,
    user: User,
):
    response = client.get("/users")
    assert response.status_code == status.HTTP_200_OK
    assert compare_sorted(
        response.json(),
        [
            dump(UserRead, logged_in_admin),
            dump(UserRead, user),
        ],
        "id",
    )


def test_users_me(client: TestClient, logged_in_user: User):
    response = client.get("/users/me")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == dump(UserRead, logged_in_user)


def test_users_user_id(
    client: TestClient,
    logged_in_admin: User,
    user: User,
):
    response = client.get(f"/users/{user.id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == dump(UserRead, user)


def test_users_create(
    client: TestClient,
    logged_in_admin: User,
    db: Session,
):
    response = client.post(
        "/users",
        json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == dump(UserRead, db.get(User, json["id"]))
