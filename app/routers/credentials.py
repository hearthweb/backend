from typing import Annotated

from fastapi import APIRouter, Depends
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
