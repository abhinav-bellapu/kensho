# LRU cache benchmark

`LRUCache` stores key/value pairs with a fixed capacity. `get` and `put` should mark entries as recently used; when full, the **least** recently used key is evicted.

**Intentional bug:** eviction removes the most recently used key (`pop()` from the end) instead of the least recently used key (`pop(0)`).
