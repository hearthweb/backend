from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.registry.credential import (
    Credential,
    CredentialRead,
)
from app.models.user import User
from tests.constants import (
    REGISTRY_CREDENTIAL_PASSWORD,
    REGISTRY_CREDENTIAL_SERVICE,
    REGISTRY_CREDENTIAL_USERNAME,
)
from tests.utils import compare_sorted, dump


def test_registry_credentials(
    client: TestClient,
    logged_in_admin: User,
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
    logged_in_admin: User,
    db: Session,
):
    response = client.post(
        "/registry/credentials",
        json={
            "service": REGISTRY_CREDENTIAL_SERVICE,
            "username_or_email": REGISTRY_CREDENTIAL_USERNAME,
            "password": REGISTRY_CREDENTIAL_PASSWORD,
        },
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json == dump(CredentialRead, db.get(Credential, json["id"]))


def test_registry_credentials_by_id_delete(
    client: TestClient,
    logged_in_admin: User,
    credential: Credential,
    db: Session,
):
    response = client.delete(f"/registry/credentials/{credential.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db.get(Credential, credential.id) is None
