from sqlalchemy import String
from sqlmodel import Field, SQLModel


class CredentialWrite(SQLModel):
    service: str = Field(sa_type=String(255))
    username_or_email: str = Field(
        default="",
        sa_type=String(255),
    )
    password: str = Field(
        default="",
        sa_type=String(255),
    )


class CredentialRead(CredentialWrite):
    id: int | None = Field(default=None, primary_key=True)


class Credential(CredentialRead, table=True):
    __tablename__ = "registry_credential"
