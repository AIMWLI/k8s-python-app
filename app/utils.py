import json
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
