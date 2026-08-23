from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import Numeric
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator
from sqlmodel import DateTime


class HTTPExceptionResponse(BaseModel):
    detail: str


def create_http_exception_response(status_code: int, description: str):
    return {
        status_code: {
            "model": HTTPExceptionResponse,
            "description": description,
        },
    }


class TZDateTime(TypeDecorator):
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


class Currency(TypeDecorator):
    """
    Numerical type designed for storing currency values
    """

    impl = Numeric(precision=12, scale=2)
    cache_ok = True
