from api.rate_limit import SlidingWindowRateLimiter, get_client_ip
from starlette.requests import Request


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


def make_request(
    *,
    client_host: str = "10.0.0.1",
    forwarded_for: str | None = None,
) -> Request:
    headers = []

    if forwarded_for:
        headers.append(
            (
                b"x-forwarded-for",
                forwarded_for.encode(),
            )
        )

    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/chat",
        "headers": headers,
        "client": (client_host, 12345),
    }

    return Request(scope)


def test_client_ip_uses_forwarded_for():
    request = make_request(
        forwarded_for="203.0.113.42"
    )

    assert get_client_ip(request) == "203.0.113.42"


def test_client_ip_uses_first_forwarded_address():
    request = make_request(
        forwarded_for="203.0.113.42, 10.0.0.2"
    )

    assert get_client_ip(request) == "203.0.113.42"


def test_client_ip_falls_back_to_request_client():
    request = make_request(
        client_host="10.0.0.1"
    )

    assert get_client_ip(request) == "10.0.0.1"


def test_client_ip_ignores_invalid_forwarded_for():
    request = make_request(
        client_host="10.0.0.1",
        forwarded_for="not-an-ip",
    )

    assert get_client_ip(request) == "10.0.0.1"