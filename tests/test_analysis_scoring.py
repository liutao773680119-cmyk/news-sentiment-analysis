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


def test_score_event_uses_company_theme_map_for_cninfo_hard_event() -> None:
    event = Event(
        event_id="event-004",
        first_seen_at="2026-04-02T11:44:27+08:00",
        last_seen_at="2026-04-02T11:44:27+08:00",
        canonical_title="关于2025年度向特定对象发行A股股票申请获得深圳证券交易所受理的公告",
        summary="关于2025年度向特定对象发行A股股票申请获得深圳证券交易所受理的公告",
        source="cninfo",
        published_at="2026-04-02T11:44:27+08:00",
        url="https://www.cninfo.com.cn/new/disclosure/detail?stockCode=300005&announcementId=1225073837",
        member_news_ids=["n4"],
        event_type="hard_event",
        event_subtype="financing_acceptance",
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert "户外经济" in analysis.themes
    assert analysis.triggered is True


def test_score_event_does_not_use_company_theme_map_for_generic_disclosure() -> None:
    event = Event(
        event_id="event-005",
        first_seen_at="2026-04-02T11:44:27+08:00",
        last_seen_at="2026-04-02T11:44:27+08:00",
        canonical_title="探路者控股集团股份有限公司最近一年的财务报告及其审计报告以及最近一期的财务报告",
        summary="探路者控股集团股份有限公司最近一年的财务报告及其审计报告以及最近一期的财务报告",
        source="cninfo",
        published_at="2026-04-02T11:44:27+08:00",
        url="https://www.cninfo.com.cn/new/disclosure/detail?stockCode=300005&announcementId=1225073841",
        member_news_ids=["n5"],
        event_type="hard_event",
        event_subtype="corporate_disclosure",
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert "户外经济" not in analysis.themes
