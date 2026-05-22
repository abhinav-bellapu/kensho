from lru_cache import LRUCache


def test_put_and_get():
    cache = LRUCache(2)
    cache.put("a", 1)
    assert cache.get("a") == 1


def test_missing_returns_none():
    cache = LRUCache(2)
    assert cache.get("missing") is None


def test_evicts_least_recently_used():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.put("c", 3)
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3


def test_get_refreshes_recency():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    cache.get("a")
    cache.put("c", 3)
    assert cache.get("b") is None
    assert cache.get("a") == 1


def test_update_existing_key():
    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("a", 10)
    assert cache.get("a") == 10


def test_capacity_one():
    cache = LRUCache(1)
    cache.put("x", 1)
    cache.put("y", 2)
    assert cache.get("x") is None
    assert cache.get("y") == 2
