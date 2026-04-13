from __future__ import annotations

import json
from datetime import datetime, timezone
from urllib.parse import urljoin

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.http import fetch_html
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


SZSE_DISCLOSURE_URL = "https://www.szse.cn/api/disc/announcement/detailinfo?plateCode=szse&pageSize=50&pageNum=1"
SZSE_ATTACHMENT_BASE_URL = "https://www.szse.cn"


def fetch_szse_news_payload(url: str = SZSE_DISCLOSURE_URL) -> str:
    source_definition = load_source_definition_map()["szse"]
    return fetch_html(
        url,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
    )


def parse_szse_news_payload(payload: str) -> list[RawNews]:
    parsed = json.loads(payload)
    captured_at = datetime.now(timezone.utc).isoformat()
    rows: list[RawNews] = []

    for company in parsed.get("data", []):
        sec_code = str(company.get("secCode", "")).strip()
        announ_list = company.get("announList", [])
        if not isinstance(announ_list, list):
            continue
        for item in announ_list:
            title = str(item.get("title", "")).strip()
            attach_path = str(item.get("attachPath", "")).strip()
            publish_time = str(item.get("publishTime", "")).strip()
            published_date = publish_time[:10]
            if not title or not attach_path or not published_date:
                continue
            rows.append(
                RawNews(
                    news_id=f"szse-{sec_code}-{published_date}-{len(rows) + 1}",
                    source="szse",
                    source_type="hard_event",
                    published_at=f"{published_date}T00:00:00+08:00",
                    captured_at=captured_at,
                    title=title,
                    content=title,
                    url=urljoin(SZSE_ATTACHMENT_BASE_URL, attach_path),
                )
            )
    return rows


def collect_szse_news() -> list[RawNews]:
    try:
        payload = fetch_szse_news_payload()
    except Exception as exc:
        raise CollectorFetchError("szse", str(exc) or exc.__class__.__name__) from exc

    if not payload.strip():
        raise CollectorEmptyResultError("szse", "empty response body")

    rows = parse_szse_news_payload(payload)
    if not rows:
        raise CollectorParseError("szse", "no announcement rows matched response")
    return rows
