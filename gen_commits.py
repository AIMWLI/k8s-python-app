"""
Generate ~50 historical git commits for contribution graph.
Run: python gen_commits.py
"""
import os
import random
import subprocess
from datetime import datetime, timedelta

random.seed(42)

REPO = "/Users/songjin/IdeaProjects/k8s-python-app"
os.chdir(REPO)

# === Date config: March 2022 - December 2022 ===
start = datetime(2022, 3, 1)
end = datetime(2022, 12, 31)
total_days = (end - start).days

# Pick ~35 days with >=1 commits, total ~50 commits
num_days = 35
chosen_days = sorted(random.sample(range(total_days), num_days))

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

# === Python code snippets ===
def make_py(filename, body):
    path = os.path.join(REPO, filename)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(body.lstrip("\n"))

def read_py(filename):
    path = os.path.join(REPO, filename)
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return None

def append_py(filename, lines):
    path = os.path.join(REPO, filename)
    with open(path, "a") as f:
        f.write("\n" + lines.lstrip("\n"))

# === Snapshot-based generation: each commit is a self-contained batch ===
SNAPSHOTS = []

def s(files, msg):
    SNAPSHOTS.append((files, msg))

# --- Snapshot 1: init utils ---
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
"""
}, "add utils module")

# --- Snapshot 2: config ---
s({
    "app/config.py": """import os


class Config:
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
"""
}, "add config module")

# --- Snapshot 3: extend main ---
s({
    "app/main.py": """from flask import Flask, jsonify, request
from app.config import Config

app = Flask(__name__)
cfg = Config()


@app.route("/")
def hello():
    return "Hello from Python!"


@app.route("/health")
def health():
    return jsonify({"status": "ok", "host": cfg.HOST})


if __name__ == "__main__":
    app.run(host=cfg.HOST, port=cfg.PORT)
"""
}, "update main with config and health endpoint")

# --- Snapshot 4: threadpool demo ---
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


def shutdown():
    _executor.shutdown(wait=True)
"""
}, "add thread pool executor")

# --- Snapshot 5: sort utils ---
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
"""
}, "add sort algorithms")

# --- Snapshot 6: test sorts ---
s({
    "tests/test_sorts.py": """import pytest
from app.sorts import quicksort, mergesort, heapsort


cases = [
    ([], []),
    ([1], [1]),
    ([3, 1, 2], [1, 2, 3]),
    ([5, 5, 5], [5, 5, 5]),
    ([9, 8, 7, 6], [6, 7, 8, 9]),
    ([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]),
    ([5, 4, 3, 2, 1], [1, 2, 3, 4, 5]),
]


@pytest.mark.parametrize("sort_fn", [quicksort, mergesort, heapsort])
def test_sorts(sort_fn):
    for inp, expected in cases:
        assert sort_fn(inp[:]) == expected
"""
}, "add sort tests")

# --- Snapshot 7: async fetch ---
s({
    "app/fetcher.py": """import asyncio
import httpx


class AsyncFetcher:
    def __init__(self, base_url, timeout=10):
        self.client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    async def get(self, path):
        r = await self.client.get(path)
        r.raise_for_status()
        return r.json()

    async def close(self):
        await self.client.aclose()
"""
}, "add async http fetcher")

# --- Snapshot 8: retry decorator ---
s({
    "app/retry.py": """import functools
import time


def retry(max_attempts=3, delay=0.5):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last = None
            for _ in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last = e
                    time.sleep(delay)
            raise last
        return wrapper
    return decorator
"""
}, "add retry decorator")

# --- Snapshot 9: cache util ---
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
"""
}, "add ttl cache")

# --- Snapshot 10: update main add routes ---
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


if __name__ == "__main__":
    app.run(host=cfg.HOST, port=cfg.PORT)
"""
}, "add echo route and cache integration")

# --- Snapshot 11: timsort ---
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
"""
}, "add timsort implementation")

# --- Snapshot 12: rate limiter ---
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
"""
}, "add rate limiter")

# --- Snapshot 13: validator ---
s({
    "app/validator.py": """import re


def validate_email(email):
    return re.match(r'^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$', email) is not None


def validate_port(port):
    return isinstance(port, int) and 0 < port < 65536


def validate_nonempty(s):
    return isinstance(s, str) and len(s.strip()) > 0
"""
}, "add validator utils")

# --- Snapshot 14: update requirements ---
s({
    "app/requirements.txt": """flask==2.2.2
httpx==0.23.0
pytest==7.1.2
gunicorn==20.1.0
orjson==3.7.2
"""
}, "update requirements")

# --- Snapshot 15: concurrency demo ---
s({
    "app/concurrency.py": """import asyncio
import httpx


