from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
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


STCN_FLASH_URL = "https://www.stcn.com/article/list/kx.html"
STCN_FLASH_DATA_URL = "https://www.stcn.com/article/list.html?type=kx"
CHINA_TZ = timezone(timedelta(hours=8))


def current_china_date() -> str:
    return datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")


def fetch_stcn_news_html(url: str = STCN_FLASH_URL) -> str:
    source_definition = load_source_definition_map()["stcn"]
    return fetch_html(
        url,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )


def fetch_stcn_news_payload(url: str = STCN_FLASH_DATA_URL) -> str:
    source_definition = load_source_definition_map()["stcn"]
    return fetch_html(
        url,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        extra_headers={
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Referer": STCN_FLASH_URL,
        },
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )


def parse_stcn_news_payload(payload: str) -> list[RawNews]:
    parsed = json.loads(payload)
    captured_at = datetime.now(timezone.utc).isoformat()
    rows: list[RawNews] = []
    for item in parsed.get("data", []):
        href = urljoin("https://www.stcn.com", str(item.get("url", "")).strip())
        title = unescape(str(item.get("title", "")).strip())
        content = unescape(str(item.get("content", "")).strip())
        timestamp_ms = int(item.get("time", 0))
        published_at = (
            datetime.fromtimestamp(timestamp_ms / 1000, tz=CHINA_TZ).isoformat()
            if timestamp_ms
            else f"{current_china_date()}T00:00:00+08:00"
        )
        slug = href.rstrip("/").split("/")[-1].replace(".html", "") or str(item.get("id", "unknown"))
        rows.append(
            RawNews(
                news_id=f"stcn-{slug}",
                source="stcn",
                source_type="fast_news",
                published_at=published_at,
                captured_at=captured_at,
                title=title,
                content=content or title,
                url=href,
            )
        )
    return rows


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
        payload = fetch_stcn_news_payload()
    except Exception as exc:
        raise CollectorFetchError("stcn", str(exc) or exc.__class__.__name__) from exc

    if not payload.strip():
        raise CollectorEmptyResultError("stcn", "empty response body")

    rows = parse_stcn_news_payload(payload)
    if not rows:
        raise CollectorParseError("stcn", "no flash news rows matched response")
    return rows
