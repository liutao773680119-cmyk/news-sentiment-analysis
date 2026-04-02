from __future__ import annotations

from news_sentiment.analysis.rules import detect_direction, detect_themes
from news_sentiment.config_loader import ScoringConfig
from news_sentiment.models import Event, EventAnalysis


def score_event(event: Event, scoring_config: ScoringConfig) -> EventAnalysis:
    text = f"{event.canonical_title} {event.summary}"
    themes = detect_themes(text)
    direction = detect_direction(text)

    score = event.source_authority_score * scoring_config.source_authority_weight
    if event.event_type == "policy":
        score += scoring_config.policy_boost_weight
    if event.event_type in {"hard_event", "fast_news"}:
        score += scoring_config.market_event_boost_weight
    if themes:
        score += scoring_config.theme_expansion_weight
    score += scoring_config.freshness_weight
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
