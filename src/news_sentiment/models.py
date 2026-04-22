from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class RawNews:
    news_id: str
    source: str
    source_type: str
    published_at: str
    captured_at: str
    title: str
    content: str
    url: str


@dataclass(frozen=True)
class NormalizedNews:
    news_id: str
    source: str
    source_type: str
    published_at: str
    captured_at: str
    title: str
    content: str
    url: str


@dataclass(frozen=True)
class Event:
    event_id: str
    first_seen_at: str
    last_seen_at: str
    canonical_title: str
    summary: str
    source: str = ""
    published_at: str = ""
    url: str = ""
    member_news_ids: List[str] = field(default_factory=list)
    event_type: str = "general"
    event_subtype: str = "general"
    primary_entities: List[str] = field(default_factory=list)
    source_authority_score: float = 0.0


@dataclass(frozen=True)
class EventAnalysis:
    event_id: str
    direction: str
    impact_score: float
    reasoning: str
    themes: List[str] = field(default_factory=list)
    new_theme_candidates: List[str] = field(default_factory=list)
    time_window: str = "intraday_next_day"
    triggered: bool = False


@dataclass(frozen=True)
class ThemeMatch:
    theme_name: str
    stock_code: str
    stock_name: str
    relation_type: str
    weight: float


@dataclass(frozen=True)
class ReportRow:
    event_id: str
    title: str
    direction: str
    impact_score: float
    themes: List[str] = field(default_factory=list)
    stock_codes: List[str] = field(default_factory=list)
    note: str = ""


@dataclass(frozen=True)
class SocialSignal:
    event_id: str
    platform: str
    captured_at: str
    heat_score: float
    heat_delta: float
    co_mentioned_themes: List[str] = field(default_factory=list)
    sample_posts: List[str] = field(default_factory=list)
