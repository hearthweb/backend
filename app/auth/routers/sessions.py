import hashlib
from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlmodel import Session, delete, select

from app.auth.common import set_session_cookie
from app.auth.dependencies.session import (
    get_login_session,
    get_login_session_completed,
    get_login_session_completed_responses,
    get_login_session_responses,
)
from app.auth.models.recovery import Recovery
from app.auth.models.session import (
    Session as AuthSession,
)
from app.auth.models.session import (
    SessionLogin,
    SessionLoginSucceeded,
    SessionLoginTotp,
    SessionLoginTotpRecovery,
    SessionLoginTOTPRequired,
)
from app.auth.models.totp import Totp
from app.auth.models.user import (
    User,
    UserRead,
)
from app.common.http import create_http_exception_response
from app.common.time import get_current_time
from app.database import get_db

router = APIRouter(prefix="/sessions")

credential_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
)

credential_exception_responses = {
    **create_http_exception_response(401, "Invalid credentials"),
}


@router.post(
    "/login",
    summary="Begin login with an email and password",
    responses={**credential_exception_responses},
    operation_id="authSessionLogin",
)
def login(
    db: Annotated[Session, Depends(get_db)],
    body: SessionLogin,
    response: Response,
    user_agent: Annotated[str, Header()] = "Unknown",
) -> SessionLoginSucceeded | SessionLoginTOTPRequired:

    # Find the user that corresponds with the provided email
    user = db.exec(
        select(User).where(User.email == body.email),
    ).one_or_none()

    # If no user was found, perform a dummy password verification to thwart
    # timing attacks; otherwise, verify the user's password
    if user is None:
        User.dummy_verify_password(body.password)
        raise credential_exception
    if not user.verify_password(body.password):
        raise credential_exception

    # Password authentication was successful, check for TOTP
    totp = db.get(Totp, user.id)
    totp_required = totp is not None and totp.encrypted_secret

    # Create the login session
    expires = datetime.now(UTC) + timedelta(hours=1)
    session = AuthSession(
        user_id=user.id,
        user_agent=user_agent,
        completed=not totp_required,
        expires=expires,
    )
    db.add(session)
    db.commit()

    # Set the session cookie
    set_session_cookie(response, session)

    # Return the appropriate response
    if totp_required:
        return SessionLoginTOTPRequired()
    return SessionLoginSucceeded.model_validate(user)


@router.post(
    "/login/totp",
    summary="Complete login with a TOTP",
    responses={
        **get_login_session_responses,
        **credential_exception_responses,
    },
    operation_id="authSessionLoginTotp",
)
def login_totp(
    db: Annotated[Session, Depends(get_db)],
    body: SessionLoginTotp,
    session: Annotated[AuthSession, Depends(get_login_session)],
    current_time: Annotated[datetime, Depends(get_current_time)],
) -> UserRead:
    totp = db.get(Totp, session.user_id)
    if (
        totp is None
        or not totp.encrypted_secret
        or not totp.verify_code(
            totp.encrypted_secret,
            body.code,
            current_time,
        )
    ):
        raise credential_exception
    session.completed = True
    db.add(session)
    db.commit()
    return session.user


@router.post(
    "/login/totp/recovery",
    summary="Complete login with a TOTP recovery code",
    responses={},
    operation_id="authSessionLoginTotpRecovery",
)
def login_totp_recover(
    db: Annotated[Session, Depends(get_db)],
    body: SessionLoginTotpRecovery,
    session: Annotated[AuthSession, Depends(get_login_session)],
) -> UserRead:
    recovery = db.exec(
        select(Recovery)
        .where(Recovery.user_id == session.user_id)
        .where(Recovery.code_hash == hashlib.sha256(body.code.encode()).hexdigest()),
    ).one_or_none()
    if recovery is None:
        raise credential_exception
    session.completed = True
    db.add(session)
    db.delete(recovery)
    db.commit()
    return session.user


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="End the current session",
    responses={**get_login_session_completed_responses},
    operation_id="authSessionLogout",
)
def logout(
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[AuthSession, Depends(get_login_session_completed)],
) -> None:
    db.delete(session)
    db.commit()


@router.post(
    "/logout/all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="End all active sessions for the current user",
    responses={**get_login_session_completed_responses},
    operation_id="authSessionLogoutAll",
)
def logout_all(
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[AuthSession, Depends(get_login_session_completed)],
) -> None:
    db.exec(
        delete(AuthSession).where(AuthSession.user_id == session.user_id),
    )
