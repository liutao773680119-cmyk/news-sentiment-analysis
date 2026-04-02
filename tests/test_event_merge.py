from news_sentiment.event_merge.core import merge_news_items
from news_sentiment.models import NormalizedNews


def test_merge_news_items_groups_similar_titles() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="fixture",
            source_type="policy",
            published_at="2026-04-01T09:30:00+08:00",
            captured_at="2026-04-01T09:31:00+08:00",
            title="工信部发文支持算力基础设施",
            content="工信部发文支持算力基础设施建设。",
            url="https://example.com/1",
        ),
        NormalizedNews(
            news_id="n2",
            source="fixture",
            source_type="policy",
            published_at="2026-04-01T09:32:00+08:00",
            captured_at="2026-04-01T09:33:00+08:00",
            title="工信部支持算力基础设施建设",
            content="工信部表示支持算力基础设施建设。",
            url="https://example.com/2",
        ),
    ]
    events = merge_news_items(items)
    assert len(events) == 1


def test_merge_news_items_prefers_more_authoritative_source_metadata() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-01T09:29:00+08:00",
            captured_at="2026-04-01T09:29:30+08:00",
            title="证券时报：中科曙光签署算力合作协议",
            content="证券时报快讯称中科曙光签署算力合作协议。",
            url="https://www.stcn.com/article/detail/123456.html",
        ),
        NormalizedNews(
            news_id="n2",
            source="cninfo",
            source_type="hard_event",
            published_at="2026-04-01T09:31:00+08:00",
            captured_at="2026-04-01T09:31:30+08:00",
            title="中科曙光关于签署算力合作协议的公告",
            content="中科曙光关于签署算力合作协议的公告。",
            url="https://www.cninfo.com.cn/new/disclosure/detail?announcementId=123456",
        ),
    ]
    events = merge_news_items(items)
    assert len(events) == 1
    assert events[0].first_seen_at == "2026-04-01T09:29:00+08:00"
    assert events[0].source == "cninfo"
    assert events[0].canonical_title == "中科曙光关于签署算力合作协议的公告"
    assert events[0].event_subtype == "cooperation_agreement"


def test_merge_news_items_classifies_control_change_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="cninfo",
            source_type="hard_event",
            published_at="2026-04-01T20:00:00+08:00",
            captured_at="2026-04-01T20:00:30+08:00",
            title="关于控股股东签署《股份转让协议》暨控制权拟发生变更的提示性公告",
            content="公司控股股东签署股份转让协议，控制权拟发生变更。",
            url="https://www.cninfo.com.cn/new/disclosure/detail?announcementId=123457",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "control_change"


def test_merge_news_items_classifies_market_move_fast_news_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-01T14:10:00+08:00",
            captured_at="2026-04-01T14:10:10+08:00",
            title="创业板指跌超2%",
            content="创业板指跌超2%，机器人概念股回调。",
            url="https://www.stcn.com/article/detail/999999.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "market_move"
