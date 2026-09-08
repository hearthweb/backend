import hashlib

from fastapi import Response

from app.auth.models.session import Session
from app.config import Environment, settings


def sha256(cleartext: str) -> str:
    hashlib.sha256(cleartext.encode()).hexdigest()


def set_session_cookie(
    response: Response,
    session: Session,
) -> None:
    response.set_cookie(
        key="session_id",
        value=session.id,
        httponly=True,
        secure=settings.ENVIRONMENT == Environment.PROD,
        expires=session.expires,
    )
