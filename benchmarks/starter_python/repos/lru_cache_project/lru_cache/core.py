"""Small in-memory LRU cache."""

from __future__ import annotations


class LRUCache:
    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self._order: list[str] = []
        self._data: dict[str, int] = {}

    def get(self, key: str) -> int | None:
        if key not in self._data:
            return None
        self._touch(key)
        return self._data[key]

    def put(self, key: str, value: int) -> None:
        if key in self._data:
            self._data[key] = value
            self._touch(key)
            return
        if len(self._data) >= self.capacity:
            # Bug: evicts most recently used (end) instead of least recently used (front)
            evicted = self._order.pop()
            del self._data[evicted]
        self._data[key] = value
        self._order.append(key)

    def _touch(self, key: str) -> None:
        self._order.remove(key)
        self._order.append(key)
