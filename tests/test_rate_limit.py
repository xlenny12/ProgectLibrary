from app.core.rate_limit import InMemoryRateLimiter


def test_in_memory_rate_limiter_blocks_until_window_expires():
    limiter = InMemoryRateLimiter(limit=2, window_seconds=60)

    assert limiter.is_allowed("client", now=100) == (True, 0)
    assert limiter.is_allowed("client", now=101) == (True, 0)

    allowed, retry_after = limiter.is_allowed("client", now=102)
    assert allowed is False
    assert retry_after > 0

    assert limiter.is_allowed("client", now=161) == (True, 0)


def test_in_memory_rate_limiter_keeps_clients_separate():
    limiter = InMemoryRateLimiter(limit=1, window_seconds=60)

    assert limiter.is_allowed("client-a", now=100) == (True, 0)
    assert limiter.is_allowed("client-b", now=100) == (True, 0)
    assert limiter.is_allowed("client-a", now=101)[0] is False
