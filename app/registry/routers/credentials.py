from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.auth.models.user import User
from app.database import get_db
from app.dependencies.auth import (
    get_current_admin,
    get_current_admin_responses,
)
from app.registry.models.credential import (
    Credential,
    CredentialRead,
    CredentialWrite,
)
from app.utils import get_or_404, get_or_404_responses

router = APIRouter(prefix="/credentials")


@router.get(
    "",
    summary="Get a list of all credentials",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
    },
    operation_id="registryCredentials",
)
def registry_credentials(
    db: Annotated[Session, Depends(get_db)],
) -> list[CredentialRead]:
    return db.exec(select(Credential))


@router.post(
    "",
    summary="Create a new credential",
    responses={
        **get_current_admin_responses,
    },
    operation_id="registryCredentialsCreate",
)
def registry_credentials_create(
    body: CredentialWrite,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_admin)],
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
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
        **get_or_404_responses,
    },
    operation_id="registryCredentialsByIdDelete",
)
def registry_credentials_by_id_delete(
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
