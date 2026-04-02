from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from news_sentiment.config_loader import load_theme_registry
from news_sentiment.models import Event

COMPANY_THEME_EVENT_SUBTYPES = {
    "financing_acceptance",
    "control_change",
    "equity_incentive",
    "executive_change",
    "order_contract",
    "cooperation_agreement",
    "acquisition_restructuring",
}


def detect_themes(text: str) -> list[str]:
    registry = load_theme_registry()
    matches: list[str] = []
    normalized_text = text.lower()
    for theme in registry.themes:
        tokens = [theme.name, *theme.aliases]
        if any(token.lower() in normalized_text for token in tokens):
            matches.append(theme.name)
    return list(dict.fromkeys(matches))


def detect_event_themes(event: Event) -> list[str]:
    text = f"{event.canonical_title} {event.summary}"
    matches = detect_themes(text)
    stock_code = _extract_stock_code_from_url(event.url)
    if stock_code and event.event_subtype in COMPANY_THEME_EVENT_SUBTYPES:
        matches.extend(_load_company_theme_map().get(stock_code, []))
    return list(dict.fromkeys(matches))


def detect_direction(text: str) -> str:
    bullish_tokens = ("支持", "推进", "发布", "突破", "增长")
    bearish_tokens = ("限制", "处罚", "下滑", "收缩", "风险")
    if any(token in text for token in bullish_tokens):
        return "bullish"
    if any(token in text for token in bearish_tokens):
        return "bearish"
    return "neutral"


def _extract_stock_code_from_url(url: str) -> str:
    if not url:
        return ""
    query = parse_qs(urlparse(url).query)
    return query.get("stockCode", [""])[0]


@lru_cache(maxsize=1)
def _load_company_theme_map() -> dict[str, list[str]]:
    path = Path(__file__).resolve().parents[3] / "data" / "reference" / "company_theme_map.csv"
    if not path.exists():
        return {}

    rows: dict[str, list[str]] = {}
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.setdefault(row["stock_code"], []).append(row["theme_name"])
    return rows
