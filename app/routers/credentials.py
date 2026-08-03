from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.database import get_db
from app.dependencies.auth import (
    get_current_admin,
    get_current_admin_responses,
)
from app.models.credential import (
    Credential,
    CredentialCreateEdit,
    CredentialPublic,
)
from app.models.user import User
from app.utils import get_or_404, get_or_404_responses

router = APIRouter(
    prefix="/credentials",
    tags=["Credentials"],
)


@router.get(
    "",
    summary="Get a list of all credentials",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
    },
    operation_id="credentials",
)
def credentials(
    db: Annotated[Session, Depends(get_db)],
) -> list[CredentialPublic]:
    return db.exec(
        select(Credential).options(selectinload(Credential.user)),
    )


@router.post(
    "",
    summary="Create a new credential",
    responses={
        **get_current_admin_responses,
    },
    operation_id="credentialsCreate",
)
def credentials_create(
    body: CredentialCreateEdit,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_admin)],
) -> CredentialPublic:
    credential = Credential.model_validate(
        body,
        update={
            "user_id": user.id,
        },
    )
    db.add(credential)
    db.commit()
    db.refresh(credential)
    return credential


@router.delete(
    "/{credential_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific credential",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
        **get_or_404_responses,
    },
    operation_id="credentialsByIdDelete",
)
def credentials_by_id_delete(
    credential_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    credential = get_or_404(
        db.exec(
            select(Credential).where(Credential.id == credential_id).with_for_update(),
        ).one_or_none(),
    )
    db.delete(credential)
    db.commit()
