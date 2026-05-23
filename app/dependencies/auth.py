from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlmodel import func, select

from app.database import get_db
from app.models.auth import LoginSession
from app.models.user import User


def get_login_session(
    session_id: Annotated[str | None, Cookie()] = None,
) -> LoginSession:
    """
    Verify that a valid login session was provided and if it is less than 30
    minutes from expiry, extend the session
    """
    with get_db() as db:
        session = db.exec(
            select(LoginSession)
            .where(LoginSession.id == session_id)
            .where(LoginSession.expires > func.now())
            .with_for_update(),
        ).first()
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        now = datetime.now(timezone.utc)
        refresh_threshold = now + timedelta(minutes=30)
        if session.expires < refresh_threshold:
            session.expires = now + timedelta(hours=1)
            db.add(session)
            db.commit()
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
