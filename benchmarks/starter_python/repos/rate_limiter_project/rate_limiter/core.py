"""Fixed-window rate limiter."""


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: float) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._window_start = 0.0
        self._count = 0

    def allow(self, timestamp: float) -> bool:
        """Return True if a request at timestamp is allowed."""
        if timestamp < self._window_start:
            return False
        # Bug: uses > instead of >= so a new window starts one tick late
        if timestamp - self._window_start > self.window_seconds:
            self._window_start = timestamp
            self._count = 0
        if self._count >= self.max_requests:
            return False
        self._count += 1
        return True
