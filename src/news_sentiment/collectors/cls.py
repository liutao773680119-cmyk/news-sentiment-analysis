from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from html import unescape

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.http import fetch_html
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


CLS_TELEGRAPH_URL = "https://www.cls.cn/telegraph"
CHINA_TZ = timezone(timedelta(hours=8))
NEXT_DATA_PATTERN = re.compile(
    r'<script id="__NEXT_DATA__" type="application/json">\s*(?P<data>.*?)\s*</script>',
    re.S,
)
HTML_TAG_PATTERN = re.compile(r"<[^>]+>")


def fetch_cls_telegraph_html(url: str = CLS_TELEGRAPH_URL) -> str:
    source_definition = load_source_definition_map()["cls"]
    return fetch_html(
        url,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )


def parse_cls_telegraph_html(html: str) -> list[RawNews]:
    match = NEXT_DATA_PATTERN.search(html)
    if match is None:
        return []

    parsed = json.loads(match.group("data"))
    props = parsed.get("props", {})
    initial_state = props.get("initialState")
    if not isinstance(initial_state, dict):
        initial_state = props.get("pageProps", {}).get("initialState", {})
    telegraph_list = initial_state.get("telegraph", {}).get("telegraphList", [])

    captured_at = datetime.now(timezone.utc).isoformat()
    rows: list[RawNews] = []
    for item in telegraph_list:
        article_id = str(item.get("id", "")).strip()
        if not article_id:
            continue
        title = _clean_cls_text(str(item.get("title", "")).strip())
        brief = _clean_cls_text(str(item.get("brief", "")).strip())
        content = _clean_cls_text(str(item.get("content", "")).strip())
        published_at = _parse_cls_timestamp(item.get("ctime"))
        resolved_title = title or brief or content
        resolved_content = content or brief or resolved_title
        if not resolved_title:
            continue
        rows.append(
            RawNews(
                news_id=f"cls-{article_id}",
                source="cls",
                source_type="fast_news",
                published_at=published_at,
                captured_at=captured_at,
                title=resolved_title,
                content=resolved_content,
                url=f"https://www.cls.cn/detail/{article_id}",
            )
        )
    return rows


def collect_cls_news() -> list[RawNews]:
    try:
        html = fetch_cls_telegraph_html()
    except Exception as exc:
        raise CollectorFetchError("cls", str(exc) or exc.__class__.__name__) from exc

    if not html.strip():
        raise CollectorEmptyResultError("cls", "empty response body")

    rows = parse_cls_telegraph_html(html)
    if not rows:
        raise CollectorParseError("cls", "no telegraph rows matched response")
    return rows


def _clean_cls_text(text: str) -> str:
    text = HTML_TAG_PATTERN.sub("", text)
    text = text.replace("\u00a0", " ")
    return unescape(text).strip()


def _parse_cls_timestamp(timestamp: object) -> str:
    if isinstance(timestamp, (int, float)) and timestamp:
        return datetime.fromtimestamp(float(timestamp), tz=CHINA_TZ).isoformat()
    return datetime.now(timezone.utc).astimezone(CHINA_TZ).replace(microsecond=0).isoformat()
