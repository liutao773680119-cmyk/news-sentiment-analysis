from __future__ import annotations

from time import sleep
from typing import Callable
from urllib.request import Request, urlopen


def fetch_html(
    url: str,
    *,
    timeout_seconds: int,
    user_agent: str,
    retry_count: int = 0,
    backoff_seconds: float = 0.0,
    urlopen_func: Callable = urlopen,
    sleep_func: Callable[[float], None] = sleep,
) -> str:
    request = Request(url, headers={"User-Agent": user_agent})
    for attempt in range(retry_count + 1):
        try:
            with urlopen_func(request, timeout=timeout_seconds) as response:
                return response.read().decode("utf-8", errors="ignore")
        except Exception:
            if attempt >= retry_count:
                raise
            delay = backoff_seconds * (attempt + 1)
            if delay > 0:
                sleep_func(delay)
    raise RuntimeError("unreachable")
