from __future__ import annotations

from typing import Callable
from urllib.request import Request, urlopen


def fetch_html(
    url: str,
    *,
    timeout_seconds: int,
    user_agent: str,
    urlopen_func: Callable = urlopen,
) -> str:
    request = Request(url, headers={"User-Agent": user_agent})
    with urlopen_func(request, timeout=timeout_seconds) as response:
        return response.read().decode("utf-8", errors="ignore")
