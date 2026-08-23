from datetime import datetime
from pathlib import Path

from sqlalchemy import BigInteger, String
from sqlmodel import Field, Relationship, SQLModel, func

from app.config import settings
from app.models.document.category import Category, CategoryRead
from app.types import TZDateTime


class DocumentWrite(SQLModel):
    name: str = Field(sa_type=String(255))
    category_id: int = Field(
        foreign_key="document_category.id",
        index=True,
    )


class DocumentRead(DocumentWrite):
    id: int | None = Field(default=None, primary_key=True)
    date: datetime = Field(
        default=None,
        sa_type=TZDateTime(),
        sa_column_kwargs={
            "server_default": func.now(),
        },
    )

    filename: str = Field(sa_type=String(255))
    filesize: int = Field(sa_type=BigInteger())
    filetype: str = Field(sa_type=String(100))


class Document(DocumentRead, table=True):
    __tablename__ = "document_document"

    category: Category = Relationship()

    @property
    def absolute_path(self) -> str:
        return str(Path(settings.UPLOAD_DIR) / "documents" / str(self.id))


class DocumentPublic(DocumentRead):
    category: CategoryRead
