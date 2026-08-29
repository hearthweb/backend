from sqlalchemy import String
from sqlmodel import Field, Relationship, SQLModel

from app.auth.models.permission import Permission
from app.auth.models.rolepermissionlink import RolePermissionLink


class RoleRead(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(sa_type=String(40))
    description: str = Field(sa_type=String(255))


class Role(RoleRead, table=True):
    __tablename__ = "auth_role"

    permissions: list[Permission] = Relationship(
        link_model=RolePermissionLink,
    )
