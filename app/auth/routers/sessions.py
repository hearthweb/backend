from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from sqlmodel import Session, select

from app.auth.dependencies.session import (
    get_login_session,
    get_login_session_responses,
)
from app.auth.models.session import Session as AuthSession
from app.auth.models.user import (
    User,
    UserLogin,
    UserRead,
)
from app.config import Environment, settings
from app.database import get_db
from app.types import create_http_exception_response

router = APIRouter(
    prefix="/session",
    tags=["Session"],
)


@router.post(
    "/login",
    summary="Login with an email and password",
    responses={
        **create_http_exception_response(401, "Invalid credentials"),
    },
    operation_id="authSessionlogin",
)
def login(
    db: Annotated[Session, Depends(get_db)],
    body: UserLogin,
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
    operation_id="authSessionlogout",
)
def logout(
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[AuthSession, Depends(get_login_session)],
) -> None:
    db.delete(session)
    db.commit()
