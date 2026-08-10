from datetime import datetime

from sqlmodel import Field, SQLModel, func

from app.types import TZDateTime


class Base(SQLModel):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    created_at: datetime = Field(
        default=None,
        sa_type=TZDateTime(),
        sa_column_kwargs={
            "server_default": func.now(),
        },
    )
    updated_at: datetime = Field(
        default=None,
        sa_type=TZDateTime(),
        sa_column_kwargs={
            "onupdate": func.now(),
            "server_default": func.now(),
        },
    )
