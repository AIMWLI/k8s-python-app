import json
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
