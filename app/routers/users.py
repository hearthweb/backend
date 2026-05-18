from typing import Annotated, List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.database import get_session
from app.dependencies.auth import (
    get_current_admin,
    get_current_admin_responses,
    get_current_user,
    get_current_user_responses,
)
from app.models.user import User, UserRead
from app.utils import get_or_404, get_or_404_responses

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "",
    summary="Get a list of all users",
    dependencies=[Depends(get_current_admin)],
    responses={**get_current_admin_responses},
)
def users(
    session: Annotated[Session, Depends(get_session)],
) -> List[UserRead]:
    return session.exec(select(User))


@router.get(
    "/{user_id}",
    summary="Get a specific user's information",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
        **get_or_404_responses,
    },
)
def users_user_id(
    user_id: int,
    session: Annotated[Session, Depends(get_session)],
) -> UserRead:
    return UserRead.model_validate(
        get_or_404(session.get(User, user_id)),
    )


@router.get(
    "/me",
    summary="Get the current user's information",
    responses={**get_current_user_responses},
)
def users_me(
    user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    return UserRead.model_validate(user)
