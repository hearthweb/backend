from pwdlib import PasswordHash
from sqlalchemy import String
from sqlmodel import Field, SQLModel

from app.models.base import Base

password_hash = PasswordHash.recommended()


class UserLogin(SQLModel):
    email: str
    password: str


class UserBase(SQLModel):
    email: str = Field(
        sa_type=String(255),
        unique=True,
        index=True,
    )
    first_name: str = Field(
        default="",
        sa_type=String(100),
    )
    last_name: str = Field(
        default="",
        sa_type=String(100),
    )


class UserAdmin(SQLModel):
    is_admin: bool = Field(
        default=False,
    )


class UserRead(Base, UserBase, UserAdmin):
    pass


class UserCreateEdit(UserBase):
    password: str = Field()


class UserCreateEditAdmin(UserAdmin, UserCreateEdit):
    is_admin: bool = Field(
        default=False,
    )


class User(Base, UserBase, UserAdmin, table=True):
    hashed_password: str = Field(
        default="",
        sa_type=String(255),
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
        """
        Perform a "dummy" password verification to prevent timing attacks
        """
        password_hash.verify(
            password,
            "$argon2id$v=19$m=65536,t=3,p=4$MJd"
            + "zkCbYMPYw31MI+n24Zg$4steBPCprRmI"
            + "jkaUBeC+yPxXRTU5p0GAarRLjQvYvs4",
        )
