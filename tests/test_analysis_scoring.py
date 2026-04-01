from news_sentiment.analysis.scoring import score_event
from news_sentiment.config_loader import load_scoring_config
from news_sentiment.models import Event


def test_score_event_flags_policy_event_as_triggered() -> None:
    event = Event(
        event_id="event-001",
        first_seen_at="2026-04-01T09:30:00+08:00",
        last_seen_at="2026-04-01T09:32:00+08:00",
        canonical_title="工信部发布算力政策",
        summary="工信部发布文件支持算力基础设施建设。",
        member_news_ids=["n1"],
        event_type="policy",
        primary_entities=["工信部"],
        source_authority_score=0.95,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.triggered is True
    assert analysis.direction == "bullish"
