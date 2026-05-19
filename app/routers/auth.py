from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session, select

from app.config import Environment, settings
from app.database import get_db
from app.dependencies.auth import get_login_session, get_login_session_responses
from app.models.auth import LoginSession
from app.models.user import User, UserLogin, UserRead

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/login",
    summary="Login with an email and password",
    responses={401: {"description": "Invalid credentials"}},
)
def login(
    body: UserLogin,
    response: Response,
    db: Annotated[Session, Depends(get_db)],
) -> UserRead:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )
    user = db.exec(
        select(User).where(User.email == body.email),
    ).first()
    if user is None:
        User.dummy_verify_password(body.password)
        raise credential_exception
    if not user.verify_password(body.password):
        raise credential_exception
    expires = datetime.now(timezone.utc) + timedelta(hours=1)
    session = LoginSession(
        user_id=user.id,
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
    summary="End the current session",
    responses={**get_login_session_responses},
)
def logout(
    session: Annotated[LoginSession, Depends(get_login_session)],
    db: Annotated[Session, Depends(get_db)],
) -> None:
    db.delete(session)
    db.commit()
