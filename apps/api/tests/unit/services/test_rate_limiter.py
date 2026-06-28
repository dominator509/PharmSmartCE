from __future__ import annotations

from app.services.rate_limit import RateLimiter


def test_rate_limiter_blocks_then_expires_window() -> None:
    clock = [0.0]
    limiter = RateLimiter(clock=lambda: clock[0])

    assert limiter.allow("key", limit=2, window_seconds=10)
    assert limiter.allow("key", limit=2, window_seconds=10)
    assert not limiter.allow("key", limit=2, window_seconds=10)

    clock[0] = 11.0
    assert limiter.allow("key", limit=2, window_seconds=10)
