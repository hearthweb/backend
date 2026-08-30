from pathlib import Path

from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.auth.models.user import User
from app.registry.models.category import Category
from app.registry.models.document import (
    Document,
    DocumentPublic,
)
from tests.utils import compare_sorted, dump

from . import (
    DOCUMENT_CONTENT,
    DOCUMENT_FILENAME,
    DOCUMENT_FILETYPE,
    DOCUMENT_NAME,
)


def test_registry_documents(
    client: TestClient,
    logged_in_user: User,
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
    logged_in_user: User,
    category: Category,
    tmp_path: str,
    db: Session,
):
    response = client.post(
        "/registry/documents",
        data={
            "name": DOCUMENT_NAME,
            "category_id": category.id,
        },
        files={
            "file": (
                DOCUMENT_FILENAME,
                DOCUMENT_CONTENT,
                DOCUMENT_FILETYPE,
            ),
        },
    )
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    document = db.get(Document, json["id"])
    assert json == dump(DocumentPublic, document)
    with open(Path(tmp_path) / document.relative_path, "r") as f:
        assert f.read() == DOCUMENT_CONTENT


def test_registry_documents_by_id_download(
    client: TestClient,
    logged_in_user: User,
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
    logged_in_user: User,
    document: Document,
    db: Session,
):
    response = client.delete(f"/registry/documents/{document.id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert db.get(Document, document.id) is None
