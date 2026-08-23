from sqlalchemy import String
from sqlmodel import Field, SQLModel


class CategoryWrite(SQLModel):
    name: str = Field(sa_type=String(100))


class CategoryRead(CategoryWrite):
    id: int | None = Field(default=None, primary_key=True)


class Category(CategoryRead, table=True):
    __tablename__ = "registry_category"
