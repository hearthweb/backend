from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session, select

from app.config import settings
from app.database import get_session
from app.models.user import User, UserRead

ALGORITHM = "HS256"

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_credentials_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials supplied",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        try:
            user_id = int(payload.get("sub"))
        except TypeError, ValueError:
            raise get_credentials_exception()
        user = session.exec(
            select(User).where(User.id == user_id).where(User.is_active),
        ).first()
        if user is None:
            raise get_credentials_exception()
    except InvalidTokenError:
        raise get_credentials_exception()
    return user


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    user = session.exec(
        select(User).where(User.username == form_data.username).where(User.is_active),
    ).first()
    if user is None:
        User.dummy_verify_password(form_data.password)
        raise get_credentials_exception()
    if not user.verify_password(form_data.password):
        raise get_credentials_exception()
    return {
        "access_token": jwt.encode(
            {
                "sub": str(user.id),
                "exp": datetime.now(timezone.utc)
                + timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME),
            },
            settings.SECRET_KEY,
            algorithm=ALGORITHM,
        ),
        "token_type": "bearer",
    }


@router.get("/me")
async def read_me(
    user: Annotated[User, Depends(get_current_user)],
) -> UserRead:
    return UserRead.model_validate(user)
