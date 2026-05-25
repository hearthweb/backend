from operator import itemgetter
from typing import Any, List, TypeVar

from pydantic import BaseModel

DictT = TypeVar("DictT", bound=dict)


def compare_sorted(l1: List[DictT], l2: List[DictT], key: str) -> bool:
    """
    Compare two lists by sorting them using a key
    """
    key_fn = itemgetter(key)
    return sorted(l1, key=key_fn) == sorted(l2, key=key_fn)


ModelT = TypeVar("ModelT", bound=BaseModel)


def dump(model: type[ModelT], obj: Any) -> dict[str, Any]:
    return model.model_validate(obj).model_dump(mode="json")
