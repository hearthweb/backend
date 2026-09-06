from datetime import UTC, datetime

from fastapi import HTTPException, status


def get_current_time() -> datetime:
    return datetime.now(tz=UTC)


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
