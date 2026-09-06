import hashlib
import secrets
from datetime import datetime
from typing import Annotated

import pyotp
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, delete, select

from app.auth.dependencies.user import (
    get_current_user,
    get_current_user_responses,
)
from app.auth.models.totp import (
    Totp,
    TotpCreateParams,
    TotpDeleteParams,
    TotpRead,
    TotpRecoveryCode,
    TotpRecoveryCodes,
    TotpSecret,
    TotpVerifyParams,
)
from app.auth.models.user import User
from app.auth.routers.sessions import (
    credential_exception,
    credential_exception_responses,
)
from app.database import get_db
from app.utils import (
    get_current_time,
    get_or_404,
    get_or_404_responses,
)

router = APIRouter(
    prefix="/totp",
    responses={**get_current_user_responses},
)


@router.get(
    "",
    summary="Get current TOTP info",
    responses={**get_or_404_responses},
    operation_id="authTotpInfo",
)
def info(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> TotpRead:
    totp = get_or_404(db.get(Totp, user.id))
    return TotpRead(
        enabled=bool(totp.encrypted_secret),
        verified=not bool(totp.encrypted_secret_new),
    )


@router.post(
    "",
    summary="Create a new TOTP key",
    responses={**credential_exception_responses},
    operation_id="authTotpCreate",
)
def create(
    body: TotpCreateParams,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    current_time: Annotated[datetime, Depends(get_current_time)],
) -> TotpSecret:
    totp = db.exec(
        select(Totp).where(Totp.user_id == user.id).with_for_update(),
    ).one_or_none()
    if totp is None:
        if not user.verify_password(body.password):
            raise credential_exception
        totp = Totp(user_id=user.id)
    else:
        if not totp.verify_code(totp.encrypted_secret, body.code, current_time):
            raise credential_exception
    secret = pyotp.random_hex()
    totp.encrypted_secret_new = secret
    db.add(totp)
    db.commit()
    return TotpSecret(secret=secret)


@router.post(
    "/verify",
    summary="Verify TOTP info",
    responses={
        **get_or_404_responses,
        **credential_exception_responses,
    },
    operation_id="authTotpVerify",
)
def verify(
    body: TotpVerifyParams,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    current_time: Annotated[datetime, Depends(get_current_time)],
) -> TotpRecoveryCodes:
    totp = get_or_404(
        db.exec(
            select(Totp).where(Totp.user_id == user.id).with_for_update(),
        ).one_or_none(),
    )
    if not totp.verify_code(totp.encrypted_secret_new, body.code, current_time):
        raise credential_exception
    totp.encrypted_secret = totp.encrypted_secret_new
    totp.encrypted_secret_new = ""
    db.add(totp)
    db.flush()
    db.exec(
        delete(TotpRecoveryCode).where(TotpRecoveryCode.totp_user_id == user.id),
    )
    codes: list[str] = []
    for i in range(8):
        code = secrets.token_hex(8)
        codes.append(code)
        db.add(
            TotpRecoveryCode(
                totp_user_id=user.id,
                code_hash=hashlib.sha256(code.encode()).hexdigest(),
            ),
        )
    db.commit()
    return TotpRecoveryCodes(codes=codes)


@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        **get_or_404_responses,
        **credential_exception_responses,
    },
    summary="Delete current TOTP key",
    operation_id="authTotpDelete",
)
def totp_delete(
    body: TotpDeleteParams,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> None:
    totp = db.exec(
        select(Totp).where(Totp.user_id == user.id).with_for_update(),
    )
    if not totp.verify_code(totp.encrypted_secret_new, body.code):
        raise credential_exception
    db.delete(totp)
    db.commit()
