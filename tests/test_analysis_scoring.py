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
        source="miit",
        published_at="2026-04-01T09:30:00+08:00",
        url="https://example.com/policy",
        member_news_ids=["n1"],
        event_type="policy",
        primary_entities=["工信部"],
        source_authority_score=0.95,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.triggered is True
    assert analysis.direction == "bullish"


def test_score_event_flags_hard_event_as_triggered() -> None:
    event = Event(
        event_id="event-002",
        first_seen_at="2026-04-02T11:46:27+08:00",
        last_seen_at="2026-04-02T11:46:27+08:00",
        canonical_title="关于聘任窦昌林博士为公司首席执行官兼首席科学家的公告",
        summary="公司公告。",
        source="cninfo",
        published_at="2026-04-02T11:46:27+08:00",
        url="https://example.com/hard-event",
        member_news_ids=["n2"],
        event_type="hard_event",
        primary_entities=["安科生物"],
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.triggered is True


def test_score_event_flags_fast_news_as_triggered() -> None:
    event = Event(
        event_id="event-003",
        first_seen_at="2026-04-02T12:14:33+08:00",
        last_seen_at="2026-04-02T12:14:33+08:00",
        canonical_title="国家药监局发布生物制品分段生产操作指南",
        summary="快讯报道监管部门发布操作指南。",
        source="stcn",
        published_at="2026-04-02T12:14:33+08:00",
        url="https://example.com/fast-news",
        member_news_ids=["n3"],
        event_type="fast_news",
        primary_entities=["国家药监局"],
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.triggered is True
