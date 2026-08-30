from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.auth.models.user import User
from app.registry.models.credential import (
    Credential,
    CredentialRead,
)
from tests.utils import compare_sorted, dump

from . import (
    CREDENTIAL_PASSWORD,
    CREDENTIAL_SERVICE,
    CREDENTIAL_USERNAME,
)


def test_registry_credentials(
    client: TestClient,
    logged_in_user: User,
    credential: Credential,
):
    response = client.get("/registry/credentials")
    assert response.status_code == status.HTTP_200_OK
    assert compare_sorted(
        response.json(),
        [
            dump(CredentialRead, credential),
        ],
        "id",
    )


def test_registry_credentials_create(
    client: TestClient,
    logged_in_user: User,
    db: Session,
):
    response = client.post(
        "/registry/credentials",
        json={
            "service": CREDENTIAL_SERVICE,
            "username_or_email": CREDENTIAL_USERNAME,
            "password": CREDENTIAL_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == dump(CredentialRead, db.get(Credential, json["id"]))


def test_registry_credentials_by_id_delete(
    client: TestClient,
    logged_in_user: User,
    credential: Credential,
    db: Session,
):
    response = client.delete(f"/registry/credentials/{credential.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db.get(Credential, credential.id) is None
