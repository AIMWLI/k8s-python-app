from app.utils import chunks, unique_preserve_order


def test_chunks_even() -> None:
    assert list(chunks([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]


def test_chunks_odd() -> None:
    assert list(chunks([1, 2, 3], 2)) == [[1, 2], [3]]


def test_chunks_empty() -> None:
    assert list(chunks([], 3)) == []


def test_unique_preserve_order() -> None:
    assert unique_preserve_order([1, 2, 1, 3, 2]) == [1, 2, 3]


def test_unique_empty() -> None:
    assert unique_preserve_order([]) == []
