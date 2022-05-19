import pytest
from app.utils import chunks


def test_chunks():
    assert list(chunks([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]


def test_chunks_odd():
    assert list(chunks([1, 2, 3], 2)) == [[1, 2], [3]]
