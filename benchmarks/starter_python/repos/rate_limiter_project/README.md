# Rate limiter benchmark

`RateLimiter(max_requests, window_seconds)` allows up to `max_requests` calls whose timestamps fall in the current window. A new window starts when `timestamp - window_start >= window_seconds`.

**Intentional bug:** uses `count > max_requests` instead of `count >= max_requests`, rejecting the Nth allowed request and mishandling window boundaries.
