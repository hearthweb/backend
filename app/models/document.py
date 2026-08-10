from sqlalchemy import BigInteger, String
from sqlmodel import Field, Relationship, SQLModel

from app.models.base import Base


class DocumentCategoryCreateEdit(SQLModel):
    name: str = Field(
        sa_type=String(100),
    )


class DocumentCategory(Base, DocumentCategoryCreateEdit, table=True):
    pass


class DocumentCreateEdit(SQLModel):
    name: str = Field(
        sa_type=String(255),
    )
    category_id: int = Field(
        foreign_key="documentcategory.id",
        index=True,
    )


class DocumentRead(Base, DocumentCreateEdit):
    filename: str = Field(
        sa_type=String(255),
    )
    filesize: int = Field(
        sa_type=BigInteger(),
    )
    filetype: str = Field(
        sa_type=String(100),
    )


class Document(DocumentRead, table=True):
    category: DocumentCategory = Relationship()


class DocumentPublic(DocumentRead):
    category: DocumentCategory
