from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlmodel import Session, func, select

from app.database import get_db
from app.models.auth import LoginSession
from app.models.user import User


def get_login_session(
    db: Annotated[Session, Depends(get_db)],
    session_id: Annotated[str | None, Cookie()] = None,
) -> LoginSession:
    session = db.exec(
        select(LoginSession)
        .where(LoginSession.id == session_id)
        .where(LoginSession.expires > func.now()),
    ).first()
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return session


get_login_session_responses = {
    401: {"description": "Not authenticated"},
}


def get_current_user(
    session: Annotated[LoginSession, Depends(get_login_session)],
) -> User:
    """
    Get the currently logged in user; raise an exception if there is none
    """
    return session.user


get_current_user_responses = {
    **get_login_session_responses,
}


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


get_current_admin_responses = {
    **get_current_user_responses,
    403: {"description": "Not authorized"},
}
