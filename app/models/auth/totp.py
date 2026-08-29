from datetime import datetime

from sqlmodel import Field, SQLModel

from app.types import TZDateTime


class TOTPRead(SQLModel):
    name: str
    verified: bool
    created_at: datetime = Field(sa_type=TZDateTime())


class TOTP(TOTPRead, table=True):
    __tablename__ = "auth_totp"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    encrypted_secret: bytes
