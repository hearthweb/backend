import secrets
from datetime import datetime

from sqlmodel import Field, Relationship, SQLModel

from app.models.user import User


def generate_id() -> str:
    return secrets.token_hex(32)


class LoginSession(SQLModel, table=True):
    id: str = Field(
        default_factory=generate_id,
        primary_key=True,
    )
    user_id: int = Field(foreign_key="user.id")
    user: User | None = Relationship()
    expires: datetime
