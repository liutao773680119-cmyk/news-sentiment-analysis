from __future__ import annotations

import re
from datetime import datetime, timezone
from html import unescape
from urllib.parse import urljoin

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.http import fetch_html
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


MIIT_NEWS_URL = "https://www.miit.gov.cn/xwfb/gxdt/index.html"


def fetch_miit_news_html(url: str = MIIT_NEWS_URL) -> str:
    source_definition = load_source_definition_map()["miit"]
    return fetch_html(
        url,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )


def parse_miit_news_list(html: str) -> list[RawNews]:
    rows: list[RawNews] = []
    pattern = re.compile(
        r'<a[^>]+href="(?P<href>[^"]+)"[^>]+title="(?P<title>[^"]+)"[^>]*>.*?</a>\s*<span>(?P<date>\d{4}-\d{2}-\d{2})</span>',
        re.S,
    )
    captured_at = datetime.now(timezone.utc).isoformat()
    for match in pattern.finditer(html):
        title = unescape(match.group("title")).strip()
        href = urljoin(MIIT_NEWS_URL, match.group("href").strip())
        published_at = f"{match.group('date')}T00:00:00+08:00"
        slug = href.rstrip("/").split("/")[-1]
        rows.append(
            RawNews(
                news_id=f"miit-{slug}",
                source="miit",
                source_type="policy",
                published_at=published_at,
                captured_at=captured_at,
                title=title,
                content=title,
                url=href,
            )
        )
    return rows


def collect_miit_news() -> list[RawNews]:
    try:
        html = fetch_miit_news_html()
    except Exception as exc:
        raise CollectorFetchError("miit", str(exc) or exc.__class__.__name__) from exc

    if not html.strip():
        raise CollectorEmptyResultError("miit", "empty response body")

    rows = parse_miit_news_list(html)
    if not rows:
        raise CollectorParseError("miit", "no news rows matched response")
    return rows
