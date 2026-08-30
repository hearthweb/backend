from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.auth.dependencies.session import (
    get_login_session,
    get_login_session_responses,
)
from app.database import get_db
from app.registry.models.category import Category

router = APIRouter(
    prefix="/categories",
    tags=["Categories"],
    dependencies=[Depends(get_login_session)],
    responses={**get_login_session_responses},
)


@router.get(
    "",
    summary="Get a list of all categories",
    operation_id="registryCategories",
)
def categories(
    db: Annotated[Session, Depends(get_db)],
) -> list[Category]:
    return db.exec(select(Category))
