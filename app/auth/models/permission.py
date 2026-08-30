from sqlmodel import SQLModel


class Permission(SQLModel):
    name: str
    description: str
