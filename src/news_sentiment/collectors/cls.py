from __future__ import annotations

import json
import re
from datetime import datetime, timedelta, timezone
from html import unescape
from urllib.parse import urlencode

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.http import fetch_html
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


CLS_TELEGRAPH_URL = "https://www.cls.cn/telegraph"
CLS_TELEGRAPH_CACHE_URL = "https://www.cls.cn/api/cache"
CHINA_TZ = timezone(timedelta(hours=8))
CLS_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/136.0.0.0 Safari/537.36"
)
CLS_PAGE_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.cls.cn/",
}
CLS_API_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": CLS_TELEGRAPH_URL,
    "X-Requested-With": "XMLHttpRequest",
}
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
        user_agent=CLS_BROWSER_USER_AGENT,
        extra_headers=CLS_PAGE_HEADERS,
        no_proxy_hosts=source_definition.no_proxy_hosts,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )


def fetch_cls_telegraph_cache_payload(last_time: int | None = None) -> str:
    source_definition = load_source_definition_map()["cls"]
    cache_url = f"{CLS_TELEGRAPH_CACHE_URL}?{urlencode(_build_cls_cache_query(last_time))}"
    return fetch_html(
        cache_url,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=CLS_BROWSER_USER_AGENT,
        extra_headers=CLS_API_HEADERS,
        no_proxy_hosts=source_definition.no_proxy_hosts,
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

    return _build_cls_rows(telegraph_list)


def parse_cls_telegraph_cache_payload(payload: str) -> list[RawNews]:
    parsed = json.loads(payload)
    roll_data = parsed.get("data", {}).get("roll_data", [])
    return _build_cls_rows(roll_data)


def collect_cls_news() -> list[RawNews]:
    cache_payload = None
    cache_error = None
    try:
        cache_payload = fetch_cls_telegraph_cache_payload()
    except Exception as exc:
        cache_error = exc
    else:
        if cache_payload.strip():
            rows = parse_cls_telegraph_cache_payload(cache_payload)
            if rows:
                return rows

    html = None
    html_error = None
    try:
        html = fetch_cls_telegraph_html()
    except Exception as exc:
        html_error = exc
    else:
        if html.strip():
            rows = parse_cls_telegraph_html(html)
            if rows:
                return rows

    if cache_error is not None and html_error is not None:
        detail = str(cache_error) or cache_error.__class__.__name__
        raise CollectorFetchError("cls", detail) from cache_error

    if (cache_payload is None or not cache_payload.strip()) and (html is None or not html.strip()):
        raise CollectorEmptyResultError("cls", "empty response body")

    raise CollectorParseError("cls", "no telegraph rows matched response")


def _build_cls_cache_query(last_time: int | None = None) -> dict[str, int | str]:
    return {
        "rn": 20,
        "lastTime": last_time or int(datetime.now(CHINA_TZ).timestamp()),
        "name": "telegraph",
    }


def _build_cls_rows(items: object) -> list[RawNews]:
    captured_at = datetime.now(timezone.utc).isoformat()
    rows: list[RawNews] = []
    if not isinstance(items, list):
        return rows
    for item in items:
        if not isinstance(item, dict):
            continue
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


def _clean_cls_text(text: str) -> str:
    text = HTML_TAG_PATTERN.sub("", text)
    text = text.replace("\u00a0", " ")
    return unescape(text).strip()


def _parse_cls_timestamp(timestamp: object) -> str:
    if isinstance(timestamp, (int, float)) and timestamp:
        return datetime.fromtimestamp(float(timestamp), tz=CHINA_TZ).isoformat()
    return datetime.now(timezone.utc).astimezone(CHINA_TZ).replace(microsecond=0).isoformat()
