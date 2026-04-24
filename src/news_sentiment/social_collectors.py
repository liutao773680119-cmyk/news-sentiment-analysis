from __future__ import annotations

import json
import os
import re
from typing import Callable

from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.collectors.http import fetch_html
from news_sentiment.models import Event, EventAnalysis, SocialSignal
from news_sentiment.settings import ProjectPaths
from news_sentiment.storage import JsonlStore


WEIBO_HOT_SEARCH_URL = "https://weibo.com/ajax/side/hotSearch"
WEIBO_REFERER_URL = "https://weibo.com/"
WEIBO_USER_AGENT = "Mozilla/5.0"


def collect_social_signals(paths: ProjectPaths, platform: str) -> list[SocialSignal]:
    if platform == "fixture":
        return collect_fixture_social_signals(paths)
    if platform == "weibo":
        return collect_weibo_social_signals(paths)
    raise ValueError(f"Unsupported social platform: {platform}")


def collect_fixture_social_signals(paths: ProjectPaths) -> list[SocialSignal]:
    events, analyses = _load_triggered_events(paths)
    if not events:
        return []

    event = events[0]
    analysis = analyses[event.event_id]
    primary_theme = analysis.themes[0] if analysis.themes else event.event_subtype
    return [
        SocialSignal(
            event_id=event.event_id,
            platform="fixture",
            captured_at=event.published_at or event.first_seen_at,
            heat_score=max(analysis.impact_score, 60.0),
            heat_delta=12.0,
            co_mentioned_themes=analysis.themes[:2],
            sample_posts=[f"{primary_theme} 相关讨论升温"],
        )
    ]


def collect_weibo_social_signals(
    paths: ProjectPaths,
    *,
    fetch_html_func: Callable[..., str] = fetch_html,
) -> list[SocialSignal]:
    payload = _fetch_weibo_hot_search_payload(fetch_html_func)
    events, analyses = _load_triggered_events(paths)
    return _match_weibo_topics_to_events(payload, events, analyses)


def _fetch_weibo_hot_search_payload(fetch_html_func: Callable[..., str]) -> dict:
    try:
        raw = fetch_html_func(
            WEIBO_HOT_SEARCH_URL,
            timeout_seconds=10,
            user_agent=WEIBO_USER_AGENT,
            extra_headers=_build_weibo_request_headers(),
        )
    except Exception as exc:  # pragma: no cover - network path
        raise CollectorFetchError("weibo", str(exc) or exc.__class__.__name__) from exc

    if raw.lstrip().startswith("<"):
        raise CollectorFetchError("weibo", "visitor gate or html fallback")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CollectorParseError("weibo", "invalid hot search payload") from exc

    if not isinstance(payload, dict):
        raise CollectorParseError("weibo", "unexpected hot search payload shape")
    return payload


def _build_weibo_request_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "Referer": WEIBO_REFERER_URL,
    }
    cookie = os.getenv("WEIBO_COOKIE", "").strip()
    if cookie:
        headers["Cookie"] = cookie
    return headers


def _match_weibo_topics_to_events(
    payload: dict,
    events: list[Event],
    analyses: dict[str, EventAnalysis],
) -> list[SocialSignal]:
    topics = payload.get("data", {}).get("realtime", [])
    if not isinstance(topics, list):
        raise CollectorParseError("weibo", "missing realtime topics")

    signals: list[SocialSignal] = []
    matched_event_ids: set[str] = set()
    for topic in topics:
        if not isinstance(topic, dict):
            continue
        word = str(topic.get("word") or "").strip()
        if not word:
            continue
        hot_value = _parse_heat_value(topic.get("num"))
        for event in events:
            if event.event_id in matched_event_ids:
                continue
            analysis = analyses[event.event_id]
            if not _topic_matches_event(word, event, analysis):
                continue
            matched_event_ids.add(event.event_id)
            signals.append(
                SocialSignal(
                    event_id=event.event_id,
                    platform="weibo",
                    captured_at=event.published_at or event.first_seen_at,
                    heat_score=hot_value or 60.0,
                    heat_delta=0.0,
                    co_mentioned_themes=analysis.themes[:2],
                    sample_posts=[word],
                )
            )
            break
    return signals


def _topic_matches_event(topic_word: str, event: Event, analysis: EventAnalysis) -> bool:
    topic = topic_word.lower()
    title = event.canonical_title.lower()
    if topic in title or title in topic:
        return True
    if any(theme.lower() in topic for theme in analysis.themes):
        return True

    topic_tokens = _tokenize(topic_word)
    title_tokens = _tokenize(event.canonical_title)
    if not topic_tokens or not title_tokens:
        return False
    overlap = topic_tokens & title_tokens
    return len(overlap) >= 2


def _tokenize(text: str) -> set[str]:
    tokens = set(re.findall(r"[A-Za-z0-9]{2,}", text.lower()))
    tokens.update(part for part in re.findall(r"[\u4e00-\u9fff]{2,}", text) if len(part) >= 2)
    return tokens


def _parse_heat_value(value: object) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def _load_triggered_events(paths: ProjectPaths) -> tuple[list[Event], dict[str, EventAnalysis]]:
    events_store = JsonlStore(paths.events_path, Event)
    analyses_store = JsonlStore(paths.analyses_path, EventAnalysis)
    analyses = {
        analysis.event_id: analysis
        for analysis in analyses_store.read_all()
        if analysis.triggered
    }
    events = [event for event in events_store.read_all() if event.event_id in analyses]
    events.sort(key=lambda event: analyses[event.event_id].impact_score, reverse=True)
    return events, analyses
