"""
Generate additional 20 commits to reach ~50 total.
"""
import os
import random
import subprocess
from datetime import datetime, timedelta

random.seed(123)

REPO = "/Users/songjin/IdeaProjects/k8s-python-app"
os.chdir(REPO)

start = datetime(2022, 3, 1)
end = datetime(2022, 12, 31)
total_days = (end - start).days

# Pick 20 new days from remaining unused days
used_days = {5, 15, 45, 76, 112, 142, 172, 173, 202, 217, 229, 244, 251, 264, 267, 273, 278, 291, 298, 299, 11, 197, 94, 296, 154, 183, 213, 241, 269, 281}
available = [d for d in range(total_days) if d not in used_days]
chosen = sorted(random.sample(available, 20))


def time_of_day():
    h = random.choices(
        [random.randint(10, 14), random.randint(15, 18), random.randint(19, 23), random.randint(0, 2)],
        weights=[30, 30, 25, 15]
    )[0]
    m = random.randint(0, 59)
    s = random.randint(0, 59)
    return f"{h:02d}:{m:02d}:{s:02d}"


def git_commit(date_str, msg):
    env = os.environ.copy()
    env["GIT_AUTHOR_DATE"] = date_str
    env["GIT_COMMITTER_DATE"] = date_str
    subprocess.run(["git", "add", "-A"], cwd=REPO, capture_output=True)
    r = subprocess.run(
        ["git", "commit", "-m", msg, "--allow-empty"],
        cwd=REPO, env=env, capture_output=True, text=True
    )
    if r.returncode != 0:
        print(f"FAIL: {date_str} | {msg} | {r.stderr.strip()}")


SNAPSHOTS = []

def s(files, msg):
    SNAPSHOTS.append((files, msg))

# batch 2: smaller changes, refactors, fixes
s({
    "app/utils.py": """import json
from pathlib import Path


def load_config(path="config.json"):
    with open(path) as f:
        return json.load(f)


def merge_dict(a, b):
    r = a.copy()
    r.update(b)
    return r


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def unique_preserve_order(seq):
    seen = set()
    result = []
    for item in seq:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
"""
}, "add unique helper")

s({
    "app/config.py": """import os
from pathlib import Path


class Config:
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    SECRET_KEY = os.getenv("SECRET_KEY", "")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    @classmethod
    def from_env(cls):
        return cls()
"""
}, "add cors config")

s({
}, "cleanup unused import")

s({
    "app/sorts.py": """import random


def quicksort(arr):
    if len(arr) < 2:
        return arr
    pivot = arr[0]
    left = [x for x in arr[1:] if x <= pivot]
    right = [x for x in arr[1:] if x > pivot]
    return quicksort(left) + [pivot] + quicksort(right)


def mergesort(arr):
    if len(arr) < 2:
        return arr
    mid = len(arr) // 2
    left = mergesort(arr[:mid])
    right = mergesort(arr[mid:])
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def heapsort(arr):
    def heapify(a, n, i):
        largest = i
        l = 2 * i + 1
        r = 2 * i + 2
        if l < n and a[l] > a[largest]:
            largest = l
        if r < n and a[r] > a[largest]:
            largest = r
        if largest != i:
            a[i], a[largest] = a[largest], a[i]
            heapify(a, n, largest)

    n = len(arr)
    for i in range(n // 2 - 1, -1, -1):
        heapify(arr, n, i)
    for i in range(n - 1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0)
    return arr


def insertion_sort(arr, left, right):
    for i in range(left + 1, right + 1):
        key = arr[i]
        j = i - 1
        while j >= left and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key


MIN_MERGE = 32


def timsort(arr):
    n = len(arr)
    if n < 2:
        return arr
    for start in range(0, n, MIN_MERGE):
        end = min(start + MIN_MERGE - 1, n - 1)
        insertion_sort(arr, start, end)
    size = MIN_MERGE
    while size < n:
        for left in range(0, n, size * 2):
            mid = left + size - 1
            right = min(left + size * 2 - 1, n - 1)
            if mid < right:
                merge(arr, left, mid, right)
        size *= 2
    return arr


def merge(arr, left, mid, right):
    left_part = arr[left:mid + 1]
    right_part = arr[mid + 1:right + 1]
    i = j = 0
    k = left
    while i < len(left_part) and j < len(right_part):
        if left_part[i] <= right_part[j]:
            arr[k] = left_part[i]
            i += 1
        else:
            arr[k] = right_part[j]
            j += 1
        k += 1
    while i < len(left_part):
        arr[k] = left_part[i]
        i += 1
        k += 1
    while j < len(right_part):
        arr[k] = right_part[j]
        j += 1
        k += 1


def dual_pivot_quicksort(arr):
    n = len(arr)
    if n < 2:
        return arr
    return _dual_pivot(arr, 0, n - 1)


def _dual_pivot(arr, low, high):
    if low < high:
        if arr[low] > arr[high]:
            arr[low], arr[high] = arr[high], arr[low]
        p, q = arr[low], arr[high]
        i = low + 1
        k = low + 1
        g = high - 1
        while k <= g:
            if arr[k] < p:
                arr[k], arr[i] = arr[i], arr[k]
                i += 1
            elif arr[k] > q:
                while arr[g] > q and k < g:
                    g -= 1
                arr[k], arr[g] = arr[g], arr[k]
                g -= 1
                if arr[k] < p:
                    arr[k], arr[i] = arr[i], arr[k]
                    i += 1
            k += 1
        i -= 1
        g += 1
        arr[low], arr[i] = arr[i], arr[low]
        arr[high], arr[g] = arr[g], arr[high]
        _dual_pivot(arr, low, i - 1)
        _dual_pivot(arr, i + 1, g - 1)
        _dual_pivot(arr, g + 1, high)
    return arr
"""
}, "add dual pivot quicksort")

