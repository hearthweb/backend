from sqlalchemy import String
from sqlmodel import Field

from .base import Base


class UserBase(Base):
    email: str = Field(
        sa_type=String(255),
        unique=True,
        index=True,
    )
    first_name: str = Field(
        sa_type=String(100),
    )
    last_name: str = Field(
        sa_type=String(100),
    )


class UserRead(UserBase):
    id: int
    is_admin: bool


class UserCreateEdit(UserBase):
    password: str = Field()


class UserCreateEditAdmin(UserCreateEdit):
    is_admin: bool = Field(
        default=False,
    )


class User(UserBase, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    hashed_password: str = Field(
        sa_type=String(60),
    )
    is_admin: bool = Field(
        default=False,
    )
