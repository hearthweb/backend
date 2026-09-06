import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.auth.models.totp import Totp
from app.auth.models.user import User

from . import (
    TOTP_CODE,
    USER_PASSWORD,
)


def test_totp(
    client: TestClient,
    logged_in_user: User,
    totp: Totp,
):
    response = client.get("/auth/totp")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "enabled": False,
        "verified": False,
    }


@pytest.mark.parametrize(
    "password, status_code",
    [
        (USER_PASSWORD, status.HTTP_200_OK),
        ("", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_totp_create(
    client: TestClient,
    logged_in_user: User,
    password: str,
    status_code: int,
):
    response = client.post(
        "/auth/totp",
        json={
            "password": password,
        },
    )
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "code, status_code",
    [
        (TOTP_CODE, status.HTTP_200_OK),
        ("", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_totp_create_existing(
    client: TestClient,
    logged_in_user: User,
    totp_verified: Totp,
    code: str,
    status_code: int,
):
    response = client.post(
        "/auth/totp",
        json={
            "code": code,
        },
    )
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "code, status_code",
    [
        (TOTP_CODE, status.HTTP_200_OK),
        ("", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_totp_verify(
    client: TestClient,
    logged_in_user: User,
    totp: Totp,
    code: str,
    status_code: int,
):
    response = client.post(
        "/auth/totp/verify",
        json={
            "code": code,
        },
    )
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "code, status_code",
    [
        (TOTP_CODE, status.HTTP_204_NO_CONTENT),
        ("", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_totp_delete(
    client: TestClient,
    logged_in_user: User,
    totp_verified: Totp,
    code: str,
    status_code: int,
):
    response = client.delete(
        "/auth/totp",
        params={
            "code": code,
        },
    )
    assert response.status_code == status_code
