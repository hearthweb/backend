from sqlmodel import Field, SQLModel


class UserRoleLink(SQLModel, table=True):
    __tablename__ = "auth_userrolelink"

    user_id: int | None = Field(
        default=None,
        foreign_key="auth_user.id",
        primary_key=True,
    )
    role_id: int | None = Field(
        default=None,
        foreign_key="auth_role.id",
        primary_key=True,
    )
