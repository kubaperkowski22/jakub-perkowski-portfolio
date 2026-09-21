import math
import os
import time
from collections import deque
from functools import lru_cache
from threading import Lock
from ipaddress import ip_address
from fastapi import (
    HTTPException,
    Request,
    status,
)


class SlidingWindowRateLimiter:
    def __init__(
        self,
        max_requests: int,
        window_seconds: int,
    ) -> None:
        if max_requests <= 0:
            raise ValueError(
                "max_requests must be positive"
            )

        if window_seconds <= 0:
            raise ValueError(
                "window_seconds must be positive"
            )

        self.max_requests = max_requests
        self.window_seconds = window_seconds

        self._requests: dict[
            str,
            deque[float],
        ] = {}

        self._lock = Lock()
        self._last_cleanup = time.monotonic()

    def check(
        self,
        key: str,
    ) -> int | None:
        now = time.monotonic()
        cutoff = now - self.window_seconds

        with self._lock:
            self._cleanup(now, cutoff)

            bucket = self._requests.setdefault(
                key,
                deque(),
            )

            while (
                bucket
                and bucket[0] <= cutoff
            ):
                bucket.popleft()

            if len(bucket) >= self.max_requests:
                retry_after = math.ceil(
                    self.window_seconds
                    - (now - bucket[0])
                )

                return max(
                    1,
                    retry_after,
                )

            bucket.append(now)

        return None

    def _cleanup(
        self,
        now: float,
        cutoff: float,
    ) -> None:
        if (
            now - self._last_cleanup
            < self.window_seconds
        ):
            return

        stale_keys = [
            key
            for key, bucket
            in self._requests.items()
            if (
                not bucket
                or bucket[-1] <= cutoff
            )
        ]

        for key in stale_keys:
            del self._requests[key]

        self._last_cleanup = now


def _get_positive_int(
    name: str,
    default: int,
) -> int:
    raw_value = os.getenv(
        name,
        str(default),
    )

    value = int(raw_value)

    if value <= 0:
        raise RuntimeError(
            f"{name} must be positive"
        )

    return value


@lru_cache(maxsize=1)
def get_chat_rate_limiter(
) -> SlidingWindowRateLimiter:
    return SlidingWindowRateLimiter(
        max_requests=_get_positive_int(
            "CHAT_RATE_LIMIT_REQUESTS",
            10,
        ),
        window_seconds=_get_positive_int(
            "CHAT_RATE_LIMIT_WINDOW_SECONDS",
            60,
        ),
    )


def enforce_chat_rate_limit(
    request: Request,
) -> None:
    client_host = get_client_ip(request)

    retry_after = (
        get_chat_rate_limiter()
        .check(client_host)
    )

    if retry_after is None:
        return

    raise HTTPException(
        status_code=(
            status.HTTP_429_TOO_MANY_REQUESTS
        ),
        detail=(
            "Too many chat requests. "
            "Please try again later."
        ),
        headers={
            "Retry-After": str(
                retry_after
            )
        },
    )


def get_client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")

    if forwarded_for:
        candidate = forwarded_for.split(",", 1)[0].strip()

        try:
            return str(ip_address(candidate))
        except ValueError:
            pass

    if request.client:
        return request.client.host

    return "unknown"