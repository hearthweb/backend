from datetime import date

from pwdlib import PasswordHash
from sqlalchemy import Date, String
from sqlmodel import Field, SQLModel

password_hash = PasswordHash.recommended()


class UserWrite(SQLModel):
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
    birthday: date | None = Field(
        default=None,
        sa_type=Date,
    )


class UserCreate(UserWrite):
    password: str


class UserRead(UserWrite):
    id: int | None = Field(default=None, primary_key=True)


class User(UserRead, table=True):
    __tablename__ = "auth_user"

    hashed_password: str = Field(
        default="",
        sa_type=String(255),
    )

    def set_password(self, password: str) -> None:
        self.hashed_password = password_hash.hash(password)

    def verify_password(self, password: str) -> bool:
        return password_hash.verify(password, self.hashed_password)

    @staticmethod
    def dummy_verify_password(password: str) -> None:
        password_hash.verify(
            password,
            "$argon2id$v=19$m=65536,t=3,p=4$MJd"
            + "zkCbYMPYw31MI+n24Zg$4steBPCprRmI"
            + "jkaUBeC+yPxXRTU5p0GAarRLjQvYvs4",
        )


class UserLogin(SQLModel):
    email: str
    password: str
