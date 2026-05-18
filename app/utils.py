from typing import TypeVar

from fastapi import HTTPException, status

get_or_404_responses = {
    404: {"description": "Object not found"},
}

T = TypeVar("T")


def get_or_404(obj: T | None) -> T:
    """
    Ensure that either an object was returned or an exception was raised
    """
    if obj is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Object not found",
        )
    return obj
