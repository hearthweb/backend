from pathlib import Path

import pytest
from sqlmodel import Session

from app.models.registry.category import Category
from app.models.registry.credential import Credential
from app.models.registry.document import Document

from . import (
    CATEGORY_NAME,
    CREDENTIAL_PASSWORD,
    CREDENTIAL_SERVICE,
    CREDENTIAL_USERNAME,
    DOCUMENT_CONTENT,
    DOCUMENT_FILENAME,
    DOCUMENT_FILETYPE,
    DOCUMENT_NAME,
)


@pytest.fixture(name="category")
def category(
    db: Session,
):
    category = Category(name=CATEGORY_NAME)
    db.add(category)
    db.commit()
    return category


@pytest.fixture(name="credential")
def credential(db: Session):
    credential = Credential(
        service=CREDENTIAL_SERVICE,
        username_or_email=CREDENTIAL_USERNAME,
        password=CREDENTIAL_PASSWORD,
    )
    db.add(credential)
    db.commit()
    return credential


@pytest.fixture(name="document")
def document(
    db: Session,
    category: Category,
    tmp_path: str,
):
    document = Document(
        name=DOCUMENT_NAME,
        category_id=category.id,
        filename=DOCUMENT_FILENAME,
        filesize=len(DOCUMENT_CONTENT),
        filetype=DOCUMENT_FILETYPE,
    )
    db.add(document)
    db.flush()
    p = Path(tmp_path) / document.relative_path
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        f.write(DOCUMENT_CONTENT)
    db.commit()
    return document
