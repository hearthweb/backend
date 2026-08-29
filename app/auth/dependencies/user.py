from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.auth.dependencies.session import (
    get_login_session,
    get_login_session_responses,
)
from app.auth.models.role import Role
from app.auth.models.session import Session as AuthSession
from app.auth.models.user import (
    User,
    UserPublic,
)
from app.database import get_db
from app.types import create_http_exception_response


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[AuthSession, Depends(get_login_session)],
) -> UserPublic:
    """
    Verify that a user is successfully logged in
    """

    # Find the user referenced by the session (and load permissions)
    user = db.exec(
        select(User)
        .where(User.id == session.user_id)
        .where(User.is_active == True)
        .options(
            selectinload(User.roles).selectinload(Role.permissions),
        ),
    ).one_or_none()

    # If the session's user is somehow invalid, return unauthorized
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized",
        )

    # Return the user
    return user


get_current_user_responses = {
    **get_login_session_responses,
}


def require_permission(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    request: Request,
) -> UserPublic:
    """
    Verify that the user has permission to access the current route
    """

    # Short circuit for admins:
    if user.is_admin:
        return User

    # Determine the name of the permission based on the route
    endpoint = request.scope.get("endpoint")

    # Check if the permission is in any of the user's roles
    for r in user.roles:
        for p in r.permissions:
            if p.name in endpoint.__name__:
                return User

    # User does not have the permission
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden",
    )


require_permission_responses = {
    **get_current_user_responses,
    **create_http_exception_response(403, "Forbidden"),
}
