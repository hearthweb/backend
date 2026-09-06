from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlmodel import Session, delete, select

from app.auth.dependencies.session import (
    get_login_session,
    get_login_session_responses,
)
from app.auth.models.session import (
    Session as AuthSession,
)
from app.auth.models.session import (
    SessionLogin,
)
from app.auth.models.user import (
    User,
    UserRead,
)
from app.config import Environment, settings
from app.database import get_db
from app.types import create_http_exception_response

router = APIRouter(prefix="/sessions")


@router.post(
    "/login",
    summary="Begin login with an email and password",
    responses={
        **create_http_exception_response(401, "Invalid credentials"),
    },
    operation_id="authSessionLogin",
)
def login(
    db: Annotated[Session, Depends(get_db)],
    body: SessionLogin,
    response: Response,
    user_agent: Annotated[str, Header()] = "Unknown",
) -> UserRead:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )
    user = db.exec(
        select(User).where(User.email == body.email),
    ).one_or_none()
    if user is None:
        User.dummy_verify_password(body.password)
        raise credential_exception
    if not user.verify_password(body.password):
        raise credential_exception
    expires = datetime.now(UTC) + timedelta(hours=1)
    session = AuthSession(
        user_id=user.id,
        user_agent=user_agent,
        completed=True,
        expires=expires,
    )
    db.add(session)
    db.commit()
    response.set_cookie(
        key="session_id",
        value=session.id,
        httponly=True,
        secure=settings.ENVIRONMENT == Environment.PROD,
        expires=expires,
    )
    return UserRead.model_validate(user)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="End the current session",
    responses={**get_login_session_responses},
    operation_id="authSessionLogout",
)
def logout(
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[AuthSession, Depends(get_login_session)],
) -> None:
    db.delete(session)
    db.commit()


@router.post(
    "/logout/all",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="End all active sessions for the current user",
    responses={**get_login_session_responses},
    operation_id="authSessionLogoutAll",
)
def logout_all(
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[AuthSession, Depends(get_login_session)],
) -> None:
    db.exec(
        delete(AuthSession).where(AuthSession.user_id == session.user_id),
    )
