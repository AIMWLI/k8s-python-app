import pytest
from app.utils import chunks, unique_preserve_order


def test_chunks():
    assert list(chunks([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]


def test_chunks_odd():
    assert list(chunks([1, 2, 3], 2)) == [[1, 2], [3]]


def test_unique_preserve_order():
    assert unique_preserve_order([1, 2, 1, 3, 2]) == [1, 2, 3]
    assert unique_preserve_order([]) == []
