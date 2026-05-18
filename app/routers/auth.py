from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.database import get_session
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
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> UserRead:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
    )
    user = session.exec(select(User).where(User.email == body.email)).first()
    if user is None:
        User.dummy_verify_password(body.password)
        raise credential_exception
    if not user.verify_password(body.password):
        raise credential_exception
    request.session.clear()
    request.session["user_id"] = user.id
    return UserRead.model_validate(user)


@router.post(
    "/logout",
    summary="End the current session",
)
def logout(request: Request) -> None:
    request.session.clear()
