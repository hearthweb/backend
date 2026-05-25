from typing import Annotated, List

from fastapi import APIRouter, Depends, status
from sqlmodel import Session, select

from app.database import get_db
from app.dependencies.auth import (
    get_current_admin,
    get_current_admin_responses,
    get_current_user,
    get_current_user_responses,
)
from app.models.user import User, UserCreateEditAdmin, UserRead
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
    db: Annotated[Session, Depends(get_db)],
) -> List[UserRead]:
    return db.exec(select(User))


@router.get(
    "/me",
    summary="Get the current user's information",
    responses={**get_current_user_responses},
)
def users_me(
    user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    return UserRead.model_validate(user)


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
    db: Annotated[Session, Depends(get_db)],
) -> UserRead:
    return UserRead.model_validate(
        get_or_404(db.get(User, user_id)),
    )


@router.post(
    "",
    summary="Create a new user",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
    },
)
def users_create(
    body: UserCreateEditAdmin,
    db: Annotated[Session, Depends(get_db)],
) -> UserRead:
    user = User.model_validate(body)
    user.set_password(body.password)
    db.add(user)
    db.commit()
    return UserRead.model_validate(user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a specific user",
    dependencies=[Depends(get_current_admin)],
    responses={
        **get_current_admin_responses,
        **get_or_404_responses,
    },
)
def users_user_id_delete(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> None:
    user = get_or_404(
        db.exec(
            select(User).where(User.id == user_id).with_for_update(),
        ).scalar_one_or_none(),
    )
    db.delete(user)
    db.commit()
