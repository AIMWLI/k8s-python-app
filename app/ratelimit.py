import time
from collections import defaultdict, deque
from typing import DefaultDict, Deque


class SlidingWindowLimiter:
    """
    O(1) sliding window limit implementation using deque for fast pops.
    """
    __slots__ = ("max_requests", "window", "_requests")

    def __init__(self, max_requests: int = 60, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self._requests: DefaultDict[str, Deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.time()
        window_start = now - self.window
        timestamps = self._requests[key]
        
        while timestamps and timestamps[0] < window_start:
            timestamps.popleft() # O(1) compared to list.pop(0) which is O(N)
            
        if len(timestamps) >= self.max_requests:
            return False
            
        timestamps.append(now)
        return True

    def remaining(self, key: str) -> int:
        now = time.time()
        window_start = now - self.window
        timestamps = self._requests[key]
        
        while timestamps and timestamps[0] < window_start:
            timestamps.popleft()
            
        return max(0, self.max_requests - len(timestamps))
