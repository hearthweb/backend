from operator import itemgetter
from typing import List, TypeVar

T = TypeVar("T")


def compare_sorted(l1: List[T], l2: List[T], key: str) -> bool:
    """
    Compare two lists by sorting them using a key
    """
    key_fn = itemgetter(key)
    return sorted(l1, key=key_fn) == sorted(l2, key=key_fn)
