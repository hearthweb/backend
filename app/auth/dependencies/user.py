from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select

from app.auth.dependencies.session import (
    get_login_session,
    get_login_session_responses,
)
from app.auth.models.session import Session as AuthSession
from app.auth.models.user import User
from app.database import get_db


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[AuthSession, Depends(get_login_session)],
) -> User:
    """
    Verify that a user is successfully logged in
    """

    # Find the user referenced by the session
    user = db.exec(select(User).where(User.id == session.user_id)).one_or_none()

    # If the session's user is somehow invalid, return unauthorized
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )

    # Return the user
    return user


get_current_user_responses = {
    **get_login_session_responses,
}
