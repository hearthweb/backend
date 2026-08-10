from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status
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
    DocumentPublic,
)
from app.utils import get_or_404, get_or_404_responses, upload_file

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
    file: Annotated[UploadFile, File()],
    name: Annotated[str, Form()],
    category_id: Annotated[int, Form()],
    db: Annotated[Session, Depends(get_db)],
) -> DocumentPublic:
    document = Document.model_validate(
        {
            "name": name,
            "category_id": category_id,
            "filename": file.filename,
            "filesize": file.size,
            "filetype": file.content_type,
        },
    )
    db.add(document)
    db.flush()
    upload_file(file, document.absolute_path)
    db.commit()
    db.refresh(document)
    return document


@router.get(
    "/{document_id}/download",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Download a document",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
        **get_or_404_responses,
    },
    operation_id="documentsByIdDownload",
)
def documents_by_id_download(
    document_id: int,
    db: Annotated[Session, Depends(get_db)],
    response: Response,
) -> None:
    document = get_or_404(
        db.exec(
            select(Document).where(Document.id == document_id),
        ).one_or_none(),
    )
    response.headers["X-Accel-Redirect"] = document.absolute_path
    response.headers["Content-Type"] = document.filetype
    response.headers["Content-Disposition"] = (
        f'attachment; filename="{document.filename}"'
    )
