from datetime import UTC, datetime

from sqlmodel import Field, SQLModel, func

from app.types import TZDateTime


def zero() -> datetime:
    return datetime.fromtimestamp(0, tz=UTC)


class Base(SQLModel):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    created_at: datetime = Field(
        default_factory=zero,
        sa_type=TZDateTime(),
        sa_column_kwargs={
            "server_default": func.now(),
        },
    )
    updated_at: datetime = Field(
        default_factory=zero,
        sa_type=TZDateTime(),
        sa_column_kwargs={
            "onupdate": func.now(),
            "server_default": func.now(),
        },
    )
