import pyotp
import pytest
from sqlmodel import Session

from app.auth.models.totp import Totp
from app.auth.models.user import User


@pytest.fixture(name="totp")
def totp_fixture(
    db: Session,
    user: User,
) -> Totp:
    totp = Totp(user_id=user.id)
    totp.set_secret(pyotp.random_hex())
    db.add(totp)
    db.commit()
