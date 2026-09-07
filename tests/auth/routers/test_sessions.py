from fastapi import status
from fastapi.testclient import TestClient

from app.auth.models import (
    Totp,
    User,
)

from . import (
    TOTP_CODE,
    USER_EMAIL,
    USER_PASSWORD,
)


def test_sessions_login_totp(
    client: TestClient,
    user: User,
    totp: Totp,
):
    response = client.post(
        "/auth/sessions/login",
        json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("status", "success")


def test_sessions_login_totp_verified(
    client: TestClient,
    user: User,
    totp_verified: Totp,
):
    response = client.post(
        "/auth/sessions/login",
        json={
            "email": USER_EMAIL,
            "password": USER_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json().get("status", "totp_required")
    response = client.post(
        "/auth/sessions/login/totp",
        json={
            "code": TOTP_CODE,
        },
    )
    assert response.status_code == status.HTTP_200_OK


def test_sessions_logout(
    client: TestClient,
    logged_in_user: User,
):
    response = client.post("/auth/sessions/logout")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    response = client.get("/auth/users/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