async def fetch_all(urls, max_concurrent=10):
    sem = asyncio.Semaphore(max_concurrent)
    async with httpx.AsyncClient() as client:
        async def fetch(url):
            async with sem:
                r = await client.get(url)
                return r.text
        tasks = [fetch(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
"""
}, "add concurrency demo")

# --- Snapshot 16: refactor config use env ---
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

    @classmethod
    def from_env(cls):
        return cls()
"""
}, "refactor config with log level and secret key")

# --- Snapshot 17: test concurrency ---
s({
    "tests/test_concurrency.py": """import pytest
from app.concurrency import fetch_all


@pytest.mark.asyncio
async def test_fetch_all():
    urls = ["https://httpbin.org/get", "https://httpbin.org/ip"]
    results = await fetch_all(urls)
    assert len(results) == 2
    for r in results:
        assert isinstance(r, str)
"""
}, "add concurrency test")

# --- Snapshot 18: logger setup ---
s({
    "app/logger.py": """import logging
import sys


def setup_logger(name, level="INFO"):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        )
        logger.addHandler(handler)
    return logger
"""
}, "add logger setup")

# --- Snapshot 19: docker compose ---
s({
    "docker/docker-compose.yaml": """version: "3.8"
services:
  app:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "5000:5000"
    environment:
      - DEBUG=true
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
"""
}, "add docker compose")

# --- Snapshot 20: wsgi entry ---
s({
    "wsgi.py": """from app.main import app

if __name__ == "__main__":
    app.run()
"""
}, "add wsgi entry point")

# --- Snapshot 21: fix sorts edge case ---
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
"""
}, "fix timsort empty array edge case")

# --- Snapshot 22: add pyproject ---
s({
    "pyproject.toml": """[project]
name = "k8s-python-app"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "flask>=2.2",
    "httpx[http2,brotli]>=0.23",
    "gunicorn>=20.1",
    "orjson>=3.7",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.1",
    "pytest-asyncio>=0.20",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
"""
}, "add pyproject.toml with async test dep")

# --- Snapshot 23: signal handler ---
s({
    "app/signals.py": """import signal
import sys


def setup_graceful_shutdown(executor):
    def _shutdown(sig, frame):
        print(f"received signal {sig}, shutting down...")
        executor.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)
"""
}, "add graceful shutdown handler")

# --- Snapshot 24: extend tests ---
s({
    "tests/test_utils.py": """import pytest
from app.utils import chunks


def test_chunks():
    assert list(chunks([1, 2, 3, 4], 2)) == [[1, 2], [3, 4]]


def test_chunks_odd():
    assert list(chunks([1, 2, 3], 2)) == [[1, 2], [3]]
"""
}, "add utility tests")

# --- Snapshot 25: cache warmup ---
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
"""
}, "add cache preload util")

# --- Snapshot 26: update k8s deployment ---
s({
    "kubernetes/deployment.yaml": """apiVersion: apps/v1
kind: Deployment
metadata:
  name: python-app
  labels:
    app: python-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: python-app
  template:
    metadata:
      labels:
        app: python-app
    spec:
      containers:
      - name: app
        image: python-app:latest
        ports:
        - containerPort: 5000
        env:
        - name: DEBUG
          value: "true"
        - name: PORT
          value: "5000"
        resources:
          requests:
            memory: "128Mi"
            cpu: "250m"
          limits:
            memory: "256Mi"
            cpu: "500m"
"""
}, "update k8s deployment config")

# --- Snapshot 27: orjson demo ---
s({
    "app/serde.py": """import orjson


def dumps(obj):
    return orjson.dumps(obj)


def loads(data):
    return orjson.loads(data)
"""
}, "add orjson serde")

# --- Snapshot 28: remove old tar ---
s({
}, "remove old tarball")

# --- Snapshot 29: update Dockerfile ---
s({
    "docker/Dockerfile": """FROM python:3.11-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
"""
}, "update Dockerfile with gunicorn")

# --- Snapshot 30: cleanup thread import fix ---
s({
}, "minor cleanup")

# === Distribute snapshots across chosen days ===
# 30 snapshots, 35 days. Pick 30 days, assign 1 snapshot each.
random.shuffle(chosen_days)
active_days = chosen_days[:len(SNAPSHOTS)]

base_date = start
for day_offset, (files, msg) in zip(active_days, SNAPSHOTS):
    date = start + timedelta(days=day_offset)
    date_str = date.strftime("%Y-%m-%d")

    # write files
    for fname, content in files.items():
        full = os.path.join(REPO, fname)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w") as f:
            f.write(content.lstrip("\n"))

    # handle deletions
    if not files:
        tar = os.path.join(REPO, "app/hellopython.tar")
        if os.path.exists(tar):
            os.remove(tar)

    ts = f"{date_str} {time_of_day()}"
    git_commit(ts, msg)
    print(f"  {ts}  {msg}")

print(f"\nDone. {len(SNAPSHOTS)} commits created.")
