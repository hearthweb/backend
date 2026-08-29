from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status
from sqlmodel import Session, func, select

from app.auth.models.session import Session as AuthSession
from app.database import get_db
from app.types import create_http_exception_response


def get_login_session(
    db: Annotated[Session, Depends(get_db)],
    session_id: Annotated[str | None, Cookie()] = None,
) -> AuthSession:
    """
    Verify that a valid login session was provided and if it is less than 30
    minutes from expiry, extend the session
    """

    # Lookup the session and confirm it was completed and has not expired
    session = db.exec(
        select(AuthSession)
        .where(AuthSession.id == session_id)
        .where(AuthSession.completed == True)
        .where(AuthSession.expires > func.now())
        .with_for_update(),
    ).one_or_none()

    # If none was found raise a 401 error
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )

    # If the session is within the refresh threshold, extend it
    now = datetime.now(UTC)
    if session.expires < now + timedelta(minutes=30):
        session.expires = now + timedelta(hours=1)
        db.add(session)
        db.commit()

    # Return the valid session
    return session


get_login_session_responses = {
    **create_http_exception_response(401, "Unauthorized"),
}
