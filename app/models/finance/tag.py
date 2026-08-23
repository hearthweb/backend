from sqlalchemy import String
from sqlmodel import Field, SQLModel


class TagWrite(SQLModel):
    name: str = Field(sa_type=String(40))
    color: str = Field(default="000000", sa_type=String(6))


class TagRead(TagWrite):
    id: int | None = Field(default=None, primary_key=True)


class Tag(TagRead, table=True):
    pass
