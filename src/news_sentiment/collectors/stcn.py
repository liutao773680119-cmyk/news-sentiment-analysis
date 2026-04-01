from __future__ import annotations

import re
from datetime import datetime, timezone
from html import unescape
from urllib.parse import urljoin
from urllib.request import urlopen

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.models import RawNews


STCN_FLASH_URL = "https://www.stcn.com/article/list/kx.html"


def current_china_date() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")


def fetch_stcn_news_html(url: str = STCN_FLASH_URL) -> str:
    with urlopen(url, timeout=10) as response:
        return response.read().decode("utf-8", errors="ignore")


def parse_stcn_news_list(html: str, date_str: str | None = None) -> list[RawNews]:
    rows: list[RawNews] = []
    pattern = re.compile(
        r'<a href="(?P<href>[^"]+)">(?P<title>[^<]+)</a>\s*<span>(?P<time>\d{2}:\d{2})</span>',
        re.S,
    )
    captured_at = datetime.now(timezone.utc).isoformat()
    base_date = date_str or current_china_date()
    for match in pattern.finditer(html):
        title = unescape(match.group("title")).strip()
        href = urljoin("https://www.stcn.com", match.group("href").strip())
        published_at = f"{base_date}T{match.group('time')}:00+08:00"
        slug = href.rstrip("/").split("/")[-1].replace(".html", "")
        rows.append(
            RawNews(
                news_id=f"stcn-{slug}",
                source="stcn",
                source_type="fast_news",
                published_at=published_at,
                captured_at=captured_at,
                title=title,
                content=title,
                url=href,
            )
        )
    return rows


def collect_stcn_news() -> list[RawNews]:
    try:
        html = fetch_stcn_news_html()
    except Exception as exc:
        raise CollectorFetchError("stcn", str(exc) or exc.__class__.__name__) from exc

    if not html.strip():
        raise CollectorEmptyResultError("stcn", "empty response body")

    rows = parse_stcn_news_list(html)
    if not rows:
        raise CollectorParseError("stcn", "no flash news rows matched response")
    return rows
