from api.rate_limit import (
    SlidingWindowRateLimiter,
)


def test_rate_limiter_blocks_after_limit():
    limiter = SlidingWindowRateLimiter(
        max_requests=2,
        window_seconds=60,
    )

    assert limiter.check("client-a") is None
    assert limiter.check("client-a") is None

    retry_after = limiter.check(
        "client-a"
    )

    assert retry_after is not None
    assert retry_after >= 1


def test_rate_limiter_separates_clients():
    limiter = SlidingWindowRateLimiter(
        max_requests=1,
        window_seconds=60,
    )

    assert limiter.check("client-a") is None
    assert limiter.check("client-a") is not None

    assert limiter.check("client-b") is None