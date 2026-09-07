from typing import Annotated

from fastapi import Depends

from app.auth.dependencies.session import (
    get_login_session_completed,
    get_login_session_completed_responses,
)
from app.auth.models.session import Session as AuthSession
from app.auth.models.user import User


def get_current_user(
    session: Annotated[AuthSession, Depends(get_login_session_completed)],
) -> User:
    return session.user


get_current_user_responses = {
    **get_login_session_completed_responses,
}
