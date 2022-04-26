import orjson


def dumps(obj):
    return orjson.dumps(obj)


def loads(data):
    return orjson.loads(data)
