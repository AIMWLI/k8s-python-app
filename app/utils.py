"""通用工具函数 — 极简、高内聚、O(1) 约束。"""
from __future__ import annotations

from typing import Generator, Iterable, TypeVar

T = TypeVar("T")


def chunks(lst: list[T], n: int) -> Generator[list[T], None, None]:
    """将列表按固定大小分块，生成器惰性输出。"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def unique_preserve_order(seq: Iterable[T]) -> list[T]:
    """去重并保持原始顺序 — dict.fromkeys 保证 O(1) 查找。"""
    return list(dict.fromkeys(seq))
