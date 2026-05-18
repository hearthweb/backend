from pwdlib import PasswordHash
from sqlalchemy import String
from sqlmodel import Field

from app.models.base import Base

password_hash = PasswordHash.recommended()


class UserBase(Base):
    username: str = Field(
        sa_type=String(100),
        unique=True,
        index=True,
    )
    email: str = Field(
        default="",
        sa_type=String(255),
    )
    first_name: str = Field(
        default="",
        sa_type=String(100),
    )
    last_name: str = Field(
        default="",
        sa_type=String(100),
    )


class UserRead(UserBase):
    id: int
    is_admin: bool
    is_active: bool


class UserCreateEdit(UserBase):
    password: str = Field()


class UserCreateEditAdmin(UserCreateEdit):
    is_admin: bool = Field(
        default=False,
    )
    is_active: bool = Field(
        default=True,
    )


class User(UserBase, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    hashed_password: str = Field(
        sa_type=String(255),
    )
    is_admin: bool = Field(
        default=False,
    )
    is_active: bool = Field(
        default=True,
    )

    def set_password(self, password: str) -> None:
        """
        Compute and set the hashed password with the supplied password
        """
        self.hashed_password = password_hash.hash(password)

    def verify_password(self, password: str) -> bool:
        """
        Verify that the supplied password matches the one stored for the user
        """
        return password_hash.verify(password, self.hashed_password)

    @staticmethod
    def dummy_verify_password(password: str) -> None:
        password_hash.verify(
            password,
            "$argon2id$v=19$m=65536,t=3,p=4$MJd"
            + "zkCbYMPYw31MI+n24Zg$4steBPCprRmI"
            + "jkaUBeC+yPxXRTU5p0GAarRLjQvYvs4",
        )
