from __future__ import annotations

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

_RATE_LIMIT_LOCK = threading.Lock()
_RATE_LIMIT_BUCKETS: dict[str, deque[float]] = defaultdict(deque)


def require_rate_limit(
    request: Request,
    *,
    action: str,
    max_attempts: int,
    window_seconds: int,
) -> None:
    client = request.client.host if request.client else "unknown"
    key = f"{action}:{client}"
    now = time.time()
    window_start = now - float(max(1, window_seconds))

    with _RATE_LIMIT_LOCK:
        bucket = _RATE_LIMIT_BUCKETS[key]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= max(1, max_attempts):
            raise HTTPException(status_code=429, detail="Too many attempts. Please retry later.")
        bucket.append(now)


def clear_rate_limits() -> None:
    with _RATE_LIMIT_LOCK:
        _RATE_LIMIT_BUCKETS.clear()
