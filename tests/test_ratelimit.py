from app.ratelimit import SlidingWindowLimiter


def test_allow():
    limiter = SlidingWindowLimiter(max_requests=5, window=60)
    for _ in range(5):
        assert limiter.allow("test")
    assert not limiter.allow("test")


def test_remaining():
    limiter = SlidingWindowLimiter(max_requests=10, window=60)
    assert limiter.remaining("test") == 10
    limiter.allow("test")
    assert limiter.remaining("test") == 9
