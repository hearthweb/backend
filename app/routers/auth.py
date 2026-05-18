from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.user import User, UserLogin, UserRead

router = APIRouter()


def get_current_user(
    request: Request,
    session: Annotated[Session, Depends(get_session)],
) -> User:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authorized",
    )
    user_id: int | None = request.session.get("user_id")
    if user_id is None:
        raise credential_exception
    user: User | None = session.get(User, user_id)
    if user is None:
        raise credential_exception
    return user


@router.post("/login")
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


@router.post("/logout")
def logout(request: Request) -> None:
    request.session.clear()


@router.get("/me")
def me(user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    return UserRead.model_validate(user)
