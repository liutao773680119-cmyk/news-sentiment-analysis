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


def test_merge_news_items_classifies_policy_signal_fast_news_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T13:02:32+08:00",
            captured_at="2026-04-02T13:02:40+08:00",
            title="四川：到2027年底在全省范围内建成205万个充电设施",
            content="四川省发展和改革委员会等部门印发《四川省电动汽车充电设施服务能力倍增行动方案》。",
            url="https://www.stcn.com/article/detail/3722999.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "policy_signal"


def test_merge_news_items_classifies_tech_breakthrough_fast_news_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T13:18:30+08:00",
            captured_at="2026-04-02T13:18:35+08:00",
            title="科学家实现DNA安全加密实景测试",
            content="研究人员开发出一种基于DNA的安全加密方案并完成真实场景测试。",
            url="https://www.stcn.com/article/detail/3723007.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "tech_breakthrough"


def test_merge_news_items_classifies_industry_data_fast_news_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T13:27:31+08:00",
            captured_at="2026-04-02T13:27:40+08:00",
            title="Sora退出 可灵AI周度活跃用户环比增长",
            content="数据显示，可灵AI周活跃用户环比增长4%，月活跃用户达780万。",
            url="https://www.stcn.com/article/detail/3723013.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "industry_data"


def test_merge_news_items_classifies_business_guidance_fast_news_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T12:57:03+08:00",
            captured_at="2026-04-02T12:57:10+08:00",
            title="安科生物：2026年曲妥珠单抗销售目标仍是收入及利润大幅增长",
            content="公司在电话会议上表示，2026年销售目标仍是收入、利润双双大幅增长。此前产品已获批上市。",
            url="https://www.stcn.com/article/detail/3722993.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "business_guidance"


def test_merge_news_items_groups_market_move_updates_for_same_asset() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T13:49:59+08:00",
            captured_at="2026-04-02T13:50:05+08:00",
            title="现货黄金日内跌幅扩大至3%",
            content="现货黄金日内跌幅扩大至3%，现货白银日内跌幅扩大至6%。",
            url="https://www.stcn.com/article/detail/3723028.html",
        ),
        NormalizedNews(
            news_id="n2",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T13:53:04+08:00",
            captured_at="2026-04-02T13:53:10+08:00",
            title="现货黄金跌破4600美元/盎司",
            content="现货黄金跌破4600美元/盎司，日内跌3.33%。",
            url="https://www.stcn.com/article/detail/3723032.html",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].first_seen_at == "2026-04-02T13:49:59+08:00"
    assert set(events[0].member_news_ids) == {"n1", "n2"}
    assert events[0].event_subtype == "market_move"


def test_merge_news_items_does_not_group_market_move_updates_for_different_assets() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T13:49:59+08:00",
            captured_at="2026-04-02T13:50:05+08:00",
            title="现货黄金日内跌幅扩大至3%",
            content="现货黄金日内跌幅扩大至3%。",
            url="https://www.stcn.com/article/detail/3723028.html",
        ),
        NormalizedNews(
            news_id="n2",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T13:56:55+08:00",
            captured_at="2026-04-02T13:57:02+08:00",
            title="沪指跌幅扩大至1%",
            content="沪指跌幅扩大至1%，深证成指跌1.87%。",
            url="https://www.stcn.com/article/detail/3723042.html",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 2
