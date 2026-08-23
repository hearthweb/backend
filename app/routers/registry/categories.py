from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_db
from app.dependencies.auth import (
    get_current_admin,
    get_current_admin_responses,
)
from app.models.registry.category import Category

router = APIRouter(prefix="/categories")


@router.get(
    "",
    summary="Get a list of all categories",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
    },
    operation_id="registryCategories",
)
def registry_categories(
    db: Annotated[Session, Depends(get_db)],
) -> list[Category]:
    return db.exec(select(Category))
