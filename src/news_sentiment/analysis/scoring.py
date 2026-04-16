from __future__ import annotations

from news_sentiment.analysis.rules import detect_direction, detect_event_themes
from news_sentiment.config_loader import ScoringConfig
from news_sentiment.models import Event, EventAnalysis

LOW_SIGNAL_CNINFO_DISCLOSURE_SCORING_KEYWORDS = (
    "环境、社会和公司治理报告",
    "业绩网上说明会",
    "责任保险",
)


def score_event(event: Event, scoring_config: ScoringConfig) -> EventAnalysis:
    text = f"{event.canonical_title} {event.summary}"
    themes = detect_event_themes(event)
    direction = detect_direction(text)
    if event.event_subtype == "general_fast_news":
        direction = "neutral"

    score = event.source_authority_score * scoring_config.source_authority_weight
    if event.event_type == "policy":
        score += scoring_config.policy_boost_weight
    if event.event_type == "hard_event":
        score += scoring_config.market_event_boost_weight
    if event.event_type == "fast_news":
        score += _fast_news_boost_weight(event, scoring_config)
    if themes:
        score += scoring_config.theme_expansion_weight
    score += scoring_config.freshness_weight
    if _is_low_signal_cninfo_disclosure_for_scoring(event, themes):
        score = min(score, scoring_config.trigger_score - 0.1)
    score = min(score, 100.0)

    return EventAnalysis(
        event_id=event.event_id,
        direction=direction,
        impact_score=score,
        reasoning="rule_based_scoring",
        themes=themes,
        new_theme_candidates=[],
        time_window="intraday_next_day",
        triggered=score >= scoring_config.trigger_score,
    )


def _fast_news_boost_weight(event: Event, scoring_config: ScoringConfig) -> float:
    if event.event_subtype == "general_fast_news":
        return scoring_config.market_event_boost_weight / 3
    return scoring_config.market_event_boost_weight


def _is_low_signal_cninfo_disclosure_for_scoring(event: Event, themes: list[str]) -> bool:
    if not (
        event.source == "cninfo"
        and event.event_type == "hard_event"
        and event.event_subtype == "corporate_disclosure"
    ):
        return False

    title = event.canonical_title
    if "责任保险" in title:
        return True

    if themes:
        return False

    return any(keyword in title for keyword in LOW_SIGNAL_CNINFO_DISCLOSURE_SCORING_KEYWORDS)
