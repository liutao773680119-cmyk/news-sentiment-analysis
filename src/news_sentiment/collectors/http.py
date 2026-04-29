from __future__ import annotations

from time import sleep
from typing import Callable
from urllib.parse import urlparse
from urllib.request import ProxyHandler, Request, build_opener, urlopen


def fetch_html(
    url: str,
    *,
    timeout_seconds: int,
    user_agent: str,
    extra_headers: dict[str, str] | None = None,
    no_proxy_hosts: tuple[str, ...] = (),
    retry_count: int = 0,
    backoff_seconds: float = 0.0,
    urlopen_func: Callable = urlopen,
    sleep_func: Callable[[float], None] = sleep,
) -> str:
    headers = {"User-Agent": user_agent}
    if extra_headers:
        headers.update(extra_headers)
    request = Request(url, headers=headers)
    opener = build_opener(ProxyHandler({})) if urlparse(url).hostname in no_proxy_hosts else None
    for attempt in range(retry_count + 1):
        try:
            open_func = opener.open if opener is not None else urlopen_func
            with open_func(request, timeout=timeout_seconds) as response:
                return response.read().decode("utf-8", errors="ignore")
        except Exception:
            if attempt >= retry_count:
                raise
            delay = backoff_seconds * (attempt + 1)
            if delay > 0:
                sleep_func(delay)
    raise RuntimeError("unreachable")
