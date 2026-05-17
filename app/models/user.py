import bcrypt
from sqlalchemy import String
from sqlmodel import Field

from .base import Base


class UserBase(Base):
    username: str = Field(
        sa_type=String(100),
        unique=True,
        index=True,
    )
    email: str = Field(
        sa_type=String(255),
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

    def set_password(self, password: str) -> None:
        """
        Compute and set the hashed password with the supplied password
        """
        self.hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

    def verify_password(self, password: str) -> bool:
        """
        Verify that the supplied password matches the one stored for the user
        """
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.hashed_password,
        )
