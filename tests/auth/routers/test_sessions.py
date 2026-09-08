import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.auth.models.totp import (
    Totp,
    TotpRecoveryCode,
)
from app.auth.models.user import User

from . import (
    TOTP_CODE,
    USER_EMAIL,
    USER_PASSWORD,
)


def test_sessions_login_totp(
    client: TestClient,
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


@pytest.mark.parametrize(
    "code, status_code",
    [
        (TOTP_CODE, status.HTTP_200_OK),
        ("", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_sessions_login_totp_verified(
    client: TestClient,
    totp_verified: Totp,
    code: str,
    status_code: int,
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
            "code": code,
        },
    )
    assert response.status_code == status_code


def test_sessions_login_totp_recovery(
    client: TestClient,
    totp_recovery: TotpRecoveryCode,
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
        "/auth/sessions/login/totp/recovery",
        json={
            "code": totp_recovery,
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
