from sqlmodel import Field, SQLModel


class Totp(SQLModel, table=True):
    __tablename__ = "auth_totp"

    user_id: int = Field(
        primary_key=True,
        foreign_key="auth_user.id",
        unique=True,
        index=True,
    )
    encrypted_secret: bytes
    verified: bool
