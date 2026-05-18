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


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials supplied",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)],
):
    user = session.exec(
        select(User).where(User.username == form_data.username),
    ).first()
    if user is None or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    return {
        "access_token": jwt.encode(
            {
                "sub": user.username,
                "exp": datetime.now(timezone.utc)
                + timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME),
            },
            settings.SECRET_KEY,
            algorithm=ALGORITHM,
        ),
        "token_type": "bearer",
    }


@router.get("/me")
async def read_me(user: Annotated[User, Depends(get_current_user)]) -> UserRead:
    return UserRead(**user.model_dump())
