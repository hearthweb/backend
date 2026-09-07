import hashlib
import secrets
from datetime import datetime
from typing import Annotated

import pyotp
from fastapi import APIRouter, Depends, status
from sqlmodel import Session, delete, select

from app.auth.dependencies.session import (
    get_login_session_completed,
    get_login_session_completed_responses,
)
from app.auth.models.session import Session as AuthSession
from app.auth.models.totp import (
    Totp,
    TotpCreateParams,
    TotpRead,
    TotpRecoveryCode,
    TotpRecoveryCodes,
    TotpSecret,
    TotpVerifyParams,
)
from app.auth.routers.sessions import (
    credential_exception,
    credential_exception_responses,
)
from app.common.db import (
    get_or_404,
    get_or_404_responses,
)
from app.common.time import get_current_time
from app.database import get_db

router = APIRouter(
    prefix="/totp",
    responses={**get_login_session_completed_responses},
)


@router.get(
    "",
    summary="Get current TOTP info",
    responses={**get_or_404_responses},
    operation_id="authTotpInfo",
)
def info(
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[AuthSession, Depends(get_login_session_completed)],
) -> TotpRead:
    totp = get_or_404(db.get(Totp, session.user_id))
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
    session: Annotated[AuthSession, Depends(get_login_session_completed)],
    current_time: Annotated[datetime, Depends(get_current_time)],
) -> TotpSecret:
    totp = db.exec(
        select(Totp).where(Totp.user_id == session.user_id).with_for_update(),
    ).one_or_none()
    if totp is None:
        if not session.user.verify_password(body.password):
            raise credential_exception
        totp = Totp(user_id=session.user_id)
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
    session: Annotated[AuthSession, Depends(get_login_session_completed)],
    current_time: Annotated[datetime, Depends(get_current_time)],
) -> TotpRecoveryCodes:
    totp = get_or_404(
        db.exec(
            select(Totp).where(Totp.user_id == session.user_id).with_for_update(),
        ).one_or_none(),
    )
    if not totp.verify_code(totp.encrypted_secret_new, body.code, current_time):
        raise credential_exception
    totp.encrypted_secret = totp.encrypted_secret_new
    totp.encrypted_secret_new = ""
    db.add(totp)
    db.exec(
        delete(TotpRecoveryCode).where(
            TotpRecoveryCode.totp_user_id == session.user_id
        ),
    )
    codes: list[str] = []
    for _ in range(8):
        code = secrets.token_hex(8)
        codes.append(code)
        db.add(
            TotpRecoveryCode(
                totp_user_id=session.user_id,
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
    db: Annotated[Session, Depends(get_db)],
    session: Annotated[AuthSession, Depends(get_login_session_completed)],
    current_time: Annotated[datetime, Depends(get_current_time)],
    code: str,
) -> None:
    totp = get_or_404(
        db.exec(
            select(Totp).where(Totp.user_id == session.user_id).with_for_update(),
        ).one_or_none(),
    )
    if not totp.verify_code(totp.encrypted_secret, code, current_time):
        raise credential_exception
    db.delete(totp)
    db.commit()
