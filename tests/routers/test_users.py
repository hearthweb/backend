from fastapi import status
from fastapi.testclient import TestClient

from app.models.user import User, UserRead
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
