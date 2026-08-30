from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.auth.dependencies.user import (
    require_permission,
    require_permission_responses,
)
from app.auth.models.role import Role
from app.database import get_db

router = APIRouter(
    prefix="/roles",
    tags=["Roles"],
)


@router.get(
    "",
    summary="Get a list of roles",
    dependencies=[Depends(require_permission)],
    responses={**require_permission_responses},
    operation_id="authRoles",
)
def roles(
    db: Annotated[Session, Depends(get_db)],
):
    return db.exec(select(Role))
