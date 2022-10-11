from app.cache import TTLCache


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
