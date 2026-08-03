from sqlalchemy import String
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import Base
from app.models.user import User


class CredentialCreateEdit(SQLModel):
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


class Credential(Base, CredentialCreateEdit, table=True):
    user_id: int = Field(foreign_key="user.id")
    user: User | None = Relationship()
