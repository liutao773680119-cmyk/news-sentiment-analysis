from __future__ import annotations

import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.http import fetch_html
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


BIS_PRESS_FEED_URL = "https://www.bis.org/doclist/all_pressrels.rss"
RSS_NS = {
    "rss": "http://purl.org/rss/1.0/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "dc": "http://purl.org/dc/elements/1.1/",
}


def fetch_bis_press_feed(url: str | None = None) -> str:
    source_definition = load_source_definition_map()["bis"]
    return fetch_html(
        url or BIS_PRESS_FEED_URL,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )


def _normalize_text(value: str | None) -> str:
    return " ".join(unescape(value or "").replace("\xa0", " ").split())


def _parse_pub_date(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def parse_bis_press_feed(payload: str) -> list[RawNews]:
    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        raise CollectorParseError("bis", f"invalid rss payload: {exc}") from exc

    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    rows: list[RawNews] = []
    seen_urls: set[str] = set()
    for index, item in enumerate(root.findall("rss:item", RSS_NS), start=1):
        title = _normalize_text(item.findtext("rss:title", "", RSS_NS))
        link = _normalize_text(item.findtext("rss:link", "", RSS_NS))
        description = _normalize_text(item.findtext("rss:description", "", RSS_NS))
        pub_date = _normalize_text(item.findtext("dc:date", "", RSS_NS))
        if not title or not link or not pub_date or link in seen_urls:
            continue
        seen_urls.add(link)
        published_at = _parse_pub_date(pub_date).replace(microsecond=0).isoformat()
        rows.append(
            RawNews(
                news_id=f"bis-{_parse_pub_date(pub_date).astimezone(timezone.utc).strftime('%Y%m%d%H%M%S')}-{index}",
                source="bis",
                source_type="policy",
                published_at=published_at,
                captured_at=captured_at,
                title=title,
                content=description or title,
                url=link,
            )
        )
    return rows


def collect_bis_news() -> list[RawNews]:
    try:
        payload = fetch_bis_press_feed()
    except Exception as exc:
        raise CollectorFetchError("bis", str(exc) or exc.__class__.__name__) from exc

    if not payload.strip():
        raise CollectorEmptyResultError("bis", "empty response body")

    rows = parse_bis_press_feed(payload)
    if not rows:
        raise CollectorParseError("bis", "no press release items matched rss")
    return rows
