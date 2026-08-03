from sqlalchemy import String
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import Base
from app.models.user import User, UserRead


class CredentialBase(SQLModel):
    service: str = Field(
        sa_type=String(255),
    )
    username_or_email: str = Field(
        default="",
        sa_type=String(255),
    )
    password: str = Field(
        default="",
        sa_type=String(255),
    )


class CredentialRead(Base, CredentialBase):
    user_id: int = Field(foreign_key="user.id")


class Credential(CredentialRead, table=True):
    user: User | None = Relationship()


class CredentialPublic(CredentialRead):
    user: UserRead | None = None
