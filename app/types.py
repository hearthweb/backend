from datetime import datetime, timezone

from sqlalchemy import types
from sqlalchemy.engine import Dialect
from sqlmodel import DateTime


class TZDateTime(types.TypeDecorator):
    impl = DateTime(timezone=True)
    cache_ok = True

    def process_result_value(
        self,
        value: datetime | None,
        dialect: Dialect,
    ) -> datetime:
        if value is not None and dialect.name == "sqlite":
            return value.replace(tzinfo=timezone.utc)
        return value
