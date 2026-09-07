from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.auth.dependencies.session import (
    get_login_session_completed,
    get_login_session_completed_responses,
)
from app.common.db import (
    get_or_404,
    get_or_404_responses,
)
from app.database import get_db
from app.registry.models.credential import (
    Credential,
    CredentialRead,
    CredentialWrite,
)

router = APIRouter(
    prefix="/credentials",
    dependencies=[Depends(get_login_session_completed)],
    responses={**get_login_session_completed_responses},
)


@router.get(
    "",
    summary="Get a list of all credentials",
    operation_id="registryCredentials",
)
def credentials(
    db: Annotated[Session, Depends(get_db)],
) -> list[CredentialRead]:
    return db.exec(select(Credential))


@router.post(
    "",
    summary="Create a new credential",
    operation_id="registryCredentialsCreate",
)
def credentials_create(
    body: CredentialWrite,
    db: Annotated[Session, Depends(get_db)],
) -> CredentialRead:
    credential = Credential.model_validate(body)
    db.add(credential)
    db.commit()
    db.refresh(credential)
    return credential


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific credential",
    responses={**get_or_404_responses},
    operation_id="registryCredentialsByIdDelete",
)
def credentials_by_id_delete(
    id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    credential = get_or_404(
        db.exec(
            select(Credential).where(Credential.id == id).with_for_update(),
        ).one_or_none(),
    )
    db.delete(credential)
    db.commit()
