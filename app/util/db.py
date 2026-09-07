from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import Numeric
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator
from sqlmodel import DateTime


class Currency(TypeDecorator):
    """
    Numerical type designed for storing currency values
    """

    impl = Numeric(precision=12, scale=2)
    cache_ok = True


class TZDateTime(TypeDecorator):
    """
    Timezone-aware type for SQLite
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_result_value(
        self,
        value: datetime | None,
        dialect: Dialect,
    ) -> datetime:
        if value is not None and dialect.name == "sqlite":
            return value.replace(tzinfo=UTC)
        return value


get_or_404_responses = {
    404: {"description": "Object not found"},
}


def get_or_404[T](obj: T | None) -> T:
    """
    Ensure that either an object was returned or an exception was raised
    """
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Object not found",
        )
    return obj
