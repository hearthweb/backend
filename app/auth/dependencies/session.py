from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

from app.auth.models.session import Session as AuthSession
from app.config import Environment, settings
from app.database import get_db
from app.types import create_http_exception_response

credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Not authorized",
)

credential_exception_responses = {
    **create_http_exception_response(401, "Unauthorized"),
}


def set_session_cookie(
    response: Response,
    session: AuthSession,
) -> None:
    response.set_cookie(
        key="session_id",
        value=session.id,
        httponly=True,
        secure=settings.ENVIRONMENT == Environment.PROD,
        expires=session.expires,
    )


def get_login_session(
    db: Annotated[Session, Depends(get_db)],
    session_id: Annotated[str | None, Cookie()] = None,
) -> AuthSession:
    """
    Verify that a login session was provided BUT do not confirm if login was
    completed; this is useful only for the /login/otp route
    """
    session = db.exec(
        select(AuthSession)
        .where(AuthSession.id == session_id)
        .where(AuthSession.expires > func.now())
        .options(selectinload(AuthSession.user))
        .with_for_update(),
    ).one_or_none()
    if session is None:
        raise credential_exception
    return session


get_login_session_responses = {
    **credential_exception_responses,
}


def get_login_session_completed(
    db: Annotated[Session, Depends(get_db)],
    response: Response,
    session: Annotated[AuthSession, Depends(get_login_session)],
) -> AuthSession:
    """
    Verify that a login session was provided AND that it was completed; also
    refresh the expiry time if it is going to occur soon
    """
    if not session.completed:
        raise credential_exception
    now = datetime.now(UTC)
    if session.expires < now + timedelta(minutes=30):
        session.expires = now + timedelta(hours=1)
        db.add(session)
        db.commit()
        set_session_cookie(response, session)
    return session


get_login_session_completed_response = {
    **get_login_session_responses,
}
