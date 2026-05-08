from typing import TypeVar, Iterable, List, Generator
from pathlib import Path
import orjson

T = TypeVar("T")

def load_config(path: str = "config.json") -> dict:
    p = Path(path)
    if not p.exists():
        return {}
    return orjson.loads(p.read_bytes())

def merge_dict(a: dict, b: dict) -> dict:
    r = a.copy()
    r.update(b)
    return r

def chunks(lst: List[T], n: int) -> Generator[List[T], None, None]:
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def unique_preserve_order(seq: Iterable[T]) -> List[T]:
    # Constraint: 去重查询强制用 set/dict. O(1) dictated dict.fromkeys which maintains order.
    return list(dict.fromkeys(seq))
