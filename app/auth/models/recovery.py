from sqlalchemy import String
from sqlmodel import Field, SQLModel


class Recovery(SQLModel, table=True):
    __tablename__ = "auth_recovery"

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(
        foreign_key="auth_user.id",
        index=True,
    )
    code_hash: str = Field(sa_type=String(255))
