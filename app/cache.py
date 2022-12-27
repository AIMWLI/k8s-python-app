import functools
import time


class TTLCache:
    def __init__(self, ttl=60):
        self._store = {}
        self._ttl = ttl

    def get(self, key):
        if key in self._store:
            val, ts = self._store[key]
            if time.time() - ts < self._ttl:
                return val
            del self._store[key]
        return None

    def set(self, key, value):
        self._store[key] = (value, time.time())

    def clear(self):
        self._store.clear()