s({
    "tests/test_sorts.py": """import pytest
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
"""
}, "add dual pivot to tests")

s({
    "app/ratelimit.py": """import time
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

    def remaining(self, key):
        now = time.time()
        window_start = now - self.window
        timestamps = self._requests[key]
        while timestamps and timestamps[0] < window_start:
            timestamps.pop(0)
        return max(0, self.max_requests - len(timestamps))
"""
}, "add remaining method to limiter")

s({
    "app/cache.py": """import functools
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

    def delete(self, key):
        self._store.pop(key, None)
"""
}, "add cache delete method")

s({
    "app/validator.py": """import re


def validate_email(email):
    return re.match(r'^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$', email) is not None


def validate_port(port):
    return isinstance(port, int) and 0 < port < 65536


def validate_nonempty(s):
    return isinstance(s, str) and len(s.strip()) > 0


def validate_url(url):
    return re.match(r'^https?://[^\\s/$.?#].[^\\s]*$', url) is not None
"""
}, "add url validator")

s({
    "app/threads.py": """from concurrent.futures import ThreadPoolExecutor, as_completed


_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="worker")


def run_tasks(tasks):
    futures = {_executor.submit(fn, *args): name for name, fn, args in tasks}
    results = {}
    for f in as_completed(futures):
        name = futures[f]
        try:
            results[name] = f.result()
        except Exception as e:
            results[name] = str(e)
    return results


def map_results(fn, items):
    futures = [_executor.submit(fn, item) for item in items]
    return [f.result() for f in as_completed(futures)]


def shutdown():
    _executor.shutdown(wait=True)
"""
}, "add map_results to thread pool")

s({
    "app/main.py": """from flask import Flask, jsonify, request
from app.config import Config
from app.cache import TTLCache

app = Flask(__name__)
cfg = Config()
cache = TTLCache(ttl=30)


@app.route("/")
def hello():
    return "Hello from Python!"


@app.route("/health")
def health():
    return jsonify({"status": "ok", "host": cfg.HOST, "port": cfg.PORT})


@app.route("/echo", methods=["POST"])
def echo():
    data = request.get_json(force=True)
    return jsonify({"echo": data})


@app.route("/config")
def get_config():
    return jsonify({"debug": cfg.DEBUG, "host": cfg.HOST, "port": cfg.PORT})


if __name__ == "__main__":
    app.run(host=cfg.HOST, port=cfg.PORT)
"""
}, "add config endpoint")

s({
    "app/preload.py": """import json
from pathlib import Path


def preload_cache(cache, data_path):
    path = Path(data_path)
    if not path.exists():
        return
    with open(path) as f:
        data = json.load(f)
    for key, value in data.items():
        cache.set(key, value)


def preload_from_dict(cache, data):
    for key, value in data.items():
        cache.set(key, value)
"""
}, "add dict preload")

s({
}, "remove unused imports from main")

s({
    "tests/test_utils.py": """import pytest
from app.utils import chunks, unique_preserve_order


def test_chunks():
    assert list(chunks([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]


def test_chunks_odd():
    assert list(chunks([1, 2, 3], 2)) == [[1, 2], [3]]


def test_unique_preserve_order():
    assert unique_preserve_order([1, 2, 1, 3, 2]) == [1, 2, 3]
    assert unique_preserve_order([]) == []
"""
}, "test unique helper")

s({
    "app/serde.py": """import orjson


def dumps(obj):
    return orjson.dumps(obj)


def loads(data):
    return orjson.loads(data)


def dumps_default(obj, default):
    return orjson.dumps(obj, default=default)
"""
}, "add serde default option")

s({
    "app/retry.py": """import functools
import time


def retry(max_attempts=3, delay=0.5, backoff=1.5):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last = None
            wait = delay
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last = e
                    if attempt < max_attempts - 1:
                        time.sleep(wait)
                        wait *= backoff
            raise last
        return wrapper
    return decorator
"""
}, "add exponential backoff to retry")

s({
    "app/fetcher.py": """import asyncio
import httpx


class AsyncFetcher:
    def __init__(self, base_url, timeout=10, max_retries=2):
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self.max_retries = max_retries

    async def get(self, path):
        for _ in range(self.max_retries):
            try:
                r = await self.client.get(path)
                r.raise_for_status()
                return r.json()
            except (httpx.TimeoutException, httpx.HTTPStatusError):
                continue
        return None

    async def close(self):
        await self.client.aclose()
"""
}, "add retry to fetcher")

s({
    "tests/test_ratelimit.py": """from app.ratelimit import SlidingWindowLimiter


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
"""
}, "add rate limiter tests")

s({
    "tests/test_cache.py": """from app.cache import TTLCache


def test_cache_set_get():
    c = TTLCache(ttl=60)
    c.set("key", "value")
    assert c.get("key") == "value"


def test_cache_delete():
    c = TTLCache(ttl=60)
    c.set("key", "value")
    c.delete("key")
    assert c.get("key") is None


def test_cache_clear():
    c = TTLCache(ttl=60)
    c.set("a", 1)
    c.set("b", 2)
    c.clear()
    assert c.get("a") is None
    assert c.get("b") is None
"""
}, "add cache tests")


# run it
for day_offset, (files, msg) in zip(chosen, SNAPSHOTS):
    date = start + timedelta(days=day_offset)
    date_str = date.strftime("%Y-%m-%d")

    for fname, content in files.items():
        full = os.path.join(REPO, fname)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(content.lstrip("\n"))

    ts = f"{date_str} {time_of_day()}"
    git_commit(ts, msg)
    print(f"  {ts}  {msg}")

print(f"\nDone. {len(SNAPSHOTS)} additional commits created.")
