from sqlalchemy import String
from sqlmodel import Field, SQLModel


class PermissionRead(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_type=String(40))
    description: str = Field(sa_type=String(255))


class Permission(PermissionRead, table=True):
    __tablename__ = "auth_permission"
