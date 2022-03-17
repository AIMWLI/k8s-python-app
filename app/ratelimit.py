import time
from collections import defaultdict


class SlidingWindowLimiter:
    def __init__(self, max_requests=60, window=60):
        self.max_requests = max_requests
        self.window = window
        self._requests = defaultdict(list)

    def allow(self, key):
        now = time.time()
        window_start = now - self.window
        timestamps = self._requests[key]
        while timestamps and timestamps[0] < window_start:
            timestamps.pop(0)
        if len(timestamps) >= self.max_requests:
            return False
        timestamps.append(now)
        return True
