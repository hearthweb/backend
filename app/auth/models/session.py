import secrets
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from app.auth.models.user import User
from app.types import TZDateTime


def generate_id() -> str:
    return secrets.token_hex(32)


class Session(SQLModel, table=True):
    __tablename__ = "auth_session"

    id: str = Field(
        default_factory=generate_id,
        primary_key=True,
    )
    user_id: int = Field(
        foreign_key="auth_user.id",
        ondelete="CASCADE",
        index=True,
    )
    user: User = Relationship()
    user_agent: str
    completed: bool = Field(default=False)
    expires: datetime = Field(sa_type=TZDateTime())


class SessionLogin(SQLModel):
    email: str
    password: str


class SessionLoginTotp(SQLModel):
    code: str
