from sqlmodel import Field, SQLModel


class RolePermissionLink(SQLModel, table=True):
    __tablename__ = "auth_rolepermissionlink"

    role_id: int | None = Field(
        default=None,
        foreign_key="role.id",
        primary_key=True,
    )
    permission_id: int | None = Field(
        default=None,
        foreign_key="permission.id",
        primary_key=True,
    )
