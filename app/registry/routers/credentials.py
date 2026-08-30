from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.auth.dependencies.user import (
    require_permission,
    require_permission_responses,
)
from app.auth.models.user import User
from app.database import get_db
from app.registry.models.credential import (
    Credential,
    CredentialRead,
    CredentialWrite,
)
from app.utils import get_or_404, get_or_404_responses

router = APIRouter(
    prefix="/credentials",
    tags=["Credentials"],
)


@router.get(
    "",
    summary="Get a list of all credentials",
    dependencies=[Depends(require_permission)],
    responses={**require_permission_responses},
    operation_id="registryCredentials",
)
def credentials(
    db: Annotated[Session, Depends(get_db)],
) -> list[CredentialRead]:
    return db.exec(select(Credential))


@router.post(
    "",
    summary="Create a new credential",
    responses={**require_permission_responses},
    operation_id="registryCredentialsCreate",
)
def credentials_create(
    body: CredentialWrite,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permission)],
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
    dependencies=[Depends(require_permission)],
    responses={
        **require_permission_responses,
        **get_or_404_responses,
    },
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
