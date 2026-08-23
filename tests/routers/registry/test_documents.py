from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.models.registry.category import Category
from app.models.registry.document import (
    Document,
    DocumentPublic,
)
from app.models.user import User
from tests.constants import (
    REGISTRY_DOCUMENT_CONTENT,
    REGISTRY_DOCUMENT_FILENAME,
    REGISTRY_DOCUMENT_FILETYPE,
    REGISTRY_DOCUMENT_NAME,
)
from tests.utils import compare_sorted, dump


def test_registry_documents(
    client: TestClient,
    logged_in_admin: User,
    document: Document,
):
    response = client.get("/registry/documents")
    assert response.status_code == status.HTTP_200_OK
    assert compare_sorted(
        response.json(),
        [
            dump(DocumentPublic, document),
        ],
        "id",
    )


def test_registry_documents_create(
    client: TestClient,
    logged_in_admin: User,
    category: Category,
    tmp_path: str,
    db: Session,
):
    response = client.post(
        "/registry/documents",
        data={
            "name": REGISTRY_DOCUMENT_NAME,
            "category_id": category.id,
        },
        files={
            "file": (
                REGISTRY_DOCUMENT_FILENAME,
                REGISTRY_DOCUMENT_CONTENT,
                REGISTRY_DOCUMENT_FILETYPE,
            ),
        },
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    document = db.get(Document, json["id"])
    assert json == dump(DocumentPublic, document)
    with open(Path(tmp_path) / document.relative_path, "r") as f:
        assert f.read() == REGISTRY_DOCUMENT_CONTENT


def test_registry_documents_by_id_download(
    client: TestClient,
    logged_in_admin: User,
    document: Document,
    tmp_path: str,
):
    response = client.get(f"/registry/documents/{document.id}/download")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert response.headers["X-Accel-Redirect"] == str(
        Path(tmp_path) / document.relative_path
    )


def test_registry_documents_by_id_delete(
    client: TestClient,
    logged_in_admin: User,
    document: Document,
    db: Session,
):
    response = client.delete(f"/registry/documents/{document.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db.get(Document, document.id) is None
