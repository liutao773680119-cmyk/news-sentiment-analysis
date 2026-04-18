from __future__ import annotations

import json
from datetime import datetime, timezone

from news_sentiment.collectors.errors import (
    CollectorEmptyResultError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.http import fetch_html
from news_sentiment.config_loader import load_source_definition_map
from news_sentiment.models import RawNews


FEDREG_SEC_URL = (
    "https://www.federalregister.gov/api/v1/documents.json"
    "?per_page=20&conditions%5Bagency_ids%5D%5B%5D=466&order=newest"
)


def fetch_fedreg_sec_payload(url: str | None = None) -> dict:
    source_definition = load_source_definition_map()["fedreg_sec"]
    payload = fetch_html(
        url or FEDREG_SEC_URL,
        timeout_seconds=source_definition.timeout_seconds,
        user_agent=source_definition.user_agent,
        retry_count=source_definition.retry_count,
        backoff_seconds=source_definition.backoff_seconds,
        extra_headers={"Accept": "application/json"},
    )
    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise CollectorParseError("fedreg_sec", f"invalid json payload: {exc}") from exc


def _normalize_text(value: str | None) -> str:
    return " ".join((value or "").replace("\xa0", " ").split())


def parse_fedreg_sec_payload(payload: dict) -> list[RawNews]:
    results = payload.get("results")
    if not isinstance(results, list):
        raise CollectorParseError("fedreg_sec", "invalid federal register payload")

    captured_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    rows: list[RawNews] = []
    seen_ids: set[str] = set()
    for item in results:
        title = _normalize_text(item.get("title"))
        document_type = _normalize_text(item.get("type"))
        abstract = _normalize_text(item.get("abstract"))
        document_number = _normalize_text(item.get("document_number"))
        html_url = _normalize_text(item.get("html_url"))
        publication_date = _normalize_text(item.get("publication_date"))
        if not title or not document_number or not html_url or not publication_date or document_number in seen_ids:
            continue
        seen_ids.add(document_number)
        published_at = f"{publication_date}T00:00:00+00:00"
        content_lines = []
        if document_type:
            content_lines.append(f"Type: {document_type}")
        if abstract:
            content_lines.append(f"Abstract: {abstract}")
        rows.append(
            RawNews(
                news_id=f"fedreg_sec-{document_number}",
                source="fedreg_sec",
                source_type="policy",
                published_at=published_at,
                captured_at=captured_at,
                title=title,
                content="\n".join(content_lines) or title,
                url=html_url,
            )
        )
    return rows


def collect_fedreg_sec_news() -> list[RawNews]:
    try:
        payload = fetch_fedreg_sec_payload()
    except Exception as exc:
        raise CollectorFetchError("fedreg_sec", str(exc) or exc.__class__.__name__) from exc

    if not payload:
        raise CollectorEmptyResultError("fedreg_sec", "empty response body")

    rows = parse_fedreg_sec_payload(payload)
    if not rows:
        raise CollectorParseError("fedreg_sec", "no federal register items matched payload")
    return rows
