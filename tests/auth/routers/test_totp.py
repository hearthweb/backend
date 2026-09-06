from fastapi import status
from fastapi.testclient import TestClient

from app.auth.models.totp import Totp
from app.auth.models.user import User


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
