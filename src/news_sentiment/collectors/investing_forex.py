from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.http import fetch_html
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


INVESTING_FOREX_FEED_URL = "https://www.investing.com/rss/news_1.rss"


def fetch_investing_forex_feed(url: str | None = None) -> str:
    source_definition = load_source_definition_map()["investing_forex"]
    return fetch_html(
        url or INVESTING_FOREX_FEED_URL,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )


def _normalize_text(value: str | None) -> str:
    return " ".join(unescape(value or "").replace("\xa0", " ").split())


def _parse_pub_date(value: str) -> datetime:
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        parsed = None
    if parsed is not None:
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def parse_investing_forex_feed(payload: str) -> list[RawNews]:
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise CollectorParseError("investing_forex", f"invalid rss payload: {exc}") from exc

    rows: list[RawNews] = []
    seen_urls: set[str] = set()
    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    for index, item in enumerate(root.findall("./channel/item"), start=1):
        title = _normalize_text(item.findtext("title"))
        link = _normalize_text(item.findtext("link"))
        pub_date = _normalize_text(item.findtext("pubDate"))
        description = _normalize_text(item.findtext("description"))
        if not title or not link or not pub_date or link in seen_urls:
            continue
        seen_urls.add(link)
        published_at = _parse_pub_date(pub_date)
        rows.append(
            RawNews(
                news_id=f"investing_forex-{published_at.astimezone(timezone.utc).strftime('%Y%m%d%H%M%S')}-{index}",
                source="investing_forex",
                source_type="fast_news",
                published_at=published_at.replace(microsecond=0).isoformat(),
                captured_at=captured_at,
                title=title,
                content=f"Summary: {description}" if description else title,
                url=link,
            )
        )
    return rows


def collect_investing_forex_news() -> list[RawNews]:
    try:
        payload = fetch_investing_forex_feed()
    except Exception as exc:
        raise CollectorFetchError("investing_forex", str(exc) or exc.__class__.__name__) from exc

    if not payload.strip():
        raise CollectorEmptyResultError("investing_forex", "empty response body")

    rows = parse_investing_forex_feed(payload)
    if not rows:
        raise CollectorParseError("investing_forex", "no feed items matched rss")
    return rows
