from rate_limiter import RateLimiter


def test_allows_up_to_limit_in_window():
    limiter = RateLimiter(max_requests=2, window_seconds=10.0)
    assert limiter.allow(0.0) is True
    assert limiter.allow(1.0) is True
    assert limiter.allow(2.0) is False


def test_rejects_after_limit_until_new_window():
    limiter = RateLimiter(max_requests=1, window_seconds=5.0)
    assert limiter.allow(0.0) is True
    assert limiter.allow(1.0) is False
    assert limiter.allow(5.0) is True


def test_boundary_at_window_edge_allows_fresh_window():
    limiter = RateLimiter(max_requests=2, window_seconds=10.0)
    assert limiter.allow(0.0) is True
    assert limiter.allow(9.9) is True
    assert limiter.allow(10.0) is True
    assert limiter.allow(10.1) is True


def test_three_request_window():
    limiter = RateLimiter(max_requests=3, window_seconds=1.0)
    assert limiter.allow(0.0) is True
    assert limiter.allow(0.2) is True
    assert limiter.allow(0.4) is True
    assert limiter.allow(0.5) is False
    assert limiter.allow(1.0) is True


def test_does_not_allow_timestamps_before_window_start():
    limiter = RateLimiter(max_requests=2, window_seconds=5.0)
    assert limiter.allow(10.0) is True
    assert limiter.allow(9.0) is False


def test_single_request_capacity():
    limiter = RateLimiter(max_requests=1, window_seconds=100.0)
    assert limiter.allow(50.0) is True
    assert limiter.allow(50.5) is False
