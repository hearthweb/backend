import pytest
from sqlmodel import Session

from app.auth.models.totp import Totp
from app.auth.models.user import User

from . import TOTP_SECRET


@pytest.fixture(name="totp")
def totp_fixture(
    db: Session,
    user: User,
) -> Totp:
    totp = Totp(user_id=user.id)
    totp.set_secret(TOTP_SECRET)
    db.add(totp)
    db.commit()
    return totp


@pytest.fixture(name="totp_verified")
def totp_verified_fixture(
    db: Session,
    totp: Totp,
) -> Totp:
    totp.encrypted_secret = totp.encrypted_secret_new
    totp.encrypted_secret_new = ""
    db.add(totp)
    db.commit()
    return totp
