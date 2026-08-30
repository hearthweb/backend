import os
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.auth.dependencies.user import (
    require_permission,
    require_permission_responses,
)
from app.database import get_db
from app.registry.models.document import (
    Document,
    DocumentPublic,
)
from app.upload import get_upload_path, upload_file
from app.utils import get_or_404, get_or_404_responses

router = APIRouter(prefix="/documents")


@router.get(
    "",
    summary="Get a list of all documents",
    dependencies=[Depends(require_permission)],
    responses={**require_permission_responses},
    operation_id="registryDocuments",
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
    dependencies=[Depends(require_permission)],
    responses={**require_permission_responses},
    operation_id="registryDocumentsCreate",
)
def documents_create(
    file: Annotated[UploadFile, File()],
    name: Annotated[str, Form()],
    category_id: Annotated[int, Form()],
    db: Annotated[Session, Depends(get_db)],
    upload_path: Annotated[Path, Depends(get_upload_path)],
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
    upload_file(file, upload_path / document.relative_path)
    db.commit()
    db.refresh(document)
    return document


@router.get(
    "/{id}/download",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Download a document",
    dependencies=[Depends(require_permission)],
    responses={
        **require_permission_responses,
        **get_or_404_responses,
    },
    operation_id="registryDocumentsByIdDownload",
)
def documents_by_id_download(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    upload_path: Annotated[Path, Depends(get_upload_path)],
    response: Response,
) -> None:
    document = get_or_404(
        db.exec(
            select(Document).where(Document.id == id),
        ).one_or_none(),
    )
    response.headers["X-Accel-Redirect"] = str(
        upload_path / document.relative_path,
    )
    response.headers["Content-Type"] = document.filetype
    response.headers["Content-Disposition"] = (
        f'attachment; filename="{document.filename}"'
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific document",
    dependencies=[Depends(require_permission)],
    responses={
        **require_permission_responses,
        **get_or_404_responses,
    },
    operation_id="registryDocumentsByIdDelete",
)
def documents_by_id_delete(
    id: int,
    db: Annotated[Session, Depends(get_db)],
    upload_path: Annotated[Path, Depends(get_upload_path)],
) -> None:
    document = get_or_404(
        db.exec(
            select(Document).where(Document.id == id).with_for_update(),
        ).one_or_none(),
    )
    os.unlink(upload_path / document.relative_path)
    db.delete(document)
    db.commit()
