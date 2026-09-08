from datetime import datetime

import pyotp
from cryptography.fernet import Fernet
from sqlalchemy import String
from sqlmodel import Field, SQLModel

from app.config import settings


class Totp(SQLModel, table=True):
    __tablename__ = "auth_totp"

    user_id: int = Field(
        primary_key=True,
        foreign_key="auth_user.id",
        unique=True,
        index=True,
    )
    encrypted_secret: str = Field(
        default="",
        sa_type=String(140),
    )
    encrypted_secret_new: str = Field(
        default="",
        sa_type=String(140),
    )
    last_code: str = Field(
        default="",
        sa_type=String(6),
    )

    @staticmethod
    def _fernet() -> Fernet:
        return Fernet(settings.TOTP_ENCRYPTION_KEY.encode())

    @classmethod
    def _totp(cls, encrypted_secret: str) -> pyotp.TOTP:
        return pyotp.TOTP(cls._fernet().decrypt(encrypted_secret).decode())

    @classmethod
    def verify_code(
        cls,
        encrypted_secret: str,
        code: str,
        current_time: datetime,
    ) -> bool:
        return cls._totp(encrypted_secret).verify(code, current_time)

    def set_secret(self, secret: str) -> None:
        self.encrypted_secret_new = self._fernet().encrypt(secret.encode()).decode()


class TotpRecoveryCode(SQLModel, table=True):
    __tablenme__ = "auth_totprecoverycode"

    id: int | None = Field(default=None, primary_key=True)
    totp_user_id: int = Field(
        foreign_key="auth_totp.user_id",
        ondelete="CASCADE",
        index=True,
    )
    code_hash: str = Field(sa_type=String(64))


class TotpRead(SQLModel):
    enabled: bool
    verified: bool


class TotpCreateParams(SQLModel):
    password: str = ""
    code: str = ""


class TotpSecret(SQLModel):
    secret: str


class TotpVerifyParams(SQLModel):
    code: str


class TotpRecoveryCodes(SQLModel):
    codes: list[str]
