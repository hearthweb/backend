from operator import itemgetter
from typing import Any

from pydantic import BaseModel


def compare_sorted[T: dict](l1: list[T], l2: list[T], key: str) -> bool:
    """
    Compare two lists by sorting them using a key
    """
    key_fn = itemgetter(key)
    return sorted(l1, key=key_fn) == sorted(l2, key=key_fn)


def dump[T: BaseModel](model: type[T], obj: Any) -> dict[str, Any]:
    return model.model_validate(obj).model_dump(mode="json")
