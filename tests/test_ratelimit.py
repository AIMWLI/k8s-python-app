from app.ratelimit import SlidingWindowLimiter


def test_allow_within_limit() -> None:
    limiter = SlidingWindowLimiter(max_requests=5, window=60)
    for _ in range(5):
        assert limiter.allow("test")
    assert not limiter.allow("test")


def test_remaining_decrements() -> None:
    limiter = SlidingWindowLimiter(max_requests=10, window=60)
    assert limiter.remaining("test") == 10
    limiter.allow("test")
    assert limiter.remaining("test") == 9


def test_independent_keys() -> None:
    limiter = SlidingWindowLimiter(max_requests=2, window=60)
    limiter.allow("a")
    limiter.allow("a")
    assert not limiter.allow("a")
    assert limiter.allow("b")
