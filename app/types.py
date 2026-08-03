from datetime import UTC, datetime

from pydantic import BaseModel
from sqlalchemy import types
from sqlalchemy.engine import Dialect
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


class TZDateTime(types.TypeDecorator):
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
