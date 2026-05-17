from datetime import datetime

from sqlalchemy import DateTime, func
from sqlmodel import Field, SQLModel


class Base(SQLModel):
    created_at: datetime = Field(
        nullable=False,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "server_default": func.now(),
        },
    )
    updated_at: datetime = Field(
        nullable=False,
        sa_type=DateTime(timezone=True),
        sa_column_kwargs={
            "onupdate": func.now(),
            "server_default": func.now(),
        },
    )
