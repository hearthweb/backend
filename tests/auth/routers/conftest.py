import secrets

import pytest
from sqlmodel import Session

from app.auth.common import sha256
from app.auth.models.totp import (
    Totp,
    TotpRecoveryCode,
)
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


@pytest.fixture(name="totp_recovery")
def totp_recovery(
    db: Session,
    user: User,
    totp_verified: Totp,
) -> str:
    code = secrets.token_hex(8)
    recovery_code = TotpRecoveryCode(
        totp_user_id=user.id,
        code_hash=sha256(code),
    )
    db.add(recovery_code)
    db.commit()
    return code
