import pytest
from app.sorts import quicksort, mergesort, heapsort, timsort, dual_pivot_quicksort


cases = [
    ([], []),
    ([1], [1]),
    ([3, 1, 2], [1, 2, 3]),
    ([5, 5, 5], [5, 5, 5]),
    ([9, 8, 7, 6], [6, 7, 8, 9]),
    ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
    ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
]


@pytest.mark.parametrize("sort_fn", [quicksort, mergesort, heapsort, timsort, dual_pivot_quicksort])
def test_sorts(sort_fn):
    for inp, expected in cases:
        assert sort_fn(inp[:]) == expected
