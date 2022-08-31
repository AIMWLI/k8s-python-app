import orjson


def dumps(obj):
    return orjson.dumps(obj)


def loads(data):
    return orjson.loads(data)


def dumps_default(obj, default):
    return orjson.dumps(obj, default=default)
