from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session

from app.database import get_db

router = APIRouter(
    prefix="/internal",
)


@router.get(
    "/health-check",
    include_in_schema=False,
)
def system(
    db: Annotated[Session, Depends(get_db)],
    request: Request,
) -> None:
    if request.client.host not in ("127.0.0.1", "::1"):
        raise HTTPException(status_code=404)
