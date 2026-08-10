from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.database import get_db
from app.dependencies.auth import (
    get_current_admin,
    get_current_admin_responses,
)
from app.models.document import (
    Document,
    DocumentCategory,
    DocumentCreateEdit,
    DocumentPublic,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


@router.get(
    "/categories",
    summary="Get a list of all document categories",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
    },
    operation_id="documentsCategories",
)
def documents_categories(
    db: Annotated[Session, Depends(get_db)],
) -> list[DocumentCategory]:
    return db.exec(select(DocumentCategory))


@router.get(
    "",
    summary="Get a list of all documents",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
    },
    operation_id="documents",
)
def documents(
    db: Annotated[Session, Depends(get_db)],
) -> list[DocumentPublic]:
    return db.exec(
        select(Document).options(selectinload(Document.category)),
    )


@router.post(
    "",
    summary="Create a new document",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
    },
    operation_id="documentsCreate",
)
def documents_create(
    body: DocumentCreateEdit,
    db: Annotated[Session, Depends(get_db)],
) -> DocumentPublic:
    document = Document.model_validate(
        body,
        update={
            "filesize": 0,
        },
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document
