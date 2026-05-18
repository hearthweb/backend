from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlmodel import Session

from app.database import get_session
from app.models.user import User

get_current_user_responses = {
    401: {"description": "Not authenticated"},
}

get_current_admin_responses = {
    403: {"description": "Not authorized"},
}


def get_current_user(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> User:
    """
    Get the currently logged in user; raise an exception if there is none
    """
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
    )
    user_id: int | None = request.session.get("user_id")
    if user_id is None:
        raise credential_exception
    user: User | None = session.get(User, user_id)
    if user is None:
        raise credential_exception
    return user


def get_current_admin(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Get the currently logged in admin; raise an exception if there is no
    logged in user or the current user is not an admin
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized",
        )
    return User
