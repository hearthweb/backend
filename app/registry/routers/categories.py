from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.auth.dependencies.user import (
    require_permission,
    require_permission_responses,
)
from app.database import get_db
from app.registry.models.category import Category

router = APIRouter(prefix="/categories")


@router.get(
    "",
    summary="Get a list of all categories",
    dependencies=[Depends(require_permission)],
    responses={**require_permission_responses},
    operation_id="registryCategories",
)
def registry_categories(
    db: Annotated[Session, Depends(get_db)],
) -> list[Category]:
    return db.exec(select(Category))
