"""滑动窗口限流器 — O(1) deque 实现，线程安全。"""
from __future__ import annotations

import time
from collections import defaultdict, deque


class SlidingWindowLimiter:
    """基于 deque 的滑动窗口限流，popleft O(1)。"""
    __slots__ = ("max_requests", "window", "_requests")

    def __init__(self, max_requests: int = 60, window: int = 60) -> None:
        self.max_requests = max_requests
        self.window = window
        self._requests: defaultdict[str, deque[float]] = defaultdict(deque)

    def _evict(self, key: str, now: float) -> deque[float]:
        """清除过期时间戳，返回当前窗口内的 deque。"""
        window_start = now - self.window
        timestamps = self._requests[key]
        while timestamps and timestamps[0] < window_start:
            timestamps.popleft()
        return timestamps

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        timestamps = self._evict(key, now)
        if len(timestamps) >= self.max_requests:
            return False
        timestamps.append(now)
        return True

    def remaining(self, key: str) -> int:
        now = time.monotonic()
        timestamps = self._evict(key, now)
        return max(0, self.max_requests - len(timestamps))
