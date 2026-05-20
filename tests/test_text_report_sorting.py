from news_sentiment.models import Event, EventAnalysis, SocialSignal
from news_sentiment.reporting.text_report import write_text_report
from news_sentiment.settings import ProjectPaths


def test_write_text_report_filters_non_triggered_and_sorts_by_score(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-1",
            first_seen_at="2026-04-01T09:30:00+08:00",
            last_seen_at="2026-04-01T09:30:00+08:00",
            canonical_title="低分事件",
            summary="summary",
            source="fixture",
            published_at="2026-04-01T09:30:00+08:00",
            url="https://example.com/1",
        ),
        Event(
            event_id="event-2",
            first_seen_at="2026-04-01T09:31:00+08:00",
            last_seen_at="2026-04-01T09:31:00+08:00",
            canonical_title="高分事件",
            summary="summary",
            source="fixture",
            published_at="2026-04-01T09:31:00+08:00",
            url="https://example.com/2",
        ),
        Event(
            event_id="event-3",
            first_seen_at="2026-04-01T09:32:00+08:00",
            last_seen_at="2026-04-01T09:32:00+08:00",
            canonical_title="未触发事件",
            summary="summary",
            source="fixture",
            published_at="2026-04-01T09:32:00+08:00",
            url="https://example.com/3",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-1",
            direction="bullish",
            impact_score=71.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-2",
            direction="bullish",
            impact_score=95.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-3",
            direction="neutral",
            impact_score=40.0,
            reasoning="rule",
            themes=[],
            triggered=False,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "未触发事件" not in content
    assert content.index("高分事件") < content.index("低分事件")


def test_write_text_report_filters_stale_events_relative_to_latest_batch_time(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-old",
            first_seen_at="2026-03-20T09:30:00+08:00",
            last_seen_at="2026-03-20T09:30:00+08:00",
            canonical_title="过旧事件",
            summary="summary",
            source="miit",
            published_at="2026-03-20T09:30:00+08:00",
            url="https://example.com/old",
        ),
        Event(
            event_id="event-new",
            first_seen_at="2026-04-02T09:30:00+08:00",
            last_seen_at="2026-04-02T09:30:00+08:00",
            canonical_title="近期事件",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T09:30:00+08:00",
            url="https://example.com/new",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-old",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-new",
            direction="bullish",
            impact_score=75.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "近期事件" in content
    assert "过旧事件" not in content


def test_write_text_report_falls_back_to_event_stock_code_for_sse_hard_event_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-fallback",
            first_seen_at="2026-05-01T00:00:00+08:00",
            last_seen_at="2026-05-01T00:00:00+08:00",
            canonical_title="皖维高新关于向特定对象发行A股股票申请获得上海证券交易所受理的公告",
            summary="皖维高新关于向特定对象发行A股股票申请获得上海证券交易所受理的公告",
            source="sse",
            published_at="2026-05-01T00:00:00+08:00",
            url="https://static.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-05-01/600063_20260501_NCRC.pdf",
            event_type="hard_event",
            event_subtype="financing_acceptance",
        )
    ]
    analyses = [
        EventAnalysis(
            event_id="event-sse-fallback",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        )
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "个股: 600063" in content


def test_write_text_report_prioritizes_event_stock_code_before_theme_peer_stocks(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-theme-priority",
            first_seen_at="2026-05-01T00:00:00+08:00",
            last_seen_at="2026-05-01T00:00:00+08:00",
            canonical_title="皖维高新关于向特定对象发行A股股票申请获得上海证券交易所受理的公告",
            summary="皖维高新关于向特定对象发行A股股票申请获得上海证券交易所受理的公告",
            source="sse",
            published_at="2026-05-01T00:00:00+08:00",
            url="https://static.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-05-01/600063_20260501_NCRC.pdf",
            event_type="hard_event",
            event_subtype="financing_acceptance",
        )
    ]
    analyses = [
        EventAnalysis(
            event_id="event-sse-theme-priority",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=["新材料"],
            triggered=True,
        )
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "题材: 新材料" in content
    assert "个股: 600063, 300285, 600206" in content
    assert "历史: hist-017" in content


def test_write_text_report_prioritizes_themed_events_when_scores_tie(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-no-theme",
            first_seen_at="2026-04-02T09:30:00+08:00",
            last_seen_at="2026-04-02T09:30:00+08:00",
            canonical_title="无题材事件",
            summary="summary",
            source="miit",
            published_at="2026-04-02T09:30:00+08:00",
            url="https://example.com/1",
        ),
        Event(
            event_id="event-theme",
            first_seen_at="2026-04-02T09:31:00+08:00",
            last_seen_at="2026-04-02T09:31:00+08:00",
            canonical_title="有题材事件",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T09:31:00+08:00",
            url="https://example.com/2",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-no-theme",
            direction="bullish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-theme",
            direction="bullish",
            impact_score=80.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert content.index("有题材事件") < content.index("无题材事件")


def test_write_text_report_filters_neutral_policy_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-policy-neutral",
            first_seen_at="2026-04-02T09:30:00+08:00",
            last_seen_at="2026-04-02T09:30:00+08:00",
            canonical_title="工信部机关开展春季植树活动",
            summary="summary",
            source="miit",
            published_at="2026-04-02T09:30:00+08:00",
            url="https://example.com/policy-neutral",
            event_type="policy",
        ),
        Event(
            event_id="event-fast-neutral",
            first_seen_at="2026-04-02T09:31:00+08:00",
            last_seen_at="2026-04-02T09:31:00+08:00",
            canonical_title="布伦特原油期货涨幅扩大至6%",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T09:31:00+08:00",
            url="https://example.com/fast-neutral",
            event_type="fast_news",
        ),
        Event(
            event_id="event-policy-bullish",
            first_seen_at="2026-04-02T09:32:00+08:00",
            last_seen_at="2026-04-02T09:32:00+08:00",
            canonical_title="工信部发布实施方案",
            summary="summary",
            source="miit",
            published_at="2026-04-02T09:32:00+08:00",
            url="https://example.com/policy-bullish",
            event_type="policy",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-policy-neutral",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-fast-neutral",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-policy-bullish",
            direction="bullish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "工信部机关开展春季植树活动" not in content
    assert "布伦特原油期货涨幅扩大至6%" in content
    assert "工信部发布实施方案" in content


def test_write_text_report_filters_miit_policy_meeting_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-miit-meeting-no-theme",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="2026年全国工业和信息化科技创新和产业创新融合发展工作座谈会在苏州召开",
            summary="会议研究部署下一阶段产业科技创新重点工作任务。",
            source="miit",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/miit-meeting",
            event_type="policy",
            event_subtype="policy_update",
        ),
        Event(
            event_id="event-miit-themed-policy",
            first_seen_at="2026-04-03T00:01:00+08:00",
            last_seen_at="2026-04-03T00:01:00+08:00",
            canonical_title="工业和信息化部举行《节能装备高质量发展实施方案（2026—2028年）》新闻发布会",
            summary="会议介绍节能装备高质量发展实施方案有关情况。",
            source="miit",
            published_at="2026-04-03T00:01:00+08:00",
            url="https://example.com/miit-themed-policy",
            event_type="policy",
            event_subtype="policy_support",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-miit-meeting-no-theme",
            direction="bullish",
            impact_score=72.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-miit-themed-policy",
            direction="bullish",
            impact_score=97.0,
            reasoning="rule",
            themes=["节能装备"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "2026年全国工业和信息化科技创新和产业创新融合发展工作座谈会在苏州召开" not in content
    assert "工业和信息化部举行《节能装备高质量发展实施方案（2026—2028年）》新闻发布会" in content


def test_write_text_report_filters_miit_policy_meeting_and_meeting_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-miit-meeting",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="工业和信息化部负责人会见苹果、高通、SK海力士等跨国企业和商协会负责人",
            summary="工业和信息化部有关司局负责人参加会见，各方表示进一步深化务实合作。",
            source="miit",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/miit-meeting-2",
            event_type="policy",
            event_subtype="policy_support",
        ),
        Event(
            event_id="event-miit-themed-policy",
            first_seen_at="2026-04-03T00:01:00+08:00",
            last_seen_at="2026-04-03T00:01:00+08:00",
            canonical_title="关于侵害用户权益行为的APP（SDK）通报",
            summary="工业和信息化部通报存在侵害用户权益行为的APP（SDK）。",
            source="miit",
            published_at="2026-04-03T00:01:00+08:00",
            url="https://example.com/miit-themed-policy-2",
            event_type="policy",
            event_subtype="policy_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-miit-meeting",
            direction="bullish",
            impact_score=72.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-miit-themed-policy",
            direction="neutral",
            impact_score=97.0,
            reasoning="rule",
            themes=["数据安全"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "工业和信息化部负责人会见苹果、高通、SK海力士等跨国企业和商协会负责人" not in content
    assert "关于侵害用户权益行为的APP（SDK）通报" in content


def test_write_text_report_filters_miit_industry_meeting_and_press_conference_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-miit-industry-meeting",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="2026年全国电子信息制造业高质量发展行业会议在武汉召开",
            summary="summary",
            source="miit",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/miit-industry-meeting",
            event_type="policy",
            event_subtype="policy_update",
        ),
        Event(
            event_id="event-miit-press-conference",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="工业和信息化部举行“推动国家高新区高质量发展”新闻发布会",
            summary="summary",
            source="miit",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/miit-press-conference",
            event_type="policy",
            event_subtype="policy_support",
        ),
        Event(
            event_id="event-miit-keep-themed-policy",
            first_seen_at="2026-04-09T00:00:00+08:00",
            last_seen_at="2026-04-09T00:00:00+08:00",
            canonical_title="工业和信息化部等四部门召开动力及储能电池行业企业座谈会",
            summary="summary",
            source="miit",
            published_at="2026-04-09T00:00:00+08:00",
            url="https://example.com/miit-keep-themed-policy",
            event_type="policy",
            event_subtype="policy_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-miit-industry-meeting",
            direction="bullish",
            impact_score=72.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-miit-press-conference",
            direction="bullish",
            impact_score=72.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-miit-keep-themed-policy",
            direction="bullish",
            impact_score=97.0,
            reasoning="rule",
            themes=["储能"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "工业和信息化部等四部门召开动力及储能电池行业企业座谈会" in content
    assert "2026年全国电子信息制造业高质量发展行业会议在武汉召开" not in content
    assert "工业和信息化部举行“推动国家高新区高质量发展”新闻发布会" not in content


def test_write_text_report_filters_miit_standardization_group_meeting_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-miit-standardization-group-meeting",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="2026年国家智能制造标准化总体组和专家咨询组全体会议在京召开",
            summary="会议研究部署下一阶段智能制造标准化重点工作。",
            source="miit",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/miit-standardization-group-meeting",
            event_type="policy",
            event_subtype="policy_update",
        ),
        Event(
            event_id="event-miit-themed-policy-standard",
            first_seen_at="2026-04-15T00:01:00+08:00",
            last_seen_at="2026-04-15T00:01:00+08:00",
            canonical_title="工业和信息化部等部门印发智能制造标准体系建设指南",
            summary="围绕智能制造标准体系建设作出部署。",
            source="miit",
            published_at="2026-04-15T00:01:00+08:00",
            url="https://example.com/miit-themed-policy-standard",
            event_type="policy",
            event_subtype="policy_support",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-miit-standardization-group-meeting",
            direction="bullish",
            impact_score=72.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-miit-themed-policy-standard",
            direction="bullish",
            impact_score=97.0,
            reasoning="rule",
            themes=["智能制造"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "2026年国家智能制造标准化总体组和专家咨询组全体会议在京召开" not in content
    assert "工业和信息化部等部门印发智能制造标准体系建设指南" in content


def test_write_text_report_filters_miit_policy_activity_and_study_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-miit-activity",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="工业和信息化部机关开展2026年春季义务植树活动",
            summary="副部长熊继军和部机关干部职工一同参加活动。",
            source="miit",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/miit-activity",
            event_type="policy",
            event_subtype="policy_update",
        ),
        Event(
            event_id="event-miit-study",
            first_seen_at="2026-04-03T00:01:00+08:00",
            last_seen_at="2026-04-03T00:01:00+08:00",
            canonical_title="工业和信息化部党组举办树立和践行正确政绩观学习教育辅导报告会暨读书班开班式",
            summary="部党组书记作开班讲话，部领导参加学习。",
            source="miit",
            published_at="2026-04-03T00:01:00+08:00",
            url="https://example.com/miit-study",
            event_type="policy",
            event_subtype="policy_update",
        ),
        Event(
            event_id="event-miit-themed-policy",
            first_seen_at="2026-04-03T00:02:00+08:00",
            last_seen_at="2026-04-03T00:02:00+08:00",
            canonical_title="工业和信息化部召开新材料领域中小企业圆桌会",
            summary="会议聚焦大力培育发展新材料领域中小企业。",
            source="miit",
            published_at="2026-04-03T00:02:00+08:00",
            url="https://example.com/miit-themed-policy-3",
            event_type="policy",
            event_subtype="policy_support",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-miit-activity",
            direction="bullish",
            impact_score=72.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-miit-study",
            direction="bullish",
            impact_score=72.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-miit-themed-policy",
            direction="bullish",
            impact_score=97.0,
            reasoning="rule",
            themes=["新材料"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "工业和信息化部机关开展2026年春季义务植树活动" not in content
    assert "工业和信息化部党组举办树立和践行正确政绩观学习教育辅导报告会暨读书班开班式" not in content
    assert "工业和信息化部召开新材料领域中小企业圆桌会" in content


def test_write_text_report_filters_miit_learning_education_update_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-miit-learning-education",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="工业和信息化部系统扎实开展学习教育推动正确政绩观内化于心 外化于行",
            summary="工业和信息化部系统通过召开动员部署会、制定工作方案、举办辅导报告会暨读书班开班式等形式，扎实推动学习教育走深走实。",
            source="miit",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/miit-learning-education",
            event_type="policy",
            event_subtype="policy_support",
        ),
        Event(
            event_id="event-miit-themed-policy",
            first_seen_at="2026-04-03T00:01:00+08:00",
            last_seen_at="2026-04-03T00:01:00+08:00",
            canonical_title="工业和信息化部召开新材料领域中小企业圆桌会",
            summary="会议聚焦大力培育发展新材料领域中小企业。",
            source="miit",
            published_at="2026-04-03T00:01:00+08:00",
            url="https://example.com/miit-themed-policy-4",
            event_type="policy",
            event_subtype="policy_support",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-miit-learning-education",
            direction="bullish",
            impact_score=72.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-miit-themed-policy",
            direction="bullish",
            impact_score=97.0,
            reasoning="rule",
            themes=["新材料"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "工业和信息化部系统扎实开展学习教育推动正确政绩观内化于心 外化于行" not in content
    assert "工业和信息化部召开新材料领域中小企业圆桌会" in content


def test_write_text_report_filters_miit_publication_update_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-miit-publication",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="《中国履行〈禁止化学武器公约〉报告（2024）》出版发行",
            summary="该报告由工业和信息化部组织编写并公开出版发行。",
            source="miit",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/miit-publication",
            event_type="policy",
            event_subtype="policy_update",
        ),
        Event(
            event_id="event-miit-themed-policy",
            first_seen_at="2026-04-03T00:01:00+08:00",
            last_seen_at="2026-04-03T00:01:00+08:00",
            canonical_title="工业和信息化部召开新材料领域中小企业圆桌会",
            summary="会议聚焦大力培育发展新材料领域中小企业。",
            source="miit",
            published_at="2026-04-03T00:01:00+08:00",
            url="https://example.com/miit-themed-policy-5",
            event_type="policy",
            event_subtype="policy_support",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-miit-publication",
            direction="bullish",
            impact_score=72.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-miit-themed-policy",
            direction="bullish",
            impact_score=97.0,
            reasoning="rule",
            themes=["新材料"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "《中国履行〈禁止化学武器公约〉报告（2024）》出版发行" not in content
    assert "工业和信息化部召开新材料领域中小企业圆桌会" in content


def test_write_text_report_filters_stcn_market_close_roundup_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-close-roundup",
            first_seen_at="2026-04-03T15:04:11+08:00",
            last_seen_at="2026-04-03T15:04:11+08:00",
            canonical_title="收评：三大指数集体收跌 CPO概念逆市上涨",
            summary="今日三大指数高开后震荡下行，截至收盘，沪指跌1%，深证成指跌0.99%，创业板指跌0.73%。盘面上，CPO概念走强，德科立、中瓷电子等多股涨停。",
            source="stcn",
            published_at="2026-04-03T15:04:11+08:00",
            url="https://example.com/stcn-close-roundup",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-stcn-themed-market-move",
            first_seen_at="2026-04-03T15:05:00+08:00",
            last_seen_at="2026-04-03T15:05:00+08:00",
            canonical_title="现货黄金跌破4600美元/盎司",
            summary="summary",
            source="stcn",
            published_at="2026-04-03T15:05:00+08:00",
            url="https://example.com/stcn-themed-market-move",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-close-roundup",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-themed-market-move",
            direction="neutral",
            impact_score=97.0,
            reasoning="rule",
            themes=["黄金"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "收评：三大指数集体收跌 CPO概念逆市上涨" not in content
    assert "现货黄金跌破4600美元/盎司" in content


def test_write_text_report_filters_stcn_market_open_roundup_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-open-roundup",
            first_seen_at="2026-04-08T09:27:29+08:00",
            last_seen_at="2026-04-08T09:27:29+08:00",
            canonical_title="开评：三大指数集体高开 创业板指涨3.07%",
            summary="人民财讯4月8日电，4月8日，三大指数集体高开，沪指涨1.03%，深证成指涨2.36%，创业板指涨3.07%。盘面上，有色、半导体、通信设备、元器件等板块涨幅居前；石油、煤炭、多元金融、供气供热等板块跌幅居前。",
            source="stcn",
            published_at="2026-04-08T09:27:29+08:00",
            url="https://example.com/stcn-open-roundup",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-stcn-themed-market-move-open",
            first_seen_at="2026-04-08T09:28:00+08:00",
            last_seen_at="2026-04-08T09:28:00+08:00",
            canonical_title="现货黄金跌破4600美元/盎司",
            summary="summary",
            source="stcn",
            published_at="2026-04-08T09:28:00+08:00",
            url="https://example.com/stcn-themed-market-move-open",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-open-roundup",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-themed-market-move-open",
            direction="neutral",
            impact_score=97.0,
            reasoning="rule",
            themes=["黄金"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "开评：三大指数集体高开 创业板指涨3.07%" not in content
    assert "现货黄金跌破4600美元/盎司" in content


def test_write_text_report_filters_cls_ashare_roundup_and_limitup_digest(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-close-roundup",
            first_seen_at="2026-04-17T15:01:54+08:00",
            last_seen_at="2026-04-17T15:01:54+08:00",
            canonical_title="收评：创业板指涨超1%再创近11年新高 算力硬件方向持续爆发",
            summary="summary",
            source="cls",
            published_at="2026-04-17T15:01:54+08:00",
            url="https://example.com/cls-close-roundup",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-cls-limit-up-digest",
            first_seen_at="2026-04-17T15:13:25+08:00",
            last_seen_at="2026-04-17T15:13:25+08:00",
            canonical_title="4月17日涨停分析",
            summary="【4月17日涨停分析】今日全市场共71股涨停。",
            source="cls",
            published_at="2026-04-17T15:13:25+08:00",
            url="https://example.com/cls-limit-up-digest",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-cls-keep-order",
            first_seen_at="2026-04-17T15:20:00+08:00",
            last_seen_at="2026-04-17T15:20:00+08:00",
            canonical_title="印度石油部表示已敲定80万吨液化石油气进口订单",
            summary="summary",
            source="cls",
            published_at="2026-04-17T15:20:00+08:00",
            url="https://example.com/cls-keep-order",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-cls-close-roundup", direction="neutral", impact_score=99.3, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-cls-limit-up-digest", direction="neutral", impact_score=99.3, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-cls-keep-order", direction="neutral", impact_score=99.3, reasoning="rule", themes=["油气"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "印度石油部表示已敲定80万吨液化石油气进口订单" in content
    assert "收评：创业板指涨超1%再创近11年新高 算力硬件方向持续爆发" not in content
    assert "4月17日涨停分析" not in content


def test_write_text_report_filters_domestic_futures_opening_roundup_variant_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-futures-open-variant",
            first_seen_at="2026-04-09T09:02:23+08:00",
            last_seen_at="2026-04-09T09:02:23+08:00",
            canonical_title="国内期市开盘多数下跌 甲醇跌超5%",
            summary="人民财讯4月9日电，国内期市开盘多数下跌，甲醇跌超5%，乙二醇、丙烯、LU燃油、液化气跌超3%。",
            source="stcn",
            published_at="2026-04-09T09:02:23+08:00",
            url="https://example.com/stcn-futures-open-variant",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-stcn-themed-market-move-futures",
            first_seen_at="2026-04-09T09:03:00+08:00",
            last_seen_at="2026-04-09T09:03:00+08:00",
            canonical_title="布油、WTI原油期货双双涨超3%",
            summary="人民财讯4月9日电，布油、WTI原油期货日内双双涨超3%。",
            source="stcn",
            published_at="2026-04-09T09:03:00+08:00",
            url="https://example.com/stcn-themed-market-move-futures",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-futures-open-variant",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-themed-market-move-futures",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "国内期市开盘多数下跌 甲醇跌超5%" not in content
    assert "布油、WTI原油期货双双涨超3%" in content


def test_write_text_report_filters_miit_statistics_supervision_feedback_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-miit-statistics-supervision",
            first_seen_at="2026-04-09T00:00:00+08:00",
            last_seen_at="2026-04-09T00:00:00+08:00",
            canonical_title="国家统计局2025年常规统计督察第9统计督察组向工业和信息化部反馈统计督察意见",
            summary="督察发现统计工作仍存在一些问题，要求从严从实推进督察反馈问题整改，并在3个月内反馈整改情况。",
            source="miit",
            published_at="2026-04-09T00:00:00+08:00",
            url="https://example.com/miit-statistics-supervision",
            event_type="policy",
            event_subtype="policy_support",
        ),
        Event(
            event_id="event-miit-themed-policy-feedback",
            first_seen_at="2026-04-09T00:01:00+08:00",
            last_seen_at="2026-04-09T00:01:00+08:00",
            canonical_title="工业和信息化部召开新材料领域中小企业圆桌会",
            summary="会议聚焦大力培育发展新材料领域中小企业。",
            source="miit",
            published_at="2026-04-09T00:01:00+08:00",
            url="https://example.com/miit-themed-policy-feedback",
            event_type="policy",
            event_subtype="policy_support",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-miit-statistics-supervision",
            direction="bullish",
            impact_score=72.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-miit-themed-policy-feedback",
            direction="bullish",
            impact_score=97.0,
            reasoning="rule",
            themes=["新材料"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "国家统计局2025年常规统计督察第9统计督察组向工业和信息化部反馈统计督察意见" not in content
    assert "工业和信息化部召开新材料领域中小企业圆桌会" in content


def test_write_text_report_filters_domestic_futures_close_roundup_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-futures-close-roundup",
            first_seen_at="2026-04-03T15:08:03+08:00",
            last_seen_at="2026-04-03T15:08:03+08:00",
            canonical_title="国内期货收盘涨跌不一 燃油涨超7%",
            summary="氧化铝涨超3%，原油、纸浆等涨超2%，玻璃、棕榈油等下跌。",
            source="stcn",
            published_at="2026-04-03T15:08:03+08:00",
            url="https://example.com/futures-close-roundup",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-themed-market-move",
            first_seen_at="2026-04-03T15:09:00+08:00",
            last_seen_at="2026-04-03T15:09:00+08:00",
            canonical_title="现货黄金跌破4600美元/盎司",
            summary="summary",
            source="stcn",
            published_at="2026-04-03T15:09:00+08:00",
            url="https://example.com/themed-market-move-2",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-futures-close-roundup",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-themed-market-move",
            direction="neutral",
            impact_score=97.0,
            reasoning="rule",
            themes=["黄金"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "国内期货收盘涨跌不一 燃油涨超7%" not in content
    assert "现货黄金跌破4600美元/盎司" in content


def test_write_text_report_filters_stock_all_time_high_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stock-ath",
            first_seen_at="2026-04-03T15:20:44+08:00",
            last_seen_at="2026-04-03T15:20:44+08:00",
            canonical_title="华瑞股份股价创下历史新高",
            summary="4月3日，华瑞股份(300626)收盘涨停，最新收盘价为24.59元/股，创下历史新高。公司预计2025年净利润为600万元至900万元，同比扭亏为盈。",
            source="stcn",
            published_at="2026-04-03T15:20:44+08:00",
            url="https://example.com/stock-ath",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-themed-market-move",
            first_seen_at="2026-04-03T15:21:00+08:00",
            last_seen_at="2026-04-03T15:21:00+08:00",
            canonical_title="现货黄金跌破4600美元/盎司",
            summary="summary",
            source="stcn",
            published_at="2026-04-03T15:21:00+08:00",
            url="https://example.com/themed-market-move-3",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stock-ath",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-themed-market-move",
            direction="neutral",
            impact_score=97.0,
            reasoning="rule",
            themes=["黄金"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "华瑞股份股价创下历史新高" not in content


def test_write_text_report_filters_cls_single_stock_limit_down_response_without_theme(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-limit-down-response",
            first_seen_at="2026-04-21T11:07:08+08:00",
            last_seen_at="2026-04-21T11:07:08+08:00",
            canonical_title="股价“一”字跌停 英维克最新回应",
            summary="【股价“一”字跌停 英维克最新回应】财联社4月21日电，液冷龙头股英维克开盘“一”字跌停，股价报108.97元/股，跌幅为10%。英维克方面回应称：“公司毛利率出现下滑，主要是调整了产品结构。公司部分项目周期比较长，一些应收账款回款周期也比较长，因此计提了坏账减值准备。此外，公司财务费用方面有一些汇兑损失。公司目前经营正常，以后续公告为准。”对于经营活动产生的现金流量净额恶化的原因，公司方面解释称，主要原因系报告期供应商款项到期支付与员工薪酬增加所致。",
            source="cls",
            published_at="2026-04-21T11:07:08+08:00",
            url="https://example.com/cls-limit-down-response",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-themed-market-move-keep",
            first_seen_at="2026-04-21T11:08:00+08:00",
            last_seen_at="2026-04-21T11:08:00+08:00",
            canonical_title="液冷服务器概念走强 达实智能等涨停",
            summary="summary",
            source="cls",
            published_at="2026-04-21T11:08:00+08:00",
            url="https://example.com/themed-market-move-keep",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cls-limit-down-response",
            direction="bearish",
            impact_score=74.3,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-themed-market-move-keep",
            direction="neutral",
            impact_score=97.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "股价“一”字跌停 英维克最新回应" not in content
    assert "液冷服务器概念走强 达实智能等涨停" in content


def test_write_text_report_filters_stock_all_time_high_variant_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stock-ath-variant",
            first_seen_at="2026-04-08T09:57:31+08:00",
            last_seen_at="2026-04-08T09:57:31+08:00",
            canonical_title="中际旭创涨超7% 股价创历史新高",
            summary="人民财讯4月8日电，中际旭创涨超7%，股价创历史新高，总市值突破7300亿元。",
            source="stcn",
            published_at="2026-04-08T09:57:31+08:00",
            url="https://example.com/stock-ath-variant",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-themed-market-move-ath-variant",
            first_seen_at="2026-04-08T09:58:00+08:00",
            last_seen_at="2026-04-08T09:58:00+08:00",
            canonical_title="液冷服务器概念走强 达实智能等涨停",
            summary="summary",
            source="stcn",
            published_at="2026-04-08T09:58:00+08:00",
            url="https://example.com/themed-market-move-ath-variant",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stock-ath-variant",
            direction="bullish",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-themed-market-move-ath-variant",
            direction="neutral",
            impact_score=97.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中际旭创涨超7% 股价创历史新高" not in content
    assert "液冷服务器概念走强 达实智能等涨停" in content


def test_write_text_report_filters_neutral_hard_event_without_catalyst_keyword(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-hard-noise",
            first_seen_at="2026-04-02T11:30:00+08:00",
            last_seen_at="2026-04-02T11:30:00+08:00",
            canonical_title="关于第九届董事会第三次会议决议的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-02T11:30:00+08:00",
            url="https://example.com/hard-noise",
            event_type="hard_event",
        ),
        Event(
            event_id="event-hard-catalyst",
            first_seen_at="2026-04-02T11:31:00+08:00",
            last_seen_at="2026-04-02T11:31:00+08:00",
            canonical_title="关于2025年度向特定对象发行A股股票申请获得深圳证券交易所受理的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-02T11:31:00+08:00",
            url="https://example.com/hard-catalyst",
            event_type="hard_event",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-hard-noise",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hard-catalyst",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "关于第九届董事会第三次会议决议的公告" not in content
    assert "关于2025年度向特定对象发行A股股票申请获得深圳证券交易所受理的公告" in content


def test_write_text_report_filters_neutral_fast_news_without_catalyst_keyword(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-noise",
            first_seen_at="2026-04-02T12:50:01+08:00",
            last_seen_at="2026-04-02T12:50:01+08:00",
            canonical_title="王毅同巴林外交大臣扎耶尼通电话",
            summary="巴林方面介绍了海湾合作委员会最新情况，中方表示愿加强沟通协调。",
            source="stcn",
            published_at="2026-04-02T12:50:01+08:00",
            url="https://example.com/fast-noise",
            event_type="fast_news",
        ),
        Event(
            event_id="event-fast-catalyst",
            first_seen_at="2026-04-02T12:28:47+08:00",
            last_seen_at="2026-04-02T12:28:47+08:00",
            canonical_title="礼来口服GLP-1减肥药在美获批上市 已提交中国上市申请",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T12:28:47+08:00",
            url="https://example.com/fast-catalyst",
            event_type="fast_news",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-noise",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-fast-catalyst",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "王毅同巴林外交大臣扎耶尼通电话" not in content
    assert "礼来口服GLP-1减肥药在美获批上市 已提交中国上市申请" in content


def test_write_text_report_filters_stcn_storage_president_appointment_without_hiding_order(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-storage-president-appointment",
            first_seen_at="2026-05-20T09:29:28+08:00",
            last_seen_at="2026-05-20T09:29:28+08:00",
            canonical_title="晶澳科技任命王君生为储能公司总裁",
            summary="人民财讯5月20日电，晶澳科技宣布任命王君生为晶澳储能公司总裁，即刻生效。"
            "此次任命是晶澳科技推进“光储智生态”战略升级的关键一步，也标志着晶澳储能业务进入"
            "专业化、规模化、全球化发展的新阶段。",
            source="stcn",
            published_at="2026-05-20T09:29:28+08:00",
            url="https://example.com/stcn-storage-president-appointment",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-stcn-storage-order",
            first_seen_at="2026-05-20T09:30:28+08:00",
            last_seen_at="2026-05-20T09:30:28+08:00",
            canonical_title="晶澳科技签署储能项目订单合同",
            summary="晶澳科技签署储能项目订单合同。",
            source="stcn",
            published_at="2026-05-20T09:30:28+08:00",
            url="https://example.com/stcn-storage-order",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-storage-president-appointment",
            direction="neutral",
            impact_score=79.0,
            reasoning="rule",
            themes=["储能"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-storage-order",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["储能"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "晶澳科技任命王君生为储能公司总裁" not in content
    assert "晶澳科技签署储能项目订单合同" in content


def test_write_text_report_filters_stcn_space_compute_ecosystem_plan_without_hiding_contract(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-space-compute-ecosystem-plan",
            first_seen_at="2026-05-20T10:57:03+08:00",
            last_seen_at="2026-05-20T10:57:03+08:00",
            canonical_title="优刻得加入上海太空算力产业生态伙伴计划",
            summary="人民财讯5月20日电，据优刻得消息，近日，上海市太空算力产业发展研讨会暨"
            "上海太空算力产业生态伙伴计划成立大会在复旦大学举办，标志着上海在太空算力领域"
            "“高校+科研院所+科技企业”的协同创新机制正式确立。优刻得作为首批成员单位正式加入"
            "上海太空算力产业生态伙伴计划，积极参与产业生态建设，推动产业协同创新与应用落地。",
            source="stcn",
            published_at="2026-05-20T10:57:03+08:00",
            url="https://example.com/stcn-space-compute-ecosystem-plan",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-stcn-space-compute-contract",
            first_seen_at="2026-05-20T10:58:03+08:00",
            last_seen_at="2026-05-20T10:58:03+08:00",
            canonical_title="优刻得签署太空算力项目合同",
            summary="优刻得签署太空算力项目合同。",
            source="stcn",
            published_at="2026-05-20T10:58:03+08:00",
            url="https://example.com/stcn-space-compute-contract",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-space-compute-ecosystem-plan",
            direction="neutral",
            impact_score=79.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-space-compute-contract",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "优刻得加入上海太空算力产业生态伙伴计划" not in content
    assert "优刻得签署太空算力项目合同" in content


def test_write_text_report_keeps_neutral_fast_news_with_market_move_keyword(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-market-move",
            first_seen_at="2026-04-02T09:31:00+08:00",
            last_seen_at="2026-04-02T09:31:00+08:00",
            canonical_title="布伦特原油期货涨幅扩大至6%",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T09:31:00+08:00",
            url="https://example.com/fast-market-move",
            event_type="fast_news",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-market-move",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "布伦特原油期货涨幅扩大至6%" in content


def test_write_text_report_filters_neutral_foreign_index_basket_fast_news(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-foreign-index",
            first_seen_at="2026-04-02T20:16:19+08:00",
            last_seen_at="2026-04-02T20:16:19+08:00",
            canonical_title="欧洲主要股指跌幅扩大",
            summary="欧洲斯托克50指数跌2.46%，英国富时100指数跌0.73%，法国CAC40指数跌1.54%。",
            source="stcn",
            published_at="2026-04-02T20:16:19+08:00",
            url="https://example.com/fast-foreign-index",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-foreign-index",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "欧洲主要股指跌幅扩大" not in content


def test_write_text_report_filters_hang_seng_tech_index_fast_news(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-hk-index",
            first_seen_at="2026-04-08T13:25:55+08:00",
            last_seen_at="2026-04-08T13:25:55+08:00",
            canonical_title="恒生科技指数涨幅扩大至超5%",
            summary="恒生科技指数涨幅扩大至超5%，恒生指数同步走高。",
            source="stcn",
            published_at="2026-04-08T13:25:55+08:00",
            url="https://example.com/fast-hk-index",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-hk-index",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "恒生科技指数涨幅扩大至超5%" not in content


def test_write_text_report_filters_kospi_index_fast_news(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-kospi-index",
            first_seen_at="2026-04-08T14:33:28+08:00",
            last_seen_at="2026-04-08T14:33:28+08:00",
            canonical_title="日韩股市集体收涨 韩国KOSPI指数涨超6%",
            summary="日韩股市集体收涨，韩国KOSPI指数涨超6%。",
            source="stcn",
            published_at="2026-04-08T14:33:28+08:00",
            url="https://example.com/fast-kospi-index",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-kospi-index",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "日韩股市集体收涨 韩国KOSPI指数涨超6%" not in content


def test_write_text_report_filters_nasdaq_china_golden_dragon_index_fast_news(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-golden-dragon-index",
            first_seen_at="2026-04-08T21:38:03+08:00",
            last_seen_at="2026-04-08T21:38:03+08:00",
            canonical_title="纳斯达克中国金龙指数涨超4%",
            summary="纳斯达克中国金龙指数涨超4%。",
            source="stcn",
            published_at="2026-04-08T21:38:03+08:00",
            url="https://example.com/fast-golden-dragon-index",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-golden-dragon-index",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "纳斯达克中国金龙指数涨超4%" not in content


def test_write_text_report_keeps_neutral_ashare_index_fast_news(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-ashare-index",
            first_seen_at="2026-04-02T14:10:00+08:00",
            last_seen_at="2026-04-02T14:10:00+08:00",
            canonical_title="沪指跌幅扩大至2%",
            summary="沪指跌幅扩大至2%，深证成指跌1.8%。",
            source="stcn",
            published_at="2026-04-02T14:10:00+08:00",
            url="https://example.com/fast-ashare-index",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-ashare-index",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "沪指跌幅扩大至2%" in content
    assert "[温度] 沪指跌幅扩大至2%" in content


def test_write_text_report_filters_single_ashare_index_roundup_fast_news(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-ashare-roundup",
            first_seen_at="2026-04-08T15:03:20+08:00",
            last_seen_at="2026-04-08T15:03:20+08:00",
            canonical_title="收评：创业板指涨5.91% AI营销概念大涨",
            summary="创业板指涨5.91%，AI营销概念大涨，算力方向活跃。",
            source="stcn",
            published_at="2026-04-08T15:03:20+08:00",
            url="https://example.com/ashare-roundup",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-ashare-roundup",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["AI应用"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "收评：创业板指涨5.91% AI营销概念大涨" not in content


def test_write_text_report_filters_cls_three_major_indices_roundup_variant(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-three-major-indices-roundup",
            first_seen_at="2026-04-21T13:17:25+08:00",
            last_seen_at="2026-04-21T13:17:25+08:00",
            canonical_title="三大指数全部翻红",
            summary="【三大指数全部翻红】财联社4月21日电，指数午后再度走强，三大指数全部翻红，创业板指、深成指早盘一度跌超1%。特种气体、PCB、算电协同等方向涨幅居前，沪深京三市上涨个股近1900只。",
            source="cls",
            published_at="2026-04-21T13:17:25+08:00",
            url="https://example.com/cls-three-major-indices-roundup",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-cls-themed-market-move-keep",
            first_seen_at="2026-04-21T13:05:55+08:00",
            last_seen_at="2026-04-21T13:05:55+08:00",
            canonical_title="铜箔概念持续走强 方邦股份触及20cm涨停",
            summary="summary",
            source="cls",
            published_at="2026-04-21T13:05:55+08:00",
            url="https://example.com/cls-themed-market-move-keep",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cls-three-major-indices-roundup",
            direction="neutral",
            impact_score=74.3,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-themed-market-move-keep",
            direction="neutral",
            impact_score=74.3,
            reasoning="rule",
            themes=["覆铜板"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "三大指数全部翻红" not in content
    assert "铜箔概念持续走强 方邦股份触及20cm涨停" in content


def test_write_text_report_filters_domestic_futures_roundup_variant_fast_news(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-domestic-futures-variant",
            first_seen_at="2026-04-08T15:04:09+08:00",
            last_seen_at="2026-04-08T15:04:09+08:00",
            canonical_title="国内商品期货多数收跌 液化气跌停",
            summary="国内商品期货多数收跌，液化气跌停。",
            source="stcn",
            published_at="2026-04-08T15:04:09+08:00",
            url="https://example.com/domestic-futures-variant",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-domestic-futures-variant",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "国内商品期货多数收跌 液化气跌停" not in content


def test_write_text_report_filters_domestic_futures_main_contract_roundup_variant(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-domestic-futures-main-contract-roundup",
            first_seen_at="2026-04-17T15:06:31+08:00",
            last_seen_at="2026-04-17T15:06:31+08:00",
            canonical_title="国内商品期货主力合约涨多跌少 集运欧线涨超6%",
            summary="人民财讯4月17日电，国内商品期货主力合约涨多跌少，集运欧线涨超6%。",
            source="stcn",
            published_at="2026-04-17T15:06:31+08:00",
            url="https://example.com/domestic-futures-main-contract-roundup",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-domestic-futures-main-contract-roundup",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "国内商品期货主力合约涨多跌少 集运欧线涨超6%" not in content


def test_write_text_report_filters_broker_allocation_commentary_fast_news(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-broker-allocation",
            first_seen_at="2026-04-08T15:10:24+08:00",
            last_seen_at="2026-04-08T15:10:24+08:00",
            canonical_title="瑞银：近期可采取平衡型配置 避免大幅调仓",
            summary="美伊达成临时停火协议后，国际油价大幅跳水，WTI原油期货价格大跌超10%。瑞银财富管理投资总监办公室指出，投资者可以考虑采取平衡型配置，而非押注地缘政治事件的走向，并避免仓促大幅调整战略资产配置。",
            source="stcn",
            published_at="2026-04-08T15:10:24+08:00",
            url="https://example.com/broker-allocation",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-broker-allocation",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "瑞银：近期可采取平衡型配置 避免大幅调仓" not in content


def test_write_text_report_filters_cninfo_equity_incentive_grant_registration(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-equity-registration",
            first_seen_at="2026-04-09T00:00:00+08:00",
            last_seen_at="2026-04-09T00:00:00+08:00",
            canonical_title="关于2026年股票期权激励计划授予登记完成的公告",
            summary="公司完成2026年股票期权激励计划授予登记。",
            source="cninfo",
            published_at="2026-04-09T00:00:00+08:00",
            url="https://example.com/cninfo-equity-registration",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-equity-registration",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "关于2026年股票期权激励计划授予登记完成的公告" not in content


def test_write_text_report_filters_exchange_equity_incentive_approval_material(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-equity-incentive-approval",
            first_seen_at="2026-05-09T00:00:00+08:00",
            last_seen_at="2026-05-09T00:00:00+08:00",
            canonical_title="中国巨石关于2025年限制性股票激励计划获得批复的公告",
            summary="中国巨石关于2025年限制性股票激励计划获得批复的公告",
            source="sse",
            published_at="2026-05-09T00:00:00+08:00",
            url="https://example.com/sse-equity-incentive-approval",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-sse-equity-incentive-approval",
            direction="bearish",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中国巨石关于2025年限制性股票激励计划获得批复的公告" not in content


def test_write_text_report_filters_cninfo_equity_incentive_vesting_listing_result(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-equity-vesting-result",
            first_seen_at="2026-04-09T00:00:00+08:00",
            last_seen_at="2026-04-09T00:00:00+08:00",
            canonical_title="关于2022、2023、2024年限制性股票激励计划归属结果暨股份上市的公告",
            summary="公司披露限制性股票激励计划归属结果暨股份上市安排。",
            source="cninfo",
            published_at="2026-04-09T00:00:00+08:00",
            url="https://example.com/cninfo-equity-vesting-result",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-equity-vesting-result",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "关于2022、2023、2024年限制性股票激励计划归属结果暨股份上市的公告" not in content


def test_write_text_report_filters_cninfo_equity_incentive_capital_reduction_notice(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-equity-capital-reduction",
            first_seen_at="2026-04-09T00:00:00+08:00",
            last_seen_at="2026-04-09T00:00:00+08:00",
            canonical_title="关于回购注销限制性股票减资暨通知债权人的公告",
            summary="公司披露回购注销限制性股票减资暨通知债权人事项。",
            source="cninfo",
            published_at="2026-04-09T00:00:00+08:00",
            url="https://example.com/cninfo-equity-capital-reduction",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-equity-capital-reduction",
            direction="bearish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "关于回购注销限制性股票减资暨通知债权人的公告" not in content


def test_write_text_report_keeps_reorganization_risk_cninfo_event(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-reorganization-risk",
            first_seen_at="2026-04-09T00:00:00+08:00",
            last_seen_at="2026-04-09T00:00:00+08:00",
            canonical_title="美克家居关于被债权人申请重整及预重整的专项自查报告",
            summary="公司被债权人申请重整及预重整，相关事项存在不确定性。",
            source="cninfo",
            published_at="2026-04-09T00:00:00+08:00",
            url="https://example.com/cninfo-reorganization-risk",
            event_type="hard_event",
            event_subtype="reorganization_risk",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-reorganization-risk",
            direction="bearish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "美克家居关于被债权人申请重整及预重整的专项自查报告" in content


def test_write_text_report_keeps_bankruptcy_liquidation_application_event(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-bankruptcy-liquidation",
            first_seen_at="2026-04-13T00:00:00+08:00",
            last_seen_at="2026-04-13T00:00:00+08:00",
            canonical_title="关于公司下属公司申请破产清算的公告",
            summary="公司下属公司申请破产清算，相关事项存在不确定性。",
            source="sse",
            published_at="2026-04-13T00:00:00+08:00",
            url="https://example.com/sse-bankruptcy-liquidation",
            event_type="hard_event",
            event_subtype="reorganization_risk",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-sse-bankruptcy-liquidation",
            direction="bearish",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "关于公司下属公司申请破产清算的公告" in content


def test_write_text_report_downgrades_ashare_index_fast_news_below_themed_events(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-ashare-index",
            first_seen_at="2026-04-02T14:10:00+08:00",
            last_seen_at="2026-04-02T14:10:00+08:00",
            canonical_title="创业板指涨超4%",
            summary="创业板指涨超4%，沪指涨1.2%，深证成指涨2.8%。",
            source="stcn",
            published_at="2026-04-02T14:10:00+08:00",
            url="https://example.com/fast-ashare-index",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-themed",
            first_seen_at="2026-04-02T14:11:00+08:00",
            last_seen_at="2026-04-02T14:11:00+08:00",
            canonical_title="液冷服务器概念走强 达实智能等涨停",
            summary="液冷服务器概念走强，达实智能等涨停。",
            source="stcn",
            published_at="2026-04-02T14:11:00+08:00",
            url="https://example.com/themed-event",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-ashare-index",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-themed",
            direction="bullish",
            impact_score=80.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "[温度] 创业板指涨超4%" in content
    assert content.index("液冷服务器概念走强 达实智能等涨停") < content.index("创业板指涨超4%")


def test_write_text_report_keeps_themed_foreign_single_stock_market_move_in_global_section(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-foreign-themed-market-move",
            first_seen_at="2026-04-24T22:33:25+08:00",
            last_seen_at="2026-04-24T22:33:25+08:00",
            canonical_title="礼来新一代口服减肥药Foundayo开局遇冷股价跌超4% 诺和诺德涨6%",
            summary="礼来股价跌超4%，诺和诺德涨6%。",
            source="cls",
            published_at="2026-04-24T22:33:25+08:00",
            url="https://example.com/foreign-themed-market-move",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-foreign-themed-market-move",
            direction="neutral",
            impact_score=99.3,
            reasoning="rule",
            themes=["创新药"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert content.index("[全球市场与商品]") < content.index("礼来新一代口服减肥药Foundayo开局遇冷")


def test_write_text_report_filters_current_live_irm_question_only_tail_noise(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-stock-price-ma",
            first_seen_at="2026-04-28T20:45:42+08:00",
            last_seen_at="2026-04-28T20:45:42+08:00",
            canonical_title="证通电子：公司的涨幅远远落后市场上其它算力股，主要原因除了业绩，可能跟公司在智算投入太小有关。最近安诺其收购算力公司大涨，公司有没有并购计划？",
            summary="问题：公司的涨幅远远落后市场上其它算力股，公司有没有并购计划？",
            source="irm_cninfo",
            published_at="2026-04-28T20:45:42+08:00",
            url="https://example.com/irm-stock-price-ma",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-irm-robot-liquid-cooling-plan",
            first_seen_at="2026-04-28T20:45:34+08:00",
            last_seen_at="2026-04-28T20:45:34+08:00",
            canonical_title="高澜股份：你好，人形机器人未来市场巨大，公司是否计划开发在人形机器人领域应用的液冷方案?",
            summary="问题：人形机器人未来市场巨大，公司是否计划开发在人形机器人领域应用的液冷方案? 回复：尊敬的投资者，您好！公司产品暂未应用于人形机器人领域。公司将依托现有液冷技术储备，持续跟踪新兴领域应用需求，适时探索相关技术与产品布局。感谢您的关注！",
            source="irm_cninfo",
            published_at="2026-04-28T20:45:34+08:00",
            url="https://example.com/irm-robot-liquid-cooling-plan",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-gross-margin-complaint",
            first_seen_at="2026-04-28T20:45:42+08:00",
            last_seen_at="2026-04-28T20:45:42+08:00",
            canonical_title="东山精密：公司2026年年报显示电子电路产品的毛利率为17.59%，而2026年深南电路PCB业务的毛利率36.91%、沪电股份PCB业务的毛利率29.73%，公司PCB的毛利率处于消费电子PCB毛利率水平，并没有体现AI服务器PCB高毛利率水平，这是为什么？公司后续有什么改善计划？",
            summary="问题：公司PCB毛利率为什么没有体现AI服务器PCB高毛利率水平？公司后续有什么改善计划？",
            source="irm_cninfo",
            published_at="2026-04-28T20:45:42+08:00",
            url="https://example.com/irm-gross-margin-complaint",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-reduction-reason",
            first_seen_at="2026-04-28T20:45:34+08:00",
            last_seen_at="2026-04-28T20:45:34+08:00",
            canonical_title="博深股份：大股东及高管持续减持的原因？",
            summary="问题：大股东及高管持续减持的原因？ 回复：您好，公司控股股东和高级管理人员近期未减持公司股份，公司将严格按照相关规定履行信息披露义务，谢谢。",
            source="irm_cninfo",
            published_at="2026-04-28T20:45:34+08:00",
            url="https://example.com/irm-reduction-reason",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-keep-substantive-order",
            first_seen_at="2026-04-28T20:46:42+08:00",
            last_seen_at="2026-04-28T20:46:42+08:00",
            canonical_title="易普力：据三峡集团招标网公示，你公司是中标三峡水运新通道项目了吗？请介绍一下具体情况",
            summary="问题：据三峡集团招标网公示，你公司是中标三峡水运新通道项目了吗？请介绍一下具体情况 回复：您好！公司在三峡水运新通道项目混装炸药及爆破作业服务集中采购项目第Ⅰ、Ⅱ标段场内、场外方案的中标候选人中均排第一。",
            source="irm_cninfo",
            published_at="2026-04-28T20:46:42+08:00",
            url="https://example.com/irm-keep-substantive-order",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-stock-price-ma", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-robot-liquid-cooling-plan", direction="neutral", impact_score=100.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-irm-gross-margin-complaint", direction="neutral", impact_score=100.0, reasoning="rule", themes=["PCB"], triggered=True),
        EventAnalysis(event_id="event-irm-reduction-reason", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-keep-substantive-order", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "公司的涨幅远远落后市场上其它算力股" not in content
    assert "公司是否计划开发在人形机器人领域应用的液冷方案" not in content
    assert "公司PCB的毛利率处于消费电子PCB毛利率水平" not in content
    assert "大股东及高管持续减持的原因？" not in content
    assert "易普力：据三峡集团招标网公示，你公司是中标三峡水运新通道项目了吗？请介绍一下具体情况" in content


def test_write_text_report_filters_current_live_exchange_annual_material_cluster_with_themes(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-board-resolution",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="徐工机械：第十届董事会第二次会议决议公告",
            summary="summary",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/board-resolution",
            event_type="hard_event",
            event_subtype="board_resolution",
        ),
        Event(
            event_id="event-board-resolution-without-meeting",
            first_seen_at="2026-04-28T00:00:00+08:00",
            last_seen_at="2026-04-28T00:00:00+08:00",
            canonical_title="保利发展控股集团股份有限公司2026年第4次临时董事会决议公告",
            summary="summary",
            source="sse",
            published_at="2026-04-28T00:00:00+08:00",
            url="https://example.com/board-resolution-without-meeting",
            event_type="hard_event",
            event_subtype="board_resolution",
        ),
        Event(
            event_id="event-accounting-policy",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="徐工机械：关于会计政策变更的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/accounting-policy",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-impairment",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="徐工机械：关于计提减值准备的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/impairment",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-buyback-cancel-result",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="徐工机械：关于回购公司股份用于注销的结果暨股份变动公告",
            summary="summary",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/buyback-cancel-result",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-fund-use-report",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="徐工机械：2025年度募集资金存放、管理与使用情况的专项报告",
            summary="summary",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/fund-use-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-buyback-report",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="新宝股份：关于回购公司部分社会公众股份的报告书",
            summary="summary",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/buyback-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sell-buyback-plan",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="桂发祥：关于出售已回购股份计划的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/sell-buyback-plan",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-equity-incentive-buyback-cancel",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="*ST新研：关于回购注销2023年限制性股票激励计划授予的部分限制性股票的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/equity-incentive-buyback-cancel",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-esg-en",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="徐工机械：XCMGConstructionMachineryCo., Ltd.2025Environmental,Social,andGovernance(ESG)Report",
            summary="summary",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/esg-en",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-esg-cn",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="徐工机械：2025年度环境、社会与治理（ESG）报告",
            summary="summary",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/esg-cn",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="华大基因：关于收购重庆新一产生命科技有限公司100%股权暨关联交易的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/keep-acquisition",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-board-resolution", direction="neutral", impact_score=100.0, reasoning="rule", themes=["工程机械"], triggered=True),
        EventAnalysis(event_id="event-board-resolution-without-meeting", direction="neutral", impact_score=100.0, reasoning="rule", themes=["房地产"], triggered=True),
        EventAnalysis(event_id="event-accounting-policy", direction="neutral", impact_score=100.0, reasoning="rule", themes=["工程机械"], triggered=True),
        EventAnalysis(event_id="event-impairment", direction="neutral", impact_score=100.0, reasoning="rule", themes=["工程机械"], triggered=True),
        EventAnalysis(event_id="event-buyback-cancel-result", direction="neutral", impact_score=100.0, reasoning="rule", themes=["工程机械"], triggered=True),
        EventAnalysis(event_id="event-fund-use-report", direction="neutral", impact_score=100.0, reasoning="rule", themes=["工程机械"], triggered=True),
        EventAnalysis(event_id="event-buyback-report", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sell-buyback-plan", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-equity-incentive-buyback-cancel", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-esg-en", direction="neutral", impact_score=100.0, reasoning="rule", themes=["工程机械"], triggered=True),
        EventAnalysis(event_id="event-esg-cn", direction="neutral", impact_score=100.0, reasoning="rule", themes=["工程机械"], triggered=True),
        EventAnalysis(event_id="event-keep-acquisition", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "第十届董事会第二次会议决议公告" not in content
    assert "保利发展控股集团股份有限公司2026年第4次临时董事会决议公告" not in content
    assert "关于会计政策变更的公告" not in content
    assert "关于计提减值准备的公告" not in content
    assert "关于回购公司股份用于注销的结果暨股份变动公告" not in content
    assert "募集资金存放、管理与使用情况的专项报告" not in content
    assert "关于回购公司部分社会公众股份的报告书" not in content
    assert "关于出售已回购股份计划的公告" not in content
    assert "回购注销2023年限制性股票激励计划授予的部分限制性股票" not in content
    assert "Environmental,Social,andGovernance(ESG)Report" not in content
    assert "2025年度环境、社会与治理（ESG）报告" not in content
    assert "华大基因：关于收购重庆新一产生命科技有限公司100%股权暨关联交易的公告" in content


def test_write_text_report_filters_foreign_market_move_even_if_analysis_has_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-us-market",
            first_seen_at="2026-04-02T21:32:39+08:00",
            last_seen_at="2026-04-02T21:32:39+08:00",
            canonical_title="美股三大指数集体低开 特斯拉跌超3%",
            summary="美股三大指数集体低开。存储芯片板块大跌，闪迪跌超5%，美光科技跌超5%。",
            source="stcn",
            published_at="2026-04-02T21:32:39+08:00",
            url="https://example.com/fast-us-market",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-fast-oil-keep",
            first_seen_at="2026-04-02T21:29:43+08:00",
            last_seen_at="2026-04-02T21:29:43+08:00",
            canonical_title="WTI原油期货涨超13%",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T21:29:43+08:00",
            url="https://example.com/fast-oil-keep",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-us-market",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-fast-oil-keep",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "WTI原油期货涨超13%" in content
    assert "美股三大指数集体低开 特斯拉跌超3%" not in content


def test_write_text_report_filters_domestic_futures_night_session_roundup(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-night-session",
            first_seen_at="2026-04-02T23:07:31+08:00",
            last_seen_at="2026-04-02T23:07:31+08:00",
            canonical_title="国内期货市场夜盘收盘多数下跌 沥青跌超2%",
            summary="人民财讯4月2日电，国内期货市场夜盘收盘多数下跌。沥青跌超2%，对二甲苯跌超1%。燃油涨超3%，甲醇涨超1%。",
            source="stcn",
            published_at="2026-04-02T23:07:31+08:00",
            url="https://example.com/night-session-roundup",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-fast-oil-keep",
            first_seen_at="2026-04-02T21:29:43+08:00",
            last_seen_at="2026-04-02T21:29:43+08:00",
            canonical_title="WTI原油期货涨超13%",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T21:29:43+08:00",
            url="https://example.com/fast-oil-keep",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-night-session",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-fast-oil-keep",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "WTI原油期货涨超13%" in content
    assert "国内期货市场夜盘收盘多数下跌 沥青跌超2%" not in content


def test_write_text_report_filters_domestic_futures_night_session_mixed_roundup(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-night-session-mixed",
            first_seen_at="2026-04-09T23:05:30+08:00",
            last_seen_at="2026-04-09T23:05:30+08:00",
            canonical_title="国内期货夜盘收盘涨跌不一 焦煤跌超4%",
            summary="人民财讯4月9日电，国内期货夜盘收盘涨跌不一，焦煤跌超4%，玻璃、纯碱跌超2%。",
            source="stcn",
            published_at="2026-04-09T23:05:30+08:00",
            url="https://example.com/night-session-mixed-roundup",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-fast-oil-keep-2",
            first_seen_at="2026-04-09T23:06:30+08:00",
            last_seen_at="2026-04-09T23:06:30+08:00",
            canonical_title="WTI原油期货涨超13%",
            summary="summary",
            source="stcn",
            published_at="2026-04-09T23:06:30+08:00",
            url="https://example.com/fast-oil-keep-2",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-night-session-mixed",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-fast-oil-keep-2",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "WTI原油期货涨超13%" in content
    assert "国内期货夜盘收盘涨跌不一 焦煤跌超4%" not in content


def test_write_text_report_filters_cls_domestic_futures_night_open_roundup_without_hiding_themed_market_move(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-futures-night-open-roundup",
            first_seen_at="2026-04-20T21:00:01+08:00",
            last_seen_at="2026-04-20T21:00:01+08:00",
            canonical_title="财联社4月20日电，国内商品期货夜盘开盘涨跌不一，原油涨2.36%，燃油涨2.2%，焦煤涨1.53%，液化气涨1.28%，沪银跌1.85%，纯苯跌0.84%，沪金跌0.68%，沪铝跌0.28%。",
            summary="财联社4月20日电，国内商品期货夜盘开盘涨跌不一，原油涨2.36%，燃油涨2.2%，焦煤涨1.53%，液化气涨1.28%，沪银跌1.85%，纯苯跌0.84%，沪金跌0.68%，沪铝跌0.28%。",
            source="cls",
            published_at="2026-04-20T21:00:01+08:00",
            url="https://www.cls.cn/detail/2349790",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-cls-themed-oil-market-move",
            first_seen_at="2026-04-20T21:01:01+08:00",
            last_seen_at="2026-04-20T21:01:01+08:00",
            canonical_title="WTI原油期货日内涨超3%",
            summary="summary",
            source="cls",
            published_at="2026-04-20T21:01:01+08:00",
            url="https://example.com/cls-themed-oil-market-move",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-cls-futures-night-open-roundup", direction="neutral", impact_score=99.3, reasoning="rule", themes=["油气"], triggered=True),
        EventAnalysis(event_id="event-cls-themed-oil-market-move", direction="neutral", impact_score=99.3, reasoning="rule", themes=["油气"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "WTI原油期货日内涨超3%" in content
    assert "财联社4月20日电，国内商品期货夜盘开盘涨跌不一" not in content


def test_write_text_report_filters_domestic_futures_night_session_up_roundup(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-night-session-up",
            first_seen_at="2026-04-16T23:05:01+08:00",
            last_seen_at="2026-04-16T23:05:01+08:00",
            canonical_title="国内期货夜盘收盘多数上涨 甲醇等涨超2%",
            summary="人民财讯4月16日电，国内期货夜盘收盘多数上涨，甲醇等涨超2%。",
            source="stcn",
            published_at="2026-04-16T23:05:01+08:00",
            url="https://example.com/night-session-up-roundup",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-fast-oil-keep-3",
            first_seen_at="2026-04-16T23:06:01+08:00",
            last_seen_at="2026-04-16T23:06:01+08:00",
            canonical_title="WTI原油期货涨超13%",
            summary="summary",
            source="stcn",
            published_at="2026-04-16T23:06:01+08:00",
            url="https://example.com/fast-oil-keep-3",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-night-session-up",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-fast-oil-keep-3",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "WTI原油期货涨超13%" in content
    assert "国内期货夜盘收盘多数上涨 甲醇等涨超2%" not in content


def test_write_text_report_filters_domestic_futures_opening_roundup(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-opening-roundup",
            first_seen_at="2026-04-03T09:01:42+08:00",
            last_seen_at="2026-04-03T09:01:42+08:00",
            canonical_title="国内期货开盘涨跌不一 燃油涨超4%",
            summary="人民财讯4月3日电，国内期货开盘涨跌不一，燃油涨超4%，原油、低硫油涨超3%，线材涨超2%；白银、沥青等跌超1%，生猪、黄金等小幅下跌。",
            source="stcn",
            published_at="2026-04-03T09:01:42+08:00",
            url="https://example.com/opening-roundup",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-fast-oil-keep",
            first_seen_at="2026-04-03T09:02:42+08:00",
            last_seen_at="2026-04-03T09:02:42+08:00",
            canonical_title="WTI原油期货涨超13%",
            summary="summary",
            source="stcn",
            published_at="2026-04-03T09:02:42+08:00",
            url="https://example.com/fast-oil-keep",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-opening-roundup",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-fast-oil-keep",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "WTI原油期货涨超13%" in content
    assert "国内期货开盘涨跌不一 燃油涨超4%" not in content


def test_write_text_report_filters_hk_listing_application_fast_news_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-hk-listing",
            first_seen_at="2026-04-02T21:59:24+08:00",
            last_seen_at="2026-04-02T21:59:24+08:00",
            canonical_title="新希望乳业股份有限公司向港交所提交上市申请书",
            summary="据港交所披露，新希望乳业股份有限公司向港交所提交上市申请书。",
            source="stcn",
            published_at="2026-04-02T21:59:24+08:00",
            url="https://example.com/fast-hk-listing",
            event_type="fast_news",
            event_subtype="regulatory_approval",
        ),
        Event(
            event_id="event-fast-power-keep",
            first_seen_at="2026-04-02T20:59:03+08:00",
            last_seen_at="2026-04-02T20:59:03+08:00",
            canonical_title="中国能建与华北电力大学签署战略合作协议",
            summary="双方将围绕构建新型能源体系和新型电力系统深化合作。",
            source="stcn",
            published_at="2026-04-02T20:59:03+08:00",
            url="https://example.com/fast-power-keep",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-hk-listing",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-fast-power-keep",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["电力资源"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中国能建与华北电力大学签署战略合作协议" in content
    assert "新希望乳业股份有限公司向港交所提交上市申请书" not in content


def test_write_text_report_filters_repeat_hk_listing_application_fast_news_without_hiding_order_contract(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-repeat-hk-listing",
            first_seen_at="2026-04-16T22:29:55+08:00",
            last_seen_at="2026-04-16T22:29:55+08:00",
            canonical_title="财联社4月16日电，利弗莫尔证券显示，珠海精实测控技术股份有限公司再次向港交所提交上市申请书，联席保荐人为中金公司、浦银国际。",
            summary="summary",
            source="cls",
            published_at="2026-04-16T22:29:55+08:00",
            url="https://example.com/fast-repeat-hk-listing",
            event_type="fast_news",
            event_subtype="regulatory_approval",
        ),
        Event(
            event_id="event-keep-order-contract",
            first_seen_at="2026-04-16T22:18:36+08:00",
            last_seen_at="2026-04-16T22:18:36+08:00",
            canonical_title="财联社4月16日电，印度石油部表示，已敲定80万吨液化石油气进口订单，相关供应货物正在运往印度途中。",
            summary="summary",
            source="cls",
            published_at="2026-04-16T22:18:36+08:00",
            url="https://example.com/keep-order-contract",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-repeat-hk-listing",
            direction="neutral",
            impact_score=74.3,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-order-contract",
            direction="neutral",
            impact_score=99.3,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "财联社4月16日电，利弗莫尔证券显示，珠海精实测控技术股份有限公司再次向港交所提交上市申请书" not in content
    assert "财联社4月16日电，印度石油部表示，已敲定80万吨液化石油气进口订单，相关供应货物正在运往印度途中。" in content


def test_write_text_report_filters_cls_after_hours_earnings_digest_without_hiding_real_guidance(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-after-hours-earnings-digest",
            first_seen_at="2026-04-16T22:37:31+08:00",
            last_seen_at="2026-04-16T22:37:31+08:00",
            canonical_title="盘后A股上市公司重点业绩公告精选",
            summary="【盘后A股上市公司重点业绩公告精选】财联社4月16日电，据财联社不完全统计，截至发稿，盘后包括中际旭创、赣锋锂业、华友钴业、宏和科技、湖南黄金、东方雨虹、永辉超市、拉卡拉、株冶集团、银邦股份、海通发展、豫园股份、杰瑞股份、金徽酒在内的多家A股上市公司发布2026年一季度业绩预告/报告。其中，中际旭创公告，一季度净利润同比增长262%。小财注：龙蟠科技、宁波富邦、鼎通科技昨日盘后发布一季度业绩预告或一季度报告，今日均收盘涨停。",
            source="cls",
            published_at="2026-04-16T22:37:31+08:00",
            url="https://example.com/cls-after-hours-earnings-digest",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-keep-guidance",
            first_seen_at="2026-04-16T22:05:36+08:00",
            last_seen_at="2026-04-16T22:05:36+08:00",
            canonical_title="【公告全知道】算力+绿色电力+储能+数据中心！公司拟245亿元投建算电协同项目",
            summary="summary",
            source="cls",
            published_at="2026-04-16T22:05:36+08:00",
            url="https://example.com/keep-guidance",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cls-after-hours-earnings-digest",
            direction="bullish",
            impact_score=74.3,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-guidance",
            direction="neutral",
            impact_score=99.3,
            reasoning="rule",
            themes=["算力", "储能"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "盘后A股上市公司重点业绩公告精选" not in content
    assert "【公告全知道】算力+绿色电力+储能+数据中心！公司拟245亿元投建算电协同项目" in content


def test_write_text_report_filters_stcn_shareholder_reduction_fast_news_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-reduction",
            first_seen_at="2026-04-02T22:09:04+08:00",
            last_seen_at="2026-04-02T22:09:04+08:00",
            canonical_title="安靠智电：实控人等拟合计减持不超2.01%公司股份",
            summary="安靠智电公告称实控人等拟合计减持不超过2.01%公司股份。",
            source="stcn",
            published_at="2026-04-02T22:09:04+08:00",
            url="https://example.com/fast-reduction",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-fast-oil-keep-2",
            first_seen_at="2026-04-02T21:29:43+08:00",
            last_seen_at="2026-04-02T21:29:43+08:00",
            canonical_title="WTI原油期货涨超13%",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T21:29:43+08:00",
            url="https://example.com/fast-oil-keep-2",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-reduction",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-fast-oil-keep-2",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "WTI原油期货涨超13%" in content
    assert "安靠智电：实控人等拟合计减持不超2.01%公司股份" not in content


def test_write_text_report_filters_bullish_general_fast_news_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-general",
            first_seen_at="2026-04-02T19:06:08+08:00",
            last_seen_at="2026-04-02T19:06:08+08:00",
            canonical_title="中国人民银行召开2026年会计财务工作会议",
            summary="会议提出推进财会监督体系建设。",
            source="stcn",
            published_at="2026-04-02T19:06:08+08:00",
            url="https://example.com/fast-general",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-fast-themed",
            first_seen_at="2026-04-02T17:45:53+08:00",
            last_seen_at="2026-04-02T17:45:53+08:00",
            canonical_title="乘联分会：3月全国乘用车厂商新能源批发预估112万辆",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T17:45:53+08:00",
            url="https://example.com/fast-themed",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-general",
            direction="bullish",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-fast-themed",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["新能源车"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "乘联分会：3月全国乘用车厂商新能源批发预估112万辆" in content
    assert "中国人民银行召开2026年会计财务工作会议" not in content


def test_write_text_report_filters_bullish_business_guidance_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-guidance",
            first_seen_at="2026-04-02T19:00:04+08:00",
            last_seen_at="2026-04-02T19:00:04+08:00",
            canonical_title="宇通重工：2025年净利润同比增长36.25% 拟10派4元",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T19:00:04+08:00",
            url="https://example.com/fast-guidance",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-fast-theme",
            first_seen_at="2026-04-02T17:49:06+08:00",
            last_seen_at="2026-04-02T17:49:06+08:00",
            canonical_title="2026清明档电影片单发布",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T17:49:06+08:00",
            url="https://example.com/fast-theme",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-guidance",
            direction="bullish",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-fast-theme",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["文旅"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "2026清明档电影片单发布" in content
    assert "宇通重工：2025年净利润同比增长36.25% 拟10派4元" not in content


def test_write_text_report_filters_fast_news_when_catalyst_only_appears_in_summary(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-earnings-noise",
            first_seen_at="2026-04-02T20:38:00+08:00",
            last_seen_at="2026-04-02T20:38:00+08:00",
            canonical_title="国瑞科技：2025年亏损5502.24万元",
            summary="行业竞争加剧导致传统市场盈利承压，公司在部分常规船型项目中接受了较低利润率的订单。",
            source="stcn",
            published_at="2026-04-02T20:38:00+08:00",
            url="https://example.com/fast-earnings-noise",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-fast-contract",
            first_seen_at="2026-04-02T20:40:00+08:00",
            last_seen_at="2026-04-02T20:40:00+08:00",
            canonical_title="中科曙光：签订10亿元算力订单",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T20:40:00+08:00",
            url="https://example.com/fast-contract",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-earnings-noise",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-fast-contract",
            direction="bullish",
            impact_score=95.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中科曙光：签订10亿元算力订单" in content
    assert "国瑞科技：2025年亏损5502.24万元" not in content


def test_write_text_report_filters_bullish_company_update_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-fast-company-update",
            first_seen_at="2026-04-02T18:47:56+08:00",
            last_seen_at="2026-04-02T18:47:56+08:00",
            canonical_title="伊朗实施“真实承诺-4”第90波打击行动 袭击美相关金属产业设施",
            summary="当地媒体称袭击针对钢铁和铝业设施。",
            source="stcn",
            published_at="2026-04-02T18:47:56+08:00",
            url="https://example.com/fast-company-update",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-fast-oil",
            first_seen_at="2026-04-02T18:57:27+08:00",
            last_seen_at="2026-04-02T18:57:27+08:00",
            canonical_title="布伦特原油期货涨幅扩大至8%",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T18:57:27+08:00",
            url="https://example.com/fast-oil",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-fast-company-update",
            direction="bullish",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-fast-oil",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "布伦特原油期货涨幅扩大至8%" in content
    assert "伊朗实施“真实承诺-4”第90波打击行动 袭击美相关金属产业设施" not in content


def test_write_text_report_demotes_cninfo_material_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-material",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="关于注销2023年股票期权激励计划部分股票期权的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-material",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-stcn-update",
            first_seen_at="2026-04-02T17:55:30+08:00",
            last_seen_at="2026-04-02T17:55:30+08:00",
            canonical_title="罗博特科：与一家于纳斯达克上市的公司签署3570万美元订单",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T17:55:30+08:00",
            url="https://example.com/stcn-update",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-material",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-update",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "关于注销2023年股票期权激励计划部分股票期权的公告" in content
    assert "罗博特科：与一家于纳斯达克上市的公司签署3570万美元订单" in content
    assert content.index("罗博特科：与一家于纳斯达克上市的公司签署3570万美元订单") < content.index(
        "关于注销2023年股票期权激励计划部分股票期权的公告"
    )


def test_write_text_report_filters_cninfo_progress_disclosure_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-progress",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="贵州茅台关于回购股份实施进展的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-progress",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-robot",
            first_seen_at="2026-04-02T17:54:26+08:00",
            last_seen_at="2026-04-02T17:54:26+08:00",
            canonical_title="步科股份：2025年净利润同比增长48.25% 拟10派3元",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T17:54:26+08:00",
            url="https://example.com/stcn-robot",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-progress",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-robot",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["机器人"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "步科股份：2025年净利润同比增长48.25% 拟10派3元" in content
    assert "贵州茅台关于回购股份实施进展的公告" not in content


def test_write_text_report_filters_cninfo_equity_unlock_condition_notice_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-equity-unlock",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="关于2024年限制性股票与股票期权激励计划首次授予限制性股票第一个解除限售期解除限售条件及股票期权第一个行权期行权条件成就的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/cninfo-equity-unlock",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-stcn-storage",
            first_seen_at="2026-04-09T18:46:06+08:00",
            last_seen_at="2026-04-09T18:46:06+08:00",
            canonical_title="德业股份：一季度净利同比预增55.91%—70.08%，储能逆变器、储能电池包产品销售收入同比大增",
            summary="summary",
            source="stcn",
            published_at="2026-04-09T18:46:06+08:00",
            url="https://example.com/stcn-storage",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-equity-unlock",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-storage",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["储能"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "德业股份：一季度净利同比预增55.91%—70.08%，储能逆变器、储能电池包产品销售收入同比大增" in content
    assert "关于2024年限制性股票与股票期权激励计划首次授予限制性股票第一个解除限售期解除限售条件及股票期权第一个行权期行权条件成就的公告" not in content


def test_write_text_report_filters_cninfo_equity_first_grant_notice_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-equity-first-grant",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="关于向2026年限制性股票激励计划激励对象首次授予限制性股票的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/cninfo-equity-first-grant",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-stcn-storage-2",
            first_seen_at="2026-04-09T18:46:06+08:00",
            last_seen_at="2026-04-09T18:46:06+08:00",
            canonical_title="德业股份：一季度净利同比预增55.91%—70.08%，储能逆变器、储能电池包产品销售收入同比大增",
            summary="summary",
            source="stcn",
            published_at="2026-04-09T18:46:06+08:00",
            url="https://example.com/stcn-storage-2",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-equity-first-grant",
            direction="bearish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-storage-2",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["储能"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "德业股份：一季度净利同比预增55.91%—70.08%，储能逆变器、储能电池包产品销售收入同比大增" in content
    assert "关于向2026年限制性股票激励计划激励对象首次授予限制性股票的公告" not in content


def test_write_text_report_filters_cninfo_creditor_notice_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-creditor",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="江苏龙蟠科技集团股份有限公司关于注销已回购股份暨通知债权人的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-creditor",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-nev",
            first_seen_at="2026-04-02T17:45:53+08:00",
            last_seen_at="2026-04-02T17:45:53+08:00",
            canonical_title="乘联分会：3月全国乘用车厂商新能源批发预估112万辆",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T17:45:53+08:00",
            url="https://example.com/stcn-nev",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-creditor",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-nev",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["新能源车"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "乘联分会：3月全国乘用车厂商新能源批发预估112万辆" in content
    assert "江苏龙蟠科技集团股份有限公司关于注销已回购股份暨通知债权人的公告" not in content


def test_write_text_report_filters_cninfo_share_increase_result_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-share-increase-result",
            first_seen_at="2026-04-09T00:00:00+08:00",
            last_seen_at="2026-04-09T00:00:00+08:00",
            canonical_title="晋西车轴关于控股股东增持公司股份结果公告",
            summary="公司披露控股股东增持公司股份结果。",
            source="cninfo",
            published_at="2026-04-09T00:00:00+08:00",
            url="https://example.com/cninfo-share-increase-result",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-battery-keep",
            first_seen_at="2026-04-08T19:41:11+08:00",
            last_seen_at="2026-04-08T19:41:11+08:00",
            canonical_title="中伟新材：一季度净利同比预增72.32%—91.82%",
            summary="summary",
            source="stcn",
            published_at="2026-04-08T19:41:11+08:00",
            url="https://example.com/stcn-battery-keep",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-share-increase-result",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-battery-keep",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["锂电池"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中伟新材：一季度净利同比预增72.32%—91.82%" in content
    assert "晋西车轴关于控股股东增持公司股份结果公告" not in content


def test_write_text_report_filters_cninfo_shareholder_query_letter_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-query-letter",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="洲际油气股份有限公司关于收到中证中小投资者服务中心《股东质询建议函》的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/cninfo-query-letter",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-oil-keep",
            first_seen_at="2026-04-10T20:33:41+08:00",
            last_seen_at="2026-04-10T20:33:41+08:00",
            canonical_title="公告精选：中国动力、沃格光电澄清媒体报道；焦作万方等一季度净利同比大幅预增",
            summary="summary",
            source="stcn",
            published_at="2026-04-10T20:33:41+08:00",
            url="https://example.com/stcn-oil-keep",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-query-letter",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-oil-keep",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["算力", "半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "公告精选：中国动力、沃格光电澄清媒体报道；焦作万方等一季度净利同比大幅预增" in content
    assert "股东质询建议函" not in content


def test_write_text_report_filters_cninfo_cancel_shareholder_meeting_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-cancel-shareholder-meeting",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="洲际油气股份有限公司关于取消2026年第一次临时股东会的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/cninfo-cancel-shareholder-meeting",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-real-estate-keep-2",
            first_seen_at="2026-04-10T20:20:32+08:00",
            last_seen_at="2026-04-10T20:20:32+08:00",
            canonical_title="保利发展：3月签约金额260.33亿元 同比减少10.28%",
            summary="summary",
            source="stcn",
            published_at="2026-04-10T20:20:32+08:00",
            url="https://example.com/stcn-real-estate-keep-2",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-cancel-shareholder-meeting",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-real-estate-keep-2",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["房地产"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "保利发展：3月签约金额260.33亿元 同比减少10.28%" in content
    assert "取消2026年第一次临时股东会" not in content


def test_write_text_report_filters_cninfo_share_increase_completion_notice_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-share-increase-completion",
            first_seen_at="2026-04-09T00:00:00+08:00",
            last_seen_at="2026-04-09T00:00:00+08:00",
            canonical_title="关于控股股东增持公司股份触及1%整数倍暨增持计划实施完成的公告",
            summary="公司披露控股股东增持公司股份触及1%整数倍暨增持计划实施完成。",
            source="cninfo",
            published_at="2026-04-09T00:00:00+08:00",
            url="https://example.com/cninfo-share-increase-completion",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-battery-keep-2",
            first_seen_at="2026-04-08T19:41:11+08:00",
            last_seen_at="2026-04-08T19:41:11+08:00",
            canonical_title="中伟新材：一季度净利同比预增72.32%—91.82%",
            summary="summary",
            source="stcn",
            published_at="2026-04-08T19:41:11+08:00",
            url="https://example.com/stcn-battery-keep-2",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-share-increase-completion",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-battery-keep-2",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["锂电池"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中伟新材：一季度净利同比预增72.32%—91.82%" in content
    assert "关于控股股东增持公司股份触及1%整数倍暨增持计划实施完成的公告" not in content


def test_write_text_report_filters_cninfo_shareholder_reduction_predisclosure_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-reduction-predisclosure",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="关于5%以上股东减持股份的预披露公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-reduction-predisclosure",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-power-keep-2",
            first_seen_at="2026-04-02T20:59:03+08:00",
            last_seen_at="2026-04-02T20:59:03+08:00",
            canonical_title="中国能建与华北电力大学签署战略合作协议",
            summary="双方将围绕构建新型能源体系和新型电力系统深化合作。",
            source="stcn",
            published_at="2026-04-02T20:59:03+08:00",
            url="https://example.com/stcn-power-keep-2",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-reduction-predisclosure",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-power-keep-2",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["电力资源"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中国能建与华北电力大学签署战略合作协议" in content
    assert "关于5%以上股东减持股份的预披露公告" not in content


def test_write_text_report_filters_cninfo_termination_of_reduction_plan_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-reduction-termination",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="关于股东提前终止股份减持计划的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-reduction-termination",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-nev-keep-2",
            first_seen_at="2026-04-02T17:45:53+08:00",
            last_seen_at="2026-04-02T17:45:53+08:00",
            canonical_title="乘联分会：3月全国乘用车厂商新能源批发预估112万辆",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T17:45:53+08:00",
            url="https://example.com/stcn-nev-keep-2",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-reduction-termination",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-nev-keep-2",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["新能源车"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "乘联分会：3月全国乘用车厂商新能源批发预估112万辆" in content
    assert "关于股东提前终止股份减持计划的公告" not in content


def test_write_text_report_filters_cninfo_shareholder_reduction_plan_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-reduction-plan",
            first_seen_at="2026-04-09T00:00:00+08:00",
            last_seen_at="2026-04-09T00:00:00+08:00",
            canonical_title="股东减持股份计划公告",
            summary="公司披露股东减持股份计划。",
            source="cninfo",
            published_at="2026-04-09T00:00:00+08:00",
            url="https://example.com/cninfo-reduction-plan",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-ai-keep",
            first_seen_at="2026-04-08T18:59:25+08:00",
            last_seen_at="2026-04-08T18:59:25+08:00",
            canonical_title="内蒙古：建设全国领先的绿色智能算力保障基地 持续提升智能算力规模",
            summary="summary",
            source="stcn",
            published_at="2026-04-08T18:59:25+08:00",
            url="https://example.com/stcn-ai-keep",
            event_type="fast_news",
            event_subtype="policy_signal",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-reduction-plan",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-ai-keep",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "内蒙古：建设全国领先的绿色智能算力保障基地 持续提升智能算力规模" in content
    assert "股东减持股份计划公告" not in content


def test_write_text_report_filters_sse_shareholder_reduction_and_increase_result_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-share-increase-result",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="关于控股股东增持股份结果的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/sse-share-increase-result",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-shareholder-reduction-plan",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="杭州钢铁股份有限公司关于持股5%以上股东减持股份计划公告",
            summary="summary",
            source="sse",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/sse-shareholder-reduction-plan",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-policy-keep-sse-filter",
            first_seen_at="2026-04-10T19:58:36+08:00",
            last_seen_at="2026-04-10T19:58:36+08:00",
            canonical_title="骄成超声：拟定增募资不超13.44亿元 用于半导体先进超声设备研发及产业化项目等",
            summary="summary",
            source="stcn",
            published_at="2026-04-10T19:58:36+08:00",
            url="https://example.com/stcn-policy-keep-sse-filter",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-sse-share-increase-result",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-sse-shareholder-reduction-plan",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-policy-keep-sse-filter",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "骄成超声：拟定增募资不超13.44亿元 用于半导体先进超声设备研发及产业化项目等" in content
    assert "关于控股股东增持股份结果的公告" not in content
    assert "杭州钢铁股份有限公司关于持股5%以上股东减持股份计划公告" not in content


def test_write_text_report_filters_cninfo_buyback_purpose_cancellation_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-buyback-purpose",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="关于调整部分回购股份用途并注销的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-buyback-purpose",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-travel-keep-2",
            first_seen_at="2026-04-02T17:49:06+08:00",
            last_seen_at="2026-04-02T17:49:06+08:00",
            canonical_title="2026清明档电影片单发布",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T17:49:06+08:00",
            url="https://example.com/stcn-travel-keep-2",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-buyback-purpose",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-travel-keep-2",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["文旅"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "2026清明档电影片单发布" in content
    assert "关于调整部分回购股份用途并注销的公告" not in content


def test_write_text_report_filters_cninfo_buyback_price_cap_adjustment_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-buyback-price-cap",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="关于2025年年度权益分派实施后调整回购股份价格上限的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/cninfo-buyback-price-cap",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-keep-real-estate",
            first_seen_at="2026-04-10T20:20:32+08:00",
            last_seen_at="2026-04-10T20:20:32+08:00",
            canonical_title="保利发展：3月签约金额260.33亿元 同比减少10.28%",
            summary="summary",
            source="stcn",
            published_at="2026-04-10T20:20:32+08:00",
            url="https://example.com/stcn-keep-real-estate",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-buyback-price-cap",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-real-estate",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["房地产"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "保利发展：3月签约金额260.33亿元 同比减少10.28%" in content
    assert "关于2025年年度权益分派实施后调整回购股份价格上限的公告" not in content


def test_write_text_report_filters_cninfo_treasury_stock_capital_reduction_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-treasury-stock-capital-reduction",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="关于注销回购专用证券账户库存股减少公司注册资本修订《公司章程》的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/cninfo-treasury-stock-capital-reduction",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-storage-keep",
            first_seen_at="2026-04-09T19:54:55+08:00",
            last_seen_at="2026-04-09T19:54:55+08:00",
            canonical_title="中矿资源：第一季度净利同比预增270.97%—308.07%",
            summary="summary",
            source="stcn",
            published_at="2026-04-09T19:54:55+08:00",
            url="https://example.com/stcn-storage-keep",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-treasury-stock-capital-reduction",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-storage-keep",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["储能", "锂电池"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中矿资源：第一季度净利同比预增270.97%—308.07%" in content
    assert "关于注销回购专用证券账户库存股减少公司注册资本修订《公司章程》的公告" not in content


def test_write_text_report_filters_sse_capital_reduction_and_progress_notice_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-capital-reduction",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="关于注销回购股份并减少注册资本的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/sse-capital-reduction",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-progress-disclosure",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="同方股份有限公司关于签署《委托管理协议之终止协议》暨关联交易进展的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/sse-progress-disclosure",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-miit-keep-sse-filter",
            first_seen_at="2026-04-09T00:00:00+08:00",
            last_seen_at="2026-04-09T00:00:00+08:00",
            canonical_title="工业和信息化部等四部门召开动力及储能电池行业企业座谈会",
            summary="summary",
            source="miit",
            published_at="2026-04-09T00:00:00+08:00",
            url="https://example.com/miit-keep-sse-filter",
            event_type="policy",
            event_subtype="policy_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-sse-capital-reduction",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-sse-progress-disclosure",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-miit-keep-sse-filter",
            direction="bullish",
            impact_score=97.0,
            reasoning="rule",
            themes=["储能"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "工业和信息化部等四部门召开动力及储能电池行业企业座谈会" in content
    assert "关于注销回购股份并减少注册资本的公告" not in content
    assert "同方股份有限公司关于签署《委托管理协议之终止协议》暨关联交易进展的公告" not in content


def test_write_text_report_filters_szse_annual_report_materials_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-annual-summary",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="浪潮信息：2025年年度报告摘要",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-annual-summary",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-annual-report",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="浪潮信息：2025年年度报告",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-annual-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-shareholder-meeting",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="浪潮信息：关于召开2025年度股东会的通知",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-shareholder-meeting",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-keep-szse-report",
            first_seen_at="2026-04-10T19:58:36+08:00",
            last_seen_at="2026-04-10T19:58:36+08:00",
            canonical_title="三峡能源与远景能源签署战略合作协议",
            summary="summary",
            source="stcn",
            published_at="2026-04-10T19:58:36+08:00",
            url="https://example.com/stcn-keep-szse-report",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-annual-summary",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-annual-report",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-shareholder-meeting",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-szse-report",
            direction="bullish",
            impact_score=97.0,
            reasoning="rule",
            themes=["电力资源", "储能"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "三峡能源与远景能源签署战略合作协议" in content
    assert "浪潮信息：2025年年度报告摘要" not in content
    assert "浪潮信息：2025年年度报告" not in content
    assert "浪潮信息：关于召开2025年度股东会的通知" not in content


def test_write_text_report_filters_szse_independent_director_and_audit_materials_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-independent-director-candidate",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="浪潮信息：独立董事候选人声明与承诺（刘培德）",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-independent-director-candidate",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-independent-director-nominator",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="浪潮信息：独立董事提名人声明与承诺（刘培德）",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-independent-director-nominator",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-internal-control-audit",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="浪潮信息：浪潮信息2025年度内部控制审计报告",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-internal-control-audit",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-annual-audit",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="浪潮信息：2025年年度审计报告",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-annual-audit",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-keep-szse-audit",
            first_seen_at="2026-04-10T19:58:36+08:00",
            last_seen_at="2026-04-10T19:58:36+08:00",
            canonical_title="两单公募REITs获批",
            summary="summary",
            source="stcn",
            published_at="2026-04-10T19:58:36+08:00",
            url="https://example.com/stcn-keep-szse-audit",
            event_type="fast_news",
            event_subtype="regulatory_approval",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-independent-director-candidate",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-independent-director-nominator",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-internal-control-audit",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-annual-audit",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-szse-audit",
            direction="bullish",
            impact_score=97.0,
            reasoning="rule",
            themes=["REITs"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "两单公募REITs获批" in content
    assert "浪潮信息：独立董事候选人声明与承诺（刘培德）" not in content
    assert "浪潮信息：独立董事提名人声明与承诺（刘培德）" not in content
    assert "浪潮信息：浪潮信息2025年度内部控制审计报告" not in content
    assert "浪潮信息：2025年年度审计报告" not in content


def test_write_text_report_filters_cninfo_disclosure_rulebook_and_buyback_report_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-rulebook",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="苏州易德龙科技股份有限公司关于公司2026年股票期权激励实施考核管理办法",
            summary="summary",
            source="cninfo",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/cninfo-rulebook",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-cninfo-buyback-report",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="苏州易德龙科技股份有限公司关于以集中竞价交易方式回购股份方案的公告暨回购报告书",
            summary="summary",
            source="cninfo",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/cninfo-buyback-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-keep",
            first_seen_at="2026-04-09T20:03:48+08:00",
            last_seen_at="2026-04-09T20:03:48+08:00",
            canonical_title="睿能科技：拟收购博泰智能75%股权 股票明起复牌",
            summary="summary",
            source="stcn",
            published_at="2026-04-09T20:03:48+08:00",
            url="https://example.com/stcn-keep",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-rulebook",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cninfo-buyback-report",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["锂电池"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "睿能科技：拟收购博泰智能75%股权 股票明起复牌" in content
    assert "苏州易德龙科技股份有限公司关于公司2026年股票期权激励实施考核管理办法" not in content
    assert "苏州易德龙科技股份有限公司关于以集中竞价交易方式回购股份方案的公告暨回购报告书" not in content


def test_write_text_report_filters_exchange_disclosure_variants_from_live_scan_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-equity-incentive-rulebook",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="张小泉：2026年限制性股票激励计划实施考核管理办法",
            summary="summary",
            source="szse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/szse-equity-incentive-rulebook",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-cninfo-independent-financial-adviser",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="东方财富证券股份有限公司关于张小泉股份有限公司2026年限制性股票激励计划（草案）之独立财务顾问报告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/cninfo-independent-financial-adviser",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-no-regulatory-measures",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="三利谱：关于公司最近五年不存在被证券监管部门和交易所采取处罚或监管措施的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/szse-no-regulatory-measures",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-reduction-expired",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="三维通信：关于实际控制人减持计划期限届满暨实施情况的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/szse-reduction-expired",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-share-subscription-agreement",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="三利谱：关于与特定对象签署附条件生效的股份认购协议的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/szse-share-subscription-agreement",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-keep-live-signal",
            first_seen_at="2026-04-13T21:45:16+08:00",
            last_seen_at="2026-04-13T21:45:16+08:00",
            canonical_title="上汽通用五菱与宁德时代达战略合作",
            summary="summary",
            source="stcn",
            published_at="2026-04-13T21:45:16+08:00",
            url="https://example.com/stcn-keep-live-signal",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-equity-incentive-rulebook",
            direction="bearish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cninfo-independent-financial-adviser",
            direction="bearish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-no-regulatory-measures",
            direction="bearish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-reduction-expired",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-share-subscription-agreement",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-live-signal",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "上汽通用五菱与宁德时代达战略合作" in content
    assert "张小泉：2026年限制性股票激励计划实施考核管理办法" not in content
    assert "东方财富证券股份有限公司关于张小泉股份有限公司2026年限制性股票激励计划（草案）之独立财务顾问报告" not in content
    assert "三利谱：关于公司最近五年不存在被证券监管部门和交易所采取处罚或监管措施的公告" not in content
    assert "三维通信：关于实际控制人减持计划期限届满暨实施情况的公告" not in content
    assert "三利谱：关于与特定对象签署附条件生效的股份认购协议的公告" not in content


def test_write_text_report_filters_cninfo_disclosure_reports_and_profit_distribution_plan_without_theme(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-auditor-duty-report",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="苏州锴威特半导体股份有限公司2025年度会计师事务所履职情况评估报告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/cninfo-auditor-duty-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-cninfo-profit-distribution-plan",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="苏州锴威特半导体股份有限公司关于2025年度利润分配预案的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/cninfo-profit-distribution-plan",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-cninfo-special-audit-opinion",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="北京德皓国际会计师事务所（特殊普通合伙）关于苏州锴威特半导体股份有限公司营业收入扣除事项的专项核查意见",
            summary="summary",
            source="cninfo",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/cninfo-special-audit-opinion",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-policy-keep",
            first_seen_at="2026-04-09T20:37:27+08:00",
            last_seen_at="2026-04-09T20:37:27+08:00",
            canonical_title="上海：深入推进直播经济集聚区建设，建设高质量直播经济生态",
            summary="summary",
            source="stcn",
            published_at="2026-04-09T20:37:27+08:00",
            url="https://example.com/stcn-policy-keep",
            event_type="policy",
            event_subtype="policy_signal",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-auditor-duty-report",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cninfo-profit-distribution-plan",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cninfo-special-audit-opinion",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-policy-keep",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["文旅"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "上海：深入推进直播经济集聚区建设，建设高质量直播经济生态" in content
    assert "苏州锴威特半导体股份有限公司2025年度会计师事务所履职情况评估报告" not in content
    assert "苏州锴威特半导体股份有限公司关于2025年度利润分配预案的公告" not in content
    assert "北京德皓国际会计师事务所（特殊普通合伙）关于苏州锴威特半导体股份有限公司营业收入扣除事项的专项核查意见" not in content


def test_write_text_report_filters_cninfo_annual_package_disclosures_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    titles = [
        "苏州锴威特半导体股份有限公司股票交易异常波动公告",
        "苏州锴威特半导体股份有限公司关于使用暂时闲置自有资金进行现金管理的公告",
        "苏州锴威特半导体股份有限公司关于公司2026年度向银行申请综合授信额度的公告",
        "苏州锴威特半导体股份有限公司关于未弥补的亏损达实收股本总额三分之一的公告",
        "苏州锴威特半导体股份有限公司2025年度募集资金存放、管理与实际使用情况的专项报告",
        "苏州锴威特半导体股份有限公司关于董事、高级管理人员2025年度薪酬确认及2026年度薪酬方案的公告",
        "苏州锴威特半导体股份有限公司2026年度“提质增效重回报”行动方案",
    ]
    events = [
        Event(
            event_id=f"event-cninfo-annual-package-{index}",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title=title,
            summary="summary",
            source="cninfo",
            published_at="2026-04-10T00:00:00+08:00",
            url=f"https://example.com/cninfo-annual-package-{index}",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        )
        for index, title in enumerate(titles, start=1)
    ]
    events.append(
        Event(
            event_id="event-stcn-policy-keep-2",
            first_seen_at="2026-04-09T20:37:27+08:00",
            last_seen_at="2026-04-09T20:37:27+08:00",
            canonical_title="上海：深入推进直播经济集聚区建设，建设高质量直播经济生态",
            summary="summary",
            source="stcn",
            published_at="2026-04-09T20:37:27+08:00",
            url="https://example.com/stcn-policy-keep-2",
            event_type="policy",
            event_subtype="policy_signal",
        )
    )
    analyses = [
        EventAnalysis(
            event_id=f"event-cninfo-annual-package-{index}",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        )
        for index in range(1, len(titles) + 1)
    ]
    analyses.append(
        EventAnalysis(
            event_id="event-stcn-policy-keep-2",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["文旅"],
            triggered=True,
        )
    )

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "上海：深入推进直播经济集聚区建设，建设高质量直播经济生态" in content
    for title in titles:
        assert title not in content


def test_write_text_report_filters_cninfo_equity_incentive_grantee_list_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-grantee-list",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="2026年股票期权激励计划首次授予部分激励对象名单",
            summary="summary",
            source="cninfo",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/cninfo-grantee-list",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-stcn-keep-2",
            first_seen_at="2026-04-09T19:54:55+08:00",
            last_seen_at="2026-04-09T19:54:55+08:00",
            canonical_title="中矿资源：第一季度净利同比预增270.97%—308.07%",
            summary="summary",
            source="stcn",
            published_at="2026-04-09T19:54:55+08:00",
            url="https://example.com/stcn-keep-2",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-grantee-list",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-2",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["储能", "锂电池"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中矿资源：第一季度净利同比预增270.97%—308.07%" in content
    assert "2026年股票期权激励计划首次授予部分激励对象名单" not in content


def test_write_text_report_filters_cninfo_board_resolution_oversight_report_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-board-oversight",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="国投资本董事会审计与风险管理委员会对2025年度会计师事务所履行监督职责情况的报告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-board-oversight",
            event_type="hard_event",
            event_subtype="board_resolution",
        ),
        Event(
            event_id="event-stcn-oil-keep-3",
            first_seen_at="2026-04-02T21:29:43+08:00",
            last_seen_at="2026-04-02T21:29:43+08:00",
            canonical_title="WTI原油期货涨超13%",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T21:29:43+08:00",
            url="https://example.com/stcn-oil-keep-3",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-board-oversight",
            direction="bearish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-oil-keep-3",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "WTI原油期货涨超13%" in content
    assert "国投资本董事会审计与风险管理委员会对2025年度会计师事务所履行监督职责情况的报告" not in content


def test_write_text_report_filters_cninfo_restructuring_legal_opinion_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-restructuring-legal-opinion",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="北京观韬律师事务所关于深圳市宇顺电子股份有限公司重大资产重组实施情况之法律意见书",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-restructuring-legal-opinion",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-stcn-travel-keep-3",
            first_seen_at="2026-04-02T17:49:06+08:00",
            last_seen_at="2026-04-02T17:49:06+08:00",
            canonical_title="2026清明档电影片单发布",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T17:49:06+08:00",
            url="https://example.com/stcn-travel-keep-3",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-restructuring-legal-opinion",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-travel-keep-3",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["文旅"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "2026清明档电影片单发布" in content
    assert "北京观韬律师事务所关于深圳市宇顺电子股份有限公司重大资产重组实施情况之法律意见书" not in content


def test_write_text_report_filters_cninfo_restructuring_regulatory_requirement_statement_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-restructuring-regulatory-statement",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="福建睿能科技股份有限公司董事会关于本次交易符合《上市公司监管指引第9号——上市公司筹划和实施重大资产重组的监管要求》第四条规定的说明",
            summary="summary",
            source="cninfo",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/cninfo-restructuring-regulatory-statement",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-stcn-storage-keep-2",
            first_seen_at="2026-04-09T19:54:55+08:00",
            last_seen_at="2026-04-09T19:54:55+08:00",
            canonical_title="中矿资源：第一季度净利同比预增270.97%—308.07%",
            summary="summary",
            source="stcn",
            published_at="2026-04-09T19:54:55+08:00",
            url="https://example.com/stcn-storage-keep-2",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-restructuring-regulatory-statement",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-storage-keep-2",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["储能", "锂电池"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中矿资源：第一季度净利同比预增270.97%—308.07%" in content
    assert "福建睿能科技股份有限公司董事会关于本次交易符合《上市公司监管指引第9号——上市公司筹划和实施重大资产重组的监管要求》第四条规定的说明" not in content


def test_write_text_report_filters_cninfo_restructuring_progress_notice_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-restructuring-progress",
            first_seen_at="2026-04-10T00:00:00+08:00",
            last_seen_at="2026-04-10T00:00:00+08:00",
            canonical_title="关于全资子公司全面要约收购Asetek A/S全部股份的进展公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-10T00:00:00+08:00",
            url="https://example.com/cninfo-restructuring-progress",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-stcn-keep-3",
            first_seen_at="2026-04-09T20:03:48+08:00",
            last_seen_at="2026-04-09T20:03:48+08:00",
            canonical_title="睿能科技：拟收购博泰智能75%股权 股票明起复牌",
            summary="summary",
            source="stcn",
            published_at="2026-04-09T20:03:48+08:00",
            url="https://example.com/stcn-keep-3",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-restructuring-progress",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-3",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["锂电池"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "睿能科技：拟收购博泰智能75%股权 股票明起复牌" in content
    assert "关于全资子公司全面要约收购Asetek A/S全部股份的进展公告" not in content


def test_write_text_report_filters_cninfo_penalty_notice_without_theme_even_if_analysis_has_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-penalty-notice",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="洲际油气股份有限公司关于公司股东收到行政处罚事先告知书的公告",
            summary="公司股东收到中国证监会下发的《行政处罚事先告知书》。",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-penalty-notice",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-nev-keep-3",
            first_seen_at="2026-04-02T17:45:53+08:00",
            last_seen_at="2026-04-02T17:45:53+08:00",
            canonical_title="乘联分会：3月全国乘用车厂商新能源批发预估112万辆",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T17:45:53+08:00",
            url="https://example.com/stcn-nev-keep-3",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-penalty-notice",
            direction="bearish",
            impact_score=100.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-nev-keep-3",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["新能源车"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "乘联分会：3月全国乘用车厂商新能源批发预估112万辆" in content
    assert "洲际油气股份有限公司关于公司股东收到行政处罚事先告知书的公告" not in content


def test_write_text_report_filters_stcn_broker_macro_commentary_even_if_analysis_has_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-broker-commentary",
            first_seen_at="2026-04-04T10:22:59+08:00",
            last_seen_at="2026-04-04T10:22:59+08:00",
            canonical_title="华泰证券：3月非农超预期回升显示美国就业市场韧性 通胀目前是联储货币政策的核心变量",
            summary="券商研报认为非农、通胀与联储政策路径仍是资产定价核心变量。",
            source="stcn",
            published_at="2026-04-04T10:22:59+08:00",
            url="https://example.com/stcn-broker-commentary",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-stcn-nev-keep-4",
            first_seen_at="2026-04-02T17:45:53+08:00",
            last_seen_at="2026-04-02T17:45:53+08:00",
            canonical_title="乘联分会：3月全国乘用车厂商新能源批发预估112万辆",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T17:45:53+08:00",
            url="https://example.com/stcn-nev-keep-4",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-broker-commentary",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-nev-keep-4",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["新能源车"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "乘联分会：3月全国乘用车厂商新能源批发预估112万辆" in content
    assert "华泰证券：3月非农超预期回升显示美国就业市场韧性 通胀目前是联储货币政策的核心变量" not in content


def test_write_text_report_filters_stcn_csc_broker_macro_commentary_even_if_analysis_has_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-csc-commentary",
            first_seen_at="2026-04-21T19:16:02+08:00",
            last_seen_at="2026-04-21T19:16:02+08:00",
            canonical_title="中信建投：A股迎修复行情 围绕景气行业布局",
            summary="券商观点认为当前市场正在修复，建议围绕景气行业进行资产配置。",
            source="stcn",
            published_at="2026-04-21T19:16:02+08:00",
            url="https://example.com/stcn-csc-commentary",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-stcn-csc-ai-commentary",
            first_seen_at="2026-04-21T07:52:19+08:00",
            last_seen_at="2026-04-21T07:52:19+08:00",
            canonical_title="中信建投：算力公司一季报亮眼 继续坚定看好算力产业链",
            summary="人民财讯4月21日电，中信建投证券研报称，台积电发布一季报，中际旭创发布2026年第一季度报告。业绩映射算力需求强劲。算力板块公司一季度业绩亮眼，继续坚定看好算力产业链。",
            source="stcn",
            published_at="2026-04-21T07:52:19+08:00",
            url="https://example.com/stcn-csc-ai-commentary",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-stcn-coop-keep",
            first_seen_at="2026-04-21T19:14:50+08:00",
            last_seen_at="2026-04-21T19:14:50+08:00",
            canonical_title="迅策：与深圳数据交易所签署战略合作协议",
            summary="summary",
            source="stcn",
            published_at="2026-04-21T19:14:50+08:00",
            url="https://example.com/stcn-coop-keep",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-csc-commentary",
            direction="bearish",
            impact_score=99.0,
            reasoning="rule",
            themes=["算力", "黄金", "锂电池"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-csc-ai-commentary",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-coop-keep",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["机器人"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "迅策：与深圳数据交易所签署战略合作协议" in content
    assert "中信建投：A股迎修复行情 围绕景气行业布局" not in content
    assert "中信建投：算力公司一季报亮眼 继续坚定看好算力产业链" not in content


def test_write_text_report_filters_stcn_early_know_roundup_without_hiding_policy_signal(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-early-know-roundup",
            first_seen_at="2026-04-21T07:49:55+08:00",
            last_seen_at="2026-04-21T07:49:55+08:00",
            canonical_title="【早知道】特朗普称在达成“协议”前不会解除对伊朗的封锁",
            summary="人民财讯4月21日电，【摘要】特朗普称在达成“协议”前不会解除对伊朗的封锁。伊朗议会议长：伊朗不接受在威胁阴影下的谈判。广东：要用好产业引导基金，加大对集成电路、具身智能、算电协同等领域的投资。",
            source="stcn",
            published_at="2026-04-21T07:49:55+08:00",
            url="https://example.com/stcn-early-know-roundup",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-policy-signal-keep",
            first_seen_at="2026-04-21T07:49:56+08:00",
            last_seen_at="2026-04-21T07:49:56+08:00",
            canonical_title="广东：要用好产业引导基金，加大对集成电路、具身智能、算电协同等领域的投资",
            summary="summary",
            source="stcn",
            published_at="2026-04-21T07:49:56+08:00",
            url="https://example.com/policy-signal-keep",
            event_type="fast_news",
            event_subtype="policy_signal",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-early-know-roundup",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-policy-signal-keep",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "【早知道】特朗普称在达成“协议”前不会解除对伊朗的封锁" not in content
    assert "广东：要用好产业引导基金，加大对集成电路、具身智能、算电协同等领域的投资" in content


def test_write_text_report_filters_stcn_gf_broker_strategy_commentary_even_if_analysis_has_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-gf-commentary",
            first_seen_at="2026-04-13T07:24:28+08:00",
            last_seen_at="2026-04-13T07:24:28+08:00",
            canonical_title="广发证券：市场情绪回升，建议积极关注保险板块",
            summary="券商观点认为市场情绪回升，建议积极关注保险板块配置机会。",
            source="stcn",
            published_at="2026-04-13T07:24:28+08:00",
            url="https://example.com/stcn-gf-commentary",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-stcn-policy-keep-gf",
            first_seen_at="2026-04-13T07:15:30+08:00",
            last_seen_at="2026-04-13T07:15:30+08:00",
            canonical_title="智能电动汽车发展高层论坛（2026）：2030年新能源车有望成市场主体",
            summary="summary",
            source="stcn",
            published_at="2026-04-13T07:15:30+08:00",
            url="https://example.com/stcn-policy-keep-gf",
            event_type="fast_news",
            event_subtype="policy_signal",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-gf-commentary",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["保险"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-policy-keep-gf",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["新能源车"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "智能电动汽车发展高层论坛（2026）：2030年新能源车有望成市场主体" in content
    assert "广发证券：市场情绪回升，建议积极关注保险板块" not in content


def test_write_text_report_filters_stcn_fund_manager_allocation_commentary_without_hiding_real_order_news(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-fund-manager-commentary",
            first_seen_at="2026-04-21T07:20:50+08:00",
            last_seen_at="2026-04-21T07:20:50+08:00",
            canonical_title="基金经理布局创新药对冲组合风险 公募对创新药配置逻辑出现新变化",
            summary="伴随各类事件催化进入密集兑现周期，不少基金经理开始切换布局创新药对冲组合风险，反映公募对创新药配置逻辑出现了新的变化。",
            source="stcn",
            published_at="2026-04-21T07:20:50+08:00",
            url="https://example.com/stcn-fund-manager-commentary",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-stcn-fund-manager-investment-opportunity",
            first_seen_at="2026-04-21T07:37:33+08:00",
            last_seen_at="2026-04-21T07:37:33+08:00",
            canonical_title="景气度“光”芒四射 基金经理把握光通信投资机会",
            summary="人民财讯4月21日电，中流击水，“光”芒四射。AI引领的科技浪潮汹涌，算力建设如火如荼，这也映射到A股市场中。从基金投资布局情况看，光通信依然是资金竞逐的方向，具体到细分方向，光模块依然闪耀，光纤乘势而起，光器件、光芯片迎风起舞。与光相关的标的，几乎都受到市场的高度关注。而在逐光前行的基金经理中，有人高歌猛进，有人复盘向新。在AI时代发展的浪潮中，与时俱进才能拥有未来。",
            source="stcn",
            published_at="2026-04-21T07:37:33+08:00",
            url="https://example.com/stcn-fund-manager-investment-opportunity",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-stcn-order-keep",
            first_seen_at="2026-04-21T07:28:53+08:00",
            last_seen_at="2026-04-21T07:28:53+08:00",
            canonical_title="上海电气中标人造卫星装备一体化自动项目",
            summary="summary",
            source="stcn",
            published_at="2026-04-21T07:28:53+08:00",
            url="https://example.com/stcn-order-keep",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-fund-manager-commentary",
            direction="bearish",
            impact_score=99.0,
            reasoning="rule",
            themes=["创新药"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-fund-manager-investment-opportunity",
            direction="neutral",
            impact_score=79.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-order-keep",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "上海电气中标人造卫星装备一体化自动项目" in content
    assert "基金经理布局创新药对冲组合风险 公募对创新药配置逻辑出现新变化" not in content
    assert "景气度“光”芒四射 基金经理把握光通信投资机会" not in content


def test_write_text_report_filters_stcn_industry_prosperity_story_without_hiding_cls_industry_signal(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-industry-prosperity",
            first_seen_at="2026-04-21T07:42:50+08:00",
            last_seen_at="2026-04-21T07:42:50+08:00",
            canonical_title="一季度锂电行业高景气延续 储能成重点布局方向",
            summary="人民财讯4月21日电，近期，锂电产业链上市公司纷纷披露一季度业绩预告或正式业绩报告。整体来看，锂电赛道维持高景气度，行业公司业绩纷纷“报喜”。与此同时，锂电企业在一季度的投资动作不断，从布局方向来看，储能行业成为重点领域。机构分析认为，在市场需求旺盛的背景下，锂电池产业链多个细分环节有望获益。",
            source="stcn",
            published_at="2026-04-21T07:42:50+08:00",
            url="https://example.com/stcn-industry-prosperity",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-cls-industry-signal-keep",
            first_seen_at="2026-04-21T06:34:58+08:00",
            last_seen_at="2026-04-21T06:34:58+08:00",
            canonical_title="AI需求强劲 PCB产业链景气度扩散",
            summary="【AI需求强劲 PCB产业链景气度扩散】财联社4月21日电，最近一周，一批PCB（印制电路板）产业链公司披露了2026年一季度业绩大增的公告。这折射出，在AI需求强劲增长的背景下，该产业链上下游的景气度正由PCB制造环节向上游材料、关键设备等领域扩散。",
            source="cls",
            published_at="2026-04-21T06:34:58+08:00",
            url="https://example.com/cls-industry-signal-keep",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-industry-prosperity",
            direction="neutral",
            impact_score=79.0,
            reasoning="rule",
            themes=["储能", "锂电池"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-industry-signal-keep",
            direction="bullish",
            impact_score=99.3,
            reasoning="rule",
            themes=["PCB"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "一季度锂电行业高景气延续 储能成重点布局方向" not in content
    assert "AI需求强劲 PCB产业链景气度扩散" in content


def test_write_text_report_filters_shareholder_reduction_threshold_and_result_disclosures(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-reduction-threshold",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="北大医药：关于持股5%以上股东减持公司股份比例触及1%及5%整数倍的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/szse-reduction-threshold",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-reduction-result",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="烟台德邦科技股份有限公司持股5%以上股东权益变动降至5%以下、提前终止减持计划暨减持股份结果公告",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-reduction-result",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-order-keep-reduction",
            first_seen_at="2026-04-13T07:28:53+08:00",
            last_seen_at="2026-04-13T07:28:53+08:00",
            canonical_title="上海电气中标人造卫星装备一体化自动项目",
            summary="summary",
            source="stcn",
            published_at="2026-04-13T07:28:53+08:00",
            url="https://example.com/stcn-order-keep-reduction",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-reduction-threshold",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-sse-reduction-result",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-order-keep-reduction",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "上海电气中标人造卫星装备一体化自动项目" in content
    assert "北大医药：关于持股5%以上股东减持公司股份比例触及1%及5%整数倍的公告" not in content
    assert "烟台德邦科技股份有限公司持股5%以上股东权益变动降至5%以下、提前终止减持计划暨减持股份结果公告" not in content


def test_write_text_report_filters_shareholder_reduction_predisclosure_and_completion_variants(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-reduction-predisclosure-variant",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="贝达药业：关于股东减持股份预披露的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/szse-reduction-predisclosure-variant",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-reduction-completion",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="华联控股：华联控股关于高级管理人员减持计划实施完成的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/szse-reduction-completion",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-reduction-expiry",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="大洋生物：关于合计持股5%以上股东减持股份计划期限届满暨实施情况的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/szse-reduction-expiry",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-order-keep-reduction-variants",
            first_seen_at="2026-04-13T07:28:53+08:00",
            last_seen_at="2026-04-13T07:28:53+08:00",
            canonical_title="上海电气中标人造卫星装备一体化自动项目",
            summary="summary",
            source="stcn",
            published_at="2026-04-13T07:28:53+08:00",
            url="https://example.com/stcn-order-keep-reduction-variants",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-reduction-predisclosure-variant",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-reduction-completion",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-reduction-expiry",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-order-keep-reduction-variants",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "上海电气中标人造卫星装备一体化自动项目" in content
    assert "贝达药业：关于股东减持股份预披露的公告" not in content
    assert "华联控股：华联控股关于高级管理人员减持计划实施完成的公告" not in content
    assert "大洋生物：关于合计持股5%以上股东减持股份计划期限届满暨实施情况的公告" not in content


def test_write_text_report_filters_exchange_penalty_and_rectification_disclosures_without_hiding_real_cooperation(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-penalty-decision",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="汉嘉数智：关于收到财政部行政处罚决定书的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/szse-penalty-decision",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-rectification-history",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="首都在线：关于最近五年被证券监管部门和交易所采取监管措施或处罚及整改情况的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/szse-rectification-history",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-coop-keep",
            first_seen_at="2026-04-14T00:01:00+08:00",
            last_seen_at="2026-04-14T00:01:00+08:00",
            canonical_title="中国能建与华北电力大学签署战略合作协议",
            summary="双方将围绕构建新型能源体系和新型电力系统深化合作。",
            source="stcn",
            published_at="2026-04-14T00:01:00+08:00",
            url="https://example.com/stcn-coop-keep",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-penalty-decision",
            direction="bearish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-rectification-history",
            direction="bearish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-coop-keep",
            direction="bullish",
            impact_score=97.0,
            reasoning="rule",
            themes=["电力资源"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中国能建与华北电力大学签署战略合作协议" in content
    assert "汉嘉数智：关于收到财政部行政处罚决定书的公告" not in content
    assert "首都在线：关于最近五年被证券监管部门和交易所采取监管措施或处罚及整改情况的公告" not in content


def test_write_text_report_filters_convertible_bond_credit_rating_report_without_hiding_financing_acceptance(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cb-credit-rating-report",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="斯达半导体股份有限公司向不特定对象发行可转换公司债券信用评级报告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/cb-credit-rating-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-financing-acceptance-keep",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="关于2025年度向特定对象发行A股股票申请获得深圳证券交易所受理的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/financing-acceptance-keep",
            event_type="hard_event",
            event_subtype="financing_acceptance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cb-credit-rating-report",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-financing-acceptance-keep",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "关于2025年度向特定对象发行A股股票申请获得深圳证券交易所受理的公告" in content
    assert "斯达半导体股份有限公司向不特定对象发行可转换公司债券信用评级报告" not in content


def test_write_text_report_filters_financing_authorization_material_without_hiding_real_financing_acceptance(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-financing-authorization-material",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="天府文旅：关于提请股东会授权董事会办理以简易程序向特定对象发行股票的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/financing-authorization-material",
            event_type="hard_event",
            event_subtype="board_resolution",
        ),
        Event(
            event_id="event-financing-acceptance-keep",
            first_seen_at="2026-04-23T00:01:00+08:00",
            last_seen_at="2026-04-23T00:01:00+08:00",
            canonical_title="关于2025年度向特定对象发行A股股票申请获得深圳证券交易所受理的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-23T00:01:00+08:00",
            url="https://example.com/financing-acceptance-keep",
            event_type="hard_event",
            event_subtype="financing_acceptance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-financing-authorization-material",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["文旅"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-financing-acceptance-keep",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "关于2025年度向特定对象发行A股股票申请获得深圳证券交易所受理的公告" in content
    assert "天府文旅：关于提请股东会授权董事会办理以简易程序向特定对象发行股票的公告" not in content


def test_write_text_report_filters_inquiry_transfer_share_verification_report_without_hiding_themed_fast_news(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-inquiry-transfer-verification-report",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="中信证券股份有限公司关于东芯半导体股份有限公司股东向特定机构投资者询价转让股份的核查报告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/inquiry-transfer-verification-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-fast-theme-keep-jilin",
            first_seen_at="2026-04-13T20:03:34+08:00",
            last_seen_at="2026-04-13T20:03:34+08:00",
            canonical_title="吉林省：加快布局算力产业 推动算力中心与零碳园区一体谋划、协同运作",
            summary="summary",
            source="stcn",
            published_at="2026-04-13T20:03:34+08:00",
            url="https://example.com/fast-theme-keep-jilin",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-inquiry-transfer-verification-report",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-fast-theme-keep-jilin",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "吉林省：加快布局算力产业 推动算力中心与零碳园区一体谋划、协同运作" in content
    assert "中信证券股份有限公司关于东芯半导体股份有限公司股东向特定机构投资者询价转让股份的核查报告" not in content


def test_write_text_report_filters_stcn_overseas_livelihood_oil_story_even_if_analysis_has_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-overseas-livelihood",
            first_seen_at="2026-04-04T10:59:31+08:00",
            last_seen_at="2026-04-04T10:59:31+08:00",
            canonical_title="中东局势致燃料紧缺 日本多地温泉被迫停业",
            summary="受中东局势影响，日本原油进口量骤降，由原油加工所得的重油供应紧张。日本多地温泉和洗浴设施因缺乏用于燃料的重油被迫停业。",
            source="stcn",
            published_at="2026-04-04T10:59:31+08:00",
            url="https://example.com/stcn-overseas-livelihood",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-stcn-ai-keep",
            first_seen_at="2026-04-04T10:44:37+08:00",
            last_seen_at="2026-04-04T10:44:37+08:00",
            canonical_title="千问3.6Plus大模型登顶全球模型调用排行榜首，日调用量破万亿",
            summary="发布仅1天的千问新模型Qwen3.6-Plus，冲上全球知名大模型API调用平台OpenRouter的日榜榜首，日调用量突破1.4万亿Token。",
            source="stcn",
            published_at="2026-04-04T10:44:37+08:00",
            url="https://example.com/stcn-ai-keep",
            event_type="fast_news",
            event_subtype="industry_data",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-overseas-livelihood",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-ai-keep",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["AI应用"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "千问3.6Plus大模型登顶全球模型调用排行榜首，日调用量破万亿" in content
    assert "中东局势致燃料紧缺 日本多地温泉被迫停业" not in content


def test_write_text_report_filters_stcn_overseas_aviation_fuel_story_even_if_analysis_has_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-overseas-aviation-fuel",
            first_seen_at="2026-04-09T12:00:16+08:00",
            last_seen_at="2026-04-09T12:00:16+08:00",
            canonical_title="国际航协：航油价格翻倍航空业承压 全球多家航司削减航班",
            summary="国际航空运输协会警告称，全球航空燃油供应恢复正常仍需要数月时间。航油供应持续紧张，全球多家航空公司纷纷削减航班。",
            source="stcn",
            published_at="2026-04-09T12:00:16+08:00",
            url="https://example.com/stcn-overseas-aviation-fuel",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-stcn-space-keep",
            first_seen_at="2026-04-09T12:24:38+08:00",
            last_seen_at="2026-04-09T12:24:38+08:00",
            canonical_title="信维通信：公司商业航天业务进展顺利",
            summary="summary",
            source="stcn",
            published_at="2026-04-09T12:24:38+08:00",
            url="https://example.com/stcn-space-keep",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-overseas-aviation-fuel",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-space-keep",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["商业航天"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "信维通信：公司商业航天业务进展顺利" in content
    assert "国际航协：航油价格翻倍航空业承压 全球多家航司削减航班" not in content


def test_write_text_report_filters_stcn_public_affairs_fast_news_even_if_analysis_gets_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-korea-public-transport",
            first_seen_at="2026-04-04T12:15:23+08:00",
            last_seen_at="2026-04-04T12:15:23+08:00",
            canonical_title="能源供应趋紧 韩国鼓励非高峰使用公共交通",
            summary="韩国政府计划通过提供奖励，鼓励民众在非高峰时段出行主动使用公共交通。",
            source="stcn",
            published_at="2026-04-04T12:15:23+08:00",
            url="https://example.com/stcn-korea-public-transport",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-stcn-south-africa-visa",
            first_seen_at="2026-04-04T12:05:25+08:00",
            last_seen_at="2026-04-04T12:05:25+08:00",
            canonical_title="南非新政延长签证宽限期 将刺激旅游市场",
            summary="签证申请人在签证审理期间可合法停留并自由出入境，业内人士认为将刺激旅游市场。",
            source="stcn",
            published_at="2026-04-04T12:05:25+08:00",
            url="https://example.com/stcn-south-africa-visa",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-stcn-holiday-flow",
            first_seen_at="2026-04-04T11:53:58+08:00",
            last_seen_at="2026-04-04T11:53:58+08:00",
            canonical_title="清明假期第一天 全社会跨区域人员流动量预计约2.96亿人次",
            summary="今天全社会跨区域人员流动量预计约2.96亿人次。",
            source="stcn",
            published_at="2026-04-04T11:53:58+08:00",
            url="https://example.com/stcn-holiday-flow",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-stcn-shenzhen-rain",
            first_seen_at="2026-04-04T11:31:48+08:00",
            last_seen_at="2026-04-04T11:31:48+08:00",
            canonical_title="深圳市暴雨黄色预警信号扩展至全市",
            summary="深圳市气象台将分区暴雨黄色预警信号扩展至全市。",
            source="stcn",
            published_at="2026-04-04T11:31:48+08:00",
            url="https://example.com/stcn-shenzhen-rain",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-stcn-turkey-fertilizer",
            first_seen_at="2026-04-04T10:59:07+08:00",
            last_seen_at="2026-04-04T10:59:07+08:00",
            canonical_title="农业成本因伊朗战事上升 土耳其取消部分化肥关税",
            summary="土耳其已取消尿素等一些基本氮肥和复合肥的关税，以保护农业部门免受成本上升影响。",
            source="stcn",
            published_at="2026-04-04T10:59:07+08:00",
            url="https://example.com/stcn-turkey-fertilizer",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-stcn-dubai-oracle-building",
            first_seen_at="2026-04-04T11:54:48+08:00",
            last_seen_at="2026-04-04T11:54:48+08:00",
            canonical_title="迪拜甲骨文大楼外立面遭防空系统拦截碎片击中 无人员伤亡",
            summary="迪拜互联网城甲骨文公司大楼建筑外立面遭防空系统拦截产生的碎片击中，造成建筑轻微损坏。",
            source="stcn",
            published_at="2026-04-04T11:54:48+08:00",
            url="https://example.com/stcn-dubai-oracle-building",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-stcn-ai-keep-public-affairs",
            first_seen_at="2026-04-04T10:44:37+08:00",
            last_seen_at="2026-04-04T10:44:37+08:00",
            canonical_title="千问3.6Plus大模型登顶全球模型调用排行榜首，日调用量破万亿",
            summary="发布仅1天的千问新模型Qwen3.6-Plus，冲上全球知名大模型API调用平台OpenRouter的日榜榜首。",
            source="stcn",
            published_at="2026-04-04T10:44:37+08:00",
            url="https://example.com/stcn-ai-keep-public-affairs",
            event_type="fast_news",
            event_subtype="industry_data",
        ),
        Event(
            event_id="event-stcn-hubei-trade-in-subsidy",
            first_seen_at="2026-05-01T11:08:24+08:00",
            last_seen_at="2026-05-01T11:08:24+08:00",
            canonical_title="5月1日正式启动 湖北以旧换新国补扩品",
            summary="湖北省商务厅发布2026年消费品以旧换新新增品类补贴政策的公告，对个人消费者购买智能服务机器人等10个品类产品给予补贴。",
            source="stcn",
            published_at="2026-05-01T11:08:24+08:00",
            url="https://example.com/stcn-hubei-trade-in-subsidy",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-stcn-data-cross-border-forum",
            first_seen_at="2026-05-01T14:24:38+08:00",
            last_seen_at="2026-05-01T14:24:38+08:00",
            canonical_title="第九届数字中国建设峰会“数据跨境”主题交流活动在福州成功举办",
            summary="第九届数字中国建设峰会“数据跨境”主题交流活动在福州成功举办，发布跨境流动与数据安全相关成果并举行签约。",
            source="stcn",
            published_at="2026-05-01T14:24:38+08:00",
            url="https://example.com/stcn-data-cross-border-forum",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-stcn-hainan-spaceport-public-affairs",
            first_seen_at="2026-05-01T18:12:30+08:00",
            last_seen_at="2026-05-01T18:12:30+08:00",
            canonical_title="刘小明在海南商业航天发射场看望慰问“五一”假期在岗一线劳动者并调研重点工作进展情况",
            summary="人民财讯5月1日电，据海南日报，5月1日上午，海南省省长刘小明在海南商业航天发射场，看望慰问“五一”假期在岗一线劳动者并调研重点工作进展情况。",
            source="stcn",
            published_at="2026-05-01T18:12:30+08:00",
            url="https://example.com/stcn-hainan-spaceport-public-affairs",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-korea-public-transport",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-south-africa-visa",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["文旅"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-holiday-flow",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["文旅"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-shenzhen-rain",
            direction="bearish",
            impact_score=99.0,
            reasoning="rule",
            themes=["电力资源"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-turkey-fertilizer",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["农业"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-dubai-oracle-building",
            direction="bearish",
            impact_score=99.0,
            reasoning="rule",
            themes=["AI应用"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-ai-keep-public-affairs",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["AI应用"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-hubei-trade-in-subsidy",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["机器人"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-data-cross-border-forum",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["数据安全"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-hainan-spaceport-public-affairs",
            direction="neutral",
            impact_score=79.0,
            reasoning="rule",
            themes=["商业航天"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "千问3.6Plus大模型登顶全球模型调用排行榜首，日调用量破万亿" in content
    assert "5月1日正式启动 湖北以旧换新国补扩品" not in content
    assert "第九届数字中国建设峰会“数据跨境”主题交流活动在福州成功举办" not in content
    assert "刘小明在海南商业航天发射场看望慰问“五一”假期在岗一线劳动者并调研重点工作进展情况" not in content
    assert "能源供应趋紧 韩国鼓励非高峰使用公共交通" not in content
    assert "南非新政延长签证宽限期 将刺激旅游市场" not in content
    assert "清明假期第一天 全社会跨区域人员流动量预计约2.96亿人次" not in content
    assert "深圳市暴雨黄色预警信号扩展至全市" not in content
    assert "农业成本因伊朗战事上升 土耳其取消部分化肥关税" not in content
    assert "迪拜甲骨文大楼外立面遭防空系统拦截碎片击中 无人员伤亡" not in content


def test_write_text_report_filters_stcn_charging_infra_general_fast_news_even_if_analysis_gets_theme(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-charging-infra-fast-news",
            first_seen_at="2026-05-03T18:13:11+08:00",
            last_seen_at="2026-05-03T18:13:11+08:00",
            canonical_title="广汽自营充电桩突破2.5万根，覆盖全国31省213市",
            summary="广汽自营充电桩规模持续扩容。",
            source="stcn",
            published_at="2026-05-03T18:13:11+08:00",
            url="https://example.com/stcn-charging-infra",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-stcn-order-keep",
            first_seen_at="2026-05-03T18:14:00+08:00",
            last_seen_at="2026-05-03T18:14:00+08:00",
            canonical_title="新势能源：与广汽签署战略合作协议",
            summary="双方签署合作协议，推进共建新能源生态。",
            source="stcn",
            published_at="2026-05-03T18:14:00+08:00",
            url="https://example.com/stcn-order-keep",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-charging-infra-fast-news",
            direction="neutral",
            impact_score=79.0,
            reasoning="rule",
            themes=["充电桩"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-order-keep",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["新能源车"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "新势能源：与广汽签署战略合作协议" in content
    assert "广汽自营充电桩突破2.5万根，覆盖全国31省213市" not in content


def test_write_text_report_filters_stcn_robot_half_marathon_story_even_if_analysis_gets_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-robot-half-marathon",
            first_seen_at="2026-04-19T08:25:29+08:00",
            last_seen_at="2026-04-19T08:25:29+08:00",
            canonical_title="“闪电”完成2026人形机器人半马",
            summary="2026人形机器人半程马拉松鸣枪开跑，参赛队伍超百支。",
            source="stcn",
            published_at="2026-04-19T08:25:29+08:00",
            url="https://example.com/stcn-robot-half-marathon",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-stcn-robot-order",
            first_seen_at="2026-04-19T08:26:00+08:00",
            last_seen_at="2026-04-19T08:26:00+08:00",
            canonical_title="某公司获人形机器人批量订单",
            summary="公司获得人形机器人批量订单。",
            source="stcn",
            published_at="2026-04-19T08:26:00+08:00",
            url="https://example.com/stcn-robot-order",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-robot-half-marathon",
            direction="neutral",
            impact_score=79.0,
            reasoning="rule",
            themes=["机器人"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-robot-order",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["机器人"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "“闪电”完成2026人形机器人半马" not in content
    assert "某公司获人形机器人批量订单" in content


def test_write_text_report_filters_current_live_stcn_nonlisted_ai_finance_story(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-webank-ai-finance-story",
            first_seen_at="2026-05-01T11:03:17+08:00",
            last_seen_at="2026-05-01T11:03:17+08:00",
            canonical_title="微众银行总资产超7600亿元 管理资产规模超3.7万亿元",
            summary="人民财讯5月1日电，微众银行披露2025年年报显示，截至2025年末，该行资产总额达7662.9亿元。年报显示，该行加速AI原生能力建设进程，截至2025年末，全行AI算力规模同比提升3.5倍，日均调用量从4.1万次大幅增长至240万次，日均Token消耗从2亿提升至超50亿。",
            source="stcn",
            published_at="2026-05-01T11:03:17+08:00",
            url="https://example.com/stcn-webank-ai-finance-story",
            event_type="fast_news",
            event_subtype="industry_data",
        ),
        Event(
            event_id="event-stcn-ai-keep-nonlisted-finance-contrast",
            first_seen_at="2026-04-04T10:44:37+08:00",
            last_seen_at="2026-04-04T10:44:37+08:00",
            canonical_title="千问3.6Plus大模型登顶全球模型调用排行榜首，日调用量破万亿",
            summary="发布仅1天的千问新模型Qwen3.6-Plus，冲上全球知名大模型API调用平台OpenRouter的日榜榜首。",
            source="stcn",
            published_at="2026-04-04T10:44:37+08:00",
            url="https://example.com/stcn-ai-keep-nonlisted-finance-contrast",
            event_type="fast_news",
            event_subtype="industry_data",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-webank-ai-finance-story",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-ai-keep-nonlisted-finance-contrast",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["AI应用"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "微众银行总资产超7600亿元 管理资产规模超3.7万亿元" not in content
    assert "千问3.6Plus大模型登顶全球模型调用排行榜首，日调用量破万亿" in content


def test_write_text_report_filters_cls_robot_half_marathon_story_without_hiding_robot_order(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-robot-half-marathon",
            first_seen_at="2026-04-19T08:34:48+08:00",
            last_seen_at="2026-04-19T08:34:48+08:00",
            canonical_title="直击2026机器人半马：荣耀闪电率先冲线 速度较去年大幅提升",
            summary="2026人形机器人半程马拉松开跑，荣耀闪电率先冲线。",
            source="cls",
            published_at="2026-04-19T08:34:48+08:00",
            url="https://example.com/cls-robot-half-marathon",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-cls-robot-order",
            first_seen_at="2026-04-19T08:36:00+08:00",
            last_seen_at="2026-04-19T08:36:00+08:00",
            canonical_title="某公司获人形机器人批量订单",
            summary="公司获得人形机器人批量订单。",
            source="cls",
            published_at="2026-04-19T08:36:00+08:00",
            url="https://example.com/cls-robot-order",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cls-robot-half-marathon",
            direction="neutral",
            impact_score=99.3,
            reasoning="rule",
            themes=["机器人"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-robot-order",
            direction="bullish",
            impact_score=99.3,
            reasoning="rule",
            themes=["机器人"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "直击2026机器人半马：荣耀闪电率先冲线 速度较去年大幅提升" not in content
    assert "某公司获人形机器人批量订单" in content


def test_write_text_report_filters_cls_robot_record_race_story_without_hiding_robot_order(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-robot-record-story",
            first_seen_at="2026-04-19T10:00:00+08:00",
            last_seen_at="2026-04-19T10:00:00+08:00",
            canonical_title="宇树称打破人类1500米世界纪录",
            summary="北京人形机器人马拉松排位赛举行，宇树称按比例计算已打破人类1500米世界纪录。",
            source="cls",
            published_at="2026-04-19T10:00:00+08:00",
            url="https://example.com/cls-robot-record-story",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-cls-robot-order-2",
            first_seen_at="2026-04-19T10:05:00+08:00",
            last_seen_at="2026-04-19T10:05:00+08:00",
            canonical_title="某公司获人形机器人批量订单",
            summary="公司获得人形机器人批量订单。",
            source="cls",
            published_at="2026-04-19T10:05:00+08:00",
            url="https://example.com/cls-robot-order-2",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cls-robot-record-story",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["机器人"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-robot-order-2",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["机器人"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "宇树称打破人类1500米世界纪录" not in content
    assert "某公司获人形机器人批量订单" in content


def test_write_text_report_filters_stcn_robot_half_marathon_supply_chain_story_without_hiding_robot_order(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-robot-half-marathon-supply-chain",
            first_seen_at="2026-04-19T11:02:14+08:00",
            last_seen_at="2026-04-19T11:02:14+08:00",
            canonical_title="荣耀机器人半马夺冠 领益智造批量交付其全套金属结构件等产品",
            summary="2026北京亦庄半程马拉松暨人形机器人半程马拉松上，“闪电”机器人夺冠。领益是其全套结构件和表面处理核心供应商，已批量交付产品。",
            source="stcn",
            published_at="2026-04-19T11:02:14+08:00",
            url="https://example.com/stcn-robot-half-marathon-supply-chain",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-cls-robot-half-marathon-uwb-supply-chain",
            first_seen_at="2026-04-21T10:39:15+08:00",
            last_seen_at="2026-04-21T10:39:15+08:00",
            canonical_title="荣耀夺冠机器人“空间神经末梢”由深圳纽瑞芯提供",
            summary="北京亦庄人形机器人半程马拉松，荣耀自研的“闪电”机器人包揽赛事该组前三。令人瞩目的是，排名前三的机器人成绩均大幅超越了目前人类半程马拉松世界纪录。近日，记者独家获悉，“闪电”机器人的“神经末梢”UWB由深圳市纽瑞芯科技有限公司提供。荣耀就走在了前面，已确定在机器人中，标配纽瑞芯UWB芯片产品。",
            source="cls",
            published_at="2026-04-21T10:39:15+08:00",
            url="https://example.com/cls-robot-half-marathon-uwb-supply-chain",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-stcn-robot-order-2",
            first_seen_at="2026-04-19T11:05:00+08:00",
            last_seen_at="2026-04-19T11:05:00+08:00",
            canonical_title="某公司获人形机器人批量订单",
            summary="公司获得人形机器人批量订单。",
            source="stcn",
            published_at="2026-04-19T11:05:00+08:00",
            url="https://example.com/stcn-robot-order-2",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-robot-half-marathon-supply-chain",
            direction="neutral",
            impact_score=79.0,
            reasoning="rule",
            themes=["机器人"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-robot-half-marathon-uwb-supply-chain",
            direction="neutral",
            impact_score=79.3,
            reasoning="rule",
            themes=["机器人"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-robot-order-2",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["机器人"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "荣耀机器人半马夺冠 领益智造批量交付其全套金属结构件等产品" not in content
    assert "荣耀夺冠机器人“空间神经末梢”由深圳纽瑞芯提供" not in content
    assert "某公司获人形机器人批量订单" in content


def test_write_text_report_filters_stcn_public_affairs_conference_story_even_if_analysis_gets_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-fujian-cultural-tourism-conference",
            first_seen_at="2026-04-19T10:12:29+08:00",
            last_seen_at="2026-04-19T10:12:29+08:00",
            canonical_title="2026年福建省文旅经济发展大会召开",
            summary="据福建日报，2026年福建省文旅经济发展大会在漳州召开，强调把文化旅游业培育成为支柱产业。",
            source="stcn",
            published_at="2026-04-19T10:12:29+08:00",
            url="https://example.com/stcn-fujian-cultural-tourism-conference",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-stcn-heilongjiang-consumption-week",
            first_seen_at="2026-05-01T08:31:17+08:00",
            last_seen_at="2026-05-01T08:31:17+08:00",
            canonical_title="黑龙江省启动“五一”文旅消费周活动",
            summary="据黑龙江发布，为贯彻落实文化和旅游部2026年全国“五一”文化和旅游消费周工作部署，“五一”假期，黑龙江省围绕“北国好风光 惠聚黑龙江”主题，发放文旅消费券5000万元，统筹推出百条精品线路、百场特色活动、百项惠民政策。",
            source="stcn",
            published_at="2026-05-01T08:31:17+08:00",
            url="https://example.com/stcn-heilongjiang-consumption-week",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-stcn-keep-cultural-tourism-order",
            first_seen_at="2026-04-19T10:20:00+08:00",
            last_seen_at="2026-04-19T10:20:00+08:00",
            canonical_title="某公司签约大型文旅项目建设协议",
            summary="公司签约大型文旅项目建设协议。",
            source="stcn",
            published_at="2026-04-19T10:20:00+08:00",
            url="https://example.com/stcn-keep-cultural-tourism-order",
            event_type="hard_event",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-fujian-cultural-tourism-conference",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["文旅"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-heilongjiang-consumption-week",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["文旅"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-cultural-tourism-order",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["文旅"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "2026年福建省文旅经济发展大会召开" not in content
    assert "黑龙江省启动“五一”文旅消费周活动" not in content
    assert "某公司签约大型文旅项目建设协议" in content


def test_write_text_report_filters_stcn_operational_update_with_stable_order_wording(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-operational-update",
            first_seen_at="2026-04-04T10:31:35+08:00",
            last_seen_at="2026-04-04T10:31:35+08:00",
            canonical_title="宏明电子：目前生产经营正常，订单情况整体稳定",
            summary="公司表示目前产销与交付安排正常，订单情况整体稳定。",
            source="stcn",
            published_at="2026-04-04T10:31:35+08:00",
            url="https://example.com/stcn-operational-update",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-stcn-travel-keep-4",
            first_seen_at="2026-04-02T17:49:06+08:00",
            last_seen_at="2026-04-02T17:49:06+08:00",
            canonical_title="2026清明档电影片单发布",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T17:49:06+08:00",
            url="https://example.com/stcn-travel-keep-4",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-operational-update",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-travel-keep-4",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["文旅"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "2026清明档电影片单发布" in content
    assert "宏明电子：目前生产经营正常，订单情况整体稳定" not in content


def test_write_text_report_filters_stcn_interactive_order_plenty_update_without_hiding_substantive_order(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-interactive-order-plenty",
            first_seen_at="2026-04-21T12:26:13+08:00",
            last_seen_at="2026-04-21T12:26:13+08:00",
            canonical_title="协创数据：2026年将持续加大算力业务投入 目前在手订单充裕",
            summary="人民财讯4月21日电，协创数据(300857)4月21日在互动平台表示，公司坚定看好AI算力市场的长期发展，2026年将持续加大算力业务投入，巩固公司云算力服务的核心竞争力，目前公司在手订单充裕，交付有序进行。",
            source="stcn",
            published_at="2026-04-21T12:26:13+08:00",
            url="https://example.com/stcn-interactive-order-plenty",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-stcn-substantive-order-keep",
            first_seen_at="2026-04-21T12:20:00+08:00",
            last_seen_at="2026-04-21T12:20:00+08:00",
            canonical_title="某公司获人形机器人批量订单",
            summary="summary",
            source="stcn",
            published_at="2026-04-21T12:20:00+08:00",
            url="https://example.com/stcn-substantive-order-keep",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-interactive-order-plenty",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-substantive-order-keep",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["机器人"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "协创数据：2026年将持续加大算力业务投入 目前在手订单充裕" not in content
    assert "某公司获人形机器人批量订单" in content


def test_write_text_report_keeps_cninfo_disclosure_with_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-themed",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="江苏华盛锂电材料股份有限公司关于召开2025年年度业绩暨现金分红说明会的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-themed",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-themed",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["锂电池"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "江苏华盛锂电材料股份有限公司关于召开2025年年度业绩暨现金分红说明会的公告" in content


def test_write_text_report_filters_cninfo_risk_assessment_report_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-risk-report",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="关于对郑州宇通集团财务有限公司风险评估报告的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-risk-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-oil",
            first_seen_at="2026-04-02T18:57:27+08:00",
            last_seen_at="2026-04-02T18:57:27+08:00",
            canonical_title="布伦特原油期货涨幅扩大至8%",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T18:57:27+08:00",
            url="https://example.com/stcn-oil",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-risk-report",
            direction="bearish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-oil",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "布伦特原油期货涨幅扩大至8%" in content
    assert "关于对郑州宇通集团财务有限公司风险评估报告的公告" not in content


def test_write_text_report_filters_cninfo_risk_sustained_assessment_report_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-risk-sustained-report",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="关于四川长虹集团财务有限公司的风险持续评估报告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-risk-sustained-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-power",
            first_seen_at="2026-04-02T20:59:03+08:00",
            last_seen_at="2026-04-02T20:59:03+08:00",
            canonical_title="中国能建与华北电力大学签署战略合作协议",
            summary="双方将围绕构建新型能源体系和新型电力系统深化合作。",
            source="stcn",
            published_at="2026-04-02T20:59:03+08:00",
            url="https://example.com/stcn-power",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-risk-sustained-report",
            direction="bearish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-power",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["电力资源"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中国能建与华北电力大学签署战略合作协议" in content
    assert "关于四川长虹集团财务有限公司的风险持续评估报告" not in content


def test_write_text_report_filters_cninfo_equity_incentive_legal_opinion_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-legal-opinion",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="2025年限制性股票激励计划第一个解除限售期解锁条件成就暨调整回购价格及回购注销部分限制性股票相关事宜的法律意见书",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-legal-opinion",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-stcn-travel",
            first_seen_at="2026-04-02T17:49:06+08:00",
            last_seen_at="2026-04-02T17:49:06+08:00",
            canonical_title="2026清明档电影片单发布",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T17:49:06+08:00",
            url="https://example.com/stcn-travel",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-legal-opinion",
            direction="bearish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-travel",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["文旅"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "2026清明档电影片单发布" in content
    assert (
        "2025年限制性股票激励计划第一个解除限售期解锁条件成就暨调整回购价格及回购注销部分限制性股票相关事宜的法律意见书"
        not in content
    )


def test_write_text_report_filters_cninfo_statement_and_briefing_materials_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-duty-report",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="晋西车轴独立董事2025年度述职报告（贾小荣）",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-duty-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-cninfo-earnings-briefing",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="晋西车轴关于召开2025年年度业绩说明会的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-earnings-briefing",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-nev",
            first_seen_at="2026-04-02T17:45:53+08:00",
            last_seen_at="2026-04-02T17:45:53+08:00",
            canonical_title="乘联分会：3月全国乘用车厂商新能源批发预估112万辆",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T17:45:53+08:00",
            url="https://example.com/stcn-nev",
            event_type="fast_news",
            event_subtype="industry_data",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-duty-report",
            direction="bullish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cninfo-earnings-briefing",
            direction="bullish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-nev",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["新能源车"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "乘联分会：3月全国乘用车厂商新能源批发预估112万辆" in content
    assert "晋西车轴独立董事2025年度述职报告（贾小荣）" not in content
    assert "晋西车轴关于召开2025年年度业绩说明会的公告" not in content


def test_write_text_report_filters_cninfo_esg_and_attestation_materials_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-esg-report",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="晋西车轴2025年度环境、社会与公司治理（ESG）报告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-esg-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-cninfo-attestation",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="晋西车轴2025年度营业收入扣除表的鉴证报告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-attestation",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-power",
            first_seen_at="2026-04-02T20:59:03+08:00",
            last_seen_at="2026-04-02T20:59:03+08:00",
            canonical_title="中国能建与华北电力大学签署战略合作协议",
            summary="双方将围绕构建新型能源体系和新型电力系统深化合作。",
            source="stcn",
            published_at="2026-04-02T20:59:03+08:00",
            url="https://example.com/stcn-power",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-esg-report",
            direction="bullish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cninfo-attestation",
            direction="bullish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-power",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["电力资源"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中国能建与华北电力大学签署战略合作协议" in content
    assert "晋西车轴2025年度环境、社会与公司治理（ESG）报告" not in content
    assert "晋西车轴2025年度营业收入扣除表的鉴证报告" not in content


def test_write_text_report_filters_board_resolution_independence_opinion_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-independence-opinion",
            first_seen_at="2026-04-03T00:00:00+08:00",
            last_seen_at="2026-04-03T00:00:00+08:00",
            canonical_title="晋西车轴董事会关于独立董事独立性情况的专项意见",
            summary="summary",
            source="cninfo",
            published_at="2026-04-03T00:00:00+08:00",
            url="https://example.com/cninfo-independence-opinion",
            event_type="hard_event",
            event_subtype="board_resolution",
        ),
        Event(
            event_id="event-stcn-travel",
            first_seen_at="2026-04-02T17:49:06+08:00",
            last_seen_at="2026-04-02T17:49:06+08:00",
            canonical_title="2026清明档电影片单发布",
            summary="summary",
            source="stcn",
            published_at="2026-04-02T17:49:06+08:00",
            url="https://example.com/stcn-travel",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-independence-opinion",
            direction="bullish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-travel",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["文旅"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "2026清明档电影片单发布" in content
    assert "晋西车轴董事会关于独立董事独立性情况的专项意见" not in content


def test_write_text_report_filters_stcn_reverse_repo_operation_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-reverse-repo",
            first_seen_at="2026-04-08T09:24:10+08:00",
            last_seen_at="2026-04-08T09:24:10+08:00",
            canonical_title="央行4月8日开展5亿元7天期逆回购操作",
            summary="人民财讯4月8日电，4月8日，央行公开市场开展5亿元7天期逆回购操作，操作利率1.40%。",
            source="stcn",
            published_at="2026-04-08T09:24:10+08:00",
            url="https://example.com/stcn-reverse-repo",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-reverse-repo",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "央行4月8日开展5亿元7天期逆回购操作" not in content


def test_write_text_report_filters_stcn_fx_fixing_update_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-fx-fixing",
            first_seen_at="2026-04-08T09:16:50+08:00",
            last_seen_at="2026-04-08T09:16:50+08:00",
            canonical_title="4月8日人民币对美元中间价调升174个基点",
            summary="人民财讯4月8日电，4月8日，人民币对美元中间价调升174个基点，报6.8680，上一交易日中间价6.8854。",
            source="stcn",
            published_at="2026-04-08T09:16:50+08:00",
            url="https://example.com/stcn-fx-fixing",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-stcn-fx-fixing",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "4月8日人民币对美元中间价调升174个基点" not in content


def test_write_text_report_filters_cninfo_restructuring_material_reply_with_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-restructuring-reply",
            first_seen_at="2026-04-08T20:00:00+08:00",
            last_seen_at="2026-04-08T20:00:00+08:00",
            canonical_title="中芯国际关于发行股份购买资产暨关联交易的审核问询函回复的提示性公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-08T20:00:00+08:00",
            url="https://example.com/cninfo-restructuring-reply",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-semiconductor-keep",
            first_seen_at="2026-04-08T20:01:00+08:00",
            last_seen_at="2026-04-08T20:01:00+08:00",
            canonical_title="国产EDA工具链和先进封装产线建设提速",
            summary="summary",
            source="stcn",
            published_at="2026-04-08T20:01:00+08:00",
            url="https://example.com/stcn-semiconductor-keep",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-restructuring-reply",
            direction="bullish",
            impact_score=100.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-semiconductor-keep",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "国产EDA工具链和先进封装产线建设提速" in content
    assert "中芯国际关于发行股份购买资产暨关联交易的审核问询函回复的提示性公告" not in content

def test_write_text_report_filters_cninfo_restructuring_revised_report_with_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-restructuring-revised-report",
            first_seen_at="2026-04-23T09:00:00+08:00",
            last_seen_at="2026-04-23T09:00:00+08:00",
            canonical_title="中芯国际集成电路制造有限公司发行股份购买资产暨关联交易报告书（修订稿）",
            summary="summary",
            source="cninfo",
            published_at="2026-04-23T09:00:00+08:00",
            url="https://example.com/cninfo-restructuring-revised-report",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-keep-semiconductor-progress",
            first_seen_at="2026-04-23T09:01:00+08:00",
            last_seen_at="2026-04-23T09:01:00+08:00",
            canonical_title="国产EDA工具链和先进封装产线建设提速",
            summary="summary",
            source="stcn",
            published_at="2026-04-23T09:01:00+08:00",
            url="https://example.com/keep-semiconductor-progress",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-restructuring-revised-report",
            direction="bullish",
            impact_score=100.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-semiconductor-progress",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "国产EDA工具链和先进封装产线建设提速" in content
    assert "中芯国际集成电路制造有限公司发行股份购买资产暨关联交易报告书（修订稿）" not in content


def test_write_text_report_filters_cninfo_restructuring_material_reply_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-restructuring-reply-no-theme",
            first_seen_at="2026-04-08T20:00:00+08:00",
            last_seen_at="2026-04-08T20:00:00+08:00",
            canonical_title="中芯国际关于发行股份购买资产暨关联交易的审核问询函回复的提示性公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-08T20:00:00+08:00",
            url="https://example.com/cninfo-restructuring-reply-no-theme",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-semiconductor-keep-no-theme",
            first_seen_at="2026-04-08T20:01:00+08:00",
            last_seen_at="2026-04-08T20:01:00+08:00",
            canonical_title="国产EDA工具链和先进封装产线建设提速",
            summary="summary",
            source="stcn",
            published_at="2026-04-08T20:01:00+08:00",
            url="https://example.com/stcn-semiconductor-keep-no-theme",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-restructuring-reply-no-theme",
            direction="neutral",
            impact_score=75.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-semiconductor-keep-no-theme",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "国产EDA工具链和先进封装产线建设提速" in content
    assert "中芯国际关于发行股份购买资产暨关联交易的审核问询函回复的提示性公告" not in content


def test_write_text_report_filters_cninfo_restructuring_revised_report_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-restructuring-revised-report-no-theme",
            first_seen_at="2026-04-23T09:00:00+08:00",
            last_seen_at="2026-04-23T09:00:00+08:00",
            canonical_title="中芯国际集成电路制造有限公司发行股份购买资产暨关联交易报告书（修订稿）",
            summary="summary",
            source="cninfo",
            published_at="2026-04-23T09:00:00+08:00",
            url="https://example.com/cninfo-restructuring-revised-report-no-theme",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-stcn-semiconductor-keep-no-theme-2",
            first_seen_at="2026-04-23T09:01:00+08:00",
            last_seen_at="2026-04-23T09:01:00+08:00",
            canonical_title="国产EDA工具链和先进封装产线建设提速",
            summary="summary",
            source="stcn",
            published_at="2026-04-23T09:01:00+08:00",
            url="https://example.com/keep-semiconductor-progress-no-theme",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-restructuring-revised-report-no-theme",
            direction="neutral",
            impact_score=75.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-semiconductor-keep-no-theme-2",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "国产EDA工具链和先进封装产线建设提速" in content
    assert "中芯国际集成电路制造有限公司发行股份购买资产暨关联交易报告书（修订稿）" not in content


def test_write_text_report_filters_cninfo_restructuring_special_audit_verification_opinion_without_theme(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-restructuring-special-audit-verification-opinion",
            first_seen_at="2026-05-05T18:45:00+08:00",
            last_seen_at="2026-05-05T18:45:00+08:00",
            canonical_title="欧菲光：中兴华会计师事务所（特殊普通合伙）关于欧菲光集团股份有限公司发行股份购买资产的审核问询函的专项核查意见",
            summary="summary",
            source="cninfo",
            published_at="2026-05-05T18:45:00+08:00",
            url="https://example.com/cninfo-restructuring-verification-opinion",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-semiconductor-progress",
            first_seen_at="2026-05-05T18:46:00+08:00",
            last_seen_at="2026-05-05T18:46:00+08:00",
            canonical_title="国产EDA工具链和先进封装产线建设提速",
            summary="summary",
            source="stcn",
            published_at="2026-05-05T18:46:00+08:00",
            url="https://example.com/keep-semiconductor-progress",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cninfo-restructuring-special-audit-verification-opinion",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-semiconductor-progress",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "国产EDA工具链和先进封装产线建设提速" in content
    assert (
        "欧菲光：中兴华会计师事务所（特殊普通合伙）关于欧菲光集团股份有限公司发行股份购买资产的审核问询函的专项核查意见"
        not in content
    )


def test_write_text_report_filters_exchange_inquiry_reply_and_special_explanation_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-annual-report-inquiry-reply",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="*ST仁东：关于对深圳证券交易所2025年年报问询函回复的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-annual-report-inquiry-reply",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-special-explanation",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="*ST仁东：评估机构关于仁东控股年报问询函有关问题的专项说明",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-special-explanation",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-keep-inquiry-filter",
            first_seen_at="2026-04-10T20:01:00+08:00",
            last_seen_at="2026-04-10T20:01:00+08:00",
            canonical_title="三峡能源与远景能源签署战略合作协议",
            summary="summary",
            source="stcn",
            published_at="2026-04-10T20:01:00+08:00",
            url="https://example.com/stcn-keep-inquiry-filter",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-annual-report-inquiry-reply",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-special-explanation",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-inquiry-filter",
            direction="bullish",
            impact_score=96.0,
            reasoning="rule",
            themes=["电力资源", "储能"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "三峡能源与远景能源签署战略合作协议" in content
    assert "*ST仁东：关于对深圳证券交易所2025年年报问询函回复的公告" not in content
    assert "*ST仁东：评估机构关于仁东控股年报问询函有关问题的专项说明" not in content


def test_write_text_report_filters_financing_inquiry_reply_and_judicial_unfreeze_without_hiding_catalyst(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-financing-inquiry-reply",
            first_seen_at="2026-04-16T00:00:00+08:00",
            last_seen_at="2026-04-16T00:00:00+08:00",
            canonical_title="亿道信息：深圳市亿道信息股份有限公司关于深圳证券交易所《关于深圳市亿道信息股份有限公司发行股份及支付现金购买资产并募集配套资金申请的审核问询函》之回复",
            summary="summary",
            source="szse",
            published_at="2026-04-16T00:00:00+08:00",
            url="https://example.com/financing-inquiry-reply",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-judicial-unfreeze",
            first_seen_at="2026-04-16T00:01:00+08:00",
            last_seen_at="2026-04-16T00:01:00+08:00",
            canonical_title="居然智家：关于公司原实际控制人所持公司股份解除司法冻结的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-16T00:01:00+08:00",
            url="https://example.com/judicial-unfreeze",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-16T00:02:00+08:00",
            last_seen_at="2026-04-16T00:02:00+08:00",
            canonical_title="云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目",
            summary="summary",
            source="cls",
            published_at="2026-04-16T18:51:44+08:00",
            url="https://example.com/keep-acquisition",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-financing-inquiry-reply",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-judicial-unfreeze",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-acquisition",
            direction="bullish",
            impact_score=99.3,
            reasoning="rule",
            themes=["锂电池"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目" in content
    assert "亿道信息：深圳市亿道信息股份有限公司关于深圳证券交易所" not in content
    assert "居然智家：关于公司原实际控制人所持公司股份解除司法冻结的公告" not in content


def test_write_text_report_filters_hkex_governance_and_material_announcements_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-hkex-placeholder",
            first_seen_at="2026-04-11T09:00:00+08:00",
            last_seen_at="2026-04-11T09:00:00+08:00",
            canonical_title="An announcement has just been published by the Company on the HKEXnews website: Chinese section of the Current Listed Company Information",
            summary="summary",
            source="hkex",
            published_at="2026-04-11T09:00:00+08:00",
            url="https://example.com/hkex-placeholder",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-monthly-return",
            first_seen_at="2026-04-11T09:01:00+08:00",
            last_seen_at="2026-04-11T09:01:00+08:00",
            canonical_title="Monthly Return of Equity Issuer on Movements in Securities for the month ended 31 March 2026",
            summary="summary",
            source="hkex",
            published_at="2026-04-11T09:01:00+08:00",
            url="https://example.com/hkex-monthly-return",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-agm-notice",
            first_seen_at="2026-04-11T09:02:00+08:00",
            last_seen_at="2026-04-11T09:02:00+08:00",
            canonical_title="Notice of Annual General Meeting",
            summary="summary",
            source="hkex",
            published_at="2026-04-11T09:02:00+08:00",
            url="https://example.com/hkex-agm-notice",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-proxy-form",
            first_seen_at="2026-04-11T09:03:00+08:00",
            last_seen_at="2026-04-11T09:03:00+08:00",
            canonical_title="Proxy Form for Annual General Meeting",
            summary="summary",
            source="hkex",
            published_at="2026-04-11T09:03:00+08:00",
            url="https://example.com/hkex-proxy-form",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-annual-report",
            first_seen_at="2026-04-11T09:04:00+08:00",
            last_seen_at="2026-04-11T09:04:00+08:00",
            canonical_title="Annual Report 2025",
            summary="summary",
            source="hkex",
            published_at="2026-04-11T09:04:00+08:00",
            url="https://example.com/hkex-annual-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-esg-report",
            first_seen_at="2026-04-11T09:05:00+08:00",
            last_seen_at="2026-04-11T09:05:00+08:00",
            canonical_title="Environmental, Social and Governance Report 2025",
            summary="summary",
            source="hkex",
            published_at="2026-04-11T09:05:00+08:00",
            url="https://example.com/hkex-esg-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-board-meeting",
            first_seen_at="2026-04-11T09:06:00+08:00",
            last_seen_at="2026-04-11T09:06:00+08:00",
            canonical_title="Date of Board Meeting",
            summary="summary",
            source="hkex",
            published_at="2026-04-11T09:06:00+08:00",
            url="https://example.com/hkex-board-meeting",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-chinese-section-placeholder",
            first_seen_at="2026-04-17T21:17:00+08:00",
            last_seen_at="2026-04-17T21:17:00+08:00",
            canonical_title="An announcement has just been published by the issuer in the Chinese section of this website, a corresponding version of which may or may not be published in this section",
            summary="summary",
            source="hkex",
            published_at="2026-04-17T21:17:00+08:00",
            url="https://example.com/hkex-chinese-section-placeholder",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-general-mandates",
            first_seen_at="2026-04-17T21:10:00+08:00",
            last_seen_at="2026-04-17T21:10:00+08:00",
            canonical_title="PROPOSALS FOR GENERAL MANDATES TO ISSUE SHARES AND PURCHASE SHARES AND RE-ELECTION OF DIRECTORS AND PROPOSED AMENDMENTS TO THE MEMORANDUM AND ARTICLES OF ASSOCIATION AND THE ADOPTION OF THE THIRD AMENDED AND RESTATED MEMORANDUM AND ARTICLES OF ASSOCIATION AND NOTICE OF ANNUAL GENERAL MEETING",
            summary="summary",
            source="hkex",
            published_at="2026-04-17T21:10:00+08:00",
            url="https://example.com/hkex-general-mandates",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-keep-hkex-filter",
            first_seen_at="2026-04-17T20:01:00+08:00",
            last_seen_at="2026-04-17T20:01:00+08:00",
            canonical_title="国产EDA工具链和先进封装产线建设提速",
            summary="summary",
            source="stcn",
            published_at="2026-04-17T20:01:00+08:00",
            url="https://example.com/stcn-keep-hkex-filter",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-hkex-placeholder",
            direction="neutral",
            impact_score=81.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-monthly-return",
            direction="neutral",
            impact_score=81.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-agm-notice",
            direction="neutral",
            impact_score=81.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-proxy-form",
            direction="neutral",
            impact_score=81.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-annual-report",
            direction="neutral",
            impact_score=81.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-esg-report",
            direction="neutral",
            impact_score=81.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-board-meeting",
            direction="neutral",
            impact_score=81.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-chinese-section-placeholder",
            direction="neutral",
            impact_score=81.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-general-mandates",
            direction="neutral",
            impact_score=81.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-hkex-filter",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "国产EDA工具链和先进封装产线建设提速" in content
    assert "An announcement has just been published by the Company" not in content
    assert "Monthly Return of Equity Issuer on Movements in Securities for the month ended 31 March 2026" not in content
    assert "Notice of Annual General Meeting" not in content
    assert "Proxy Form for Annual General Meeting" not in content
    assert "Annual Report 2025" not in content
    assert "Environmental, Social and Governance Report 2025" not in content
    assert "Date of Board Meeting" not in content
    assert "An announcement has just been published by the issuer in the Chinese section" not in content
    assert "PROPOSALS FOR GENERAL MANDATES TO ISSUE SHARES AND PURCHASE SHARES" not in content


def test_write_text_report_keeps_hkex_transaction_catalyst_while_filtering_governance_material(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-hkex-governance-material",
            first_seen_at="2026-04-17T21:17:00+08:00",
            last_seen_at="2026-04-17T21:17:00+08:00",
            canonical_title="NOTICE OF ANNUAL GENERAL MEETING",
            summary="NOTICE OF ANNUAL GENERAL MEETING",
            source="hkex",
            published_at="2026-04-17T21:17:00+08:00",
            url="https://example.com/hkex-governance-material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-transaction-catalyst",
            first_seen_at="2026-04-17T21:08:00+08:00",
            last_seen_at="2026-04-17T21:08:00+08:00",
            canonical_title="MAJOR TRANSACTION - SALE AND LEASEBACK ARRANGEMENT",
            summary="MAJOR TRANSACTION - SALE AND LEASEBACK ARRANGEMENT",
            source="hkex",
            published_at="2026-04-17T21:08:00+08:00",
            url="https://example.com/hkex-transaction-catalyst",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-hkex-governance-material",
            direction="neutral",
            impact_score=81.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-transaction-catalyst",
            direction="neutral",
            impact_score=81.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "MAJOR TRANSACTION - SALE AND LEASEBACK ARRANGEMENT" in content
    assert "NOTICE OF ANNUAL GENERAL MEETING" not in content


def test_write_text_report_filters_hkex_compound_governance_transaction_material_without_hiding_pure_transaction(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-hkex-compound-governance-transaction-material",
            first_seen_at="2026-04-17T22:48:00+08:00",
            last_seen_at="2026-04-17T22:48:00+08:00",
            canonical_title="(1) RENEWAL OF EXISTING CONTINUING CONNECTED TRANSACTIONS; (2) PROPOSED GRANT OF GENERAL MANDATES TO ISSUE AND REPURCHASE SHARES; (3) RE-ELECTION OF RETIRING DIRECTORS; (4) RE-APPOINTMENT OF AUDITOR; AND NOTICE OF ANNUAL GENERAL MEETING",
            summary="(1) RENEWAL OF EXISTING CONTINUING CONNECTED TRANSACTIONS; (2) PROPOSED GRANT OF GENERAL MANDATES TO ISSUE AND REPURCHASE SHARES; (3) RE-ELECTION OF RETIRING DIRECTORS; (4) RE-APPOINTMENT OF AUDITOR; AND NOTICE OF ANNUAL GENERAL MEETING",
            source="hkex",
            published_at="2026-04-17T22:48:00+08:00",
            url="https://example.com/hkex-compound-governance-transaction-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-pure-transaction-keep",
            first_seen_at="2026-04-17T22:55:00+08:00",
            last_seen_at="2026-04-17T22:55:00+08:00",
            canonical_title="DISCLOSEABLE TRANSACTION - PROVISION OF LOAN",
            summary="DISCLOSEABLE TRANSACTION - PROVISION OF LOAN",
            source="hkex",
            published_at="2026-04-17T22:55:00+08:00",
            url="https://example.com/hkex-pure-transaction-keep",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-hkex-compound-governance-transaction-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-pure-transaction-keep",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "DISCLOSEABLE TRANSACTION - PROVISION OF LOAN" in content
    assert "RENEWAL OF EXISTING CONTINUING CONNECTED TRANSACTIONS" not in content


def test_write_text_report_filters_hkex_rule_14a60_continuing_connected_transaction_without_hiding_plain_connected_transaction(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-hkex-rule-14a60-material",
            first_seen_at="2026-04-17T22:08:00+08:00",
            last_seen_at="2026-04-17T22:08:00+08:00",
            canonical_title="CONTINUING CONNECTED TRANSACTIONS PURSUANT TO RULE 14A.60 OF THE LISTING RULES",
            summary="CONTINUING CONNECTED TRANSACTIONS PURSUANT TO RULE 14A.60 OF THE LISTING RULES",
            source="hkex",
            published_at="2026-04-17T22:08:00+08:00",
            url="https://example.com/hkex-rule-14a60-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-plain-connected-transaction-keep",
            first_seen_at="2026-04-17T22:54:00+08:00",
            last_seen_at="2026-04-17T22:54:00+08:00",
            canonical_title="PLACING OF NEW SHARES UNDER SPECIFIC MANDATE AND CONNECTED TRANSACTION UNDERWRITING ARRANGEMENT BY A CONTROLLING SHAREHOLDER",
            summary="PLACING OF NEW SHARES UNDER SPECIFIC MANDATE AND CONNECTED TRANSACTION UNDERWRITING ARRANGEMENT BY A CONTROLLING SHAREHOLDER",
            source="hkex",
            published_at="2026-04-17T22:54:00+08:00",
            url="https://example.com/hkex-plain-connected-transaction-keep",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-hkex-rule-14a60-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-plain-connected-transaction-keep",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "CONNECTED TRANSACTION UNDERWRITING ARRANGEMENT" in content
    assert "CONTINUING CONNECTED TRANSACTIONS PURSUANT TO RULE 14A.60" not in content


def test_write_text_report_filters_hkex_material_disclosure_variants_without_hiding_profit_warning_or_transactions(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-hkex-performance-undertaking-material",
            first_seen_at="2026-04-21T09:00:00+08:00",
            last_seen_at="2026-04-21T09:00:00+08:00",
            canonical_title="ANNOUNCEMENT ON THE RESULTS OF FULFILMENT OF THE PERFORMANCE UNDERTAKING IN RELATION TO THE ACQUISITION",
            summary="ANNOUNCEMENT ON THE RESULTS OF FULFILMENT OF THE PERFORMANCE UNDERTAKING IN RELATION TO THE ACQUISITION",
            source="hkex",
            published_at="2026-04-21T09:00:00+08:00",
            url="https://example.com/hkex-performance-undertaking-material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-results-update-material",
            first_seen_at="2026-04-21T09:01:00+08:00",
            last_seen_at="2026-04-21T09:01:00+08:00",
            canonical_title="INSIDE INFORMATION LATEST RESULTS UPDATE FOR THE FIRST QUARTER OF 2026 AND EXPLANATION OF THE EXPECTED IMPACT OF THE ACCOUNTING TREATMENT OF THE CONVERTIBLE BONDS ON THE FINANCIAL PERFORMANCE FOR THE FISCAL YEAR 2026",
            summary="INSIDE INFORMATION LATEST RESULTS UPDATE FOR THE FIRST QUARTER OF 2026 AND EXPLANATION OF THE EXPECTED IMPACT OF THE ACCOUNTING TREATMENT OF THE CONVERTIBLE BONDS ON THE FINANCIAL PERFORMANCE FOR THE FISCAL YEAR 2026",
            source="hkex",
            published_at="2026-04-21T09:01:00+08:00",
            url="https://example.com/hkex-results-update-material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-resumption-guidance-material",
            first_seen_at="2026-04-21T09:02:00+08:00",
            last_seen_at="2026-04-21T09:02:00+08:00",
            canonical_title="ADDITIONAL RESUMPTION GUIDANCE AND CONTINUED SUSPENSION OF TRADING",
            summary="ADDITIONAL RESUMPTION GUIDANCE AND CONTINUED SUSPENSION OF TRADING",
            source="hkex",
            published_at="2026-04-21T09:02:00+08:00",
            url="https://example.com/hkex-resumption-guidance-material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-profit-warning-keep",
            first_seen_at="2026-04-21T09:03:00+08:00",
            last_seen_at="2026-04-21T09:03:00+08:00",
            canonical_title="INSIDE INFORMATION - PROFIT WARNING",
            summary="INSIDE INFORMATION - PROFIT WARNING",
            source="hkex",
            published_at="2026-04-21T09:03:00+08:00",
            url="https://example.com/hkex-profit-warning-keep",
            event_type="hard_event",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-hkex-transaction-keep",
            first_seen_at="2026-04-21T09:04:00+08:00",
            last_seen_at="2026-04-21T09:04:00+08:00",
            canonical_title="DISCLOSEABLE TRANSACTION - PROVISION OF LOAN",
            summary="DISCLOSEABLE TRANSACTION - PROVISION OF LOAN",
            source="hkex",
            published_at="2026-04-21T09:04:00+08:00",
            url="https://example.com/hkex-transaction-keep",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-hkex-performance-undertaking-material",
            direction="neutral",
            impact_score=81.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-results-update-material",
            direction="neutral",
            impact_score=81.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-resumption-guidance-material",
            direction="neutral",
            impact_score=81.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-profit-warning-keep",
            direction="bearish",
            impact_score=88.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-transaction-keep",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "ANNOUNCEMENT ON THE RESULTS OF FULFILMENT OF THE PERFORMANCE UNDERTAKING IN RELATION TO THE ACQUISITION" not in content
    assert "INSIDE INFORMATION LATEST RESULTS UPDATE FOR THE FIRST QUARTER OF 2026" not in content
    assert "ADDITIONAL RESUMPTION GUIDANCE AND CONTINUED SUSPENSION OF TRADING" not in content
    assert "INSIDE INFORMATION - PROFIT WARNING" in content
    assert "DISCLOSEABLE TRANSACTION - PROVISION OF LOAN" in content


def test_write_text_report_filters_hkex_transaction_material_variants_without_hiding_pure_transaction(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-hkex-agm-transaction-material",
            first_seen_at="2026-04-21T20:13:00+08:00",
            last_seen_at="2026-04-21T20:13:00+08:00",
            canonical_title="NOTICE OF THE 2025 AGM AND ADDITIONAL INFORMATION ON THE CONTINUING CONNECTED TRANSACTION",
            summary="NOTICE OF THE 2025 AGM AND ADDITIONAL INFORMATION ON THE CONTINUING CONNECTED TRANSACTION",
            source="hkex",
            published_at="2026-04-21T20:13:00+08:00",
            url="https://example.com/hkex-agm-transaction-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-circular-delay-material",
            first_seen_at="2026-04-21T19:22:00+08:00",
            last_seen_at="2026-04-21T19:22:00+08:00",
            canonical_title="FURTHER DELAY IN DESPATCH OF THE MAJOR AND CONNECTED TRANSACTION CIRCULAR IN RELATION TO THE PROPOSED VAX ACQUISITION UNDER THE VAX SALE AND PURCHASE AGREEMENT INVOLVING ISSUE OF CONSIDERATION CONVERTIBLE BONDS UNDER SPECIFIC MANDATE",
            summary="FURTHER DELAY IN DESPATCH OF THE MAJOR AND CONNECTED TRANSACTION CIRCULAR IN RELATION TO THE PROPOSED VAX ACQUISITION UNDER THE VAX SALE AND PURCHASE AGREEMENT INVOLVING ISSUE OF CONSIDERATION CONVERTIBLE BONDS UNDER SPECIFIC MANDATE",
            source="hkex",
            published_at="2026-04-21T19:22:00+08:00",
            url="https://example.com/hkex-circular-delay-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-egm-transaction-material",
            first_seen_at="2026-04-21T12:00:00+08:00",
            last_seen_at="2026-04-21T12:00:00+08:00",
            canonical_title="I. DISCLOSEABLE TRANSACTION IN RELATION TO PROPOSED ACQUISITION OF THE SALE SHARES OF THE TARGET COMPANY INVOLVING ISSUE OF CONSIDERATION SHARES UNDER SPECIFIC MANDATE; AND II. NOTICE OF EGM",
            summary="I. DISCLOSEABLE TRANSACTION IN RELATION TO PROPOSED ACQUISITION OF THE SALE SHARES OF THE TARGET COMPANY INVOLVING ISSUE OF CONSIDERATION SHARES UNDER SPECIFIC MANDATE; AND II. NOTICE OF EGM",
            source="hkex",
            published_at="2026-04-21T12:00:00+08:00",
            url="https://example.com/hkex-egm-transaction-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-major-transaction-keep",
            first_seen_at="2026-04-21T11:00:00+08:00",
            last_seen_at="2026-04-21T11:00:00+08:00",
            canonical_title="MAJOR TRANSACTION - SALE AND LEASEBACK ARRANGEMENT",
            summary="MAJOR TRANSACTION - SALE AND LEASEBACK ARRANGEMENT",
            source="hkex",
            published_at="2026-04-21T11:00:00+08:00",
            url="https://example.com/hkex-major-transaction-keep",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-hkex-agm-transaction-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-circular-delay-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-egm-transaction-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-major-transaction-keep",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "NOTICE OF THE 2025 AGM AND ADDITIONAL INFORMATION ON THE CONTINUING CONNECTED TRANSACTION" not in content
    assert "FURTHER DELAY IN DESPATCH OF THE MAJOR AND CONNECTED TRANSACTION CIRCULAR" not in content
    assert "I. DISCLOSEABLE TRANSACTION IN RELATION TO PROPOSED ACQUISITION OF THE SALE SHARES OF THE TARGET COMPANY INVOLVING ISSUE OF CONSIDERATION SHARES UNDER SPECIFIC MANDATE; AND II. NOTICE OF EGM" not in content
    assert "MAJOR TRANSACTION - SALE AND LEASEBACK ARRANGEMENT" in content


def test_write_text_report_filters_hkex_transaction_progress_and_director_share_material_without_hiding_pure_transaction(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-hkex-director-share-acquisition-material",
            first_seen_at="2026-04-21T19:47:00+08:00",
            last_seen_at="2026-04-21T19:47:00+08:00",
            canonical_title="VOLUNTARY ANNOUNCEMENT - ACQUISITION OF SHARES IN THE COMPANY BY A DIRECTOR",
            summary="VOLUNTARY ANNOUNCEMENT - ACQUISITION OF SHARES IN THE COMPANY BY A DIRECTOR",
            source="hkex",
            published_at="2026-04-21T19:47:00+08:00",
            url="https://example.com/hkex-director-share-acquisition-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-completion-delay-material",
            first_seen_at="2026-04-21T16:59:00+08:00",
            last_seen_at="2026-04-21T16:59:00+08:00",
            canonical_title="EXTENSION OF PROPOSED COMPLETION DATE IN RELATION TO DISCLOSEABLE TRANSACTION REGARDING ACQUISITION OF PROPERTY",
            summary="EXTENSION OF PROPOSED COMPLETION DATE IN RELATION TO DISCLOSEABLE TRANSACTION REGARDING ACQUISITION OF PROPERTY",
            source="hkex",
            published_at="2026-04-21T16:59:00+08:00",
            url="https://example.com/hkex-completion-delay-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-discloseable-transaction-keep",
            first_seen_at="2026-04-21T17:21:00+08:00",
            last_seen_at="2026-04-21T17:21:00+08:00",
            canonical_title="DISCLOSEABLE TRANSACTION ENTERING INTO A FINANCE LEASE AS THE LESSOR",
            summary="DISCLOSEABLE TRANSACTION ENTERING INTO A FINANCE LEASE AS THE LESSOR",
            source="hkex",
            published_at="2026-04-21T17:21:00+08:00",
            url="https://example.com/hkex-discloseable-transaction-keep",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-hkex-director-share-acquisition-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-completion-delay-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-discloseable-transaction-keep",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "VOLUNTARY ANNOUNCEMENT - ACQUISITION OF SHARES IN THE COMPANY BY A DIRECTOR" not in content
    assert "EXTENSION OF PROPOSED COMPLETION DATE IN RELATION TO DISCLOSEABLE TRANSACTION REGARDING ACQUISITION OF PROPERTY" not in content
    assert "DISCLOSEABLE TRANSACTION ENTERING INTO A FINANCE LEASE AS THE LESSOR" in content


def test_write_text_report_filters_hkex_supplemental_and_annual_caps_material_without_hiding_pure_transaction(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-hkex-supplemental-discloseable-material",
            first_seen_at="2026-04-21T14:00:00+08:00",
            last_seen_at="2026-04-21T14:00:00+08:00",
            canonical_title="SUPPLEMENTAL ANNOUNCEMENT IN RELATION TO DISCLOSEABLE TRANSACTIONS: DISPOSALS OF REAL ESTATE AND ASSETS",
            summary="SUPPLEMENTAL ANNOUNCEMENT IN RELATION TO DISCLOSEABLE TRANSACTIONS: DISPOSALS OF REAL ESTATE AND ASSETS",
            source="hkex",
            published_at="2026-04-21T14:00:00+08:00",
            url="https://example.com/hkex-supplemental-discloseable-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-supplemental-connected-material",
            first_seen_at="2026-04-21T13:00:00+08:00",
            last_seen_at="2026-04-21T13:00:00+08:00",
            canonical_title="SUPPLEMENTAL ANNOUNCEMENT CONTINUING CONNECTED TRANSACTIONS - PROCUREMENT OF NATURAL GAS",
            summary="SUPPLEMENTAL ANNOUNCEMENT CONTINUING CONNECTED TRANSACTIONS - PROCUREMENT OF NATURAL GAS",
            source="hkex",
            published_at="2026-04-21T13:00:00+08:00",
            url="https://example.com/hkex-supplemental-connected-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-annual-caps-material",
            first_seen_at="2026-04-21T12:00:00+08:00",
            last_seen_at="2026-04-21T12:00:00+08:00",
            canonical_title="CONTINUING CONNECTED TRANSACTIONS - 2024 PROPERTY MANAGEMENT AND COMMERCIAL OPERATION AND MANAGEMENT SERVICES FRAMEWORK AGREEMENT REVISION OF ANNUAL CAPS",
            summary="CONTINUING CONNECTED TRANSACTIONS - 2024 PROPERTY MANAGEMENT AND COMMERCIAL OPERATION AND MANAGEMENT SERVICES FRAMEWORK AGREEMENT REVISION OF ANNUAL CAPS",
            source="hkex",
            published_at="2026-04-21T12:00:00+08:00",
            url="https://example.com/hkex-annual-caps-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-major-transaction-keep-2",
            first_seen_at="2026-04-21T11:00:00+08:00",
            last_seen_at="2026-04-21T11:00:00+08:00",
            canonical_title="MAJOR TRANSACTION - SALE AND LEASEBACK ARRANGEMENT",
            summary="MAJOR TRANSACTION - SALE AND LEASEBACK ARRANGEMENT",
            source="hkex",
            published_at="2026-04-21T11:00:00+08:00",
            url="https://example.com/hkex-major-transaction-keep-2",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-hkex-supplemental-discloseable-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-supplemental-connected-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-annual-caps-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-major-transaction-keep-2",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "SUPPLEMENTAL ANNOUNCEMENT IN RELATION TO DISCLOSEABLE TRANSACTIONS: DISPOSALS OF REAL ESTATE AND ASSETS" not in content
    assert "SUPPLEMENTAL ANNOUNCEMENT CONTINUING CONNECTED TRANSACTIONS - PROCUREMENT OF NATURAL GAS" not in content
    assert "CONTINUING CONNECTED TRANSACTIONS - 2024 PROPERTY MANAGEMENT AND COMMERCIAL OPERATION AND MANAGEMENT SERVICES FRAMEWORK AGREEMENT REVISION OF ANNUAL CAPS" not in content
    assert "MAJOR TRANSACTION - SALE AND LEASEBACK ARRANGEMENT" in content


def test_write_text_report_filters_hkex_framework_and_maintenance_connected_transaction_material_without_hiding_pure_transaction(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-hkex-maintenance-contract-material",
            first_seen_at="2026-04-21T16:55:00+08:00",
            last_seen_at="2026-04-21T16:55:00+08:00",
            canonical_title="ANNOUNCEMENT - CONTINUING CONNECTED TRANSACTIONS: MAINTENANCE WORK CONTRACTS",
            summary="ANNOUNCEMENT - CONTINUING CONNECTED TRANSACTIONS: MAINTENANCE WORK CONTRACTS",
            source="hkex",
            published_at="2026-04-21T16:55:00+08:00",
            url="https://example.com/hkex-maintenance-contract-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-service-framework-material",
            first_seen_at="2026-04-20T21:32:00+08:00",
            last_seen_at="2026-04-20T21:32:00+08:00",
            canonical_title="CONTINUING CONNECTED TRANSACTIONS 2026 SERVICE FRAMEWORK AGREEMENT",
            summary="CONTINUING CONNECTED TRANSACTIONS 2026 SERVICE FRAMEWORK AGREEMENT",
            source="hkex",
            published_at="2026-04-20T21:32:00+08:00",
            url="https://example.com/hkex-service-framework-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-leasing-framework-material",
            first_seen_at="2026-04-21T19:24:00+08:00",
            last_seen_at="2026-04-21T19:24:00+08:00",
            canonical_title="MAJOR TRANSACTION, DISCLOSEABLE TRANSACTIONS AND CONTINUING CONNECTED TRANSACTIONS IN RELATION TO NEW LEASING AND LICENSING FRAMEWORK AGREEMENT AND OTHER CONTINUING CONNECTED TRANSACTIONS",
            summary="MAJOR TRANSACTION, DISCLOSEABLE TRANSACTIONS AND CONTINUING CONNECTED TRANSACTIONS IN RELATION TO NEW LEASING AND LICENSING FRAMEWORK AGREEMENT AND OTHER CONTINUING CONNECTED TRANSACTIONS",
            source="hkex",
            published_at="2026-04-21T19:24:00+08:00",
            url="https://example.com/hkex-leasing-framework-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-discloseable-transaction-keep-2",
            first_seen_at="2026-04-21T17:21:00+08:00",
            last_seen_at="2026-04-21T17:21:00+08:00",
            canonical_title="DISCLOSEABLE TRANSACTION ENTERING INTO A FINANCE LEASE AS THE LESSOR",
            summary="DISCLOSEABLE TRANSACTION ENTERING INTO A FINANCE LEASE AS THE LESSOR",
            source="hkex",
            published_at="2026-04-21T17:21:00+08:00",
            url="https://example.com/hkex-discloseable-transaction-keep-2",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-hkex-maintenance-contract-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-service-framework-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-leasing-framework-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-discloseable-transaction-keep-2",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "ANNOUNCEMENT - CONTINUING CONNECTED TRANSACTIONS: MAINTENANCE WORK CONTRACTS" not in content
    assert "CONTINUING CONNECTED TRANSACTIONS 2026 SERVICE FRAMEWORK AGREEMENT" not in content
    assert "MAJOR TRANSACTION, DISCLOSEABLE TRANSACTIONS AND CONTINUING CONNECTED TRANSACTIONS IN RELATION TO NEW LEASING AND LICENSING FRAMEWORK AGREEMENT AND OTHER CONTINUING CONNECTED TRANSACTIONS" not in content
    assert "DISCLOSEABLE TRANSACTION ENTERING INTO A FINANCE LEASE AS THE LESSOR" in content


def test_write_text_report_filters_hkex_lng_framework_connected_transaction_without_hiding_other_connected_transaction(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-hkex-lng-framework-material",
            first_seen_at="2026-04-20T21:20:00+08:00",
            last_seen_at="2026-04-20T21:20:00+08:00",
            canonical_title="CONTINUING CONNECTED TRANSACTIONS IN RELATION TO (1) THE LNG PURCHASE AGREEMENTS AND (2) THE LNG SALES AGREEMENTS",
            summary="CONTINUING CONNECTED TRANSACTIONS IN RELATION TO (1) THE LNG PURCHASE AGREEMENTS AND (2) THE LNG SALES AGREEMENTS",
            source="hkex",
            published_at="2026-04-20T21:20:00+08:00",
            url="https://example.com/hkex-lng-framework-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-connected-fund-keep",
            first_seen_at="2026-04-20T20:39:00+08:00",
            last_seen_at="2026-04-20T20:39:00+08:00",
            canonical_title="CONNECTED TRANSACTION ESTABLISHMENT OF THE FUND",
            summary="CONNECTED TRANSACTION ESTABLISHMENT OF THE FUND",
            source="hkex",
            published_at="2026-04-20T20:39:00+08:00",
            url="https://example.com/hkex-connected-fund-keep",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-discloseable-transaction-keep-3",
            first_seen_at="2026-04-21T17:21:00+08:00",
            last_seen_at="2026-04-21T17:21:00+08:00",
            canonical_title="DISCLOSEABLE TRANSACTION ENTERING INTO A FINANCE LEASE AS THE LESSOR",
            summary="DISCLOSEABLE TRANSACTION ENTERING INTO A FINANCE LEASE AS THE LESSOR",
            source="hkex",
            published_at="2026-04-21T17:21:00+08:00",
            url="https://example.com/hkex-discloseable-transaction-keep-3",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-hkex-lng-framework-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-connected-fund-keep",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-discloseable-transaction-keep-3",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "CONTINUING CONNECTED TRANSACTIONS IN RELATION TO (1) THE LNG PURCHASE AGREEMENTS AND (2) THE LNG SALES AGREEMENTS" not in content
    assert "CONNECTED TRANSACTION ESTABLISHMENT OF THE FUND" in content
    assert "DISCLOSEABLE TRANSACTION ENTERING INTO A FINANCE LEASE AS THE LESSOR" in content


def test_write_text_report_filters_hkex_results_and_suspension_material_without_hiding_profit_warning(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-hkex-management-accounts-suspension-material",
            first_seen_at="2026-04-22T08:11:00+08:00",
            last_seen_at="2026-04-22T08:11:00+08:00",
            canonical_title="(1) PUBLICATION OF UNAUDITED MANAGEMENT ACCOUNTS FOR THE THREE MONTHS ENDED 31 MARCH 2026 AND (2) CONTINUED SUSPENSION OF TRADING",
            summary="(1) PUBLICATION OF UNAUDITED MANAGEMENT ACCOUNTS FOR THE THREE MONTHS ENDED 31 MARCH 2026 AND (2) CONTINUED SUSPENSION OF TRADING",
            source="hkex",
            published_at="2026-04-22T08:11:00+08:00",
            url="https://example.com/hkex-management-accounts-suspension-material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-annual-results-suspension-material",
            first_seen_at="2026-04-21T22:46:00+08:00",
            last_seen_at="2026-04-21T22:46:00+08:00",
            canonical_title="ANNUAL RESULTS ANNOUNCEMENT FOR THE YEAR ENDED 31 DECEMBER 2025 AND CONTINUED SUSPENSION OF TRADING",
            summary="ANNUAL RESULTS ANNOUNCEMENT FOR THE YEAR ENDED 31 DECEMBER 2025 AND CONTINUED SUSPENSION OF TRADING",
            source="hkex",
            published_at="2026-04-21T22:46:00+08:00",
            url="https://example.com/hkex-annual-results-suspension-material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-interim-results-suspension-material",
            first_seen_at="2026-04-21T22:39:00+08:00",
            last_seen_at="2026-04-21T22:39:00+08:00",
            canonical_title="INTERIM RESULTS ANNOUNCEMENT FOR THE SIX MONTHS ENDED 30 JUNE 2025 AND CONTINUED SUSPENSION OF TRADING",
            summary="INTERIM RESULTS ANNOUNCEMENT FOR THE SIX MONTHS ENDED 30 JUNE 2025 AND CONTINUED SUSPENSION OF TRADING",
            source="hkex",
            published_at="2026-04-21T22:39:00+08:00",
            url="https://example.com/hkex-interim-results-suspension-material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hkex-profit-warning-keep-2",
            first_seen_at="2026-04-21T22:01:00+08:00",
            last_seen_at="2026-04-21T22:01:00+08:00",
            canonical_title="PROFIT WARNING",
            summary="PROFIT WARNING",
            source="hkex",
            published_at="2026-04-21T22:01:00+08:00",
            url="https://example.com/hkex-profit-warning-keep-2",
            event_type="hard_event",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-hkex-management-accounts-suspension-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-annual-results-suspension-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-interim-results-suspension-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-profit-warning-keep-2",
            direction="bearish",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "(1) PUBLICATION OF UNAUDITED MANAGEMENT ACCOUNTS FOR THE THREE MONTHS ENDED 31 MARCH 2026 AND (2) CONTINUED SUSPENSION OF TRADING" not in content
    assert "ANNUAL RESULTS ANNOUNCEMENT FOR THE YEAR ENDED 31 DECEMBER 2025 AND CONTINUED SUSPENSION OF TRADING" not in content
    assert "INTERIM RESULTS ANNOUNCEMENT FOR THE SIX MONTHS ENDED 30 JUNE 2025 AND CONTINUED SUSPENSION OF TRADING" not in content
    assert "PROFIT WARNING" in content


def test_write_text_report_filters_hkex_voluntary_asset_acquisition_material_without_hiding_connected_transaction(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-hkex-voluntary-asset-acquisition-material",
            first_seen_at="2026-04-21T22:58:00+08:00",
            last_seen_at="2026-04-21T22:58:00+08:00",
            canonical_title="VOLUNTARY ANNOUNCEMENT ACQUISITION OF ASSETS",
            summary="VOLUNTARY ANNOUNCEMENT ACQUISITION OF ASSETS",
            source="hkex",
            published_at="2026-04-21T22:58:00+08:00",
            url="https://example.com/hkex-voluntary-asset-acquisition-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-connected-transaction-keep-2",
            first_seen_at="2026-04-22T08:00:00+08:00",
            last_seen_at="2026-04-22T08:00:00+08:00",
            canonical_title="CONNECTED TRANSACTION - ACQUISITION OF SOFTWARE ASSETS",
            summary="CONNECTED TRANSACTION - ACQUISITION OF SOFTWARE ASSETS",
            source="hkex",
            published_at="2026-04-22T08:00:00+08:00",
            url="https://example.com/hkex-connected-transaction-keep-2",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-hkex-voluntary-asset-acquisition-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-connected-transaction-keep-2",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "VOLUNTARY ANNOUNCEMENT ACQUISITION OF ASSETS" not in content
    assert "CONNECTED TRANSACTION - ACQUISITION OF SOFTWARE ASSETS" in content


def test_write_text_report_filters_hkex_lease_agreement_material_without_hiding_connected_asset_acquisition(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-hkex-lease-agreement-material",
            first_seen_at="2026-04-21T21:30:00+08:00",
            last_seen_at="2026-04-21T21:30:00+08:00",
            canonical_title="CONNECTED TRANSACTION AND CONTINUING CONNECTED TRANSACTION IN RELATION TO THE LEASE AGREEMENT",
            summary="CONNECTED TRANSACTION AND CONTINUING CONNECTED TRANSACTION IN RELATION TO THE LEASE AGREEMENT",
            source="hkex",
            published_at="2026-04-21T21:30:00+08:00",
            url="https://example.com/hkex-lease-agreement-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-hkex-connected-asset-acquisition-keep",
            first_seen_at="2026-04-22T08:00:00+08:00",
            last_seen_at="2026-04-22T08:00:00+08:00",
            canonical_title="CONNECTED TRANSACTION - ACQUISITION OF SOFTWARE ASSETS",
            summary="CONNECTED TRANSACTION - ACQUISITION OF SOFTWARE ASSETS",
            source="hkex",
            published_at="2026-04-22T08:00:00+08:00",
            url="https://example.com/hkex-connected-asset-acquisition-keep",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-hkex-lease-agreement-material",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-hkex-connected-asset-acquisition-keep",
            direction="neutral",
            impact_score=77.9,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "CONNECTED TRANSACTION AND CONTINUING CONNECTED TRANSACTION IN RELATION TO THE LEASE AGREEMENT" not in content
    assert "CONNECTED TRANSACTION - ACQUISITION OF SOFTWARE ASSETS" in content


def test_write_text_report_filters_exchange_low_signal_project_sales_and_mou_announcements(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-related-party-fund-material",
            first_seen_at="2026-04-18T00:00:00+08:00",
            last_seen_at="2026-04-18T00:00:00+08:00",
            canonical_title="保利发展控股集团股份有限公司关于与关联合伙企业及相关主体开展关联交易的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-18T00:00:00+08:00",
            url="https://example.com/sse-related-party-fund-material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-financial-support-material",
            first_seen_at="2026-04-18T00:00:00+08:00",
            last_seen_at="2026-04-18T00:00:00+08:00",
            canonical_title="保利发展控股集团股份有限公司关于2026年度对外提供财务资助的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-18T00:00:00+08:00",
            url="https://example.com/sse-financial-support-material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-property-offset-material",
            first_seen_at="2026-04-18T00:00:00+08:00",
            last_seen_at="2026-04-18T00:00:00+08:00",
            canonical_title="ST中迪：中迪投资关于公司子公司达州绵石房地产开发有限公司以房抵款事项的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-18T00:00:00+08:00",
            url="https://example.com/szse-property-offset-material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-real-estate-project",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="保利发展控股集团股份有限公司关于本公司获得房地产项目的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/sse-real-estate-project",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-sales-briefing",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="保利发展控股集团股份有限公司2026年3月份销售情况简报",
            summary="summary",
            source="sse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/sse-sales-briefing",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-buyback-loan",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="中国东方航空股份有限公司关于取得金融机构股票回购贷款承诺函的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/sse-buyback-loan",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-mou",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="建发股份关于控股子公司签署《谅解备忘录》暨关联交易的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/sse-mou",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-convertible-bond-interest-notice",
            first_seen_at="2026-05-08T00:00:00+08:00",
            last_seen_at="2026-05-08T00:00:00+08:00",
            canonical_title="保利发展控股集团股份有限公司关于“保利定转”2026年付息公告",
            summary="summary",
            source="sse",
            published_at="2026-05-08T00:00:00+08:00",
            url="https://example.com/sse-convertible-bond-interest-notice",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-keep-low-signal-exchange",
            first_seen_at="2026-04-18T00:01:00+08:00",
            last_seen_at="2026-04-18T00:01:00+08:00",
            canonical_title="国产EDA工具链和先进封装产线建设提速",
            summary="summary",
            source="stcn",
            published_at="2026-04-18T00:01:00+08:00",
            url="https://example.com/stcn-keep-low-signal-exchange",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-sse-related-party-fund-material",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["房地产"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-sse-financial-support-material",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["房地产"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-property-offset-material",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["房地产"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-sse-real-estate-project",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["房地产"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-sse-sales-briefing",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["房地产"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-sse-buyback-loan",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-sse-mou",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-sse-convertible-bond-interest-notice",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["房地产"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-low-signal-exchange",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "国产EDA工具链和先进封装产线建设提速" in content
    assert "保利发展控股集团股份有限公司关于与关联合伙企业及相关主体开展关联交易的公告" not in content
    assert "保利发展控股集团股份有限公司关于2026年度对外提供财务资助的公告" not in content
    assert "ST中迪：中迪投资关于公司子公司达州绵石房地产开发有限公司以房抵款事项的公告" not in content
    assert "保利发展控股集团股份有限公司关于本公司获得房地产项目的公告" not in content
    assert "保利发展控股集团股份有限公司2026年3月份销售情况简报" not in content
    assert "保利发展控股集团股份有限公司关于“保利定转”2026年付息公告" not in content
    assert "中国东方航空股份有限公司关于取得金融机构股票回购贷款承诺函的公告" not in content
    assert "建发股份关于控股子公司签署《谅解备忘录》暨关联交易的公告" not in content


def test_write_text_report_filters_exchange_investment_property_accounting_policy_change_without_hiding_semiconductor_buildout(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-investment-property-accounting-policy-change",
            first_seen_at="2026-04-20T00:00:00+08:00",
            last_seen_at="2026-04-20T00:00:00+08:00",
            canonical_title="江钨装备关于投资性房地产会计政策变更的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-20T00:00:00+08:00",
            url="https://example.com/sse-investment-property-accounting-policy-change",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-keep-semiconductor-buildout",
            first_seen_at="2026-04-18T00:01:00+08:00",
            last_seen_at="2026-04-18T00:01:00+08:00",
            canonical_title="国产EDA工具链和先进封装产线建设提速",
            summary="summary",
            source="stcn",
            published_at="2026-04-18T00:01:00+08:00",
            url="https://example.com/stcn-keep-semiconductor-buildout",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-sse-investment-property-accounting-policy-change",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["房地产"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-semiconductor-buildout",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "江钨装备关于投资性房地产会计政策变更的公告" not in content
    assert "国产EDA工具链和先进封装产线建设提速" in content


def test_write_text_report_filters_cls_share_disposal_financial_gain_story_without_hiding_control_change_progress(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-share-disposal-financial-gain",
            first_seen_at="2026-04-20T20:00:53+08:00",
            last_seen_at="2026-04-20T20:00:53+08:00",
            canonical_title="翔港科技：拟2.76亿元出售参股公司金泰克13.19%股权",
            summary="财联社4月20日电，翔港科技公告称，公司拟将持有的深圳市金泰克半导体有限公司13.1944%股权转让给南宁市和鸣启半导体合伙企业。本次交易完成后，公司将不再持有金泰克股权。预计本次交易将产生收益约2598.66万元，对公司2026年财务报表产生积极影响。",
            source="cls",
            published_at="2026-04-20T20:00:53+08:00",
            url="https://example.com/cls-share-disposal-financial-gain",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-keep-control-change-progress",
            first_seen_at="2026-04-20T20:01:00+08:00",
            last_seen_at="2026-04-20T20:01:00+08:00",
            canonical_title="盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告",
            summary="summary",
            source="szse",
            published_at="2026-04-20T20:01:00+08:00",
            url="https://example.com/keep-control-change-progress",
            event_type="hard_event",
            event_subtype="control_change",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cls-share-disposal-financial-gain",
            direction="neutral",
            impact_score=99.3,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-control-change-progress",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "翔港科技：拟2.76亿元出售参股公司金泰克13.19%股权" not in content
    assert "盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告" in content


def test_write_text_report_filters_exchange_buyback_result_purpose_and_plan_materials(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-buyback-result",
            first_seen_at="2026-04-12T00:00:00+08:00",
            last_seen_at="2026-04-12T00:00:00+08:00",
            canonical_title="神马股份关于股份回购实施结果暨股份变动的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-12T00:00:00+08:00",
            url="https://example.com/sse-buyback-result",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-buyback-purpose-cancellation",
            first_seen_at="2026-04-12T00:00:00+08:00",
            last_seen_at="2026-04-12T00:00:00+08:00",
            canonical_title="圣农发展：关于变更回购股份的用途并注销公司部分股份的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-12T00:00:00+08:00",
            url="https://example.com/szse-buyback-purpose-cancellation",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-buyback-plan-keep",
            first_seen_at="2026-04-12T00:00:00+08:00",
            last_seen_at="2026-04-12T00:00:00+08:00",
            canonical_title="贵州茅台关于以集中竞价交易方式回购股份方案的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-12T00:00:00+08:00",
            url="https://example.com/sse-buyback-plan-keep",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-sse-buyback-result",
            direction="neutral",
            impact_score=96.0,
            reasoning="rule",
            themes=["化工"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-buyback-purpose-cancellation",
            direction="neutral",
            impact_score=95.0,
            reasoning="rule",
            themes=["白羽鸡"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-sse-buyback-plan-keep",
            direction="neutral",
            impact_score=94.0,
            reasoning="rule",
            themes=["白酒"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "贵州茅台关于以集中竞价交易方式回购股份方案的公告" not in content
    assert "神马股份关于股份回购实施结果暨股份变动的公告" not in content
    assert "圣农发展：关于变更回购股份的用途并注销公司部分股份的公告" not in content


def test_write_text_report_filters_exchange_rulebook_and_ipo_risk_notice_without_hiding_real_license_deal(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-ir-platform-rulebook",
            first_seen_at="2026-04-13T00:00:00+08:00",
            last_seen_at="2026-04-13T00:00:00+08:00",
            canonical_title="龙利得：互动易平台信息发布及回复内部审核制度（2026年4月）",
            summary="summary",
            source="szse",
            published_at="2026-04-13T00:00:00+08:00",
            url="https://example.com/szse-ir-platform-rulebook",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-cninfo-ipo-risk-notice",
            first_seen_at="2026-04-13T00:00:00+08:00",
            last_seen_at="2026-04-13T00:00:00+08:00",
            canonical_title="联讯仪器首次公开发行股票并在科创板上市投资风险特别公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-13T00:00:00+08:00",
            url="https://example.com/cninfo-ipo-risk-notice",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-license-deal-keep",
            first_seen_at="2026-04-13T00:00:00+08:00",
            last_seen_at="2026-04-13T00:00:00+08:00",
            canonical_title="海思科：关于与AbbVie签署Nav1.8抑制剂授权许可协议的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-13T00:00:00+08:00",
            url="https://example.com/szse-license-deal-keep",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-ir-platform-rulebook",
            direction="bullish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cninfo-ipo-risk-notice",
            direction="bearish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-license-deal-keep",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "海思科：关于与AbbVie签署Nav1.8抑制剂授权许可协议的公告" in content
    assert "龙利得：互动易平台信息发布及回复内部审核制度（2026年4月）" not in content
    assert "联讯仪器首次公开发行股票并在科创板上市投资风险特别公告" not in content


def test_write_text_report_filters_exchange_share_purchase_agreement_material_without_result_words(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-share-purchase-material",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="若羽臣：关于全资孙公司收购股权暨签署股份购买协议的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-share-purchase-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-stcn-keep-share-purchase",
            first_seen_at="2026-04-09T20:03:48+08:00",
            last_seen_at="2026-04-09T20:03:48+08:00",
            canonical_title="睿能科技：拟收购博泰智能75%股权 股票明起复牌",
            summary="summary",
            source="stcn",
            published_at="2026-04-09T20:03:48+08:00",
            url="https://example.com/stcn-keep-share-purchase",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-share-purchase-material",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-share-purchase",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["锂电池"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "睿能科技：拟收购博泰智能75%股权 股票明起复牌" in content
    assert "若羽臣：关于全资孙公司收购股权暨签署股份购买协议的公告" not in content


def test_write_text_report_filters_exchange_shareholder_agreement_supplement_material_without_hiding_control_change_progress(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-shareholder-agreement-supplement-material",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="东睦股份关于签署《关于上海富驰高科技股份有限公司之股东协议的补充协议（三）》的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/sse-shareholder-agreement-supplement-material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-control-change-progress",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告",
            summary="公司推进控制权收购事项。",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/keep-control-change-progress",
            event_type="hard_event",
            event_subtype="control_change",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-sse-shareholder-agreement-supplement-material",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-control-change-progress",
            direction="bullish",
            impact_score=100.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "东睦股份关于签署《关于上海富驰高科技股份有限公司之股东协议的补充协议（三）》的公告" not in content
    assert "盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告" in content


def test_write_text_report_filters_exchange_litigation_and_dishonest_person_notices_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-litigation-progress",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="合力泰：关于诉讼事项的进展暨公司部分银行账户及子公司股权解除冻结的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-litigation-progress",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-dishonest-person",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="麦趣尔：关于公司被纳入失信被执行人的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-dishonest-person",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-cumulative-litigation",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="幸福蓝海：关于累计诉讼、仲裁案件情况的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-cumulative-litigation",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-guarantee-litigation-unfreeze",
            first_seen_at="2026-04-24T00:00:00+08:00",
            last_seen_at="2026-04-24T00:00:00+08:00",
            canonical_title="*ST美谷：关于担保事项涉及诉讼进展暨银行账户解除冻结的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-24T00:00:00+08:00",
            url="https://example.com/szse-guarantee-litigation-unfreeze",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-forced-execution-complete",
            first_seen_at="2026-04-24T00:00:00+08:00",
            last_seen_at="2026-04-24T00:00:00+08:00",
            canonical_title="龙大美食：关于控股股东所持公司1000万股股份被强制执行完成暨解除冻结的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-24T00:00:00+08:00",
            url="https://example.com/szse-forced-execution-complete",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-asset-sale-inquiry-reply",
            first_seen_at="2026-04-24T00:00:00+08:00",
            last_seen_at="2026-04-24T00:00:00+08:00",
            canonical_title="泰达股份：天津泰达资源循环集团股份有限公司关于重大资产出售暨关联交易问询函回复的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-24T00:00:00+08:00",
            url="https://example.com/szse-asset-sale-inquiry-reply",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-keep-litigation-filter",
            first_seen_at="2026-04-10T20:01:00+08:00",
            last_seen_at="2026-04-10T20:01:00+08:00",
            canonical_title="两单公募REITs获批",
            summary="summary",
            source="stcn",
            published_at="2026-04-10T20:01:00+08:00",
            url="https://example.com/stcn-keep-litigation-filter",
            event_type="fast_news",
            event_subtype="regulatory_approval",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-litigation-progress",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-dishonest-person",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-cumulative-litigation",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-guarantee-litigation-unfreeze",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-forced-execution-complete",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-asset-sale-inquiry-reply",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-litigation-filter",
            direction="bullish",
            impact_score=97.0,
            reasoning="rule",
            themes=["REITs"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "两单公募REITs获批" in content
    assert "合力泰：关于诉讼事项的进展暨公司部分银行账户及子公司股权解除冻结的公告" not in content
    assert "麦趣尔：关于公司被纳入失信被执行人的公告" not in content
    assert "幸福蓝海：关于累计诉讼、仲裁案件情况的公告" not in content
    assert "*ST美谷：关于担保事项涉及诉讼进展暨银行账户解除冻结的公告" not in content
    assert "龙大美食：关于控股股东所持公司1000万股股份被强制执行完成暨解除冻结的公告" not in content
    assert "泰达股份：天津泰达资源循环集团股份有限公司关于重大资产出售暨关联交易问询函回复的公告" not in content


def test_write_text_report_filters_exchange_major_litigation_and_filing_progress_notices_without_theme(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-litigation-filing-progress",
            first_seen_at="2026-04-13T00:00:00+08:00",
            last_seen_at="2026-04-13T00:00:00+08:00",
            canonical_title="关于控股子公司提起诉讼的进展公告",
            summary="summary",
            source="sse",
            published_at="2026-04-13T00:00:00+08:00",
            url="https://example.com/sse-litigation-filing-progress",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-major-litigation",
            first_seen_at="2026-04-13T00:00:00+08:00",
            last_seen_at="2026-04-13T00:00:00+08:00",
            canonical_title="长药退：重大诉讼公告",
            summary="summary",
            source="szse",
            published_at="2026-04-13T00:00:00+08:00",
            url="https://example.com/szse-major-litigation",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-keep-major-litigation",
            first_seen_at="2026-04-12T19:14:50+08:00",
            last_seen_at="2026-04-12T19:14:50+08:00",
            canonical_title="迅策：与深圳数据交易所签署战略合作协议",
            summary="summary",
            source="stcn",
            published_at="2026-04-12T19:14:50+08:00",
            url="https://example.com/stcn-keep-major-litigation",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-sse-litigation-filing-progress",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-major-litigation",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-major-litigation",
            direction="neutral",
            impact_score=99.0,
            reasoning="rule",
            themes=["机器人"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "迅策：与深圳数据交易所签署战略合作协议" in content
    assert "关于控股子公司提起诉讼的进展公告" not in content
    assert "长药退：重大诉讼公告" not in content


def test_write_text_report_filters_exchange_share_freeze_waiting_notice_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-share-freeze-waiting",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="关于持股5%以上股东及其一致行动人股份被轮候冻结的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-share-freeze-waiting",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-keep-freeze-filter",
            first_seen_at="2026-04-10T20:01:00+08:00",
            last_seen_at="2026-04-10T20:01:00+08:00",
            canonical_title="中国能建与华北电力大学签署战略合作协议",
            summary="双方将围绕构建新型能源体系和新型电力系统深化合作。",
            source="stcn",
            published_at="2026-04-10T20:01:00+08:00",
            url="https://example.com/stcn-keep-freeze-filter",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-share-freeze-waiting",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-freeze-filter",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["电力资源"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中国能建与华北电力大学签署战略合作协议" in content
    assert "关于持股5%以上股东及其一致行动人股份被轮候冻结的公告" not in content


def test_write_text_report_filters_exchange_reduction_predisclosure_and_risk_control_opinion_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-reduction-predisclosure",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="天禾股份：关于公司高级管理人员减持股份预披露公告（刘勇峰）",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-reduction-predisclosure",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-cninfo-risk-control-opinion",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="中银证券关于宏盛华源金融服务协议及相关风险控制措施执行情况的核查意见",
            summary="summary",
            source="cninfo",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/cninfo-risk-control-opinion",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-keep-reduction-filter",
            first_seen_at="2026-04-10T20:01:00+08:00",
            last_seen_at="2026-04-10T20:01:00+08:00",
            canonical_title="中国能建与华北电力大学签署战略合作协议",
            summary="双方将围绕构建新型能源体系和新型电力系统深化合作。",
            source="stcn",
            published_at="2026-04-10T20:01:00+08:00",
            url="https://example.com/stcn-keep-reduction-filter",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-reduction-predisclosure",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cninfo-risk-control-opinion",
            direction="bearish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-reduction-filter",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["电力资源"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中国能建与华北电力大学签署战略合作协议" in content
    assert "天禾股份：关于公司高级管理人员减持股份预披露公告（刘勇峰）" not in content
    assert "中银证券关于宏盛华源金融服务协议及相关风险控制措施执行情况的核查意见" not in content


def test_write_text_report_filters_exchange_risk_management_materials_without_hiding_substantive_disclosure(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-aml-risk-management",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="国元证券：国元证券股份有限公司防控洗钱和恐怖融资风险管理办法",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-aml-risk-management",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-risk-control-indicator-report",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="长城证券：2025年度风险控制指标报告",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-risk-control-indicator-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-keep-substantive-disclosure",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="华测导航：关于开展供应链融资业务合作暨对外担保的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-keep-substantive-disclosure",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-szse-aml-risk-management", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-risk-control-indicator-report", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-keep-substantive-disclosure", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "国元证券：国元证券股份有限公司防控洗钱和恐怖融资风险管理办法" not in content
    assert "长城证券：2025年度风险控制指标报告" not in content
    assert "华测导航：关于开展供应链融资业务合作暨对外担保的公告" in content


def test_write_text_report_filters_current_live_equity_incentive_and_land_use_materials_without_hiding_substantive_items(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-equity-opinion-current-2",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="英维克：薪酬和考核委员会关于 2024年股票期权激励计划有关事项的核查意见",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-equity-opinion-current-2",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-equity-exercise-condition-current-2",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="英维克：关于2024年股票期权激励计划第二个行权期行权条件达成的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-equity-exercise-condition-current-2",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-land-use-contract-current",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="合肥城建：关于全资子公司签订国有建设用地使用权出让合同的公告（一）",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-land-use-contract-current",
            event_type="hard_event",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-keep-substantive-order-contract-current",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="杭可科技：拟1.79亿元增资杭可仪器获51%股权",
            summary="summary",
            source="cls",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/keep-substantive-order-contract-current",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-szse-equity-opinion-current-2", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-equity-exercise-condition-current-2", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-land-use-contract-current", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-substantive-order-contract-current", direction="neutral", impact_score=99.3, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "英维克：薪酬和考核委员会关于 2024年股票期权激励计划有关事项的核查意见" not in content
    assert "英维克：关于2024年股票期权激励计划第二个行权期行权条件达成的公告" not in content
    assert "合肥城建：关于全资子公司签订国有建设用地使用权出让合同的公告（一）" not in content
    assert "杭可科技：拟1.79亿元增资杭可仪器获51%股权" in content


def test_write_text_report_filters_current_live_buyback_and_equity_incentive_materials_without_hiding_substantive_items(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-buyback-plan-current",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="纳尔股份：关于回购公司股份方案的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-buyback-plan-current",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-reserved-grant-current",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="纳尔股份：关于向2025年限制性股票激励计划激励对象授予预留限制性股票的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-reserved-grant-current",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-adjust-unvested-current",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="美好医疗：关于调整已授予尚未归属限制性股票数量的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-adjust-unvested-current",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-void-restricted-stock-current",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="光大同创：关于作废部分限制性股票的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-void-restricted-stock-current",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-unlock-listing-current",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="京基智农：关于2023年限制性股票激励计划第二个解除限售期解除限售股份上市流通的提示性公告",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-unlock-listing-current",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-keep-substantive-item-current-2",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="杭可科技：拟1.79亿元增资杭可仪器获51%股权",
            summary="summary",
            source="cls",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/keep-substantive-item-current-2",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-szse-buyback-plan-current", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-reserved-grant-current", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-adjust-unvested-current", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-void-restricted-stock-current", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-unlock-listing-current", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-substantive-item-current-2", direction="neutral", impact_score=99.3, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "纳尔股份：关于回购公司股份方案的公告" not in content
    assert "纳尔股份：关于向2025年限制性股票激励计划激励对象授予预留限制性股票的公告" not in content
    assert "美好医疗：关于调整已授予尚未归属限制性股票数量的公告" not in content
    assert "光大同创：关于作废部分限制性股票的公告" not in content
    assert "京基智农：关于2023年限制性股票激励计划第二个解除限售期解除限售股份上市流通的提示性公告" not in content
    assert "杭可科技：拟1.79亿元增资杭可仪器获51%股权" in content


def test_write_text_report_filters_exchange_template_cooperation_agreement_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-template-cooperation",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="江特电机：关于签订合作协议书的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-template-cooperation",
            event_type="hard_event",
            event_subtype="cooperation_agreement",
        ),
        Event(
            event_id="event-szse-framework-cooperation",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="江特电机：关于签订战略合作框架协议的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/szse-framework-cooperation",
            event_type="hard_event",
            event_subtype="cooperation_agreement",
        ),
        Event(
            event_id="event-stcn-keep-template-cooperation",
            first_seen_at="2026-04-14T00:01:00+08:00",
            last_seen_at="2026-04-14T00:01:00+08:00",
            canonical_title="中国能建与华北电力大学签署战略合作协议",
            summary="双方将围绕构建新型能源体系和新型电力系统深化合作。",
            source="stcn",
            published_at="2026-04-14T00:01:00+08:00",
            url="https://example.com/stcn-keep-template-cooperation",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-template-cooperation",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-framework-cooperation",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-keep-template-cooperation",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["电力资源"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中国能建与华北电力大学签署战略合作协议" in content
    assert "江特电机：关于签订合作协议书的公告" not in content
    assert "江特电机：关于签订战略合作框架协议的公告" not in content


def test_write_text_report_filters_sse_template_disclosures_without_hiding_policy_signal(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-lockup-listing",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="道生天合关于首次公开发行网下发行限售股上市流通的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-lockup-listing",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-board-meeting-date",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="董事會會議召開日期",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-board-meeting-date",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-profit-distribution-plan",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="福建省燕京惠泉啤酒股份有限公司2025年度利润分配方案公告",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-profit-distribution-plan",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-charter-amendment",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="浙江德宏汽车电子电器股份有限公司章程(2026年4月修订)",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-charter-amendment",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-internal-control-audit",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="浙江德宏汽车电子电器股份有限公司内部控制审计报告",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-internal-control-audit",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-shareholder-meeting-materials",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="新疆众和股份有限公司2025年年度股东会会议资料",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-shareholder-meeting-materials",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-credit-line",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="宁波富邦关于公司及子公司2026年度向银行申请综合授信额度的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-credit-line",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-entrusted-wealth",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="宁波富邦关于公司使用临时闲置资金进行委托理财的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-entrusted-wealth",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-related-party-estimate",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="宁波富邦关于2026日常关联交易预计的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-related-party-estimate",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-prospectus",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="埃泰克首次公开发行股票并在主板上市招股说明书",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-prospectus",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-special-audit-note",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="关于浙江德宏汽车电子电器股份有限公司非经营性资金占用及其他关联资金往来情况的专项审核说明",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-special-audit-note",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-policy-keep-new-material",
            first_seen_at="2026-04-14T00:01:00+08:00",
            last_seen_at="2026-04-14T00:01:00+08:00",
            canonical_title="工业和信息化部召开新材料领域中小企业圆桌会",
            summary="会议聚焦先进基础材料、关键战略材料等方向。",
            source="miit",
            published_at="2026-04-14T00:01:00+08:00",
            url="https://example.com/policy-keep-new-material",
            event_type="policy",
            event_subtype="policy_support",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-sse-lockup-listing", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-board-meeting-date", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-profit-distribution-plan", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-charter-amendment", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-internal-control-audit", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-shareholder-meeting-materials", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-credit-line", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-entrusted-wealth", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-related-party-estimate", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-prospectus", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-special-audit-note", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-policy-keep-new-material", direction="bullish", impact_score=97.0, reasoning="rule", themes=["新材料"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "工业和信息化部召开新材料领域中小企业圆桌会" in content
    assert "道生天合关于首次公开发行网下发行限售股上市流通的公告" not in content
    assert "董事會會議召開日期" not in content
    assert "福建省燕京惠泉啤酒股份有限公司2025年度利润分配方案公告" not in content
    assert "浙江德宏汽车电子电器股份有限公司章程(2026年4月修订)" not in content
    assert "浙江德宏汽车电子电器股份有限公司内部控制审计报告" not in content
    assert "新疆众和股份有限公司2025年年度股东会会议资料" not in content
    assert "宁波富邦关于公司及子公司2026年度向银行申请综合授信额度的公告" not in content
    assert "宁波富邦关于公司使用临时闲置资金进行委托理财的公告" not in content
    assert "宁波富邦关于2026日常关联交易预计的公告" not in content
    assert "埃泰克首次公开发行股票并在主板上市招股说明书" not in content
    assert "关于浙江德宏汽车电子电器股份有限公司非经营性资金占用及其他关联资金往来情况的专项审核说明" not in content


def test_write_text_report_filters_exchange_equity_incentive_audit_materials_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-option-cancel-opinion",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="通源石油：董事会薪酬与考核委员会关于2024年股票期权激励计划部分股票期权注销事项的核查意见",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-option-cancel-opinion",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-insider-self-check",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="博彦科技：关于2026年限制性股票激励计划内幕信息知情人及激励对象买卖公司股票情况的自查报告",
            summary="summary",
            source="szse",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/szse-insider-self-check",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-cninfo-vesting-condition",
            first_seen_at="2026-04-11T00:00:00+08:00",
            last_seen_at="2026-04-11T00:00:00+08:00",
            canonical_title="关于2022年限制性股票激励计划首次授予第三个归属期符合归属条件的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-11T00:00:00+08:00",
            url="https://example.com/cninfo-vesting-condition",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-keep-reits",
            first_seen_at="2026-04-10T22:25:11+08:00",
            last_seen_at="2026-04-10T22:25:11+08:00",
            canonical_title="两单公募REITs获批",
            summary="summary",
            source="stcn",
            published_at="2026-04-10T22:25:11+08:00",
            url="https://example.com/keep-reits",
            event_type="fast_news",
            event_subtype="regulatory_approval",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-option-cancel-opinion",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-insider-self-check",
            direction="bearish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cninfo-vesting-condition",
            direction="bearish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-reits",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "两单公募REITs获批" in content
    assert "通源石油：董事会薪酬与考核委员会关于2024年股票期权激励计划部分股票期权注销事项的核查意见" not in content
    assert "博彦科技：关于2026年限制性股票激励计划内幕信息知情人及激励对象买卖公司股票情况的自查报告" not in content
    assert "关于2022年限制性股票激励计划首次授予第三个归属期符合归属条件的公告" not in content


def test_write_text_report_filters_exchange_equity_incentive_plan_summary_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-equity-incentive-summary",
            first_seen_at="2026-04-13T00:00:00+08:00",
            last_seen_at="2026-04-13T00:00:00+08:00",
            canonical_title="顶固集创：2026年限制性股票激励计划（草案）摘要",
            summary="summary",
            source="szse",
            published_at="2026-04-13T00:00:00+08:00",
            url="https://example.com/szse-equity-incentive-summary",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-stcn-nev-keep-equity-summary",
            first_seen_at="2026-04-12T17:45:53+08:00",
            last_seen_at="2026-04-12T17:45:53+08:00",
            canonical_title="乘联分会：3月全国乘用车厂商新能源批发预估112万辆",
            summary="summary",
            source="stcn",
            published_at="2026-04-12T17:45:53+08:00",
            url="https://example.com/stcn-nev-keep-equity-summary",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-equity-incentive-summary",
            direction="bearish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-nev-keep-equity-summary",
            direction="bullish",
            impact_score=99.0,
            reasoning="rule",
            themes=["新能源车"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "乘联分会：3月全国乘用车厂商新能源批发预估112万辆" in content
    assert "顶固集创：2026年限制性股票激励计划（草案）摘要" not in content


def test_write_text_report_filters_current_live_equity_and_order_data_disclosures(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-equity-related-matters",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="中岩大地：关于公司2024年股票期权激励计划相关事项的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-equity-related-matters",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-cninfo-order-data",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="豪森智能关于自愿披露2026年第一季度订单数据的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/cninfo-order-data",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-order-contract",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="中科曙光：签订10亿元算力订单",
            summary="公司签订10亿元算力订单。",
            source="stcn",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/keep-order-contract",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-equity-related-matters",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cninfo-order-data",
            direction="neutral",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-order-contract",
            direction="bullish",
            impact_score=100.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中岩大地：关于公司2024年股票期权激励计划相关事项的公告" not in content
    assert "豪森智能关于自愿披露2026年第一季度订单数据的公告" not in content
    assert "中科曙光：签订10亿元算力订单" in content


def test_write_text_report_filters_new_exchange_disclosure_noise_families(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-dno-insurance",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="上海电力股份有限公司关于为董事及高级管理人员投保责任保险的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-dno-insurance",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-cash-management",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="宁波联合关于使用暂时闲置自有资金开展国债逆回购、结构性存款业务的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-cash-management",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-reduction-predisclosure",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="启迪环境：关于持股5%以上股东股份减持计划的预披露公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-reduction-predisclosure",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-equity-legal-opinion",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="创业慧康：北京市天元律师事务所关于创业慧康科技股份有限公司作废处理部分限制性股票的法律意见",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-equity-legal-opinion",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-15T00:01:00+08:00",
            last_seen_at="2026-04-15T00:01:00+08:00",
            canonical_title="盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:01:00+08:00",
            url="https://example.com/keep-acquisition",
            event_type="hard_event",
            event_subtype="control_change",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-sse-dno-insurance",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["保险"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-sse-cash-management",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-reduction-predisclosure",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-equity-legal-opinion",
            direction="bearish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-acquisition",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告" in content
    assert "上海电力股份有限公司关于为董事及高级管理人员投保责任保险的公告" not in content
    assert "宁波联合关于使用暂时闲置自有资金开展国债逆回购、结构性存款业务的公告" not in content
    assert "启迪环境：关于持股5%以上股东股份减持计划的预披露公告" not in content
    assert "创业慧康：北京市天元律师事务所关于创业慧康科技股份有限公司作废处理部分限制性股票的法律意见" not in content


def test_write_text_report_filters_followup_live_head_disclosure_noise(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-option-cancel",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="上海电力股份有限公司关于注销首期股票期权激励计划部分股票期权的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-option-cancel",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-option-review-opinion",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="创业慧康：董事会薪酬与考核委员会关于公司作废部分已授予尚未归属的限制性股票相关事项的核查意见",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-option-review-opinion",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-share-buyback-board",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="燕京啤酒：关于提请股东会授权董事会审议股份回购事项的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-share-buyback-board",
            event_type="hard_event",
            event_subtype="board_resolution",
        ),
        Event(
            event_id="event-szse-repurchase-cancel",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="盛视科技：关于回购注销部分限制性股票的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-repurchase-cancel",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-ongoing-supervision",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="力合科创：国信证券股份有限公司关于《深圳市力合科创股份有限公司收购报告书》之持续督导意见",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-ongoing-supervision",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-miit-inspection-meeting",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="工业和信息化部党组召开第六轮巡视动员部署会",
            summary="会议对巡视工作进行动员部署。",
            source="miit",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/miit-inspection-meeting",
            event_type="policy",
            event_subtype="policy_support",
        ),
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-15T00:01:00+08:00",
            last_seen_at="2026-04-15T00:01:00+08:00",
            canonical_title="盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:01:00+08:00",
            url="https://example.com/keep-acquisition",
            event_type="hard_event",
            event_subtype="control_change",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-sse-option-cancel", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-option-review-opinion", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-share-buyback-board", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-repurchase-cancel", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-ongoing-supervision", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-miit-inspection-meeting", direction="bullish", impact_score=72.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-acquisition", direction="neutral", impact_score=100.0, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告" in content
    assert "上海电力股份有限公司关于注销首期股票期权激励计划部分股票期权的公告" not in content
    assert "创业慧康：董事会薪酬与考核委员会关于公司作废部分已授予尚未归属的限制性股票相关事项的核查意见" not in content
    assert "燕京啤酒：关于提请股东会授权董事会审议股份回购事项的公告" not in content
    assert "盛视科技：关于回购注销部分限制性股票的公告" not in content
    assert "力合科创：国信证券股份有限公司关于《深圳市力合科创股份有限公司收购报告书》之持续督导意见" not in content
    assert "工业和信息化部党组召开第六轮巡视动员部署会" not in content


def test_write_text_report_filters_remaining_live_template_agreements_and_equity_opinions(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-template-cooperation",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="齐翔腾达：关于与蓝帆医疗股份有限公司签署《深化战略合作框架协议》的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-template-cooperation",
            event_type="hard_event",
            event_subtype="cooperation_agreement",
        ),
        Event(
            event_id="event-szse-equity-review-opinion",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="盛视科技：董事会薪酬与考核委员会关于2024年限制性股票激励计划相关事项的核查意见",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-equity-review-opinion",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-15T00:01:00+08:00",
            last_seen_at="2026-04-15T00:01:00+08:00",
            canonical_title="盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:01:00+08:00",
            url="https://example.com/keep-acquisition",
            event_type="hard_event",
            event_subtype="control_change",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-szse-template-cooperation", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-equity-review-opinion", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-acquisition", direction="neutral", impact_score=100.0, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告" in content
    assert "齐翔腾达：关于与蓝帆医疗股份有限公司签署《深化战略合作框架协议》的公告" not in content
    assert "盛视科技：董事会薪酬与考核委员会关于2024年限制性股票激励计划相关事项的核查意见" not in content


def test_write_text_report_filters_exchange_order_contract_progress_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-order-progress",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="行云科技：关于中标项目签订协议的进展公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-order-progress",
            event_type="hard_event",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-15T00:01:00+08:00",
            last_seen_at="2026-04-15T00:01:00+08:00",
            canonical_title="盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:01:00+08:00",
            url="https://example.com/keep-acquisition",
            event_type="hard_event",
            event_subtype="control_change",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-szse-order-progress", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-acquisition", direction="neutral", impact_score=100.0, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告" in content
    assert "行云科技：关于中标项目签订协议的进展公告" not in content


def test_write_text_report_filters_exchange_cash_management_variants_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-cash-management-product",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="南方精工：关于利用自有闲置资金择机购买中短期低风险金融理财产品的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-cash-management-product",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-15T00:01:00+08:00",
            last_seen_at="2026-04-15T00:01:00+08:00",
            canonical_title="盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:01:00+08:00",
            url="https://example.com/keep-acquisition",
            event_type="hard_event",
            event_subtype="control_change",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-szse-cash-management-product", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-acquisition", direction="neutral", impact_score=100.0, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告" in content
    assert "南方精工：关于利用自有闲置资金择机购买中短期低风险金融理财产品的公告" not in content


def test_write_text_report_filters_latest_live_exchange_disclosure_variants(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-reduction-complete",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="罗博特科：关于股东股份减持计划完成的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/szse-reduction-complete",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-equity-self-check",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="瑞丰光电：关于2026年股票期权与限制性股票激励计划内幕信息知情人买卖公司股票情况的自查报告",
            summary="summary",
            source="szse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/szse-equity-self-check",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-rights-transfer",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="乐普医疗：关于子公司签署药品受让协议的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/szse-rights-transfer",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-15T00:01:00+08:00",
            last_seen_at="2026-04-15T00:01:00+08:00",
            canonical_title="盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:01:00+08:00",
            url="https://example.com/keep-acquisition",
            event_type="hard_event",
            event_subtype="control_change",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-szse-reduction-complete", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-equity-self-check", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-rights-transfer", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-acquisition", direction="neutral", impact_score=100.0, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告" in content
    assert "罗博特科：关于股东股份减持计划完成的公告" not in content
    assert "瑞丰光电：关于2026年股票期权与限制性股票激励计划内幕信息知情人买卖公司股票情况的自查报告" not in content
    assert "乐普医疗：关于子公司签署药品受让协议的公告" not in content


def test_write_text_report_filters_current_live_exchange_material_disclosures(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-audit-duty-report",
            first_seen_at="2026-04-14T00:00:00+08:00",
            last_seen_at="2026-04-14T00:00:00+08:00",
            canonical_title="上海电力股份有限公司董事会审计与风险委员会2025年度履职情况报告",
            summary="summary",
            source="sse",
            published_at="2026-04-14T00:00:00+08:00",
            url="https://example.com/sse-audit-duty-report",
            event_type="hard_event",
            event_subtype="board_resolution",
        ),
        Event(
            event_id="event-szse-stock-appreciation-opinion",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="哈尔斯：董事会薪酬与考核委员会关于2024年股票增值权激励计划第一个行权期的行权名单的核查意见",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-stock-appreciation-opinion",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-restructuring-impairment-test",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="广东建工：关于重大资产重组业绩承诺期满标的资产减值测试情况的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-restructuring-impairment-test",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-szse-restructuring-impairment-test-jman",
            first_seen_at="2026-05-01T00:00:00+08:00",
            last_seen_at="2026-05-01T00:00:00+08:00",
            canonical_title="维业股份：关于重大资产重组业绩承诺期届满标的资产减值测试情况的公告",
            summary="summary",
            source="szse",
            published_at="2026-05-01T00:00:00+08:00",
            url="https://example.com/szse-restructuring-impairment-test-jman",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-szse-reduction-expire-no-sale",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="凯瑞德：关于持股5%以上股东减持期限届满未减持股份的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-reduction-expire-no-sale",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-real-estate-brief",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="中国国贸2026年第一季度房地产行业经营性信息简报",
            summary="summary",
            source="sse",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/sse-real-estate-brief",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-real-estate-appraisal",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="房地产估价报告-沪城估（2025）(咨)字第00973号",
            summary="summary",
            source="sse",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/sse-real-estate-appraisal",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-bank-risk-rule",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="华夏银行董事会风险合规与消费者权益保护委员会工作规则",
            summary="summary",
            source="sse",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/sse-bank-risk-rule",
            event_type="hard_event",
            event_subtype="board_resolution",
        ),
        Event(
            event_id="event-szse-share-change-one-percent",
            first_seen_at="2026-05-01T00:00:00+08:00",
            last_seen_at="2026-05-01T00:00:00+08:00",
            canonical_title="达刚控股：关于股东减持股份变动比例触及1%整数倍的公告",
            summary="summary",
            source="szse",
            published_at="2026-05-01T00:00:00+08:00",
            url="https://example.com/szse-share-change-one-percent",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-below-five-percent",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="华大九天：关于持股5%以上股东减持至5%以下暨权益变动的提示性公告",
            summary="summary",
            source="szse",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/szse-below-five-percent",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-share-change-plan-complete",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="泰和科技：关于控股股东、实际控制人及其一致行动人权益变动触及1%整数倍暨减持计划实施完毕的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/szse-share-change-plan-complete",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-equity-adjustment",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="ST迪威迅：关于调整2026年限制性股票激励计划相关事项的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/szse-equity-adjustment",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-15T00:01:00+08:00",
            last_seen_at="2026-04-15T00:01:00+08:00",
            canonical_title="盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:01:00+08:00",
            url="https://example.com/keep-acquisition",
            event_type="hard_event",
            event_subtype="control_change",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-sse-audit-duty-report", direction="bearish", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-stock-appreciation-opinion", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-restructuring-impairment-test", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-restructuring-impairment-test-jman", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-reduction-expire-no-sale", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-real-estate-brief", direction="neutral", impact_score=100.0, reasoning="rule", themes=["房地产"], triggered=True),
        EventAnalysis(event_id="event-sse-real-estate-appraisal", direction="neutral", impact_score=100.0, reasoning="rule", themes=["房地产"], triggered=True),
        EventAnalysis(event_id="event-sse-bank-risk-rule", direction="bearish", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-share-change-one-percent", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-below-five-percent", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-share-change-plan-complete", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-equity-adjustment", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-acquisition", direction="neutral", impact_score=100.0, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告" in content
    assert "上海电力股份有限公司董事会审计与风险委员会2025年度履职情况报告" not in content
    assert "哈尔斯：董事会薪酬与考核委员会关于2024年股票增值权激励计划第一个行权期的行权名单的核查意见" not in content
    assert "广东建工：关于重大资产重组业绩承诺期满标的资产减值测试情况的公告" not in content
    assert "维业股份：关于重大资产重组业绩承诺期届满标的资产减值测试情况的公告" not in content
    assert "凯瑞德：关于持股5%以上股东减持期限届满未减持股份的公告" not in content
    assert "中国国贸2026年第一季度房地产行业经营性信息简报" not in content
    assert "房地产估价报告-沪城估（2025）(咨)字第00973号" not in content
    assert "华夏银行董事会风险合规与消费者权益保护委员会工作规则" not in content
    assert "达刚控股：关于股东减持股份变动比例触及1%整数倍的公告" not in content
    assert "华大九天：关于持股5%以上股东减持至5%以下暨权益变动的提示性公告" not in content
    assert "泰和科技：关于控股股东、实际控制人及其一致行动人权益变动触及1%整数倍暨减持计划实施完毕的公告" not in content
    assert "ST迪威迅：关于调整2026年限制性股票激励计划相关事项的公告" not in content


def test_write_text_report_filters_current_live_szse_disclosure_variants_without_hiding_policy_signal(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-stock-pledge-repurchase",
            first_seen_at="2026-04-20T00:00:00+08:00",
            last_seen_at="2026-04-20T00:00:00+08:00",
            canonical_title="利安隆：关于控股股东部分股份办理股票质押式回购交易业务的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-20T00:00:00+08:00",
            url="https://example.com/szse-stock-pledge-repurchase",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-top-shareholders-buyback",
            first_seen_at="2026-04-20T00:00:00+08:00",
            last_seen_at="2026-04-20T00:00:00+08:00",
            canonical_title="力源信息：关于回购股份事项前十名股东及前十名无限售条件股东持股情况的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-20T00:00:00+08:00",
            url="https://example.com/szse-top-shareholders-buyback",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-equity-review-opinion-current",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="万讯自控：董事会薪酬与考核委员会关于回购注销及作废2023年限制性股票激励计划部分限制性股票的核查意见",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-equity-review-opinion-current",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-reduction-finish-current",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="海泰科：关于控股股东、实际控制人提前终止减持计划暨减持结果的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-reduction-finish-current",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-policy-signal-current",
            first_seen_at="2026-04-20T20:24:07+08:00",
            last_seen_at="2026-04-20T20:24:07+08:00",
            canonical_title="广东：要用好产业引导基金 加大对集成电路、具身智能、算电协同等领域的投资",
            summary="summary",
            source="cls",
            published_at="2026-04-20T20:24:07+08:00",
            url="https://example.com/keep-policy-signal-current",
            event_type="fast_news",
            event_subtype="policy_signal",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-szse-stock-pledge-repurchase", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-top-shareholders-buyback", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-equity-review-opinion-current", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-reduction-finish-current", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-policy-signal-current", direction="bullish", impact_score=99.3, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "广东：要用好产业引导基金 加大对集成电路、具身智能、算电协同等领域的投资" in content
    assert "利安隆：关于控股股东部分股份办理股票质押式回购交易业务的公告" not in content
    assert "力源信息：关于回购股份事项前十名股东及前十名无限售条件股东持股情况的公告" not in content
    assert "万讯自控：董事会薪酬与考核委员会关于回购注销及作废2023年限制性股票激励计划部分限制性股票的核查意见" not in content
    assert "海泰科：关于控股股东、实际控制人提前终止减持计划暨减持结果的公告" not in content


def test_write_text_report_filters_current_live_equity_incentive_variants(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-option-exercise-condition",
            first_seen_at="2026-04-16T00:00:00+08:00",
            last_seen_at="2026-04-16T00:00:00+08:00",
            canonical_title="中远海能关于2023年股票期权激励计划首次授予期权第一个行权期符合行权条件的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-16T00:00:00+08:00",
            url="https://example.com/sse-option-exercise-condition",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-sse-option-adjust-cancel",
            first_seen_at="2026-04-16T00:00:00+08:00",
            last_seen_at="2026-04-16T00:00:00+08:00",
            canonical_title="中远海能关于调整2023年股票期权激励计划期权数量、行权价格并注销部分已获授但未行权的股票期权的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-16T00:00:00+08:00",
            url="https://example.com/sse-option-adjust-cancel",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-equity-plan-draft",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="汇成真空：2026年限制性股票激励计划（草案）",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/szse-equity-plan-draft",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-16T18:51:44+08:00",
            last_seen_at="2026-04-16T18:51:44+08:00",
            canonical_title="云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目",
            summary="summary",
            source="cls",
            published_at="2026-04-16T18:51:44+08:00",
            url="https://example.com/keep-acquisition",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-sse-option-exercise-condition", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-option-adjust-cancel", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-equity-plan-draft", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-acquisition", direction="bullish", impact_score=99.3, reasoning="rule", themes=["锂电池"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目" in content
    assert "中远海能关于2023年股票期权激励计划首次授予期权第一个行权期符合行权条件的公告" not in content
    assert "中远海能关于调整2023年股票期权激励计划期权数量、行权价格并注销部分已获授但未行权的股票期权的公告" not in content
    assert "汇成真空：2026年限制性股票激励计划（草案）" not in content


def test_write_text_report_filters_remaining_live_equity_and_cls_admin_fast_news(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-repurchase-cancel-unlock",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="宇环数控：关于回购注销部分已获授但尚未解除限售的限制性股票的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/szse-repurchase-cancel-unlock",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-equity-void-unvested",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="开立医疗：关于2023年限制性股票激励计划第三个归属期归属条件未成就暨作废部分已授予但尚未归属的限制性股票的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/szse-equity-void-unvested",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-cls-reduction",
            first_seen_at="2026-04-16T19:29:02+08:00",
            last_seen_at="2026-04-16T19:29:02+08:00",
            canonical_title="致远新能：股东王然拟合计减持不超3%公司股份",
            summary="summary",
            source="cls",
            published_at="2026-04-16T19:29:02+08:00",
            url="https://example.com/cls-reduction",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-cls-lof-suspension",
            first_seen_at="2026-04-16T19:12:28+08:00",
            last_seen_at="2026-04-16T19:12:28+08:00",
            canonical_title="财联社4月16日电，南方原油LOF(501018)将于2026年4月17日开市起至当日10:30停牌，自2026年4月17日10:30复牌。",
            summary="summary",
            source="cls",
            published_at="2026-04-16T19:12:28+08:00",
            url="https://example.com/cls-lof-suspension",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-keep-catalyst",
            first_seen_at="2026-04-16T18:51:44+08:00",
            last_seen_at="2026-04-16T18:51:44+08:00",
            canonical_title="云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目",
            summary="summary",
            source="cls",
            published_at="2026-04-16T18:51:44+08:00",
            url="https://example.com/keep-catalyst",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-szse-repurchase-cancel-unlock", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-equity-void-unvested", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-cls-reduction", direction="neutral", impact_score=74.3, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-cls-lof-suspension", direction="neutral", impact_score=79.3, reasoning="rule", themes=["油气"], triggered=True),
        EventAnalysis(event_id="event-keep-catalyst", direction="bullish", impact_score=99.3, reasoning="rule", themes=["锂电池"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目" in content
    assert "宇环数控：关于回购注销部分已获授但尚未解除限售的限制性股票的公告" not in content
    assert "开立医疗：关于2023年限制性股票激励计划第三个归属期归属条件未成就暨作废部分已授予但尚未归属的限制性股票的公告" not in content
    assert "致远新能：股东王然拟合计减持不超3%公司股份" not in content
    assert "南方原油LOF(501018)" not in content


def test_write_text_report_filters_control_change_performance_statement_and_share_increase_plan(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-share-increase-plan",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="共达电声：共达电声股份有限公司关于控股股东的一致行动人增持公司股份计划的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/szse-share-increase-plan",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-control-change-performance",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="金一文化：关于收购开科唯识控制权事项业绩承诺实现情况的专项说明",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/szse-control-change-performance",
            event_type="hard_event",
            event_subtype="control_change",
        ),
        Event(
            event_id="event-keep-catalyst",
            first_seen_at="2026-04-16T18:51:44+08:00",
            last_seen_at="2026-04-16T18:51:44+08:00",
            canonical_title="云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目",
            summary="summary",
            source="cls",
            published_at="2026-04-16T18:51:44+08:00",
            url="https://example.com/keep-catalyst",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-szse-share-increase-plan", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-control-change-performance", direction="bullish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-catalyst", direction="bullish", impact_score=99.3, reasoning="rule", themes=["锂电池"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目" in content
    assert "共达电声：共达电声股份有限公司关于控股股东的一致行动人增持公司股份计划的公告" not in content
    assert "金一文化：关于收购开科唯识控制权事项业绩承诺实现情况的专项说明" not in content


def test_write_text_report_filters_central_bank_gold_reserve_brief_without_hiding_catalyst(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-gold-reserve-brief",
            first_seen_at="2026-04-16T19:36:58+08:00",
            last_seen_at="2026-04-16T19:36:58+08:00",
            canonical_title="财联社4月16日电，据土耳其央行数据，截至4月10日当周，其国际标准黄金储备增加5.77吨，至699.89吨。",
            summary="summary",
            source="cls",
            published_at="2026-04-16T19:36:58+08:00",
            url="https://example.com/cls-gold-reserve-brief",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-keep-catalyst",
            first_seen_at="2026-04-16T18:51:44+08:00",
            last_seen_at="2026-04-16T18:51:44+08:00",
            canonical_title="云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目",
            summary="summary",
            source="cls",
            published_at="2026-04-16T18:51:44+08:00",
            url="https://example.com/keep-catalyst",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-cls-gold-reserve-brief", direction="neutral", impact_score=79.3, reasoning="rule", themes=["黄金"], triggered=True),
        EventAnalysis(event_id="event-keep-catalyst", direction="bullish", impact_score=99.3, reasoning="rule", themes=["锂电池"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目" in content
    assert "国际标准黄金储备增加5.77吨" not in content


def test_write_text_report_filters_cls_retail_gold_price_commentary_without_hiding_gold_market_move(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-retail-gold-price-commentary",
            first_seen_at="2026-05-01T12:32:12+08:00",
            last_seen_at="2026-05-01T12:32:12+08:00",
            canonical_title="品牌金饰克价超1400元 贵金属分析师：预计价格中心年内将逐步上移",
            summary="【品牌金饰克价超1400元 贵金属分析师：预计价格中心年内将逐步上移】财联社5月1日电，国内品牌金饰价格已纷纷来到1400元/克上方。今日周生生足金饰品报价1415元/克、周大福足金饰品价格更达到1419元/克，老凤祥报价也在1410元/克。上海钢联铅锌资讯部贵金属分析师黄廷分析称，预计价格中心年内将逐步上移。",
            source="cls",
            published_at="2026-05-01T12:32:12+08:00",
            url="https://example.com/cls-retail-gold-price-commentary",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-cls-gold-market-move-keep",
            first_seen_at="2026-04-03T09:15:00+08:00",
            last_seen_at="2026-04-03T09:15:00+08:00",
            canonical_title="现货黄金跌破4600美元/盎司",
            summary="summary",
            source="cls",
            published_at="2026-04-03T09:15:00+08:00",
            url="https://example.com/cls-gold-market-move-keep",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cls-retail-gold-price-commentary",
            direction="neutral",
            impact_score=99.3,
            reasoning="rule",
            themes=["黄金"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-gold-market-move-keep",
            direction="neutral",
            impact_score=74.3,
            reasoning="rule",
            themes=["黄金"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "品牌金饰克价超1400元 贵金属分析师：预计价格中心年内将逐步上移" not in content
    assert "现货黄金跌破4600美元/盎司" in content


def test_write_text_report_filters_local_leader_manufacturing_visit_and_repeated_delisting_risk_notice(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-local-leader-visit",
            first_seen_at="2026-04-16T19:28:56+08:00",
            last_seen_at="2026-04-16T19:28:56+08:00",
            canonical_title="河南省省长王凯到郑州调研先进制造业发展",
            summary="summary",
            source="stcn",
            published_at="2026-04-16T19:28:56+08:00",
            url="https://example.com/stcn-local-leader-visit",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-repeated-delisting-risk",
            first_seen_at="2026-04-16T00:00:00+08:00",
            last_seen_at="2026-04-16T00:00:00+08:00",
            canonical_title="*ST椰岛关于公司股票交易风险暨可能被终止上市的第六次风险提示公告",
            summary="summary",
            source="sse",
            published_at="2026-04-16T00:00:00+08:00",
            url="https://example.com/sse-repeated-delisting-risk",
            event_type="hard_event",
            event_subtype="delisting_risk",
        ),
        Event(
            event_id="event-keep-catalyst",
            first_seen_at="2026-04-16T18:51:44+08:00",
            last_seen_at="2026-04-16T18:51:44+08:00",
            canonical_title="云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目",
            summary="summary",
            source="cls",
            published_at="2026-04-16T18:51:44+08:00",
            url="https://example.com/keep-catalyst",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-stcn-local-leader-visit", direction="bullish", impact_score=99.0, reasoning="rule", themes=["新能源车"], triggered=True),
        EventAnalysis(event_id="event-sse-repeated-delisting-risk", direction="bearish", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-catalyst", direction="bullish", impact_score=99.3, reasoning="rule", themes=["锂电池"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目" in content
    assert "河南省省长王凯到郑州调研先进制造业发展" not in content
    assert "*ST椰岛关于公司股票交易风险暨可能被终止上市的第六次风险提示公告" not in content


def test_write_text_report_filters_news_broadcast_roundup_without_hiding_catalyst(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-news-broadcast-roundup",
            first_seen_at="2026-04-16T20:10:21+08:00",
            last_seen_at="2026-04-16T20:10:21+08:00",
            canonical_title="4月16日周四《新闻联播》要闻22条",
            summary="summary",
            source="cls",
            published_at="2026-04-16T20:10:21+08:00",
            url="https://example.com/cls-news-broadcast-roundup",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-keep-catalyst",
            first_seen_at="2026-04-16T18:51:44+08:00",
            last_seen_at="2026-04-16T18:51:44+08:00",
            canonical_title="云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目",
            summary="summary",
            source="cls",
            published_at="2026-04-16T18:51:44+08:00",
            url="https://example.com/keep-catalyst",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-cls-news-broadcast-roundup", direction="bullish", impact_score=99.3, reasoning="rule", themes=["算力", "文旅"], triggered=True),
        EventAnalysis(event_id="event-keep-catalyst", direction="bullish", impact_score=99.3, reasoning="rule", themes=["锂电池"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目" in content
    assert "《新闻联播》要闻22条" not in content


def test_write_text_report_filters_cls_telegraph_interpretation_column_without_hiding_catalyst(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-telegraph-interpretation",
            first_seen_at="2026-04-16T20:06:58+08:00",
            last_seen_at="2026-04-16T20:06:58+08:00",
            canonical_title="【电报解读】马斯克要求“光速”推进Terafab项目！分析师强Call“火箭+卫星+光伏+算力芯片”全面布局下，马斯克太空算力版图有望实现商业闭环，这家公司设备主要应用于逻辑芯片、存储芯片制造领域",
            summary="summary",
            source="cls",
            published_at="2026-04-16T20:06:58+08:00",
            url="https://example.com/cls-telegraph-interpretation",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-keep-catalyst",
            first_seen_at="2026-04-16T18:51:44+08:00",
            last_seen_at="2026-04-16T18:51:44+08:00",
            canonical_title="云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目",
            summary="summary",
            source="cls",
            published_at="2026-04-16T18:51:44+08:00",
            url="https://example.com/keep-catalyst",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-cls-telegraph-interpretation", direction="neutral", impact_score=79.3, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-keep-catalyst", direction="bullish", impact_score=99.3, reasoning="rule", themes=["锂电池"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目" in content
    assert "【电报解读】马斯克要求“光速”推进Terafab项目" not in content


def test_write_text_report_filters_cls_wind_research_column_and_share_reduction_plan_variant(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-wind-research",
            first_seen_at="2026-04-21T10:15:59+08:00",
            last_seen_at="2026-04-21T10:15:59+08:00",
            canonical_title="【风口研报·公司】积极拓展智算服务+数据智能，这家公司加码扩充万卡级算力、租赁服务需求可期，多路径布局AI算力和应用产品线；这家光通信芯片公司在数据中心侧芯片实现从追赶到并跑的突破",
            summary="summary",
            source="cls",
            published_at="2026-04-21T10:15:59+08:00",
            url="https://example.com/cls-wind-research",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-cls-wind-research-business-guidance",
            first_seen_at="2026-04-21T10:58:48+08:00",
            last_seen_at="2026-04-21T10:58:48+08:00",
            canonical_title="【风口研报·公司】造船景气周期+产能扩张共振，这家公司切入高端船舶制造及配套产业链、油轮新船市占率高达40%实现行业断层领先，高价订单陆续交付助推业绩增长",
            summary="summary",
            source="cls",
            published_at="2026-04-21T10:58:48+08:00",
            url="https://example.com/cls-wind-research-business-guidance",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-szse-share-reduction-plan",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="和胜股份：关于股东计划减持公司股份的预披露公告",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-share-reduction-plan",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-catalyst",
            first_seen_at="2026-04-21T10:51:44+08:00",
            last_seen_at="2026-04-21T10:51:44+08:00",
            canonical_title="云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目",
            summary="summary",
            source="cls",
            published_at="2026-04-21T10:51:44+08:00",
            url="https://example.com/keep-catalyst",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-cls-wind-research", direction="neutral", impact_score=79.3, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-cls-wind-research-business-guidance", direction="bullish", impact_score=74.3, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-share-reduction-plan", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-catalyst", direction="bullish", impact_score=99.3, reasoning="rule", themes=["锂电池"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目" in content
    assert "【风口研报·公司】积极拓展智算服务+数据智能" not in content
    assert "【风口研报·公司】造船景气周期+产能扩张共振" not in content
    assert "和胜股份：关于股东计划减持公司股份的预披露公告" not in content


def test_write_text_report_filters_current_live_related_party_and_restructuring_material_cluster(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-financial-service-agreement",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="佛山照明：关于与广东省广晟财务有限公司签署《金融服务协议》的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/szse-financial-service-agreement",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-equity-entrust-manage",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="中成股份：中成进出口股份有限公司关于与中国成套设备进出口集团有限公司签署《股权委托管理协议》暨关联交易的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/szse-equity-entrust-manage",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-restructuring-review-approved",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="电投能源：关于公司发行股份及支付现金购买资产并募集配套资金暨关联交易获得深圳证券交易所并购重组审核委员会审核通过的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/szse-restructuring-review-approved",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-sse-restructuring-review-meeting-schedule",
            first_seen_at="2026-04-24T00:00:00+08:00",
            last_seen_at="2026-04-24T00:00:00+08:00",
            canonical_title="东睦股份关于上海证券交易所并购重组审核委员会审核公司发行股份及支付现金购买资产并募集配套资金暨关联交易事项会议安排的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-24T00:00:00+08:00",
            url="https://example.com/sse-restructuring-review-meeting-schedule",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-szse-restructuring-risk-resume",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="甘肃能化：关于披露发行股份及支付现金购买资产并募集配套资金暨关联交易预案的一般风险提示暨公司股票复牌的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/szse-restructuring-risk-resume",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-price-fluctuation-note",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="甘肃能化：董事会关于本次交易信息发布前公司股票价格波动情况的说明",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/szse-price-fluctuation-note",
            event_type="hard_event",
            event_subtype="board_resolution",
        ),
        Event(
            event_id="event-keep-catalyst",
            first_seen_at="2026-04-16T18:51:44+08:00",
            last_seen_at="2026-04-16T18:51:44+08:00",
            canonical_title="云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目",
            summary="summary",
            source="cls",
            published_at="2026-04-16T18:51:44+08:00",
            url="https://example.com/keep-catalyst",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-szse-financial-service-agreement", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-equity-entrust-manage", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-restructuring-review-approved", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-restructuring-review-meeting-schedule", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-restructuring-risk-resume", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-price-fluctuation-note", direction="bullish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-catalyst", direction="bullish", impact_score=99.3, reasoning="rule", themes=["锂电池"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目" in content
    assert "佛山照明：关于与广东省广晟财务有限公司签署《金融服务协议》的公告" not in content
    assert "中成股份：中成进出口股份有限公司关于与中国成套设备进出口集团有限公司签署《股权委托管理协议》暨关联交易的公告" not in content
    assert "电投能源：关于公司发行股份及支付现金购买资产并募集配套资金暨关联交易获得深圳证券交易所并购重组审核委员会审核通过的公告" not in content
    assert "东睦股份关于上海证券交易所并购重组审核委员会审核公司发行股份及支付现金购买资产并募集配套资金暨关联交易事项会议安排的公告" not in content
    assert "甘肃能化：关于披露发行股份及支付现金购买资产并募集配套资金暨关联交易预案的一般风险提示暨公司股票复牌的公告" not in content
    assert "甘肃能化：董事会关于本次交易信息发布前公司股票价格波动情况的说明" not in content


def test_write_text_report_filters_current_live_disclosure_tail_noise_cluster(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-shareholder-meeting-legal-opinion",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="ST岭南：北京市康达(深圳)律师事务所关于岭南生态文旅股份有限公司2026年第一次临时股东会的法律意见书",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/szse-shareholder-meeting-legal-opinion",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-equity-creditor-notice",
            first_seen_at="2026-04-16T00:00:00+08:00",
            last_seen_at="2026-04-16T00:00:00+08:00",
            canonical_title="索菱股份：关于回购注销2023年限制性股票与股票期权激励计划部分限制性股票暨通知债权人的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-16T00:00:00+08:00",
            url="https://example.com/szse-equity-creditor-notice",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-buyback-purpose-change",
            first_seen_at="2026-04-16T00:00:00+08:00",
            last_seen_at="2026-04-16T00:00:00+08:00",
            canonical_title="中宠股份：关于变更股份回购用途的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-16T00:00:00+08:00",
            url="https://example.com/szse-buyback-purpose-change",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-share-reduction-finished",
            first_seen_at="2026-04-16T00:00:00+08:00",
            last_seen_at="2026-04-16T00:00:00+08:00",
            canonical_title="红棉股份：关于持股5%以上股东股份减持完成的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-16T00:00:00+08:00",
            url="https://example.com/szse-share-reduction-finished",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-catalyst",
            first_seen_at="2026-04-16T00:00:00+08:00",
            last_seen_at="2026-04-16T00:00:00+08:00",
            canonical_title="华业香料：关于实施食品添加剂数智化改扩建项目暨拟签署投资协议的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-16T00:00:00+08:00",
            url="https://example.com/keep-catalyst",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-szse-shareholder-meeting-legal-opinion", direction="neutral", impact_score=100.0, reasoning="rule", themes=["文旅"], triggered=True),
        EventAnalysis(event_id="event-szse-equity-creditor-notice", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-buyback-purpose-change", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-share-reduction-finished", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-catalyst", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "华业香料：关于实施食品添加剂数智化改扩建项目暨拟签署投资协议的公告" in content
    assert "ST岭南：北京市康达(深圳)律师事务所关于岭南生态文旅股份有限公司2026年第一次临时股东会的法律意见书" not in content
    assert "索菱股份：关于回购注销2023年限制性股票与股票期权激励计划部分限制性股票暨通知债权人的公告" not in content
    assert "中宠股份：关于变更股份回购用途的公告" not in content
    assert "红棉股份：关于持股5%以上股东股份减持完成的公告" not in content


def test_write_text_report_filters_current_live_sse_tail_noise_cluster(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-option-cancel-finished",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="上海电力股份有限公司关于首期股票期权激励计划部分股票期权注销完成的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/sse-option-cancel-finished",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-sse-share-increase-legal-opinion",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="新疆天阳律师事务所关于新疆天业股份有限公司控股股东增持股份之法律意见书",
            summary="summary",
            source="sse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/sse-share-increase-legal-opinion",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-related-party-shipbuilding",
            first_seen_at="2026-04-16T00:00:00+08:00",
            last_seen_at="2026-04-16T00:00:00+08:00",
            canonical_title="公告2026-017-中远海能关于投资建造两艘巴拿马型原油轮暨关联交易的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-16T00:00:00+08:00",
            url="https://example.com/keep-related-party-shipbuilding",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-sse-option-cancel-finished", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-share-increase-legal-opinion", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-related-party-shipbuilding", direction="neutral", impact_score=100.0, reasoning="rule", themes=["油气"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "公告2026-017-中远海能关于投资建造两艘巴拿马型原油轮暨关联交易的公告" in content
    assert "上海电力股份有限公司关于首期股票期权激励计划部分股票期权注销完成的公告" not in content
    assert "新疆天阳律师事务所关于新疆天业股份有限公司控股股东增持股份之法律意见书" not in content


def test_write_text_report_filters_stock_trading_risk_tip_and_halt_check_notice_without_hiding_cls_halt_check(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cninfo-risk-tip-halt-check",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="关于股票交易风险提示暨停牌核查的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/cninfo-risk-tip-halt-check",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-catalyst",
            first_seen_at="2026-04-16T20:16:13+08:00",
            last_seen_at="2026-04-16T20:16:13+08:00",
            canonical_title="甘肃能化：拟收购金昌化工100%股权 股票复牌",
            summary="summary",
            source="cls",
            published_at="2026-04-16T20:16:13+08:00",
            url="https://example.com/keep-catalyst",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-cninfo-risk-tip-halt-check", direction="bearish", impact_score=80.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-catalyst", direction="neutral", impact_score=74.3, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "关于股票交易风险提示暨停牌核查的公告" not in content
    assert "甘肃能化：拟收购金昌化工100%股权 股票复牌" in content


def test_write_text_report_filters_repeated_delisting_risk_tip_variants_without_hiding_revocation(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-repeated-stock-risk-tip",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="中化岩土：关于公司股票交易风险的第三次提示性公告",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/repeated-stock-risk-tip",
            event_type="hard_event",
            event_subtype="delisting_risk",
        ),
        Event(
            event_id="event-repeated-delisting-risk-tip",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="GQY视讯：关于公司股票可能被实施退市风险警示的第三次提示性公告",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/repeated-delisting-risk-tip",
            event_type="hard_event",
            event_subtype="delisting_risk",
        ),
        Event(
            event_id="event-keep-delisting-revocation",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="*ST铖昌：浙江铖昌科技股份有限公司关于申请撤销公司股票退市风险警示的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/keep-delisting-revocation",
            event_type="hard_event",
            event_subtype="delisting_risk",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-repeated-stock-risk-tip", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-repeated-delisting-risk-tip", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-delisting-revocation", direction="bullish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中化岩土：关于公司股票交易风险的第三次提示性公告" not in content
    assert "GQY视讯：关于公司股票可能被实施退市风险警示的第三次提示性公告" not in content
    assert "*ST铖昌：浙江铖昌科技股份有限公司关于申请撤销公司股票退市风险警示的公告" in content


def test_write_text_report_keeps_current_live_related_party_shipbuilding_catalyst(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-shipbuilding-related-party-catalyst",
            first_seen_at="2026-04-16T00:00:00+08:00",
            last_seen_at="2026-04-16T00:00:00+08:00",
            canonical_title="公告2026-017-中远海能关于投资建造两艘巴拿马型原油轮暨关联交易的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-16T00:00:00+08:00",
            url="https://example.com/shipbuilding-related-party-catalyst",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-shipbuilding-related-party-catalyst",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "公告2026-017-中远海能关于投资建造两艘巴拿马型原油轮暨关联交易的公告" in content


def test_write_text_report_keeps_current_live_first_delisting_risk_tip_notice(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-first-delisting-risk-tip",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="关于延期披露2025年年度报告及退市风险提示性公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/first-delisting-risk-tip",
            event_type="hard_event",
            event_subtype="delisting_risk",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-first-delisting-risk-tip",
            direction="bearish",
            impact_score=80.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "关于延期披露2025年年度报告及退市风险提示性公告" in content


def test_write_text_report_filters_cls_wind_research_insight_column_without_hiding_real_fast_news(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-wind-research-insight",
            first_seen_at="2026-04-16T21:54:41+08:00",
            last_seen_at="2026-04-16T21:54:41+08:00",
            canonical_title="【风口研报·洞察】SpaceX星舰V3发射在即，深蓝航天等企业计划首飞，商业航天催化剂在第二季度密集进入落地期，分析师看好太空光伏逻辑持续演绎；权益反攻正在进行",
            summary="summary",
            source="cls",
            published_at="2026-04-16T21:54:41+08:00",
            url="https://example.com/cls-wind-research-insight",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-keep-fast-news",
            first_seen_at="2026-04-16T21:57:51+08:00",
            last_seen_at="2026-04-16T21:57:51+08:00",
            canonical_title="上交所就晶科科技公告拟投资245亿元建设算力中心相关项目发布监管工作函",
            summary="summary",
            source="cls",
            published_at="2026-04-16T21:57:51+08:00",
            url="https://example.com/keep-fast-news",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-cls-wind-research-insight", direction="bullish", impact_score=99.3, reasoning="rule", themes=["商业航天"], triggered=True),
        EventAnalysis(event_id="event-keep-fast-news", direction="bullish", impact_score=99.3, reasoning="rule", themes=["算力"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "【风口研报·洞察】SpaceX星舰V3发射在即" not in content
    assert "上交所就晶科科技公告拟投资245亿元建设算力中心相关项目发布监管工作函" in content


def test_write_text_report_filters_cls_gold_memo_column_without_hiding_notice_digest(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-gold-memo",
            first_seen_at="2026-04-16T22:15:55+08:00",
            last_seen_at="2026-04-16T22:15:55+08:00",
            canonical_title="【金牌纪要库】中国移动启动AI超节点设备集采，国产AI算力生态在大规模推理时代迎来关键拐点，核心增量在于内部高效互联的Scale up环节",
            summary="summary",
            source="cls",
            published_at="2026-04-16T22:15:55+08:00",
            url="https://example.com/cls-gold-memo",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-keep-notice-digest",
            first_seen_at="2026-04-16T22:05:36+08:00",
            last_seen_at="2026-04-16T22:05:36+08:00",
            canonical_title="【公告全知道】算力+绿色电力+储能+数据中心！公司拟245亿元投建算电协同项目",
            summary="summary",
            source="cls",
            published_at="2026-04-16T22:05:36+08:00",
            url="https://example.com/keep-notice-digest",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-cls-gold-memo", direction="neutral", impact_score=79.3, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-keep-notice-digest", direction="neutral", impact_score=99.3, reasoning="rule", themes=["算力", "储能"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "【金牌纪要库】中国移动启动AI超节点设备集采" not in content
    assert "【公告全知道】算力+绿色电力+储能+数据中心！公司拟245亿元投建算电协同项目" in content


def test_write_text_report_filters_cls_global_market_brief_without_hiding_domestic_order_catalyst(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-silver-brief",
            first_seen_at="2026-04-16T22:05:49+08:00",
            last_seen_at="2026-04-16T22:05:49+08:00",
            canonical_title="财联社4月16日电，现货白银跌1%，报78.12美元/盎司。",
            summary="summary",
            source="cls",
            published_at="2026-04-16T22:05:49+08:00",
            url="https://example.com/cls-silver-brief",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-cls-us-optical-brief",
            first_seen_at="2026-04-16T21:49:48+08:00",
            last_seen_at="2026-04-16T21:49:48+08:00",
            canonical_title="美股光通信股走势分化",
            summary="summary",
            source="cls",
            published_at="2026-04-16T21:49:48+08:00",
            url="https://example.com/cls-us-optical-brief",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-keep-domestic-order",
            first_seen_at="2026-04-16T22:18:36+08:00",
            last_seen_at="2026-04-16T22:18:36+08:00",
            canonical_title="财联社4月16日电，印度石油部表示，已敲定80万吨液化石油气进口订单，相关供应货物正在运往印度途中。",
            summary="summary",
            source="cls",
            published_at="2026-04-16T22:18:36+08:00",
            url="https://example.com/keep-domestic-order",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-cls-silver-brief", direction="neutral", impact_score=79.3, reasoning="rule", themes=["黄金"], triggered=True),
        EventAnalysis(event_id="event-cls-us-optical-brief", direction="neutral", impact_score=79.3, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-keep-domestic-order", direction="neutral", impact_score=99.3, reasoning="rule", themes=["油气"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "财联社4月16日电，现货白银跌1%，报78.12美元/盎司。" not in content
    assert "美股光通信股走势分化" not in content
    assert "财联社4月16日电，印度石油部表示，已敲定80万吨液化石油气进口订单，相关供应货物正在运往印度途中。" in content


def test_write_text_report_filters_cls_notice_digest_roundup_without_hiding_single_strong_notice_digest(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-notice-digest-roundup",
            first_seen_at="2026-04-20T22:03:01+08:00",
            last_seen_at="2026-04-20T22:03:01+08:00",
            canonical_title="【公告全知道】CPO+液冷+芯片+数据中心+机器人！公司1.6T光模块小批量供货",
            summary="①CPO+液冷+芯片+数据中心+机器人！这家公司1.6T光模块小批量供货且适用于下一代高速光模块的超薄型液冷散热解决方案已小批量试产；②商业航天+算力+液冷+AI智能体+数据中心+机器人！这家公司自有算力规模已超10000P且行业内率先实现Openclaw云端部署；③光通信+芯片+量子科技！公司一季度净利同比增超500%且光通信领域收入同比增近150%。",
            source="cls",
            published_at="2026-04-20T22:03:01+08:00",
            url="https://example.com/cls-notice-digest-roundup",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-cls-notice-digest-keep",
            first_seen_at="2026-04-20T22:05:36+08:00",
            last_seen_at="2026-04-20T22:05:36+08:00",
            canonical_title="【公告全知道】算力+绿色电力+储能+数据中心！公司拟245亿元投建算电协同项目",
            summary="summary",
            source="cls",
            published_at="2026-04-20T22:05:36+08:00",
            url="https://example.com/cls-notice-digest-keep",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cls-notice-digest-roundup",
            direction="neutral",
            impact_score=99.3,
            reasoning="rule",
            themes=["算力", "机器人"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-notice-digest-keep",
            direction="neutral",
            impact_score=99.3,
            reasoning="rule",
            themes=["算力", "储能"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "【公告全知道】CPO+液冷+芯片+数据中心+机器人！公司1.6T光模块小批量供货" not in content
    assert "【公告全知道】算力+绿色电力+储能+数据中心！公司拟245亿元投建算电协同项目" in content


def test_write_text_report_filters_cls_science_feature_story_without_hiding_company_product_progress(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-science-feature-story",
            first_seen_at="2026-04-17T15:22:35+08:00",
            last_seen_at="2026-04-17T15:22:35+08:00",
            canonical_title="全球首款可耐受1300℃高温的锂电池材料研发成功",
            summary="【全球首款可耐受1300℃高温的锂电池材料研发成功】财联社4月17日电，在4月初举行的第十四届储能国际峰会暨展览会上，南京工业大学教授沈晓冬团队展示的一款新材料，引发众人关注。这便是全球首款可耐受1300℃高温的新能源锂离子电池用高热阻气凝胶隔热片。“十五五”规划纲要提出，加快新能源、新材料等战略性新兴产业发展，这让沈晓冬对未来充满期待：“我们将加强基础研究和产业化进程，推动气凝胶隔热材料从新能源电池的‘高端选配’变为‘主流必配’，同时探索开拓其在消防、商业航天、太空算力等领域的应用，推动建立中国的气凝胶纳米材料产业体系。” (科技日报)",
            source="cls",
            published_at="2026-04-17T15:22:35+08:00",
            url="https://example.com/cls-science-feature-story",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-keep-company-product-progress",
            first_seen_at="2026-04-17T15:10:22+08:00",
            last_seen_at="2026-04-17T15:10:22+08:00",
            canonical_title="华荣股份：国内首创智能化防爆高压环网柜研制成功",
            summary="人民财讯4月17日电，从华荣股份了解到，公司面向海外高端市场，海洋油气钻井平台危险作业区定制研发的智能化防爆高压环网柜正式研制成功，目前已顺利进入IECEx/ATEX/CCC认证阶段。该产品为国内首创，填补了我国在海洋平台智能化防爆高压环网柜领域的技术空白。",
            source="stcn",
            published_at="2026-04-17T15:10:22+08:00",
            url="https://example.com/keep-company-product-progress",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-cls-science-feature-story", direction="neutral", impact_score=79.3, reasoning="rule", themes=["锂电池"], triggered=True),
        EventAnalysis(event_id="event-keep-company-product-progress", direction="neutral", impact_score=99.0, reasoning="rule", themes=["油气"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "全球首款可耐受1300℃高温的锂电池材料研发成功" not in content
    assert "华荣股份：国内首创智能化防爆高压环网柜研制成功" in content


def test_write_text_report_filters_current_live_asset_valuation_and_governance_material_without_hiding_real_disclosure(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-asset-valuation-report",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="东方雨虹：北京东方雨虹防水技术股份有限公司拟处置资产涉及的成都市金堂县格林雅苑四处房地产及无锡市锡山区美溪蓝庭一处房地产市场价值资产评估报告（中评正信评报字[2026]162号）",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/asset-valuation-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-governance-policy-material",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="*ST荣控：内部控制及风险管理制度",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/governance-policy-material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-disclosure",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="华测导航：关于开展供应链融资业务合作暨对外担保的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/keep-disclosure",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-asset-valuation-report", direction="neutral", impact_score=100.0, reasoning="rule", themes=["房地产"], triggered=True),
        EventAnalysis(event_id="event-governance-policy-material", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-disclosure", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "东方雨虹：北京东方雨虹防水技术股份有限公司拟处置资产涉及的成都市金堂县格林雅苑四处房地产及无锡市锡山区美溪蓝庭一处房地产市场价值资产评估报告" not in content
    assert "*ST荣控：内部控制及风险管理制度" not in content
    assert "华测导航：关于开展供应链融资业务合作暨对外担保的公告" in content


def test_write_text_report_filters_irm_cninfo_investor_complaint_and_shareholder_count_without_hiding_substantive_reply(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-shareholder-count",
            first_seen_at="2026-04-17T21:57:33+08:00",
            last_seen_at="2026-04-17T21:57:33+08:00",
            canonical_title="TCL中环：请问截止4月10日股东人数是多少？",
            summary="问题：请问截止4月10日股东人数是多少？\n回复：您好，截至3月31日，公司普通股股东总数约为28.9万，感谢您的关注！",
            source="irm_cninfo",
            published_at="2026-04-17T21:57:33+08:00",
            url="https://example.com/irm-shareholder-count",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-market-cap-complaint",
            first_seen_at="2026-04-17T21:54:03+08:00",
            last_seen_at="2026-04-17T21:54:03+08:00",
            canonical_title="TCL中环：尊敬的TCL中环管理层：当前公司股价持续承压，而隆基、爱旭等同行已通过积极举措带动股价回暖。股价关乎公司口碑、员工士气、市场形象、融资授信和政府观感，政府、银行和客户看到这种K线图，谁还愿意给低成本融资和长期订单？股价也是社会各界对管理层能力的直观评价。希望各位正视行业差距，拿出切实的市值管理行动，稳定投资者信心，跟上同行步伐。",
            summary="问题：当前公司股价持续承压，希望管理层拿出切实的市值管理行动。\n回复：公司会持续做好经营管理并加强沟通，感谢您的关注。",
            source="irm_cninfo",
            published_at="2026-04-17T21:54:03+08:00",
            url="https://example.com/irm-market-cap-complaint",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-keep-substantive-reply",
            first_seen_at="2026-04-17T21:47:03+08:00",
            last_seen_at="2026-04-17T21:47:03+08:00",
            canonical_title="TCL中环：董秘您好：公司拥有大量BC核心专利，但尚未形成规模化、高盈利的BC量产能力。请问当前BC技术在专利授权、技术合作、量产落地方面的真实进展如何？",
            summary="问题：请问当前BC技术在量产落地方面的真实进展如何？\n回复：公司已围绕BC技术完成多项专利布局，并推进重点客户验证与量产准备。",
            source="irm_cninfo",
            published_at="2026-04-17T21:47:03+08:00",
            url="https://example.com/irm-keep-substantive-reply",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-shareholder-count", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-market-cap-complaint", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-keep-substantive-reply", direction="bullish", impact_score=75.2, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "TCL中环：请问截止4月10日股东人数是多少？" not in content
    assert "当前公司股价持续承压" not in content
    assert "TCL中环：董秘您好：公司拥有大量BC核心专利" in content


def test_write_text_report_filters_irm_cninfo_theme_and_export_qa_without_hiding_substantive_progress(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-future-energy",
            first_seen_at="2026-04-20T22:42:33+08:00",
            last_seen_at="2026-04-20T22:42:33+08:00",
            canonical_title="迈为股份：十五五规划培育未来能源产业，公司作为新能源光伏公司领头企业，是否属于未来能源？",
            summary="问题：十五五规划培育未来能源产业，公司作为新能源光伏公司领头企业，是否属于未来能源？ 回复：投资者您好，光伏属于未来能源产业，且在 “十五五” 规划中被明确为构建新型能源体系的核心基底与主力电源，同时其前沿技术方向被列为未来能源重点培育领域，感谢您的关注！",
            source="irm_cninfo",
            published_at="2026-04-20T22:42:33+08:00",
            url="https://example.com/irm-future-energy",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-export-rumor",
            first_seen_at="2026-04-20T22:41:33+08:00",
            last_seen_at="2026-04-20T22:41:33+08:00",
            canonical_title="迈为股份：针对网络传言，光伏设备限制出口的小作文，请问公司有方面的信息吗，公司目前出口正常吗，比如出口美国设备有无被限制或者新前的订单出口设备有没有被限制暂停出口",
            summary="问题：针对网络传言，光伏设备限制出口的小作文，请问公司有方面的信息吗，公司目前出口正常吗，比如出口美国设备有无被限制或者新前的订单出口设备有没有被限制暂停出口 回复：投资者您好，公司主营业务产品太阳能电池丝网印刷设备、太阳能异质结电池整线设备，产品出口业务严格遵守国家相关法律法规及国际通行规则，感谢您的关注！",
            source="irm_cninfo",
            published_at="2026-04-20T22:41:33+08:00",
            url="https://example.com/irm-export-rumor",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-big-order",
            first_seen_at="2026-04-20T22:44:03+08:00",
            last_seen_at="2026-04-20T22:44:03+08:00",
            canonical_title="迈为股份：请问公司拟投资35亿元建设“钙钛矿叠层电池成套装备项目”。同时，控股子公司宸微设备拟投资15亿元建设“半导体装备研发制造项目”。是否2个事项都已有大订单，才实施此次投资，担忧公司投资步子跨太大，希望公司说说",
            summary="问题：请问公司拟投资35亿元建设“钙钛矿叠层电池成套装备项目”。同时，控股子公司宸微设备拟投资15亿元建设“半导体装备研发制造项目”。是否2个事项都已有大订单，才实施此次投资，担忧公司投资步子跨太大，希望公司说说 回复：投资者您好，公司坚定看好异质结钙钛矿叠层电池工艺的发展，钙钛矿/硅叠层电池依托我国成熟的晶硅光伏产业链，具备完善的产业配套，产业化落地条件完备，公司已于2025年12月签订业内首条钙钛矿/硅异质结叠层电池整线设备供应合同，标志着相关技术正式迈向产业化应用，目前项目正按计划稳步推进。在半导体领域，公司针对刻蚀、薄膜沉积及先进封装领域加速布局，推出了多种产品及成套解决方案，与头部客户建立了良好的合作关系。感谢您的关注！",
            source="irm_cninfo",
            published_at="2026-04-20T22:44:03+08:00",
            url="https://example.com/irm-big-order",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-keep-substantive-progress",
            first_seen_at="2026-04-20T22:40:03+08:00",
            last_seen_at="2026-04-20T22:40:03+08:00",
            canonical_title="某公司：产品在商业航天和卫星互联网方面市场拓展如何？",
            summary="问题：产品在商业航天和卫星互联网方面市场拓展如何？ 回复：您好！2026年以来，公司相关产品已完成多家商业航天客户送样验证，并取得批量订单，部分型号已进入卫星互联网配套供应链。",
            source="irm_cninfo",
            published_at="2026-04-20T22:40:03+08:00",
            url="https://example.com/irm-keep-substantive-progress",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-future-energy", direction="neutral", impact_score=100.0, reasoning="rule", themes=["电力资源"], triggered=True),
        EventAnalysis(event_id="event-irm-export-rumor", direction="bearish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-big-order", direction="bullish", impact_score=100.0, reasoning="rule", themes=["半导体"], triggered=True),
        EventAnalysis(event_id="event-irm-keep-substantive-progress", direction="bullish", impact_score=100.0, reasoning="rule", themes=["商业航天"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "是否属于未来能源" not in content
    assert "出口正常吗" not in content
    assert "是否2个事项都已有大订单" not in content
    assert "产品在商业航天和卫星互联网方面市场拓展如何" in content


def test_write_text_report_filters_irm_cninfo_generic_followup_and_no_impact_reply_without_hiding_substantive_reply(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-generic-followup",
            first_seen_at="2026-04-19T12:18:33+08:00",
            last_seen_at="2026-04-19T12:18:33+08:00",
            canonical_title="长春高新：公司管理层有没有思考过,贵公司和真正的创新药企业到底差在哪里？为什么荣昌生物和三生制药这种企业可以小投入换来大收获，而贵公司恰恰相反？",
            summary="问题：公司管理层有没有思考过,贵公司和真正的创新药企业到底差在哪里？为什么荣昌生物和三生制药这种企业可以小投入换来大收获，而贵公司恰恰相反？ 回复：您好，您所提的类似问题公司已经多次回复，具体请参见之前问题回复，谢谢！",
            source="irm_cninfo",
            published_at="2026-04-19T12:18:33+08:00",
            url="https://example.com/irm-generic-followup",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-no-impact-reply",
            first_seen_at="2026-04-19T09:34:03+08:00",
            last_seen_at="2026-04-19T09:34:03+08:00",
            canonical_title="长春高新：美国对进口创新药增收100％关税，请问对公司以后拓展美国市场有什么影响？谢谢",
            summary="问题：美国对进口创新药增收100％关税，请问对公司以后拓展美国市场有什么影响？谢谢 回复：您好，目前美国关税政策对公司业务无影响，谢谢！",
            source="irm_cninfo",
            published_at="2026-04-19T09:34:03+08:00",
            url="https://example.com/irm-no-impact-reply",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-keep-substantive-reply-2",
            first_seen_at="2026-04-19T09:20:00+08:00",
            last_seen_at="2026-04-19T09:20:00+08:00",
            canonical_title="长春高新：请问贵公司创新药海外授权推进进展如何？",
            summary="问题：请问贵公司创新药海外授权推进进展如何？ 回复：公司正推进多个海外商务合作项目，并与潜在合作方就授权方案持续沟通。",
            source="irm_cninfo",
            published_at="2026-04-19T09:20:00+08:00",
            url="https://example.com/irm-keep-substantive-reply-2",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-disclosure-fallback",
            first_seen_at="2026-04-19T09:32:33+08:00",
            last_seen_at="2026-04-19T09:32:33+08:00",
            canonical_title="长春高新：贵公司能不能尽快剥离房地产业务？给个时间表可以吗？",
            summary="问题：贵公司能不能尽快剥离房地产业务？给个时间表可以吗？ 回复：您好，如有达到信息披露标准的情况，公司会按照法律法规要求履行披露义务，谢谢！",
            source="irm_cninfo",
            published_at="2026-04-19T09:32:33+08:00",
            url="https://example.com/irm-disclosure-fallback",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-report-fallback",
            first_seen_at="2026-04-18T18:43:03+08:00",
            last_seen_at="2026-04-18T18:43:03+08:00",
            canonical_title="圣阳股份：贵公司是否有中东订单",
            summary="问题：贵公司是否有中东订单 回复：您好！有关公司业务及订单情况敬请关注公司定期报告。公司将于2026年4月24日披露2025年年度报告。感谢您的关注!",
            source="irm_cninfo",
            published_at="2026-04-18T18:43:03+08:00",
            url="https://example.com/irm-report-fallback",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-generic-followup", direction="neutral", impact_score=100.0, reasoning="rule", themes=["创新药"], triggered=True),
        EventAnalysis(event_id="event-irm-no-impact-reply", direction="neutral", impact_score=100.0, reasoning="rule", themes=["创新药"], triggered=True),
        EventAnalysis(event_id="event-irm-keep-substantive-reply-2", direction="bullish", impact_score=88.0, reasoning="rule", themes=["创新药"], triggered=True),
        EventAnalysis(event_id="event-irm-disclosure-fallback", direction="neutral", impact_score=100.0, reasoning="rule", themes=["房地产"], triggered=True),
        EventAnalysis(event_id="event-irm-report-fallback", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "公司管理层有没有思考过" not in content
    assert "美国对进口创新药增收100％关税" not in content
    assert "贵公司能不能尽快剥离房地产业务" not in content
    assert "贵公司是否有中东订单" not in content
    assert "长春高新：请问贵公司创新药海外授权推进进展如何？" in content


def test_write_text_report_filters_irm_cninfo_negative_project_reply_without_hiding_substantive_project_progress(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-negative-project-reply",
            first_seen_at="2026-04-20T19:46:33+08:00",
            last_seen_at="2026-04-20T19:46:33+08:00",
            canonical_title="震裕科技：贵公司在越南的机器人零部件生产工厂目前进展如何？一期二期预计产能多少？主要生产丝杠么？",
            summary="问题：贵公司在越南的机器人零部件生产工厂目前进展如何？一期二期预计产能多少？主要生产丝杠么？ 回复：您好，我司尚未在越南投资建设项目，感谢您的关注。",
            source="irm_cninfo",
            published_at="2026-04-20T19:46:33+08:00",
            url="https://example.com/irm-negative-project-reply",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-keep-project-progress",
            first_seen_at="2026-04-20T19:56:03+08:00",
            last_seen_at="2026-04-20T19:56:03+08:00",
            canonical_title="易普力：据三峡集团招标网公示，你公司是中标三峡水运新通道项目了吗？请介绍一下具体情况",
            summary="问题：据三峡集团招标网公示，你公司是中标三峡水运新通道项目了吗？请介绍一下具体情况 回复：您好！公司依托深厚的技术储备、丰富的施工经验和良好的属地口碑，在三峡水运新通道项目混装炸药及爆破作业服务集中采购项目第Ⅰ、Ⅱ标段场内、场外方案的中标候选人中均排第一。",
            source="irm_cninfo",
            published_at="2026-04-20T19:56:03+08:00",
            url="https://example.com/irm-keep-project-progress",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-negative-project-reply", direction="neutral", impact_score=100.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-irm-keep-project-progress", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "震裕科技：贵公司在越南的机器人零部件生产工厂目前进展如何？" not in content
    assert "易普力：据三峡集团招标网公示，你公司是中标三峡水运新通道项目了吗？请介绍一下具体情况" in content


def test_write_text_report_filters_irm_cninfo_weak_order_contract_and_market_move_replies_without_hiding_substantive_progress(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-order-contract-fallback",
            first_seen_at="2026-04-20T19:47:03+08:00",
            last_seen_at="2026-04-20T19:47:03+08:00",
            canonical_title="易普力：2026年3月，三峡招标网显示，葛洲坝中标三峡新航道施工准备试验工程（先行开挖区）， 金额：约 4.62 亿元，请问易普力是否已与葛洲坝签署分包合同？",
            summary="问题：2026年3月，三峡招标网显示，葛洲坝中标三峡新航道施工准备试验工程（先行开挖区）， 金额：约 4.62 亿元，请问易普力是否已与葛洲坝签署分包合同？ 回复：您好！具体中标情况请查询相关平台公示信息。公司将密切关注有关后续业务的进展。感谢您对公司的关注。",
            source="irm_cninfo",
            published_at="2026-04-20T19:47:03+08:00",
            url="https://example.com/irm-order-contract-fallback",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-market-move-fallback",
            first_seen_at="2026-04-20T19:59:33+08:00",
            last_seen_at="2026-04-20T19:59:33+08:00",
            canonical_title="易普力：2026年以来，硝酸铵价格大涨，每吨上涨800～1000元，相比广东宏大、雪峰科技，凯龙股份有自产硝酸铵的企业，对于纯外购的易普力而言，是一笔沉重的负担。一个连主要原材料都要外购，受制于成本，未构建全产业链的民爆企业，公司还认为是龙头企业吗？",
            summary="问题：2026年以来，硝酸铵价格大涨，每吨上涨800～1000元。 回复：您好！请查阅同类问题回复。感谢您对公司的关注。",
            source="irm_cninfo",
            published_at="2026-04-20T19:59:33+08:00",
            url="https://example.com/irm-market-move-fallback",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-irm-keep-order-progress",
            first_seen_at="2026-04-20T19:55:33+08:00",
            last_seen_at="2026-04-20T19:55:33+08:00",
            canonical_title="易普力：据三峡集团招标网公示，你公司是中标三峡水运新通道项目了吗？请介绍一下具体情况",
            summary="问题：据三峡集团招标网公示，你公司是中标三峡水运新通道项目了吗？请介绍一下具体情况 回复：您好！公司依托深厚的技术储备、丰富的施工经验和良好的属地口碑，在三峡水运新通道项目混装炸药及爆破作业服务集中采购项目第Ⅰ、Ⅱ标段场内、场外方案的中标候选人中均排第一。",
            source="irm_cninfo",
            published_at="2026-04-20T19:55:33+08:00",
            url="https://example.com/irm-keep-order-progress",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-keep-market-move-response",
            first_seen_at="2026-04-20T20:00:05+08:00",
            last_seen_at="2026-04-20T20:00:05+08:00",
            canonical_title="易普力：去年我多次建议公司，在硝酸铵价格低廉时，抓紧并购四川美丰，完善全产业链，请问面对硝酸铵价格大涨，公司如何应对？",
            summary="问题：面对硝酸铵价格大涨，公司如何应对？ 回复：您好！公司深化集团化采购信息联动机制，实施采购渠道集中管控，健全完善价格传导与库存调节机制，有效化解原材料价格上涨带来的挑战。",
            source="irm_cninfo",
            published_at="2026-04-20T20:00:05+08:00",
            url="https://example.com/irm-keep-market-move-response",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-irm-order-contract-rumor-no-reply-current",
            first_seen_at="2026-05-08T09:33:38+08:00",
            last_seen_at="2026-05-08T09:33:38+08:00",
            canonical_title="中超控股：董秘您好，请问网传中标国家管网集团2026年度电缆集约化采购项目8.79个亿是真的吗",
            summary="董秘您好，请问网传中标国家管网集团2026年度电缆集约化采购项目8.79个亿是真的吗",
            source="irm_cninfo",
            published_at="2026-05-08T09:33:38+08:00",
            url="https://example.com/irm-order-contract-rumor-no-reply-current",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-order-contract-fallback", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-market-move-fallback", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-keep-order-progress", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-keep-market-move-response", direction="bearish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-order-contract-rumor-no-reply-current", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "易普力是否已与葛洲坝签署分包合同" not in content
    assert "公司还认为是龙头企业吗？" not in content
    assert "网传中标国家管网集团2026年度电缆集约化采购项目8.79个亿是真的吗" not in content
    assert "易普力：据三峡集团招标网公示，你公司是中标三峡水运新通道项目了吗？请介绍一下具体情况" in content
    assert "易普力：去年我多次建议公司，在硝酸铵价格低廉时，抓紧并购四川美丰" in content


def test_write_text_report_filters_irm_cninfo_weak_theme_inquiry_replies_without_hiding_substantive_progress(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-humanoid-confidence-fallback",
            first_seen_at="2026-04-20T20:45:33+08:00",
            last_seen_at="2026-04-20T20:45:33+08:00",
            canonical_title="恒锋工具：董秘你好！1年前已经看到公司有在人形机器人用的行星减速器内齿轮刀具小批量出货的消息，公司现在还在小批量试样，还是有明显出货了?",
            summary="问题：公司现在还在小批量试样，还是有明显出货了? 回复：你好，公司高度关注人形机器人产业发展进程，在装备投资、技术人员储备上高度重视，对人形机器人产业的发展充满信心，感谢您的关注。",
            source="irm_cninfo",
            published_at="2026-04-20T20:45:33+08:00",
            url="https://example.com/irm-humanoid-confidence-fallback",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-robot-investment-fallback",
            first_seen_at="2026-04-20T20:45:33+08:00",
            last_seen_at="2026-04-20T20:45:33+08:00",
            canonical_title="远东传动：您好，公司对于现在机器人领域有没有参与投资？比如重型机器人之类",
            summary="问题：公司对于现在机器人领域有没有参与投资？ 回复：您好！公司将会持续关注机器人零部件领域的发展前景，向其行业内的优秀配套企业学习与合作，探索向高端装备领域传动部件转型的可能性，回报投资者的关切。谢谢！",
            source="irm_cninfo",
            published_at="2026-04-20T20:45:33+08:00",
            url="https://example.com/irm-robot-investment-fallback",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-stock-price-image-fallback",
            first_seen_at="2026-04-20T20:45:33+08:00",
            last_seen_at="2026-04-20T20:45:33+08:00",
            canonical_title="华伍股份：尊敬的董秘你好，公司是否有提升公司形象提振股价的计划？",
            summary="问题：公司是否有提升公司形象提振股价的计划？ 回复：您好！公司将继续坚持以投资者需求为导向，强化信息披露与投资者关系管理工作，通过多种渠道加强与市场的沟通交流，积极传递公司价值，努力维护公司资本市场形象。谢谢关注！",
            source="irm_cninfo",
            published_at="2026-04-20T20:45:33+08:00",
            url="https://example.com/irm-stock-price-image-fallback",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-report-calendar-fallback",
            first_seen_at="2026-04-20T20:45:33+08:00",
            last_seen_at="2026-04-20T20:45:33+08:00",
            canonical_title="ST恒信：平潭两岸融合智算中心项目一期已完工，目前是否有客户签约？算力出租率如何？",
            summary="问题：项目一期已完工，目前是否有客户签约？算力出租率如何？ 回复：尊敬的投资者您好，相关业务情况请关注公司即将披露的《2025年年度报告》，公司将严格按照信息披露相关规定，及时履行信息披露义务。感谢您对公司的关注。",
            source="irm_cninfo",
            published_at="2026-04-20T20:45:33+08:00",
            url="https://example.com/irm-report-calendar-fallback",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-future-layout-fallback",
            first_seen_at="2026-04-20T20:45:33+08:00",
            last_seen_at="2026-04-20T20:45:33+08:00",
            canonical_title="中青宝：贵公司未来会在内蒙、新疆大规模发展算力中心吗",
            summary="问题：贵公司未来会在内蒙、新疆大规模发展算力中心吗 回复：尊敬的投资者，感谢您对公司的关注。公司目前聚焦现有深圳、成都、乐山三大数据中心的运营与优化，密切关注国内其他地区的算力行业发展情况，未来若有相关业务布局规划，公司将严格按照法律法规履行信息披露义务，敬请以法定公告为准。",
            source="irm_cninfo",
            published_at="2026-04-20T20:45:33+08:00",
            url="https://example.com/irm-future-layout-fallback",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-compute-infra-fallback",
            first_seen_at="2026-04-21T09:09:33+08:00",
            last_seen_at="2026-04-21T09:09:33+08:00",
            canonical_title="中亦科技：你好董秘，中亦科技是否有算力基建吗？有是哪些简单说说，如果没有，后期会布局介入吗？谢谢",
            summary="问题：你好董秘，中亦科技是否有算力基建吗？有是哪些简单说说，如果没有，后期会布局介入吗？谢谢 回复：尊敬的投资者，感谢您的关注！公司是一家IT基础架构全栈式、全周期的“服务+产品”提供商，主营业务专注于IT基础架构层。公司面向客户数据中心，提供IT基础架构层从规划咨询、架构设计、集成实施、投产上线到运行维护的全周期服务，并以智能化的运维产品提升运维过程的自动化和智能化水平。公司密切关注与主营业务协同性强的产业机遇，围绕主营业务进行合理布局。",
            source="irm_cninfo",
            published_at="2026-04-21T09:09:33+08:00",
            url="https://example.com/irm-compute-infra-fallback",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-revenue-order-fallback",
            first_seen_at="2026-04-21T09:14:33+08:00",
            last_seen_at="2026-04-21T09:14:33+08:00",
            canonical_title="冰轮环境：董秘您好，公司核能业务营收大概有多少？在手订单大概有多少？",
            summary="问题：董秘您好，公司核能业务营收大概有多少？在手订单大概有多少？ 回复：您好，公司生产经营业务情况请关注公司定期报告和临时报告。感谢关注",
            source="irm_cninfo",
            published_at="2026-04-21T09:14:33+08:00",
            url="https://example.com/irm-revenue-order-fallback",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-h-share-equity-incentive-metric-fallback",
            first_seen_at="2026-05-09T10:48:33+08:00",
            last_seen_at="2026-05-09T10:48:33+08:00",
            canonical_title="京新药业：问吕董，如果公司H股上市那么公司股权激励后续条件如何变化，难道还是公司利润总额吗？还是每股利润增长每年不低于10%？",
            summary="问题：问吕董，如果公司H股上市那么公司股权激励后续条件如何变化，难道还是公司利润总额吗？还是每股利润增长每年不低于10%？ 回复：您好！公司的员工持股计划公司层面的业绩考核指标是以经审计的归属于上市公司股东的扣除非经常性损益后的净利润为计算依据，相关具体内容敬请查看相关公告。谢谢！",
            source="irm_cninfo",
            published_at="2026-05-09T10:48:33+08:00",
            url="https://example.com/irm-h-share-equity-incentive-metric-fallback",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-stock-price-project-fallback",
            first_seen_at="2026-04-21T09:13:33+08:00",
            last_seen_at="2026-04-21T09:13:33+08:00",
            canonical_title="中电港：美股存储公司大涨，国内龙头公司都在做加快发展，贵公司是英伟达、AMD的授权分销商之一，股价与业绩不对称，有瞄准市场机遇签订新项目么",
            summary="问题：美股存储公司大涨，国内龙头公司都在做加快发展，贵公司是英伟达、AMD的授权分销商之一，股价与业绩不对称，有瞄准市场机遇签订新项目么 回复：公司当前经营发展趋势向好，持续深化在关键应用领域的布局。具体业务情况请以公司披露的定期报告和临时公告为准。感谢您对公司的关注！",
            source="irm_cninfo",
            published_at="2026-04-21T09:13:33+08:00",
            url="https://example.com/irm-stock-price-project-fallback",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-irm-keep-substantive-theme-progress",
            first_seen_at="2026-04-20T20:46:03+08:00",
            last_seen_at="2026-04-20T20:46:03+08:00",
            canonical_title="久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？",
            summary="问题：公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？ 回复：您好！2026年以来，公司相关产品已完成多家商业航天客户送样验证，并取得批量订单，部分型号已进入卫星互联网配套供应链。",
            source="irm_cninfo",
            published_at="2026-04-20T20:46:03+08:00",
            url="https://example.com/irm-keep-substantive-theme-progress",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-generic-storage-theme-no-reply-current",
            first_seen_at="2026-05-08T10:01:50+08:00",
            last_seen_at="2026-05-08T10:01:50+08:00",
            canonical_title="青鸟智控：您好董秘，公司有涉及光伏储能相关业务吗？",
            summary="您好董秘，公司有涉及光伏储能相关业务吗？",
            source="irm_cninfo",
            published_at="2026-05-08T10:01:50+08:00",
            url="https://example.com/irm-generic-storage-theme-no-reply-current",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-jiantou-zhisuan-injection-no-info",
            first_seen_at="2026-05-09T14:52:33+08:00",
            last_seen_at="2026-05-09T14:52:33+08:00",
            canonical_title="建投能源：大股东建投集团有考虑将建投智算注入建投能源吗？",
            summary="问题：大股东建投集团有考虑将建投智算注入建投能源吗？ 回复：您好！公司未得到相关信息。",
            source="irm_cninfo",
            published_at="2026-05-09T14:52:33+08:00",
            url="https://example.com/irm-jiantou-zhisuan-injection-no-info",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-humanoid-confidence-fallback", direction="bullish", impact_score=100.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-irm-robot-investment-fallback", direction="bullish", impact_score=100.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-irm-stock-price-image-fallback", direction="bullish", impact_score=100.0, reasoning="rule", themes=["油气"], triggered=True),
        EventAnalysis(event_id="event-irm-report-calendar-fallback", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-future-layout-fallback", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-compute-infra-fallback", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-revenue-order-fallback", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-h-share-equity-incentive-metric-fallback", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-stock-price-project-fallback", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-keep-substantive-theme-progress", direction="bullish", impact_score=100.0, reasoning="rule", themes=["商业航天"], triggered=True),
        EventAnalysis(event_id="event-irm-generic-storage-theme-no-reply-current", direction="neutral", impact_score=100.0, reasoning="rule", themes=["储能"], triggered=True),
        EventAnalysis(event_id="event-irm-jiantou-zhisuan-injection-no-info", direction="neutral", impact_score=75.0, reasoning="rule", themes=["算力"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "恒锋工具：董秘你好！1年前已经看到公司有在人形机器人用的行星减速器内齿轮刀具小批量出货的消息" not in content
    assert "远东传动：您好，公司对于现在机器人领域有没有参与投资？比如重型机器人之类" not in content
    assert "华伍股份：尊敬的董秘你好，公司是否有提升公司形象提振股价的计划？" not in content
    assert "ST恒信：平潭两岸融合智算中心项目一期已完工，目前是否有客户签约？算力出租率如何？" not in content
    assert "中青宝：贵公司未来会在内蒙、新疆大规模发展算力中心吗" not in content
    assert "中亦科技：你好董秘，中亦科技是否有算力基建吗？有是哪些简单说说，如果没有，后期会布局介入吗？谢谢" not in content
    assert "冰轮环境：董秘您好，公司核能业务营收大概有多少？在手订单大概有多少？" not in content
    assert "公司H股上市那么公司股权激励后续条件如何变化" not in content
    assert "中电港：美股存储公司大涨，国内龙头公司都在做加快发展，贵公司是英伟达、AMD的授权分销商之一，股价与业绩不对称，有瞄准市场机遇签订新项目么" not in content
    assert "青鸟智控：您好董秘，公司有涉及光伏储能相关业务吗？" not in content
    assert "建投能源：大股东建投集团有考虑将建投智算注入建投能源吗？" not in content
    assert "久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？" in content


def test_write_text_report_filters_stcn_negative_platform_reply_without_hiding_robotaxi_launch(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-stcn-negative-platform-reply",
            first_seen_at="2026-04-21T08:55:09+08:00",
            last_seen_at="2026-04-21T08:55:09+08:00",
            canonical_title="国星光电：暂未参股CPO、存储芯片类科技公司",
            summary="人民财讯4月21日电，国星光电(002449)4月21日在互动平台表示，目前公司暂未参股CPO、存储芯片类科技公司。",
            source="stcn",
            published_at="2026-04-21T08:55:09+08:00",
            url="https://example.com/stcn-negative-platform-reply",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-stcn-negative-platform-vanadium-reply",
            first_seen_at="2026-05-01T21:12:17+08:00",
            last_seen_at="2026-05-01T21:12:17+08:00",
            canonical_title="安宁股份：目前公司未单独提取钒产品",
            summary="人民财讯5月1日电，安宁股份(002978)5月1日在互动平台表示，公司一直致力于钒钛磁铁矿的综合利用，在钒清洁提取以及钒电解液制备方面有一定的技术储备，但目前公司未单独提取钒产品。",
            source="stcn",
            published_at="2026-05-01T21:12:17+08:00",
            url="https://example.com/stcn-negative-platform-vanadium-reply",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-cls-robotaxi-launch-keep",
            first_seen_at="2026-04-21T08:44:12+08:00",
            last_seen_at="2026-04-21T08:44:12+08:00",
            canonical_title="吉利将于2026北京车展发布中国首台原生Robotaxi原型车",
            summary="【吉利将于2026北京车展发布中国首台原生Robotaxi原型车】财联社4月21日电，吉利汽车集团宣布，4月24日将以半包馆形式亮相2026北京国际车展。核心看点在于中国首台原生Robotaxi原型车首发。该车基于吉利L4级AI数字架构开发，融合WAM世界动作模型与L4级自动驾驶技术。",
            source="cls",
            published_at="2026-04-21T08:44:12+08:00",
            url="https://example.com/cls-robotaxi-launch-keep",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-stcn-negative-platform-reply", direction="neutral", impact_score=99.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-stcn-negative-platform-vanadium-reply", direction="neutral", impact_score=99.0, reasoning="rule", themes=["锂电池"], triggered=True),
        EventAnalysis(event_id="event-cls-robotaxi-launch-keep", direction="bullish", impact_score=99.3, reasoning="rule", themes=["算力"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "国星光电：暂未参股CPO、存储芯片类科技公司" not in content
    assert "安宁股份：目前公司未单独提取钒产品" not in content
    assert "吉利将于2026北京车展发布中国首台原生Robotaxi原型车" in content


def test_write_text_report_filters_current_live_irm_question_only_titles_without_hiding_substantive_progress(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-overseas-supply-question-only",
            first_seen_at="2026-04-21T10:49:36+08:00",
            last_seen_at="2026-04-21T10:49:36+08:00",
            canonical_title="新雷能：董秘好，请问公司的太空数据中心电源产品供应海外吗？请及时回复，谢谢。",
            summary="董秘好，请问公司的太空数据中心电源产品供应海外吗？请及时回复，谢谢。",
            source="irm_cninfo",
            published_at="2026-04-21T10:49:36+08:00",
            url="https://example.com/irm-overseas-supply-question-only",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-robot-application-question-only",
            first_seen_at="2026-04-21T10:49:36+08:00",
            last_seen_at="2026-04-21T10:49:36+08:00",
            canonical_title="山东威达：董秘你好:公司入股的知行机器人的产品具体应用在哪些行业？",
            summary="董秘你好:公司入股的知行机器人的产品具体应用在哪些行业？",
            source="irm_cninfo",
            published_at="2026-04-21T10:49:36+08:00",
            url="https://example.com/irm-robot-application-question-only",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-multi-question-shareholder-only",
            first_seen_at="2026-04-21T11:09:50+08:00",
            last_seen_at="2026-04-21T11:09:50+08:00",
            canonical_title="盛视科技：董秘您好，作为公司股东，想了解以下几个问题： 1. 公司对航天物联网的投资目前是否产生了投资收益？该投资对公司未来的业务布局和业绩增长有何预期贡献？ ​ 2. 商业航天是国家重点支持的战略新兴产业，公司作为AI和物联网领域的领先企业，是否有计划利用自身技术优势切入该赛道，培育新的业绩增长点？ ​ 3. 太空算力被认为是下一代算力的重要方向，公司在算力方面的布局是否会考虑向太空领",
            summary="董秘您好，作为公司股东，想了解以下几个问题： 1. 公司对航天物联网的投资目前是否产生了投资收益？该投资对公司未来的业务布局和业绩增长有何预期贡献？ ​ 2. 商业航天是国家重点支持的战略新兴产业，公司作为AI和物联网领域的领先企业，是否有计划利用自身技术优势切入该赛道，培育新的业绩增长点？ ​ 3. 太空算力被认为是下一代算力的重要方向，公司在算力方面的布局是否会考虑向太空领",
            source="irm_cninfo",
            published_at="2026-04-21T11:09:50+08:00",
            url="https://example.com/irm-multi-question-shareholder-only",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-disclosure-rule-question-only",
            first_seen_at="2026-04-21T11:09:50+08:00",
            last_seen_at="2026-04-21T11:09:50+08:00",
            canonical_title="常山药业：董秘你好！贵公司1类原研创新药阿贝那肽近日被国家医保局纳入第一批参照药预沟通药品名单，公示期已过，请问贵公司是否收到国家医保局的相关通知？此信息是否应该按规则进行披露？",
            summary="董秘你好！贵公司1类原研创新药阿贝那肽近日被国家医保局纳入第一批参照药预沟通药品名单，公示期已过，请问贵公司是否收到国家医保局的相关通知？此信息是否应该按规则进行披露？",
            source="irm_cninfo",
            published_at="2026-04-21T11:09:50+08:00",
            url="https://example.com/irm-disclosure-rule-question-only",
            event_type="fast_news",
            event_subtype="policy_signal",
        ),
        Event(
            event_id="event-irm-order-cut-question-only",
            first_seen_at="2026-04-30T19:19:29+08:00",
            last_seen_at="2026-04-30T19:19:29+08:00",
            canonical_title="华工科技：北美大客户（微软/Meta/英伟达）有没有砍单、转移订单？",
            summary="北美大客户（微软/Meta/英伟达）有没有砍单、转移订单？",
            source="irm_cninfo",
            published_at="2026-04-30T19:19:29+08:00",
            url="https://example.com/irm-order-cut-question-only",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-overseas-order-speed-question-only",
            first_seen_at="2026-04-30T19:17:29+08:00",
            last_seen_at="2026-04-30T19:17:29+08:00",
            canonical_title="华工科技：根据公开资料，2025年12月华工正源胡长飞经理表示26年国内订单有望翻倍，海外订单5-10倍增速，今年3月，胡长飞经理表示订单超预期，海外订单量是预期的两三倍，是否可以理解为，今年海外订单有望10-20倍增速？",
            summary="根据公开资料，2025年12月华工正源胡长飞经理表示26年国内订单有望翻倍，海外订单5-10倍增速，今年3月，胡长飞经理表示订单超预期，海外订单量是预期的两三倍，是否可以理解为，今年海外订单有望10-20倍增速？",
            source="irm_cninfo",
            published_at="2026-04-30T19:17:29+08:00",
            url="https://example.com/irm-overseas-order-speed-question-only",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-capacity-order-question-only",
            first_seen_at="2026-04-30T19:16:29+08:00",
            last_seen_at="2026-04-30T19:16:29+08:00",
            canonical_title="华工科技：董秘你好，公司春节宣传“订单排至Q4、满产”，与投资者关会数据产能利用数据矛盾。“订单排至Q4”是正式合同还是意向？当前真实产能利用率、交付率是多少？当前产能与在手订单缺口巨大，仍计划大幅扩产。请说明扩产必要性、资金来源、回报周期及产能消化计划，是否存在误导性宣传？",
            summary="董秘你好，公司春节宣传“订单排至Q4、满产”，与投资者关会数据产能利用数据矛盾。“订单排至Q4”是正式合同还是意向？当前真实产能利用率、交付率是多少？当前产能与在手订单缺口巨大，仍计划大幅扩产。请说明扩产必要性、资金来源、回报周期及产能消化计划，是否存在误导性宣传？",
            source="irm_cninfo",
            published_at="2026-04-30T19:16:29+08:00",
            url="https://example.com/irm-capacity-order-question-only",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-legal-disclosure-question-only",
            first_seen_at="2026-04-30T18:30:00+08:00",
            last_seen_at="2026-04-30T18:30:00+08:00",
            canonical_title="山石网科：董秘您好，请问公司对于未决诉讼事项的信息披露标准及会计处理政策是怎样的？对于已发生的劳动争议类案件，公司是否会按照监管规则履行相应的披露义务？",
            summary="董秘您好，请问公司对于未决诉讼事项的信息披露标准及会计处理政策是怎样的？对于已发生的劳动争议类案件，公司是否会按照监管规则履行相应的披露义务？",
            source="irm_cninfo",
            published_at="2026-04-30T18:30:00+08:00",
            url="https://example.com/irm-legal-disclosure-question-only",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-mna-question-only",
            first_seen_at="2026-04-30T20:46:32+08:00",
            last_seen_at="2026-04-30T20:46:32+08:00",
            canonical_title="优宁维：请问，贵公司一直宣称要并购重组抗体上下游应用公司？请问具体包括哪些行业范围？包括有创新药管线储备的公司吗？包含细胞免疫治疗，也就是CGT产业的公司吗？请耐心回答，谢谢！",
            summary="请问，贵公司一直宣称要并购重组抗体上下游应用公司？请问具体包括哪些行业范围？包括有创新药管线储备的公司吗？包含细胞免疫治疗，也就是CGT产业的公司吗？请耐心回答，谢谢！",
            source="irm_cninfo",
            published_at="2026-04-30T20:46:32+08:00",
            url="https://example.com/irm-mna-question-only",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-irm-robot-feature-question-only",
            first_seen_at="2026-04-30T20:46:32+08:00",
            last_seen_at="2026-04-30T20:46:32+08:00",
            canonical_title="华自科技：尊敬的董秘，请问公司得电力巡检机器人有哪些优势？可以实现什么样的功能",
            summary="尊敬的董秘，请问公司得电力巡检机器人有哪些优势？可以实现什么样的功能",
            source="irm_cninfo",
            published_at="2026-04-30T20:46:32+08:00",
            url="https://example.com/irm-robot-feature-question-only",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-robot-falsify-question-only",
            first_seen_at="2026-04-30T20:46:32+08:00",
            last_seen_at="2026-04-30T20:46:32+08:00",
            canonical_title="英力股份：市场对人形机器人业务多持观望态度。请公司给出一个明确的‘证伪指标’：未来12个月内，若机器人业务营收占比未达到5%，是否意味着本次转型失败，公司将回归传统制造主业？",
            summary="市场对人形机器人业务多持观望态度。请公司给出一个明确的‘证伪指标’：未来12个月内，若机器人业务营收占比未达到5%，是否意味着本次转型失败，公司将回归传统制造主业？",
            source="irm_cninfo",
            published_at="2026-04-30T20:46:32+08:00",
            url="https://example.com/irm-robot-falsify-question-only",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-earnings-multi-question-only",
            first_seen_at="2026-04-30T20:46:32+08:00",
            last_seen_at="2026-04-30T20:46:32+08:00",
            canonical_title="佐力药业：1. 新收资产组2026年一季度应收及净利润情况如何？是否符合公司收购前的预期？2. 公司一季度应收账款进一步增加，明显快于营收，是什么原因，影响如何？3. 乌灵胶囊增速明显放缓，什么原因？后三季度是否有改善预期？是否已到业务瓶颈期？4. 对26年全年的预期如何？能否维持25年的增速？",
            summary="1. 新收资产组2026年一季度应收及净利润情况如何？是否符合公司收购前的预期？2. 公司一季度应收账款进一步增加，明显快于营收，是什么原因，影响如何？3. 乌灵胶囊增速明显放缓，什么原因？后三季度是否有改善预期？是否已到业务瓶颈期？4. 对26年全年的预期如何？能否维持25年的增速？",
            source="irm_cninfo",
            published_at="2026-04-30T20:46:32+08:00",
            url="https://example.com/irm-earnings-multi-question-only",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-new-management-suggestion-only",
            first_seen_at="2026-04-30T20:46:32+08:00",
            last_seen_at="2026-04-30T20:46:32+08:00",
            canonical_title="思创智联：新领导层到位了.应该有新动作如回购股份、购买新资产以提高公司盈利模式",
            summary="新领导层到位了.应该有新动作如回购股份、购买新资产以提高公司盈利模式",
            source="irm_cninfo",
            published_at="2026-04-30T20:46:32+08:00",
            url="https://example.com/irm-new-management-suggestion-only",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-profit-placeholder-reply",
            first_seen_at="2026-04-30T19:31:33+08:00",
            last_seen_at="2026-04-30T19:31:33+08:00",
            canonical_title="华工科技：华工作为光模块最先进的公司，订单排满了全年，请问今年净利润能否到25亿？谢谢。",
            summary="问题：华工作为光模块最先进的公司，订单排满了全年，请问今年净利润能否到25亿？谢谢。 回复：投资者您好，公司业绩情况请以定期报告及相关公告为准，感谢您对公司的关注。",
            source="irm_cninfo",
            published_at="2026-04-30T19:31:33+08:00",
            url="https://example.com/irm-profit-placeholder-reply",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-fullkun-finance-question-only",
            first_seen_at="2026-04-30T22:59:30+08:00",
            last_seen_at="2026-04-30T22:59:30+08:00",
            canonical_title="满坤科技：请问2025年净利增长12%但经营现金流减半，存货库存量大增78%，是否预示销售受阻？募投项目达产后效益为负，为何仍计划发行7.6亿可转债？此外，股权激励费用冲回854万对当期利润影响多大？盼复，谢谢。",
            summary="请问2025年净利增长12%但经营现金流减半，存货库存量大增78%，是否预示销售受阻？募投项目达产后效益为负，为何仍计划发行7.6亿可转债？此外，股权激励费用冲回854万对当期利润影响多大？盼复，谢谢。",
            source="irm_cninfo",
            published_at="2026-04-30T22:59:30+08:00",
            url="https://example.com/irm-fullkun-finance-question-only",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-fensheng-valuation-question-only",
            first_seen_at="2026-05-01T00:36:19+08:00",
            last_seen_at="2026-05-01T00:36:19+08:00",
            canonical_title="分众传媒：最近二级市场连创新低，请问是公司出线了大问题还是什么原因？盘中大资金持续卖出，请公司详细介绍一下近期的经营情况？收购新潮是否会影响盈利？拉低公司的估值？还造成巨大的商誉？请董秘详细说明！",
            summary="最近二级市场连创新低，请问是公司出线了大问题还是什么原因？盘中大资金持续卖出，请公司详细介绍一下近期的经营情况？收购新潮是否会影响盈利？拉低公司的估值？还造成巨大的商誉？请董秘详细说明！",
            source="irm_cninfo",
            published_at="2026-05-01T00:36:19+08:00",
            url="https://example.com/irm-fensheng-valuation-question-only",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-zhongmi-revenue-drop-question-only",
            first_seen_at="2026-04-30T23:36:19+08:00",
            last_seen_at="2026-04-30T23:36:19+08:00",
            canonical_title="中密控股：公司一直说在手订单充足，但是26年1季度，营收同比下降是什么原因？",
            summary="公司一直说在手订单充足，但是26年1季度，营收同比下降是什么原因？",
            source="irm_cninfo",
            published_at="2026-04-30T23:36:19+08:00",
            url="https://example.com/irm-zhongmi-revenue-drop-question-only",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-zhongmi-wordgame-question-only",
            first_seen_at="2026-04-30T23:36:19+08:00",
            last_seen_at="2026-04-30T23:36:19+08:00",
            canonical_title="中密控股：打公司投资者电话回复25年股权激励达标，这是不是在和投资者玩文字游戏，公司年报的扣非净利润是3.661亿，按照这个数股权激励没有达标，而董秘和投资者电话中说已达标，扣非需要加上摊销费用，咱们股权激励草案可没说扣非加上摊销费用，如果已达标就请公司修改年报的扣非净利润，如果不修改就是糊弄投资者。变相给公司高管等人谋福利",
            summary="打公司投资者电话回复25年股权激励达标，这是不是在和投资者玩文字游戏，公司年报的扣非净利润是3.661亿，按照这个数股权激励没有达标，而董秘和投资者电话中说已达标，扣非需要加上摊销费用，咱们股权激励草案可没说扣非加上摊销费用，如果已达标就请公司修改年报的扣非净利润，如果不修改就是糊弄投资者。变相给公司高管等人谋福利",
            source="irm_cninfo",
            published_at="2026-04-30T23:36:19+08:00",
            url="https://example.com/irm-zhongmi-wordgame-question-only",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-zhongmi-target-gap-question-only",
            first_seen_at="2026-04-30T23:07:42+08:00",
            last_seen_at="2026-04-30T23:07:42+08:00",
            canonical_title="中密控股：你好，2025年年报中公司未来展望：2026年实现营收约18.2亿元，归属上市公司股东净利润约4.14亿元，剔除2024年限制性股票激励计划的股份支付摊销后，归属上市公司股东净利润4.43亿元。而2024年限制性股权激励方案，对归母净利润的考核是2021-2023年平均净利润3.15亿基数，增长45%即4.56亿元。为什么公司对未来的展望，2026年的净利润会低于股权激励的考核指标呢？",
            summary="你好，2025年年报中公司未来展望：2026年实现营收约18.2亿元，归属上市公司股东净利润约4.14亿元，剔除2024年限制性股票激励计划的股份支付摊销后，归属上市公司股东净利润4.43亿元。而2024年限制性股权激励方案，对归母净利润的考核是2021-2023年平均净利润3.15亿基数，增长45%即4.56亿元。为什么公司对未来的展望，2026年的净利润会低于股权激励的考核指标呢？",
            source="irm_cninfo",
            published_at="2026-04-30T23:07:42+08:00",
            url="https://example.com/irm-zhongmi-target-gap-question-only",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-stnengte-major-holder-increase-question-only",
            first_seen_at="2026-05-01T14:41:13+08:00",
            last_seen_at="2026-05-01T14:41:13+08:00",
            canonical_title="ST能特：大股东怎么不发增持消息。",
            summary="大股东怎么不发增持消息。",
            source="irm_cninfo",
            published_at="2026-05-01T14:41:13+08:00",
            url="https://example.com/irm-stnengte-major-holder-increase-question-only",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-stjingji-reduction-disclosure-question-only",
            first_seen_at="2026-05-01T14:41:13+08:00",
            last_seen_at="2026-05-01T14:41:13+08:00",
            canonical_title="ST京机：为什么第一季度京山京源持股数量减少，却没有发布减持公告",
            summary="为什么第一季度京山京源持股数量减少，却没有发布减持公告",
            source="irm_cninfo",
            published_at="2026-05-01T14:41:13+08:00",
            url="https://example.com/irm-stjingji-reduction-disclosure-question-only",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-yanhu-buyback-dividend-pressure-question-only",
            first_seen_at="2026-05-01T14:41:13+08:00",
            last_seen_at="2026-05-01T14:41:13+08:00",
            canonical_title="盐湖股份：优质公司普遍珍惜股权，通过回购增持、高分红回馈股东。反观公司，尽管业绩向好，却历史上面临银行，中化等股东持续减持，且连续多年未现金分红，令中小投资者对股权价值产生疑虑。请问公司：后续是否有具体计划（如加大回购注销力度、恢复分红政策）来对冲陕煤减持压力，并实质性提升股东回报？而非仅停留在“口头重视”层面。期待明确的时间表与量化目标。",
            summary="优质公司普遍珍惜股权，通过回购增持、高分红回馈股东。反观公司，尽管业绩向好，却历史上面临银行，中化等股东持续减持，且连续多年未现金分红，令中小投资者对股权价值产生疑虑。请问公司：后续是否有具体计划（如加大回购注销力度、恢复分红政策）来对冲陕煤减持压力，并实质性提升股东回报？而非仅停留在“口头重视”层面。期待明确的时间表与量化目标。",
            source="irm_cninfo",
            published_at="2026-05-01T14:41:13+08:00",
            url="https://example.com/irm-yanhu-buyback-dividend-pressure-question-only",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-genesis-robot-parts-question-only",
            first_seen_at="2026-05-01T15:43:17+08:00",
            last_seen_at="2026-05-01T15:43:17+08:00",
            canonical_title="创世纪：公司领导层重视机器人领域的发展嘛？在AI智能机床的深化改革发展中，机器人所需的减速器、行星滚柱丝杠、灵巧手等机器人产品零部件，公司后续是否会逐步投入研发和销售？",
            summary="公司领导层重视机器人领域的发展嘛？在AI智能机床的深化改革发展中，机器人所需的减速器、行星滚柱丝杠、灵巧手等机器人产品零部件，公司后续是否会逐步投入研发和销售？",
            source="irm_cninfo",
            published_at="2026-05-01T15:43:17+08:00",
            url="https://example.com/irm-genesis-robot-parts-question-only",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-jinshi-liquid-cooling-question-only",
            first_seen_at="2026-05-01T15:43:17+08:00",
            last_seen_at="2026-05-01T15:43:17+08:00",
            canonical_title="金时科技：董秘您好，作为股东，时刻关注着公司的成长与发展，请问公司在液冷服务器领域有什么产品布局？公司产品是否已经在液冷服务器方面有所应用？谢谢。",
            summary="董秘您好，作为股东，时刻关注着公司的成长与发展，请问公司在液冷服务器领域有什么产品布局？公司产品是否已经在液冷服务器方面有所应用？谢谢。",
            source="irm_cninfo",
            published_at="2026-05-01T15:43:17+08:00",
            url="https://example.com/irm-jinshi-liquid-cooling-question-only",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-sthuangting-reorg-semiconductor-question-only",
            first_seen_at="2026-05-01T15:43:17+08:00",
            last_seen_at="2026-05-01T15:43:17+08:00",
            canonical_title="*ST皇庭：公司有没可能通过重整引入有实力的半导体行业产业投资者和公司现有的半导体业务产生协同效应",
            summary="公司有没可能通过重整引入有实力的半导体行业产业投资者和公司现有的半导体业务产生协同效应",
            source="irm_cninfo",
            published_at="2026-05-01T15:43:17+08:00",
            url="https://example.com/irm-sthuangting-reorg-semiconductor-question-only",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-fujianjinsen-three-operations-question-only",
            first_seen_at="2026-05-01T19:51:40+08:00",
            last_seen_at="2026-05-01T19:51:40+08:00",
            canonical_title="福建金森：董秘好； 咨询三个公司运营情况，第一，公司林业碳汇推进多年，为何不见营收？是政策问题还是公司推进问题？第二，生物质燃料投产了没？与申能的战略合作是否稳步推进。第三，转接收金湖电力股份一事是否作罢？ 另外提供一个建议，林下经济难成规模，并且容易“林下黑”，建议放弃！ 祝好。",
            summary="董秘好； 咨询三个公司运营情况，第一，公司林业碳汇推进多年，为何不见营收？是政策问题还是公司推进问题？第二，生物质燃料投产了没？与申能的战略合作是否稳步推进。第三，转接收金湖电力股份一事是否作罢？ 另外提供一个建议，林下经济难成规模，并且容易“林下黑”，建议放弃！ 祝好。",
            source="irm_cninfo",
            published_at="2026-05-01T19:51:40+08:00",
            url="https://example.com/irm-fujianjinsen-three-operations-question-only",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-dongfangta-valuation-roadshow-question-only",
            first_seen_at="2026-05-01T20:24:34+08:00",
            last_seen_at="2026-05-01T20:24:34+08:00",
            canonical_title="东方钽业：目前资本市场仍把贵公司传统归类为小金属题材，并未充分认知公司在AI光模块、薄膜铌酸锂上游的核心龙头价值。公司后续是否计划举办专项路演、机构调研、价值宣讲，向市场充分介绍5N/6N高纯铌在TFLN、AI算力产业链的稀缺地位与成长前景，修复公司合理市值估值？",
            summary="目前资本市场仍把贵公司传统归类为小金属题材，并未充分认知公司在AI光模块、薄膜铌酸锂上游的核心龙头价值。公司后续是否计划举办专项路演、机构调研、价值宣讲，向市场充分介绍5N/6N高纯铌在TFLN、AI算力产业链的稀缺地位与成长前景，修复公司合理市值估值？",
            source="irm_cninfo",
            published_at="2026-05-01T20:24:34+08:00",
            url="https://example.com/irm-dongfangta-valuation-roadshow-question-only",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-xinyuguoke-space-order-question-only",
            first_seen_at="2026-05-07T21:33:20+08:00",
            last_seen_at="2026-05-07T21:33:20+08:00",
            canonical_title="新余国科：请问贵司在商业航天领域是否已经有订单？目前与哪些商业航天公司有合作？贵司自称点火装置可应用于商业航天领域，是否主动去寻找合作?",
            summary="请问贵司在商业航天领域是否已经有订单？目前与哪些商业航天公司有合作？贵司自称点火装置可应用于商业航天领域，是否主动去寻找合作?",
            source="irm_cninfo",
            published_at="2026-05-07T21:33:20+08:00",
            url="https://example.com/irm-xinyuguoke-space-order-question-only",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-huatian-huayi-supply-question-only",
            first_seen_at="2026-05-07T22:30:03+08:00",
            last_seen_at="2026-05-07T22:30:03+08:00",
            canonical_title="华天科技：你好董秘，贵公司收购的华羿微电有为安森美和意法半导体供货吗？",
            summary="问题：你好董秘，贵公司收购的华羿微电有为安森美和意法半导体供货吗？ 回复：华羿微电为安森美、意法半导体提供封测服务。谢谢！",
            source="irm_cninfo",
            published_at="2026-05-07T22:30:03+08:00",
            url="https://example.com/irm-huatian-huayi-supply-question-only",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-irm-huatian-huayi-sic-question-only",
            first_seen_at="2026-05-07T22:31:03+08:00",
            last_seen_at="2026-05-07T22:31:03+08:00",
            canonical_title="华天科技：你好董秘，贵公司收购的华羿微电有碳化硅SiC相关封测业务吗？",
            summary="问题：你好董秘，贵公司收购的华羿微电有碳化硅SiC相关封测业务吗？ 回复：有。谢谢！",
            source="irm_cninfo",
            published_at="2026-05-07T22:31:03+08:00",
            url="https://example.com/irm-huatian-huayi-sic-question-only",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-irm-sharetronic-compute-scale-question-only",
            first_seen_at="2026-05-07T22:17:03+08:00",
            last_seen_at="2026-05-07T22:17:03+08:00",
            canonical_title="协创数据：贵公司自有算力和在建算力有多少P？总共可调度算力有多少P？",
            summary="问题：贵公司自有算力和在建算力有多少P？总共可调度算力有多少P？ 回复：您好，公司正积极构建全球化算力网络，已在上海、宁波、成都、乌兰察布等国内核心节点及东南亚、美国等海外市场布局分布式算力资源，持续提升服务能力。感谢您的关注。",
            source="irm_cninfo",
            published_at="2026-05-07T22:17:03+08:00",
            url="https://example.com/irm-sharetronic-compute-scale-question-only",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-dongli-robot-reducer-question-only",
            first_seen_at="2026-05-07T21:33:20+08:00",
            last_seen_at="2026-05-07T21:33:20+08:00",
            canonical_title="东利机械：公司是否生产销售用于人形机器人的减速器",
            summary="公司是否生产销售用于人形机器人的减速器",
            source="irm_cninfo",
            published_at="2026-05-07T21:33:20+08:00",
            url="https://example.com/irm-dongli-robot-reducer-question-only",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-h-share-equity-incentive-question-only",
            first_seen_at="2026-05-09T11:09:52+08:00",
            last_seen_at="2026-05-09T11:09:52+08:00",
            canonical_title="京新药业：问吕董，如果公司H股上市那么公司股权激励后续条件如何变化，难道还是公司利润总额吗？还是每股利润增长每年不低于10%？",
            summary="问吕董，如果公司H股上市那么公司股权激励后续条件如何变化，难道还是公司利润总额吗？还是每股利润增长每年不低于10%？",
            source="irm_cninfo",
            published_at="2026-05-09T11:09:52+08:00",
            url="https://example.com/irm-h-share-equity-incentive-question-only",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-keep-substantive-progress",
            first_seen_at="2026-04-20T20:46:03+08:00",
            last_seen_at="2026-04-20T20:46:03+08:00",
            canonical_title="久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？",
            summary="问题：公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？ 回复：您好！2026年以来，公司相关产品已完成多家商业航天客户送样验证，并取得批量订单，部分型号已进入卫星互联网配套供应链。",
            source="irm_cninfo",
            published_at="2026-04-20T20:46:03+08:00",
            url="https://example.com/irm-keep-substantive-theme-progress",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-overseas-supply-question-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-robot-application-question-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-irm-multi-question-shareholder-only", direction="bullish", impact_score=100.0, reasoning="rule", themes=["算力", "商业航天"], triggered=True),
        EventAnalysis(event_id="event-irm-disclosure-rule-question-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["创新药"], triggered=True),
        EventAnalysis(event_id="event-irm-order-cut-question-only", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-overseas-order-speed-question-only", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-capacity-order-question-only", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-legal-disclosure-question-only", direction="bearish", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-mna-question-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["创新药"], triggered=True),
        EventAnalysis(event_id="event-irm-robot-feature-question-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-irm-robot-falsify-question-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-irm-earnings-multi-question-only", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-new-management-suggestion-only", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-profit-placeholder-reply", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-fullkun-finance-question-only", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-fensheng-valuation-question-only", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-zhongmi-revenue-drop-question-only", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-zhongmi-wordgame-question-only", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-zhongmi-target-gap-question-only", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-stnengte-major-holder-increase-question-only", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-stjingji-reduction-disclosure-question-only", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-yanhu-buyback-dividend-pressure-question-only", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-genesis-robot-parts-question-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-irm-jinshi-liquid-cooling-question-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-sthuangting-reorg-semiconductor-question-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["半导体"], triggered=True),
        EventAnalysis(event_id="event-irm-fujianjinsen-three-operations-question-only", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-dongfangta-valuation-roadshow-question-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-xinyuguoke-space-order-question-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["商业航天"], triggered=True),
        EventAnalysis(event_id="event-irm-huatian-huayi-supply-question-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["半导体"], triggered=True),
        EventAnalysis(event_id="event-irm-huatian-huayi-sic-question-only", direction="neutral", impact_score=75.2, reasoning="rule", themes=["半导体"], triggered=True),
        EventAnalysis(event_id="event-irm-sharetronic-compute-scale-question-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-dongli-robot-reducer-question-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-irm-h-share-equity-incentive-question-only", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-keep-substantive-progress", direction="bullish", impact_score=100.0, reasoning="rule", themes=["商业航天"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "新雷能：董秘好，请问公司的太空数据中心电源产品供应海外吗？请及时回复，谢谢。" not in content
    assert "山东威达：董秘你好:公司入股的知行机器人的产品具体应用在哪些行业？" not in content
    assert "盛视科技：董秘您好，作为公司股东，想了解以下几个问题" not in content
    assert "常山药业：董秘你好！贵公司1类原研创新药阿贝那肽近日被国家医保局纳入第一批参照药预沟通药品名单" not in content
    assert "华工科技：北美大客户（微软/Meta/英伟达）有没有砍单、转移订单？" not in content
    assert "华工科技：根据公开资料，2025年12月华工正源胡长飞经理表示26年国内订单有望翻倍" not in content
    assert "华工科技：董秘你好，公司春节宣传“订单排至Q4、满产”" not in content
    assert "山石网科：董秘您好，请问公司对于未决诉讼事项的信息披露标准及会计处理政策是怎样的？" not in content
    assert "优宁维：请问，贵公司一直宣称要并购重组抗体上下游应用公司？" not in content
    assert "华自科技：尊敬的董秘，请问公司得电力巡检机器人有哪些优势？" not in content
    assert "英力股份：市场对人形机器人业务多持观望态度。请公司给出一个明确的‘证伪指标’" not in content
    assert "佐力药业：1. 新收资产组2026年一季度应收及净利润情况如何？" not in content
    assert "思创智联：新领导层到位了.应该有新动作如回购股份、购买新资产以提高公司盈利模式" not in content
    assert "华工科技：华工作为光模块最先进的公司，订单排满了全年，请问今年净利润能否到25亿？谢谢。" not in content
    assert "满坤科技：请问2025年净利增长12%但经营现金流减半" not in content
    assert "分众传媒：最近二级市场连创新低，请问是公司出线了大问题还是什么原因？" not in content
    assert "中密控股：公司一直说在手订单充足，但是26年1季度，营收同比下降是什么原因？" not in content
    assert "中密控股：打公司投资者电话回复25年股权激励达标" not in content
    assert "中密控股：你好，2025年年报中公司未来展望" not in content
    assert "ST能特：大股东怎么不发增持消息。" not in content
    assert "ST京机：为什么第一季度京山京源持股数量减少，却没有发布减持公告" not in content
    assert "盐湖股份：优质公司普遍珍惜股权，通过回购增持、高分红回馈股东。" not in content
    assert "创世纪：公司领导层重视机器人领域的发展嘛？" not in content
    assert "金时科技：董秘您好，作为股东，时刻关注着公司的成长与发展，请问公司在液冷服务器领域有什么产品布局？" not in content
    assert "*ST皇庭：公司有没可能通过重整引入有实力的半导体行业产业投资者" not in content
    assert "福建金森：董秘好； 咨询三个公司运营情况，第一，公司林业碳汇推进多年" not in content
    assert "东方钽业：目前资本市场仍把贵公司传统归类为小金属题材" not in content
    assert "新余国科：请问贵司在商业航天领域是否已经有订单？" not in content
    assert "华天科技：你好董秘，贵公司收购的华羿微电有为安森美和意法半导体供货吗？" not in content
    assert "华天科技：你好董秘，贵公司收购的华羿微电有碳化硅SiC相关封测业务吗？" not in content
    assert "协创数据：贵公司自有算力和在建算力有多少P？总共可调度算力有多少P？" not in content
    assert "东利机械：公司是否生产销售用于人形机器人的减速器" not in content
    assert "京新药业：问吕董，如果公司H股上市那么公司股权激励后续条件如何变化" not in content
    assert "久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？" in content


def test_write_text_report_filters_current_live_irm_weak_replies_without_hiding_substantive_progress(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-ai-subsidiary-scope-intro",
            first_seen_at="2026-04-21T11:45:33+08:00",
            last_seen_at="2026-04-21T11:45:33+08:00",
            canonical_title="协创数据：看到公司资讯成立了词元智算科技公司含AI业务是公司准备做什么？",
            summary="问题：看到公司资讯成立了词元智算科技公司含AI业务是公司准备做什么？ 回复：您好，公司新设立控股子公司天津词元智算科技有限公司，主要经营范围为数据处理服务；计算机软硬件及辅助设备零售，软件销售；信息安全设备销售，云计算设备销售，人工智能应用软件开发；网络与信息安全软件开发，软件开发等。感谢您的关注。",
            source="irm_cninfo",
            published_at="2026-04-21T11:45:33+08:00",
            url="https://example.com/irm-ai-subsidiary-scope-intro",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-order-plenty-report-later",
            first_seen_at="2026-04-21T11:45:33+08:00",
            last_seen_at="2026-04-21T11:45:33+08:00",
            canonical_title="协创数据：你好，本人非常认同协创耿总的战略眼光，多方面的布局算力中心赛道，那么协创目前在手还未交付的算力规模还有多少。谢谢",
            summary="问题：你好，本人非常认同协创耿总的战略眼光，多方面的布局算力中心赛道，那么协创目前在手还未交付的算力规模还有多少。谢谢 回复：您好，公司坚定看好AI算力市场的长期发展，2026年将持续加大算力业务投入，巩固公司云算力服务的核心竞争力，目前公司在手订单充裕，交付有序进行。具体经营情况届时详见后续定期报告及相关公告。感谢您的关注。",
            source="irm_cninfo",
            published_at="2026-04-21T11:45:33+08:00",
            url="https://example.com/irm-order-plenty-report-later",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-no-undisclosed-restructuring",
            first_seen_at="2026-04-21T11:45:33+08:00",
            last_seen_at="2026-04-21T11:45:33+08:00",
            canonical_title="协鑫集成：董秘您好！公司2026年中标华电68亿大单、业绩扭亏，基本面全面反转 。但控股股东协鑫集团高比例质押问题仍制约估值。 请问：集团是否计划通过资产注入（优质光伏/储能/钙钛矿资产）、引入战略投资者、或重组方式降低质押、优化上市公司资产负债表？ 是否存在应披露未披露的重大资产重组、资产注入安排？请正面回应市场对价值重估、解决质押的核心关切。",
            summary="问题：董秘您好！公司2026年中标华电68亿大单、业绩扭亏，基本面全面反转 。但控股股东协鑫集团高比例质押问题仍制约估值。 请问：集团是否计划通过资产注入（优质光伏/储能/钙钛矿资产）、引入战略投资者、或重组方式降低质押、优化上市公司资产负债表？ 是否存在应披露未披露的重大资产重组、资产注入安排？请正面回应市场对价值重估、解决质押的核心关切。 回复：尊敬的投资者您好，公司不存在应披露而未披露的事项，感谢您的关注。",
            source="irm_cninfo",
            published_at="2026-04-21T11:45:33+08:00",
            url="https://example.com/irm-no-undisclosed-restructuring",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-prudent-study-order-loss-risk",
            first_seen_at="2026-04-21T11:45:03+08:00",
            last_seen_at="2026-04-21T11:45:03+08:00",
            canonical_title="通化金马：目前行业内在仲丁基锂连续流规模化生产上已出现明显技术领先企业，该技术直接决定高难度创新药分子的可开发性与商业化效率。请问公司是否掌握相关核心工艺？有无具体项目案例、产能规模及客户验证？若存在明显技术代差，将如何应对高端订单流失的风险？",
            summary="问题：目前行业内在仲丁基锂连续流规模化生产上已出现明显技术领先企业，该技术直接决定高难度创新药分子的可开发性与商业化效率。请问公司是否掌握相关核心工艺？有无具体项目案例、产能规模及客户验证？若存在明显技术代差，将如何应对高端订单流失的风险？ 回复：您好，公司密切关注行业前沿技术的发展动态，根据市场需求，结合自身情况，审慎论证。",
            source="irm_cninfo",
            published_at="2026-04-21T11:45:03+08:00",
            url="https://example.com/irm-prudent-study-order-loss-risk",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-ma-direction-disclosure-only",
            first_seen_at="2026-04-21T11:45:03+08:00",
            last_seen_at="2026-04-21T11:45:03+08:00",
            canonical_title="宏明电子：恭喜公司成功上市，请问管理层对公司未来做大做强有哪些举措？就目前公司的产品涉及各种产业链来说，贵司未来有哪些方向的并购或收购方向？目前光通信，算力，存储芯片，半导体等产业链非常火爆，期待贵司能找准这些火爆热门方向做大做强。",
            summary="问题：恭喜公司成功上市，请问管理层对公司未来做大做强有哪些举措？就目前公司的产品涉及各种产业链来说，贵司未来有哪些方向的并购或收购方向？目前光通信，算力，存储芯片，半导体等产业链非常火爆，期待贵司能找准这些火爆热门方向做大做强。 回复：尊敬的投资者，您好！公司坚守“做电子元件先锋、铸国防工业基石”的使命，实施“一干多枝、枝繁叶茂”经营战略，聚焦高可靠电子元器件与精密零组件主业，通过技术创新、产能扩张、市场拓展与数字化升级持续做强做优、高质量发展；公司如有并购、收购等相关信息，将严格按照规定履行信息披露义务。感谢您的关注！",
            source="irm_cninfo",
            published_at="2026-04-21T11:45:03+08:00",
            url="https://example.com/irm-ma-direction-disclosure-only",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-irm-small-batch-low-revenue-risk-note",
            first_seen_at="2026-04-21T11:45:03+08:00",
            last_seen_at="2026-04-21T11:45:03+08:00",
            canonical_title="宏明电子：请问贵公司和华为算力服务器相关产品的合作进展如何？是否有形成订单批量供货？",
            summary="问题：请问贵公司和华为算力服务器相关产品的合作进展如何？是否有形成订单批量供货？ 回复：尊敬的投资者，您好！公司算力服务器领域结构件产品已向上述客户送样合格，开始小批量供货。但目前公司在该领域相关业务收入在公司整体营业收入中占比较小。敬请投资者理性判断，注意投资风险。感谢您的关注！",
            source="irm_cninfo",
            published_at="2026-04-21T11:45:03+08:00",
            url="https://example.com/irm-small-batch-low-revenue-risk-note",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-share-reduction-pre-disclosure-rule",
            first_seen_at="2026-04-21T11:45:33+08:00",
            last_seen_at="2026-04-21T11:45:33+08:00",
            canonical_title="大华股份：请问中国移动所持公司股份已经解禁上市流通，因为是特定对象增发，减持是不是不需要提前发预告？",
            summary="问题：请问中国移动所持公司股份已经解禁上市流通，因为是特定对象增发，减持是不是不需要提前发预告？ 回复：尊敬的投资者，您好！中国移动目前持股超过5%，其减持需要按照相关法律法规预披露，感谢您的关注！",
            source="irm_cninfo",
            published_at="2026-04-21T11:45:33+08:00",
            url="https://example.com/irm-share-reduction-pre-disclosure-rule",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-buyback-request-dividend-reply",
            first_seen_at="2026-04-21T11:45:33+08:00",
            last_seen_at="2026-04-21T11:45:33+08:00",
            canonical_title="海康威视：董秘，你好，公司股价四五年低位横盘，请公司继续回购股份，谢谢",
            summary="问题：董秘，你好，公司股价四五年低位横盘，请公司继续回购股份，谢谢 回复：您好，公司高度重视股东回报，致力于保持并提升股东回报水平，同时增加分红频次，提升股东获得感，谢谢。2025年10月，公司派发2025年半年度现金分红。2026年4月，公司披露2025年度利润分配方案。2025年9月，公司注销完成了以集中竞价交易方式回购的股份6,833万股。",
            source="irm_cninfo",
            published_at="2026-04-21T11:45:33+08:00",
            url="https://example.com/irm-buyback-request-dividend-reply",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-fixed-increase-normal-progress",
            first_seen_at="2026-04-21T11:45:03+08:00",
            last_seen_at="2026-04-21T11:45:03+08:00",
            canonical_title="茂化实华：定增失败了嘛？定增失败了嘛？定增失败了嘛？公司是否考虑增持自家股票？",
            summary="问题：定增失败了嘛？定增失败了嘛？定增失败了嘛？公司是否考虑增持自家股票？ 回复：尊敬的投资者：您好！目前公司定增工作正常进行中，请留意公司后续相关报告。感谢您的关注！谢谢！",
            source="irm_cninfo",
            published_at="2026-04-21T11:45:03+08:00",
            url="https://example.com/irm-fixed-increase-normal-progress",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-boya-weak-reply",
            first_seen_at="2026-05-09T14:12:33+08:00",
            last_seen_at="2026-05-09T14:12:33+08:00",
            canonical_title="博雅生物：请问贵司在收购博雅生物之后为什么业绩大不如前，股价也一路走低，有没有采取切实可行的措施提升公司业绩，提振股民信心，大家对贵司的期望很大，希望别让大家失望！",
            summary="问题：请问贵司在收购博雅生物之后为什么业绩大不如前，股价也一路走低，有没有采取切实可行的措施提升公司业绩，提振股民信心，大家对贵司的期望很大，希望别让大家失望！ 回复：您好，感谢您对本公司的关注。面对血液制品行业深度调整与转型压力，公司将始终围绕战略目标，持续深耕血液制品主业，多措并举夯实发展根基，聚焦血浆、营销、研发、国际化等核心业务领域，持续蓄力厚植增长动能，提升综合竞争力。",
            source="irm_cninfo",
            published_at="2026-05-09T14:12:33+08:00",
            url="https://example.com/irm-boya-weak-reply",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-focus-media-report-fallback",
            first_seen_at="2026-05-01T00:03:33+08:00",
            last_seen_at="2026-05-01T00:03:33+08:00",
            canonical_title="分众传媒：最近二级市场连创新低，请问是公司出线了大问题还是什么原因？盘中大资金持续卖出，请公司详细介绍一下近期的经营情况？收购新潮是否会影响盈利？拉低公司的估值？还造成巨大的商誉？请董秘详细说明！",
            summary="问题：最近二级市场连创新低，请问是公司出线了大问题还是什么原因？盘中大资金持续卖出，请公司详细介绍一下近期的经营情况？收购新潮是否会影响盈利？拉低公司的估值？还造成巨大的商誉？请董秘详细说明！ 回复：您好，公司最新的经营情况烦请参考公司于4月29日披露的定期报告，感谢您的关注。",
            source="irm_cninfo",
            published_at="2026-05-01T00:03:33+08:00",
            url="https://example.com/irm-focus-media-report-fallback",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-zhongmi-target-gap-fallback",
            first_seen_at="2026-04-30T23:00:33+08:00",
            last_seen_at="2026-04-30T23:00:33+08:00",
            canonical_title="中密控股：你好，2025年年报中公司未来展望：2026年实现营收约18.2亿元，归属上市公司股东净利润约4.14亿元，剔除2024年限制性股票激励计划的股份支付摊销后，归属上市公司股东净利润4.43亿元。而2024年限制性股权激励方案，对归母净利润的考核是2021-2023年平均净利润3.15亿基数，增长45%即4.56亿元。为什么公司对未来的展望，2026年的净利润会低于股权激励的考核指标呢？",
            summary="问题：你好，2025年年报中公司未来展望：2026年实现营收约18.2亿元，归属上市公司股东净利润约4.14亿元，剔除2024年限制性股票激励计划的股份支付摊销后，归属上市公司股东净利润4.43亿元。而2024年限制性股权激励方案，对归母净利润的考核是2021-2023年平均净利润3.15亿基数，增长45%即4.56亿元。为什么公司对未来的展望，2026年的净利润会低于股权激励的考核指标呢？ 回复：投资者你好，公司《2024年限制性股票激励计划（草案）》（以下简称“《草案》”）中规定考核的“净利润”指归属于母公司扣除非经常性损益后的净利润（以下简称“归母扣非净利润”），该内容在《草案》是明确写出的，具体请查阅公司披露在巨潮资讯网的《草案》。 根据《草案》的规定，第三个解除限售期解除限售的归母扣非净利润考核目标为：以 2021年-2023 年三年归母扣非净利润的平均值为基数，2026 年归母扣非净利润的增长率不低于 45%（约41,435万元）。考核期内，前述归母扣非净利润计算时需剔除有效期内正在实施的所有股权激励计划和员工持股计划所涉股份支付费用影响的数值。 另外，公司2025年度报告中未来展望章节所述经营目标提到的是归母净利润，并非归母扣非净利润，年报中的经营目标不能与《草案》中的考核目标直接比较。",
            source="irm_cninfo",
            published_at="2026-04-30T23:00:33+08:00",
            url="https://example.com/irm-zhongmi-target-gap-fallback",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-zhongmi-incentive-wordgame-fallback",
            first_seen_at="2026-04-30T22:58:33+08:00",
            last_seen_at="2026-04-30T22:58:33+08:00",
            canonical_title="中密控股：打公司投资者电话回复25年股权激励达标，这是不是在和投资者玩文字游戏，公司年报的扣非净利润是3.661亿，按照这个数股权激励没有达标，而董秘和投资者电话中说已达标，扣非需要加上摊销费用，咱们股权激励草案可没说扣非加上摊销费用，如果已达标就请公司修改年报的扣非净利润，如果不修改就是糊弄投资者。变相给公司高管等人谋福利",
            summary="问题：打公司投资者电话回复25年股权激励达标，这是不是在和投资者玩文字游戏，公司年报的扣非净利润是3.661亿，按照这个数股权激励没有达标，而董秘和投资者电话中说已达标，扣非需要加上摊销费用，咱们股权激励草案可没说扣非加上摊销费用，如果已达标就请公司修改年报的扣非净利润，如果不修改就是糊弄投资者。变相给公司高管等人谋福利 回复：投资者你好，公司《2024年限制性股票激励计划（草案）》（以下简称“《草案》”）中明确写出“考核期内，以上扣非归母净利润计算时需剔除有效期内正在实施的所有股权激励计划和员 工持股计划所涉股份支付费用影响的数值。”具体请查阅公司披露在巨潮资讯网的《草案》。",
            source="irm_cninfo",
            published_at="2026-04-30T22:58:33+08:00",
            url="https://example.com/irm-zhongmi-incentive-wordgame-fallback",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-zhongmi-revenue-drop-fallback",
            first_seen_at="2026-04-30T23:01:33+08:00",
            last_seen_at="2026-04-30T23:01:33+08:00",
            canonical_title="中密控股：公司一直说在手订单充足，但是26年1季度，营收同比下降是什么原因？",
            summary="问题：公司一直说在手订单充足，但是26年1季度，营收同比下降是什么原因？ 回复：投资者你好，2026年一季度，公司实现营业收入39,797万元，较去年同期下降3.05%，略有减少。主要受行业竞争加剧与毛利率较低的增量业务占比同比提升双重影响。",
            source="irm_cninfo",
            published_at="2026-04-30T23:01:33+08:00",
            url="https://example.com/irm-zhongmi-revenue-drop-fallback",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-keep-substantive-progress-live",
            first_seen_at="2026-04-20T20:46:03+08:00",
            last_seen_at="2026-04-20T20:46:03+08:00",
            canonical_title="久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？",
            summary="问题：公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？ 回复：您好！2026年以来，公司相关产品已完成多家商业航天客户送样验证，并取得批量订单，部分型号已进入卫星互联网配套供应链。",
            source="irm_cninfo",
            published_at="2026-04-20T20:46:03+08:00",
            url="https://example.com/irm-keep-substantive-progress-live",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-ai-subsidiary-scope-intro", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-order-plenty-report-later", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-no-undisclosed-restructuring", direction="neutral", impact_score=100.0, reasoning="rule", themes=["储能"], triggered=True),
        EventAnalysis(event_id="event-irm-prudent-study-order-loss-risk", direction="bearish", impact_score=100.0, reasoning="rule", themes=["创新药"], triggered=True),
        EventAnalysis(event_id="event-irm-ma-direction-disclosure-only", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力", "半导体"], triggered=True),
        EventAnalysis(event_id="event-irm-small-batch-low-revenue-risk-note", direction="bearish", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-share-reduction-pre-disclosure-rule", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-buyback-request-dividend-reply", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-fixed-increase-normal-progress", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-boya-weak-reply", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-focus-media-report-fallback", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-zhongmi-target-gap-fallback", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-zhongmi-incentive-wordgame-fallback", direction="bearish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-zhongmi-revenue-drop-fallback", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-keep-substantive-progress-live", direction="bullish", impact_score=100.0, reasoning="rule", themes=["商业航天"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "协创数据：看到公司资讯成立了词元智算科技公司含AI业务是公司准备做什么？" not in content
    assert "协创数据：你好，本人非常认同协创耿总的战略眼光，多方面的布局算力中心赛道，那么协创目前在手还未交付的算力规模还有多少。谢谢" not in content
    assert "协鑫集成：董秘您好！公司2026年中标华电68亿大单、业绩扭亏，基本面全面反转" not in content
    assert "通化金马：目前行业内在仲丁基锂连续流规模化生产上已出现明显技术领先企业" not in content
    assert "宏明电子：恭喜公司成功上市，请问管理层对公司未来做大做强有哪些举措？" not in content
    assert "宏明电子：请问贵公司和华为算力服务器相关产品的合作进展如何？是否有形成订单批量供货？" not in content
    assert "大华股份：请问中国移动所持公司股份已经解禁上市流通，因为是特定对象增发，减持是不是不需要提前发预告？" not in content
    assert "海康威视：董秘，你好，公司股价四五年低位横盘，请公司继续回购股份，谢谢" not in content
    assert "茂化实华：定增失败了嘛？定增失败了嘛？定增失败了嘛？公司是否考虑增持自家股票？" not in content
    assert "博雅生物：请问贵司在收购博雅生物之后为什么业绩大不如前，股价也一路走低" not in content
    assert "分众传媒：最近二级市场连创新低，请问是公司出线了大问题还是什么原因？" not in content
    assert "中密控股：你好，2025年年报中公司未来展望" not in content
    assert "中密控股：打公司投资者电话回复25年股权激励达标" not in content
    assert "中密控股：公司一直说在手订单充足，但是26年1季度，营收同比下降是什么原因？" not in content
    assert "久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？" in content


def test_write_text_report_filters_irm_cninfo_disclosure_threshold_and_low_revenue_replies_without_hiding_substantive_progress(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-disclosure-threshold-fallback",
            first_seen_at="2026-04-20T20:45:33+08:00",
            last_seen_at="2026-04-20T20:45:33+08:00",
            canonical_title="*ST中地：您好董秘，公司年报说中标宁夏中交云数据中心，武汉环贸数据中心，乌兰察布数据中心等运营项目，为什么没发公告呢？是公司独立中标还是中交集团联合中标？公司有运营数据中心的能力吗？",
            summary="问题：为什么没发公告？公司有运营数据中心的能力吗？ 回复：您好，上述轻资产服务业务未达到披露标准，公司系独立中标，具备相关运营能力。谢谢关注！",
            source="irm_cninfo",
            published_at="2026-04-20T20:45:33+08:00",
            url="https://example.com/irm-disclosure-threshold-fallback",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-low-revenue-ratio-fallback",
            first_seen_at="2026-04-20T20:45:33+08:00",
            last_seen_at="2026-04-20T20:45:33+08:00",
            canonical_title="濮阳惠成：公司的联营企业是否提供商业航天火箭精密器件解决方案？",
            summary="问题：公司的联营企业是否提供商业航天火箭精密器件解决方案？ 回复：尊敬的投资者您好，公司联营企业相关产品可用于航空航天高能燃料等领域，其高能燃料相关产品收入占其总体业务收入比重较低。感谢您对公司的关注。",
            source="irm_cninfo",
            published_at="2026-04-20T20:45:33+08:00",
            url="https://example.com/irm-low-revenue-ratio-fallback",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-keep-substantive-order-progress-3",
            first_seen_at="2026-04-20T20:46:03+08:00",
            last_seen_at="2026-04-20T20:46:03+08:00",
            canonical_title="久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？",
            summary="问题：公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？ 回复：您好！2026年以来，公司相关产品已完成多家商业航天客户送样验证，并取得批量订单，部分型号已进入卫星互联网配套供应链。",
            source="irm_cninfo",
            published_at="2026-04-20T20:46:03+08:00",
            url="https://example.com/irm-keep-substantive-order-progress-3",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-disclosure-threshold-fallback", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-low-revenue-ratio-fallback", direction="neutral", impact_score=100.0, reasoning="rule", themes=["商业航天"], triggered=True),
        EventAnalysis(event_id="event-irm-keep-substantive-order-progress-3", direction="bullish", impact_score=100.0, reasoning="rule", themes=["商业航天"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "*ST中地：您好董秘，公司年报说中标宁夏中交云数据中心" not in content
    assert "濮阳惠成：公司的联营企业是否提供商业航天火箭精密器件解决方案？" not in content
    assert "久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？" in content


def test_write_text_report_filters_irm_cninfo_gamble_clause_explanation_without_hiding_substantive_progress(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-gamble-clause-fallback",
            first_seen_at="2026-04-20T20:45:33+08:00",
            last_seen_at="2026-04-20T20:45:33+08:00",
            canonical_title="*ST中地：您好董秘，公司收购中交物业时有对赌协议，3年净利润不低于2.31亿元，对赌协议是最多补偿2.31亿，不管是否亏损，还是对亏损额也要补偿？谢谢",
            summary="问题：对赌协议是最多补偿2.31亿，不管是否亏损，还是对亏损额也要补偿？ 回复：您好，请参见已披露年报承诺事项中的计算方法，谢谢！",
            source="irm_cninfo",
            published_at="2026-04-20T20:45:33+08:00",
            url="https://example.com/irm-gamble-clause-fallback",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-keep-substantive-order-progress-4",
            first_seen_at="2026-04-20T20:46:03+08:00",
            last_seen_at="2026-04-20T20:46:03+08:00",
            canonical_title="久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？",
            summary="问题：公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？ 回复：您好！2026年以来，公司相关产品已完成多家商业航天客户送样验证，并取得批量订单，部分型号已进入卫星互联网配套供应链。",
            source="irm_cninfo",
            published_at="2026-04-20T20:46:03+08:00",
            url="https://example.com/irm-keep-substantive-order-progress-4",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-gamble-clause-fallback", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-keep-substantive-order-progress-4", direction="bullish", impact_score=100.0, reasoning="rule", themes=["商业航天"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "*ST中地：您好董秘，公司收购中交物业时有对赌协议" not in content
    assert "久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？" in content


def test_write_text_report_filters_irm_cninfo_supply_chain_and_small_revenue_replies_without_hiding_substantive_progress(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-enterprise-ssd-fallback",
            first_seen_at="2026-04-20T21:35:33+08:00",
            last_seen_at="2026-04-20T21:35:33+08:00",
            canonical_title="江波龙：董秘您好，AI算力爆发带动SSD市场需求持续扩容，请问公司2026年在企业级SSD业务上的核心发展规划是什么？目前公司企业级PCIe 5.0 SSD产品在国内AI数据中心头部云计算厂商的客户导入和批量出货进展如何？",
            summary="问题：企业级PCIe 5.0 SSD产品在头部云计算厂商的客户导入和批量出货进展如何？ 回复：尊敬的投资者，您好。公司企业级存储产品已导入头部互联网企业的供应链体系中，客户涵盖运营商、互联网企业、服务器厂商等。公司将持续深化与多个领域知名客户的研发项目合作。具体产品进展请以公司公开发布的信息为准。感谢您的关注。",
            source="irm_cninfo",
            published_at="2026-04-20T21:35:33+08:00",
            url="https://example.com/irm-enterprise-ssd-fallback",
            event_type="fast_news",
            event_subtype="policy_signal",
        ),
        Event(
            event_id="event-irm-domestic-substitution-fallback",
            first_seen_at="2026-04-20T21:33:03+08:00",
            last_seen_at="2026-04-20T21:33:03+08:00",
            canonical_title="江波龙：董秘您好，公司核心存储颗粒100%依赖海外原厂采购，请问公司针对供应链卡脖子风险，是否制定了明确的国产替代落地计划？目前在国产存储颗粒的适配、批量采购方面有无实质性进展？谢谢",
            summary="问题：目前在国产存储颗粒的适配、批量采购方面有无实质性进展？ 回复：尊敬的投资者，您好。您提及的信息并不符合公司实际情况。公司已与包括长江存储、长鑫存储在内的全球主要晶圆原厂达成深层次、多角度的合作关系，在晶圆供应保障上具备明显优势。感谢您的关注。",
            source="irm_cninfo",
            published_at="2026-04-20T21:33:03+08:00",
            url="https://example.com/irm-domestic-substitution-fallback",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-small-revenue-impact-fallback",
            first_seen_at="2026-04-20T20:45:33+08:00",
            last_seen_at="2026-04-20T20:45:33+08:00",
            canonical_title="久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？公司如何看待商业航天和卫星互联网未来发展前景，公司如何推进相关产品与之相配套？",
            summary="问题：产品在商业航天和卫星互联网方面市场拓展如何？ 回复：感谢您的关注。2026年以来，公司持续关注商业航天及卫星互联网领域的行业动态，相关工作正在开展。目前，商业航天与卫星互联网行业尚处于起步阶段，公司在商业航天和卫星互联网领域的收入占整体营业收入的比例较小，对公司业绩无重大影响，请投资者注意风险，理性决策，审慎投资。感谢您的关注。",
            source="irm_cninfo",
            published_at="2026-04-20T20:45:33+08:00",
            url="https://example.com/irm-small-revenue-impact-fallback",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-keep-substantive-theme-progress-5",
            first_seen_at="2026-04-20T20:46:03+08:00",
            last_seen_at="2026-04-20T20:46:03+08:00",
            canonical_title="久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？",
            summary="问题：产品在商业航天和卫星互联网方面市场拓展如何？ 回复：您好！2026年以来，公司相关产品已完成多家商业航天客户送样验证，并取得批量订单，部分型号已进入卫星互联网配套供应链。",
            source="irm_cninfo",
            published_at="2026-04-20T20:46:03+08:00",
            url="https://example.com/irm-keep-substantive-theme-progress-5",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-enterprise-ssd-fallback", direction="bullish", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-domestic-substitution-fallback", direction="bearish", impact_score=100.0, reasoning="rule", themes=["半导体"], triggered=True),
        EventAnalysis(event_id="event-irm-small-revenue-impact-fallback", direction="bullish", impact_score=100.0, reasoning="rule", themes=["商业航天"], triggered=True),
        EventAnalysis(event_id="event-irm-keep-substantive-theme-progress-5", direction="bullish", impact_score=100.0, reasoning="rule", themes=["商业航天"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "江波龙：董秘您好，AI算力爆发带动SSD市场需求持续扩容" not in content
    assert "江波龙：董秘您好，公司核心存储颗粒100%依赖海外原厂采购" not in content
    assert "久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？公司如何看待商业航天和卫星互联网未来发展前景，公司如何推进相关产品与之相配套？" not in content
    assert "久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？" in content


def test_write_text_report_filters_current_live_buyback_completion_material_without_hiding_substantive_item(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-buyback-cancel-complete-current",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="广东鸿图：关于限制性股票回购注销完成的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/szse-buyback-cancel-complete-current",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-keep-substantive-item-current-3",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="杭可科技：拟1.79亿元增资杭可仪器获51%股权",
            summary="summary",
            source="cls",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/keep-substantive-item-current-3",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-szse-buyback-cancel-complete-current", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-substantive-item-current-3", direction="neutral", impact_score=99.3, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "广东鸿图：关于限制性股票回购注销完成的公告" not in content
    assert "杭可科技：拟1.79亿元增资杭可仪器获51%股权" in content


def test_write_text_report_filters_irm_cninfo_inventory_capacity_and_registration_progress_replies_without_hiding_substantive_progress(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-inventory-lta-fallback",
            first_seen_at="2026-04-20T21:38:03+08:00",
            last_seen_at="2026-04-20T21:38:03+08:00",
            canonical_title="江波龙：董秘您好，当前全球存储原厂产能持续向AI专用、企业级存储倾斜，行业普遍面临晶圆/颗粒供给紧张的局面。请问公司2026全年的存储晶圆/颗粒长单锁定比例是多少？现有库存水位能否足额覆盖下游客户的交付需求？是否存在订单无法按期交付的风险？谢谢",
            summary="问题：长单锁定比例是多少？现有库存水位能否足额覆盖交付需求？ 回复：尊敬的投资者，您好。公司已与全球主要存储晶圆原厂建立合作关系，通过签署长期供货协议（LTA）或商业合作备忘录（MOU），构建起有韧性及有保障的晶圆供应体系。公司库存水位处于健康合理区间。届时欢迎您查阅定期报告以获取更详细的存货信息。感谢您的关注。",
            source="irm_cninfo",
            published_at="2026-04-20T21:38:03+08:00",
            url="https://example.com/irm-inventory-lta-fallback",
            event_type="fast_news",
            event_subtype="policy_signal",
        ),
        Event(
            event_id="event-irm-vehicle-supply-chain-fallback",
            first_seen_at="2026-04-20T21:36:33+08:00",
            last_seen_at="2026-04-20T21:36:33+08:00",
            canonical_title="江波龙：董秘您好，高阶智能驾驶与车载端侧AI的快速普及，带动车规级存储市场迎来确定性增长。请问目前公司车规级存储产品在国内头部新能源车企的批量出货进展如何？2026年公司在车规级存储赛道的营收占比目标分别是什么？谢谢",
            summary="问题：车规级存储产品在国内头部新能源车企的批量出货进展如何？2026年营收占比目标分别是什么？ 回复：尊敬的投资者，您好。公司构建了UFS、eMMC、LPDDR、USB在内的车规级存储产品矩阵，已经进入北美智能汽车及自动驾驶科技巨头等知名车企的供应链体系中，并将持续深化与知名客户的研发和商业化项目合作。具体业务的业绩情况，请您以公司发布的定期报告为准。感谢您的关注。",
            source="irm_cninfo",
            published_at="2026-04-20T21:36:33+08:00",
            url="https://example.com/irm-vehicle-supply-chain-fallback",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-capacity-report-fallback",
            first_seen_at="2026-04-20T21:38:33+08:00",
            last_seen_at="2026-04-20T21:38:33+08:00",
            canonical_title="江波龙：董秘您好，当前存储行业景气度持续走高，公司下游需求旺盛。请问公司目前整体产能利用率如何，订单是否接近满产满销？谢谢。",
            summary="问题：公司目前整体产能利用率如何，订单是否接近满产满销？ 回复：尊敬的投资者，您好。公司已经构建了全球化与国内产能并重、自主产能与委外产能并行的制造格局，能够灵活高效地满足下游客户的多样化需求。届时欢迎您查阅定期报告以获取更详细的产销情况信息。感谢您的关注。",
            source="irm_cninfo",
            published_at="2026-04-20T21:38:33+08:00",
            url="https://example.com/irm-capacity-report-fallback",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-registration-progress-fallback",
            first_seen_at="2026-04-20T20:45:33+08:00",
            last_seen_at="2026-04-20T20:45:33+08:00",
            canonical_title="华伍股份：董秘你好，股东大会开完一周了，注销回购股份减少注册资本的工商登记是否变更完成了？公司是否能够及时快速的落实股东大会决议？！几个月前公司就公告了拟注销回购的股份，一切手续是不是早就准备好了？",
            summary="问题：注销回购股份减少注册资本的工商登记是否变更完成了？ 回复：您好！公司已组织人员办理回购股份注销业务。目前相关工作正在有序推进中，公司将根据业务办理进度及时履行信息披露义务。具体完成时间及进展情况请以公司后续公告为准。谢谢关注！",
            source="irm_cninfo",
            published_at="2026-04-20T20:45:33+08:00",
            url="https://example.com/irm-registration-progress-fallback",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-keep-substantive-theme-progress-6",
            first_seen_at="2026-04-20T20:46:03+08:00",
            last_seen_at="2026-04-20T20:46:03+08:00",
            canonical_title="久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？",
            summary="问题：产品在商业航天和卫星互联网方面市场拓展如何？ 回复：您好！2026年以来，公司相关产品已完成多家商业航天客户送样验证，并取得批量订单，部分型号已进入卫星互联网配套供应链。",
            source="irm_cninfo",
            published_at="2026-04-20T20:46:03+08:00",
            url="https://example.com/irm-keep-substantive-theme-progress-6",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-inventory-lta-fallback", direction="bearish", impact_score=100.0, reasoning="rule", themes=["半导体"], triggered=True),
        EventAnalysis(event_id="event-irm-vehicle-supply-chain-fallback", direction="bullish", impact_score=100.0, reasoning="rule", themes=["新能源车"], triggered=True),
        EventAnalysis(event_id="event-irm-capacity-report-fallback", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-registration-progress-fallback", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-keep-substantive-theme-progress-6", direction="bullish", impact_score=100.0, reasoning="rule", themes=["商业航天"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "江波龙：董秘您好，当前全球存储原厂产能持续向AI专用、企业级存储倾斜" not in content
    assert "江波龙：董秘您好，高阶智能驾驶与车载端侧AI的快速普及" not in content
    assert "江波龙：董秘您好，当前存储行业景气度持续走高" not in content
    assert "华伍股份：董秘你好，股东大会开完一周了" not in content
    assert "久之洋：您好，请问2026年以来，公司的星体跟踪器和光纤放大器等产品在商业航天和卫星互联网方面市场拓展如何？" in content


def test_write_text_report_filters_overseas_single_stock_cls_acquisition_without_theme_or_entities(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-overseas-single-stock-acquisition",
            first_seen_at="2026-04-20T21:35:53+08:00",
            last_seen_at="2026-04-20T21:35:53+08:00",
            canonical_title="财联社4月20日电，美国稀土集团股价上涨13%，因其将以28亿美元收购巴西的SERRA VERDE。",
            summary="财联社4月20日电，美国稀土集团股价上涨13%，因其将以28亿美元收购巴西的SERRA VERDE。",
            source="cls",
            published_at="2026-04-20T21:35:53+08:00",
            url="https://example.com/cls-overseas-single-stock-acquisition",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-keep-substantive-acquisition-current-4",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="杭可科技：拟1.79亿元增资杭可仪器获51%股权",
            summary="summary",
            source="cls",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/keep-substantive-acquisition-current-4",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-cls-overseas-single-stock-acquisition", direction="neutral", impact_score=74.3, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-substantive-acquisition-current-4", direction="neutral", impact_score=99.3, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "财联社4月20日电，美国稀土集团股价上涨13%，因其将以28亿美元收购巴西的SERRA VERDE。" not in content
    assert "杭可科技：拟1.79亿元增资杭可仪器获51%股权" in content


def test_write_text_report_filters_sse_einteractive_investor_complaint_and_report_calendar_without_hiding_substantive_reply(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-einteractive-complaint",
            first_seen_at="2026-04-17T18:21:00+08:00",
            last_seen_at="2026-04-17T18:21:00+08:00",
            canonical_title="有友食品：尊敬的董秘，近期贵公司市值持续下跌且遭受315的风波冲击，贵公司是否考虑回购注销一定量的股票来增强市场投资者的信心，请您回复谢谢。",
            summary="问题：近期贵公司市值持续下跌，是否考虑回购注销股票增强投资者信心？\n回复：公司将始终聚焦主业经营，切实维护全体股东权益。感谢您的关注。",
            source="sse_einteractive",
            published_at="2026-04-17T18:21:00+08:00",
            url="https://example.com/sse-einteractive-complaint",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-sse-einteractive-report-calendar",
            first_seen_at="2026-04-17T18:21:00+08:00",
            last_seen_at="2026-04-17T18:21:00+08:00",
            canonical_title="豫园股份：董秘您好，请问贵公司2026年1季度报告什么时候发布，谢谢",
            summary="问题：请问贵公司2026年1季度报告什么时候发布？\n回复：公司已于4月17日在上交所网站披露了2026年第一季度报告，感谢您对公司的关注。",
            source="sse_einteractive",
            published_at="2026-04-17T18:21:00+08:00",
            url="https://example.com/sse-einteractive-report-calendar",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-einteractive-keep-substantive",
            first_seen_at="2026-04-17T18:21:00+08:00",
            last_seen_at="2026-04-17T18:21:00+08:00",
            canonical_title="聚合顺：你好，我司年报中提及我司高端复合尼龙新材料应用于商业航天，新能源汽车电池等应用场景，请问为何我司产品可应用到以上场景？",
            summary="问题：我司高端复合尼龙新材料为何可应用于商业航天和新能源汽车电池场景？\n回复：公司产品经下游企业改性技术后，可在商业航天和新能源汽车相关场景提供轻量化与耐化学性支持。",
            source="sse_einteractive",
            published_at="2026-04-17T18:21:00+08:00",
            url="https://example.com/sse-einteractive-keep-substantive",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-sse-einteractive-buyback-rule-complaint",
            first_seen_at="2026-04-17T18:21:00+08:00",
            last_seen_at="2026-04-17T18:21:00+08:00",
            canonical_title="豫园股份：根据上市公司股份回购规则《上海证券交易所自律监管指引第7号-回购股份》等相关规定为维护公司价值及股东权益所必需回购情形，应当符合以下条件公司股票收盘价格低于最近一期每股净资产连续二十个交易日内公司股票收盘价格跌幅累计达到百分之二十公司股票收盘价格低于最近一年股票最高收盘价格的百分之五十中国证监会规定的其他条件公司股价低于每股净资产严重损害到全体股东利益为维护全体股东权益强烈要求公司回购的股份进行注销",
            summary="问题：根据上交所回购规则，强烈要求公司回购注销股份。\n回复：尊敬的投资者，您好！您的建议已收悉，公司将严格按照监管规则审慎评估。",
            source="sse_einteractive",
            published_at="2026-04-17T18:21:00+08:00",
            url="https://example.com/sse-einteractive-buyback-rule-complaint",
            event_type="fast_news",
            event_subtype="policy_signal",
        ),
        Event(
            event_id="event-sse-einteractive-plunge-complaint",
            first_seen_at="2026-04-17T18:21:00+08:00",
            last_seen_at="2026-04-17T18:21:00+08:00",
            canonical_title="山东出版：尊敬的董秘您好，近日公司股价突发性暴跌超过15%，公司是否有未公告潜在重大利空?面对打压，公司不作为也是在默许或配合了资本市场玩家，为什么不及时澄清?",
            summary="问题：近日公司股价突发性暴跌超过15%，是否有未公告潜在重大利空？\n回复：尊敬的投资者您好，公司不存在应披露未披露事项，感谢您的关注。",
            source="sse_einteractive",
            published_at="2026-04-17T18:21:00+08:00",
            url="https://example.com/sse-einteractive-plunge-complaint",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-sse-einteractive-disclosure-fallback",
            first_seen_at="2026-04-17T18:22:00+08:00",
            last_seen_at="2026-04-17T18:22:00+08:00",
            canonical_title="贵州燃气：您好！贵州燃气公司有氢燃料或相关技术储备吗？",
            summary="问题：贵州燃气公司有氢燃料或相关技术储备吗？\n回复：尊敬的投资者您好，感谢您对公司的关注！在“双碳”背景下，公司积极响应国家政策，具体请关注公司定期报告及有关公告，谢谢！",
            source="sse_einteractive",
            published_at="2026-04-17T18:22:00+08:00",
            url="https://example.com/sse-einteractive-disclosure-fallback",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-einteractive-annual-report-fallback",
            first_seen_at="2026-04-17T18:21:00+08:00",
            last_seen_at="2026-04-17T18:21:00+08:00",
            canonical_title="*ST星农：会不会出非标审计报告？",
            summary="问题：会不会出非标审计报告？\n回复：尊敬的投资者您好，最终审计意见以2025年年度报告披露为准，感谢您的关注。",
            source="sse_einteractive",
            published_at="2026-04-17T18:21:00+08:00",
            url="https://example.com/sse-einteractive-annual-report-fallback",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-einteractive-undisclosed-info-fallback",
            first_seen_at="2026-04-17T18:21:00+08:00",
            last_seen_at="2026-04-17T18:21:00+08:00",
            canonical_title="山东出版：尊敬的董秘您好，近日公司股价突发性暴跌超过15%，公司是否有未公告潜在重大利空?",
            summary="问题：近日公司股价突发性暴跌超过15%，是否有未公告潜在重大利空？\n回复：尊敬的投资者您好，公司不存在应披露而未披露的信息，感谢您的关注。",
            source="sse_einteractive",
            published_at="2026-04-17T18:21:00+08:00",
            url="https://example.com/sse-einteractive-undisclosed-info-fallback",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-sse-einteractive-complaint", direction="neutral", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-report-calendar", direction="bullish", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-keep-substantive", direction="bullish", impact_score=99.9, reasoning="rule", themes=["商业航天", "新能源车"], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-buyback-rule-complaint", direction="neutral", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-plunge-complaint", direction="neutral", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-disclosure-fallback", direction="neutral", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-annual-report-fallback", direction="neutral", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-undisclosed-info-fallback", direction="neutral", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "近期贵公司市值持续下跌" not in content
    assert "2026年1季度报告什么时候发布" not in content
    assert "强烈要求公司回购的股份进行注销" not in content
    assert "股价突发性暴跌超过15%" not in content
    assert "贵州燃气公司有氢燃料或相关技术储备吗" not in content
    assert "会不会出非标审计报告" not in content
    assert "是否有未公告潜在重大利空" not in content
    assert "聚合顺：你好，我司年报中提及我司高端复合尼龙新材料应用于商业航天" in content


def test_write_text_report_filters_sse_einteractive_theme_qa_without_hiding_substantive_reply(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-einteractive-innovative-drug",
            first_seen_at="2026-04-20T18:19:00+08:00",
            last_seen_at="2026-04-20T18:19:00+08:00",
            canonical_title="肯特催化：请问公司产品是否可服务于创新药制造与研发？",
            summary="问题：请问公司产品是否可服务于创新药制造与研发？ 回复：答：尊敬的投资者，您好。公司生产的部分产品，可应用于医药领域。感谢您对公司的关注。谢谢。",
            source="sse_einteractive",
            published_at="2026-04-20T18:19:00+08:00",
            url="https://example.com/sse-einteractive-innovative-drug",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-einteractive-pcb",
            first_seen_at="2026-04-20T18:19:00+08:00",
            last_seen_at="2026-04-20T18:19:00+08:00",
            canonical_title="肯特催化：肯特催化的部分产品可以配套于PCB（印刷线路板）的生产？作为电子化学品产业链的一员公司的产品主要应用于PCB生产的哪些过程？",
            summary="问题：肯特催化的部分产品可以配套于PCB（印刷线路板）的生产？作为电子化学品产业链的一员公司的产品主要应用于PCB生产的哪些过程？ 回复：答：尊敬的投资者，您好！关于公司产品应用的具体信息，请查阅公司招股说明书、定期报告及相关公告。感谢您对公司的关注！谢谢！",
            source="sse_einteractive",
            published_at="2026-04-20T18:19:00+08:00",
            url="https://example.com/sse-einteractive-pcb",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-einteractive-solar-investment",
            first_seen_at="2026-04-20T18:19:00+08:00",
            last_seen_at="2026-04-20T18:19:00+08:00",
            canonical_title="中新集团：您好，公司在光伏领域有哪些知名投资，劳请列举回复。",
            summary="问题：您好，公司在光伏领域有哪些知名投资，劳请列举回复。 回复：尊敬的投资者，您好。公司绿色发电以旗下控股子公司中新绿能为主要平台，以国内一流绿色能源运营商为发展定位，开发风光等可再生能源，近期以分布式光伏为重点发展方向，着力开发、投资、建设、运营和管理分布式光伏发电、储能等能源项目。感谢关注。",
            source="sse_einteractive",
            published_at="2026-04-20T18:19:00+08:00",
            url="https://example.com/sse-einteractive-solar-investment",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-einteractive-investment-count",
            first_seen_at="2026-04-20T18:04:00+08:00",
            last_seen_at="2026-04-20T18:04:00+08:00",
            canonical_title="中新集团：您好，请问公司投资的私募共计投资了大约多少家半导体公司，多少家机器人公司，多少家医药医疗器械公司？",
            summary="问题：您好，请问公司投资的私募共计投资了大约多少家半导体公司，多少家机器人公司，多少家医药医疗器械公司？ 回复：尊敬的投资者，您好！关于产业投资情况，请关注公司相关公告和定期报告。您也可以通过国家企业信用信息公示系统等渠道进行查询。感谢关注。",
            source="sse_einteractive",
            published_at="2026-04-20T18:04:00+08:00",
            url="https://example.com/sse-einteractive-investment-count",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-einteractive-investment-count-variant",
            first_seen_at="2026-04-20T18:04:00+08:00",
            last_seen_at="2026-04-20T18:04:00+08:00",
            canonical_title="中新集团：您好，公司投资的创新药企业大致有多少家，取得新技术新成绩有代表性的企业有那些。",
            summary="问题：您好，公司投资的创新药企业大致有多少家，取得新技术新成绩有代表性的企业有那些。 回复：尊敬的投资者，您好！关于产业投资情况，请关注公司相关公告和定期报告。您也可以通过国家企业信用信息公示系统等渠道进行查询。感谢关注。",
            source="sse_einteractive",
            published_at="2026-04-20T18:04:00+08:00",
            url="https://example.com/sse-einteractive-investment-count-variant",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-einteractive-keep-substantive-2",
            first_seen_at="2026-04-20T18:04:00+08:00",
            last_seen_at="2026-04-20T18:04:00+08:00",
            canonical_title="中新集团：您好，公司50亿私募投资和科创直投有无在头显眼镜领域布局投资？",
            summary="问题：您好，公司50亿私募投资和科创直投有无在头显眼镜领域布局投资？ 回复：尊敬的投资者，您好。公司通过参投基金间接投资布局了AR眼镜产业链，包括Micro-LED微显示屏研发、Micro-LED硅基微显示芯片研发、AR衍射光波导、衍射光栅、微纳光学元件研发、AR/VR镜片等。感谢关注。",
            source="sse_einteractive",
            published_at="2026-04-20T18:04:00+08:00",
            url="https://example.com/sse-einteractive-keep-substantive-2",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-sse-einteractive-innovative-drug", direction="neutral", impact_score=99.9, reasoning="rule", themes=["创新药"], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-pcb", direction="neutral", impact_score=99.9, reasoning="rule", themes=["PCB"], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-solar-investment", direction="neutral", impact_score=99.9, reasoning="rule", themes=["储能"], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-investment-count", direction="neutral", impact_score=99.9, reasoning="rule", themes=["机器人", "半导体"], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-investment-count-variant", direction="neutral", impact_score=99.9, reasoning="rule", themes=["创新药"], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-keep-substantive-2", direction="neutral", impact_score=99.9, reasoning="rule", themes=["AR眼镜"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "请问公司产品是否可服务于创新药制造与研发" not in content
    assert "产品主要应用于PCB生产的哪些过程" not in content
    assert "公司在光伏领域有哪些知名投资" not in content
    assert "投资的私募共计投资了大约多少家半导体公司" not in content
    assert "公司投资的创新药企业大致有多少家" not in content
    assert "公司50亿私募投资和科创直投有无在头显眼镜领域布局投资" in content


def test_write_text_report_filters_sse_einteractive_progress_followups_that_only_point_to_announcements(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-einteractive-placement-progress",
            first_seen_at="2026-04-22T18:10:00+08:00",
            last_seen_at="2026-04-22T18:10:00+08:00",
            canonical_title="中国能建：贵公司子公司中电智算对城地香江的定增今年内可以完成吗，看好算电协同，希望可以加快进度。",
            summary="问题：贵公司子公司中电智算对城地香江的定增今年内可以完成吗，看好算电协同，希望可以加快进度。 回复：感谢您对公司的关注！相关进展情况请查询定增公司公告。",
            source="sse_einteractive",
            published_at="2026-04-22T18:10:00+08:00",
            url="https://example.com/sse-einteractive-placement-progress",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-einteractive-order-followup",
            first_seen_at="2026-04-22T18:10:00+08:00",
            last_seen_at="2026-04-22T18:10:00+08:00",
            canonical_title="瑞华泰：你好，一季报航空航天板块业绩都很好，请问贵公司一季度航空航天业务订单如何？嘉兴项目产能是否已满产？所有产品是否满产满销？从你们的业务布局来看，你们是在布局未来，希望这个未来就在一年之内，也希望贵公司业绩越来越好。",
            summary="问题：你好，一季报航空航天板块业绩都很好，请问贵公司一季度航空航天业务订单如何？嘉兴项目产能是否已满产？所有产品是否满产满销？从你们的业务布局来看，你们是在布局未来，希望这个未来就在一年之内，也希望贵公司业绩越来越好。 回复：尊敬的投资者您好！具体经营情况，请关注公司披露的定期报告及相关公告。感谢您对公司的关注。",
            source="sse_einteractive",
            published_at="2026-04-22T18:10:00+08:00",
            url="https://example.com/sse-einteractive-order-followup",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-sse-einteractive-keep-chiplet",
            first_seen_at="2026-04-22T18:12:00+08:00",
            last_seen_at="2026-04-22T18:12:00+08:00",
            canonical_title="芯碁微装：芯碁微装是否布局先进封装，光模块/CPO等前沿赛道的设备业务？",
            summary="问题：芯碁微装是否布局先进封装，光模块/CPO等前沿赛道的设备业务？ 回复：尊敬的投资者您好！公司WLP系列直写光刻设备已实现多家头部厂商类CoWoS-L产品的量产导入，并预计于2026年下半年进入量产爬坡阶段。此外，公司设备在光电封装、硅穿孔等关键环节具备技术优势，可满足光模块等领域的高精度制造需求，感谢关注！",
            source="sse_einteractive",
            published_at="2026-04-22T18:12:00+08:00",
            url="https://example.com/sse-einteractive-keep-chiplet",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-einteractive-keep-hydrogen",
            first_seen_at="2026-04-22T18:10:00+08:00",
            last_seen_at="2026-04-22T18:10:00+08:00",
            canonical_title="中国能建：尊敬的领导您好，请问贵公司生产的绿色氢氨醇是否为主营业务之一？原油价格上涨到多少，贵公司的绿色氢氨醇就会有显著成本优势以替代传统石油？绿色氢氨醇绿甲醇是否正加速切入国内传统石油替代市场？一期产能利用率是否超预期？ 能否推动出口订单快速放量？二期绿色氢氨醇规划是否将提前提速？ 绿色氢氨醇是否有望成为公司第二增长曲线的核心引擎？",
            summary="问题：尊敬的领导您好，请问贵公司生产的绿色氢氨醇是否为主营业务之一？原油价格上涨到多少，贵公司的绿色氢氨醇就会有显著成本优势以替代传统石油？绿色氢氨醇绿甲醇是否正加速切入国内传统石油替代市场？一期产能利用率是否超预期？ 能否推动出口订单快速放量？二期绿色氢氨醇规划是否将提前提速？ 绿色氢氨醇是否有望成为公司第二增长曲线的核心引擎？ 回复：感谢您对公司的关注！公司将围绕“一体化氢能”这一核心模式，打造绿色氢基能源产业龙头。以绿电制绿氢为切入点，围绕绿色氢、氨、甲醇、航油四大产品，全面进军、集中布局绿色氢基能源制备领域。吉林松原项目一期总投资69.46亿元，项目达产后可实现年产合成氨15.83万吨。当前装置正处于试生产阶段，装置运行稳定，单日最高生产负荷已突破80%，预计本月底产能利用率实现设计水平。二期项目正在进行可研方案优化，预计今年开工建设。",
            source="sse_einteractive",
            published_at="2026-04-22T18:10:00+08:00",
            url="https://example.com/sse-einteractive-keep-hydrogen",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-sse-einteractive-placement-progress", direction="neutral", impact_score=99.9, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-order-followup", direction="neutral", impact_score=99.9, reasoning="rule", themes=["航空"], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-keep-chiplet", direction="neutral", impact_score=99.9, reasoning="rule", themes=["先进封装"], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-keep-hydrogen", direction="bullish", impact_score=99.9, reasoning="rule", themes=["油气"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "中电智算对城地香江的定增今年内可以完成吗" not in content
    assert "一季度航空航天业务订单如何" not in content
    assert "芯碁微装是否布局先进封装" in content
    assert "绿色氢氨醇是否为主营业务之一" in content


def test_write_text_report_filters_exchange_governance_material_attachments_without_hiding_real_notices(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-keep-no-dividend",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="天府文旅：关于2025年度拟不进行利润分配的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/keep-no-dividend",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-governance-esg-report",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="天府文旅：2025年度环境、社会和公司治理（ESG)报告",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/governance-esg-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-governance-special-audit",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="天府文旅：2025年非经营性资金占用及其他关联资金往来情况汇总表的专项审核报告-众环专字（2026）2800005号",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/governance-special-audit",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-governance-sponsor-summary",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="广联航空：中航证券有限公司关于广联航空工业股份有限公司向不特定对象发行可转换公司债券之持续督导保荐总结报告书",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/governance-sponsor-summary",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-governance-charter",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="广联航空：公司章程（2026年4月修订）",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/governance-charter",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-governance-rules",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="广联航空：股东会议事规则",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/governance-rules",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-charter-amendment-notice",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="广联航空：关于修订《公司章程》等相关制度的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/keep-charter-amendment-notice",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-keep-no-dividend", direction="neutral", impact_score=100.0, reasoning="rule", themes=["房地产"], triggered=True),
        EventAnalysis(event_id="event-governance-esg-report", direction="neutral", impact_score=100.0, reasoning="rule", themes=["房地产"], triggered=True),
        EventAnalysis(event_id="event-governance-special-audit", direction="neutral", impact_score=100.0, reasoning="rule", themes=["房地产"], triggered=True),
        EventAnalysis(event_id="event-governance-sponsor-summary", direction="neutral", impact_score=100.0, reasoning="rule", themes=["航空"], triggered=True),
        EventAnalysis(event_id="event-governance-charter", direction="neutral", impact_score=100.0, reasoning="rule", themes=["航空"], triggered=True),
        EventAnalysis(event_id="event-governance-rules", direction="neutral", impact_score=100.0, reasoning="rule", themes=["航空"], triggered=True),
        EventAnalysis(event_id="event-keep-charter-amendment-notice", direction="neutral", impact_score=100.0, reasoning="rule", themes=["航空"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "关于2025年度拟不进行利润分配的公告" in content
    assert "关于修订《公司章程》等相关制度的公告" in content
    assert "2025年度环境、社会和公司治理（ESG)报告" not in content
    assert "专项审核报告-众环专字（2026）2800005号" not in content
    assert "持续督导保荐总结报告书" not in content
    assert "公司章程（2026年4月修订）" not in content
    assert "股东会议事规则" not in content


def test_write_text_report_filters_irm_cninfo_registration_placeholder_and_no_project_order_reply(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-registration-placeholder",
            first_seen_at="2026-04-23T15:10:00+08:00",
            last_seen_at="2026-04-23T15:10:00+08:00",
            canonical_title="乐普医疗：公司的三文鱼针，目前注册上市进行到了什么阶段？预计何时获批上市？",
            summary="问题：公司的三文鱼针，目前注册上市进行到了什么阶段？预计何时获批上市？ 回复：尊敬的投资者您好，目前该产品处于审评审批中。",
            source="irm_cninfo",
            published_at="2026-04-23T15:10:00+08:00",
            url="https://example.com/irm-registration-placeholder",
            event_type="fast_news",
            event_subtype="regulatory_approval",
        ),
        Event(
            event_id="event-irm-no-project-order-reply",
            first_seen_at="2026-04-23T15:11:00+08:00",
            last_seen_at="2026-04-23T15:11:00+08:00",
            canonical_title="新天地：目前行业内在仲丁基锂连续流规模化生产上已出现明显技术领先企业，该技术直接决定高难度创新药分子的可开发性与商业化效率。请问公司是否掌握相关核心工艺？有无具体项目案例、产能规模及客户验证？若存在明显技术代差，将如何应对高端订单流失的风险？",
            summary="问题：目前行业内在仲丁基锂连续流规模化生产上已出现明显技术领先企业，该技术直接决定高难度创新药分子的可开发性与商业化效率。请问公司是否掌握相关核心工艺？有无具体项目案例、产能规模及客户验证？若存在明显技术代差，将如何应对高端订单流失的风险？ 回复：尊敬的投资者您好，公司暂无项目涉及仲丁基锂使用。公司与清华大学合作开展连续流技术的开发研究与应用，相关技术储备及项目进展请以公司公开披露信息为准，感谢您对公司的关注！",
            source="irm_cninfo",
            published_at="2026-04-23T15:11:00+08:00",
            url="https://example.com/irm-no-project-order-reply",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-keep-obesity-drug-progress",
            first_seen_at="2026-04-23T15:12:00+08:00",
            last_seen_at="2026-04-23T15:12:00+08:00",
            canonical_title="乐普医疗：子公司民为生物的三靶点减肥药MWM109，当前国内二期临床试验进展到了哪一步？国外的临床进展如何？",
            summary="问题：子公司民为生物的三靶点减肥药MWM109，当前国内二期临床试验进展到了哪一步？国外的临床进展如何？ 回复：尊敬的投资者您好，MWN109 注射剂国内减重II 期低剂量组已完成；MWN109 口服片剂国内减重 II 期目前已到 8 周；MWN109 口服片剂国内维持 II 期已到 4周。澳洲注射剂和口服片临床I期已完成。",
            source="irm_cninfo",
            published_at="2026-04-23T15:12:00+08:00",
            url="https://example.com/irm-keep-obesity-drug-progress",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-keep-chip-adaptation",
            first_seen_at="2026-04-23T15:13:00+08:00",
            last_seen_at="2026-04-23T15:13:00+08:00",
            canonical_title="东华软件：请问贵公司软件AI服务器及算力相关产品是否都已接入DeepSeek系列模型？贵公司大模型在与国产芯片是否实现深度融合？",
            summary="问题：请问贵公司软件AI服务器及算力相关产品是否都已接入DeepSeek系列模型？贵公司大模型在与国产芯片是否实现深度融合？ 回复：您好，公司与主流的芯片厂商都具有技术适配，目前在昇腾、摩尔线程等GPU均有深入合作，公司多行业与DeepSeek等模型均已深度适配。感谢您的关注与支持。",
            source="irm_cninfo",
            published_at="2026-04-23T15:13:00+08:00",
            url="https://example.com/irm-keep-chip-adaptation",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-registration-placeholder", direction="neutral", impact_score=100.0, reasoning="rule", themes=["创新药"], triggered=True),
        EventAnalysis(event_id="event-irm-no-project-order-reply", direction="neutral", impact_score=100.0, reasoning="rule", themes=["创新药"], triggered=True),
        EventAnalysis(event_id="event-irm-keep-obesity-drug-progress", direction="bullish", impact_score=100.0, reasoning="rule", themes=["创新药"], triggered=True),
        EventAnalysis(event_id="event-irm-keep-chip-adaptation", direction="bullish", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "注册上市进行到了什么阶段" not in content
    assert "高端订单流失的风险" not in content
    assert "三靶点减肥药MWM109" in content
    assert "DeepSeek系列模型" in content


def test_write_text_report_filters_irm_cninfo_asset_injection_boilerplate_without_hiding_substantive_commercialization_reply(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-irm-asset-injection-boilerplate",
            first_seen_at="2026-04-23T15:20:00+08:00",
            last_seen_at="2026-04-23T15:20:00+08:00",
            canonical_title="新柴股份：尊敬的董秘，公司市值这么小按当前市值实际流通盘是不是太小了，估计十二亿都不到吧，为什么不公积金扩股，未来有没有资产注入，会不会重组啊，",
            summary="问题：尊敬的董秘，公司市值这么小按当前市值实际流通盘是不是太小了，估计十二亿都不到吧，为什么不公积金扩股，未来有没有资产注入，会不会重组啊， 回复：您好，公司严格遵循法律法规关于信息披露的规定，若满足披露条件，公司将及时、准确、完整地履行信息披露义务，请您关注公司在指定信息披露媒体发布的相关公告。感谢您的关注！",
            source="irm_cninfo",
            published_at="2026-04-23T15:20:00+08:00",
            url="https://example.com/irm-asset-injection-boilerplate",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-irm-keep-dbs-commercialization",
            first_seen_at="2026-04-23T15:21:00+08:00",
            last_seen_at="2026-04-23T15:21:00+08:00",
            canonical_title="乐普医疗：请公司介绍下DBS产品订单情况、入院数量、医保落地进展情况等，谢谢。",
            summary="问题：请公司介绍下DBS产品订单情况、入院数量、医保落地进展情况等，谢谢。 回复：尊敬的投资者您好，DBS目前处于商业化初期，公司正积极推动该产品的入院及临床植入工作，感谢您对公司的关心。",
            source="irm_cninfo",
            published_at="2026-04-23T15:21:00+08:00",
            url="https://example.com/irm-keep-dbs-commercialization",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-irm-asset-injection-boilerplate", direction="neutral", impact_score=100.0, reasoning="rule", themes=["重组"], triggered=True),
        EventAnalysis(event_id="event-irm-keep-dbs-commercialization", direction="bullish", impact_score=100.0, reasoning="rule", themes=["创新药"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "未来有没有资产注入，会不会重组" not in content
    assert "DBS产品订单情况" in content


def test_write_text_report_filters_exchange_risk_assessment_and_governance_rules_without_hiding_real_disclosures(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-risk-assessment-report",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="湖北楚天智能交通股份有限公司关于湖北交投集团财务有限公司2025年度风险评估的报告",
            summary="summary",
            source="sse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/risk-assessment-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-innovation-management-rules",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="视源股份：广州视源电子科技股份有限公司支持创新创业管理办法",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/innovation-management-rules",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-derivatives-control-rules",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="视源股份：广州视源电子科技股份有限公司期货和衍生品交易业务内部控制制度",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/derivatives-control-rules",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-independent-director-opinion",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="湖北楚天智能交通股份有限公司董事会对独立董事独立性情况的专项意见",
            summary="summary",
            source="sse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/independent-director-opinion",
            event_type="hard_event",
            event_subtype="board_resolution",
        ),
        Event(
            event_id="event-keep-impairment-notice",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="湖北楚天智能交通股份有限公司关于计提资产减值准备的公告",
            summary="summary",
            source="sse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/keep-impairment-notice",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-keep-hedging-notice",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="视源股份：关于开展外汇套期保值业务的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/keep-hedging-notice",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-risk-assessment-report", direction="neutral", impact_score=100.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-innovation-management-rules", direction="neutral", impact_score=100.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-derivatives-control-rules", direction="neutral", impact_score=100.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-independent-director-opinion", direction="neutral", impact_score=100.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-impairment-notice", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-hedging-notice", direction="bullish", impact_score=100.0, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "湖北交投集团财务有限公司2025年度风险评估的报告" not in content
    assert "支持创新创业管理办法" not in content
    assert "期货和衍生品交易业务内部控制制度" not in content
    assert "独立董事独立性情况的专项意见" not in content
    assert "关于计提资产减值准备的公告" in content
    assert "关于开展外汇套期保值业务的公告" in content


def test_write_text_report_filters_sse_einteractive_stock_price_complaints_with_generic_market_reply(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-stock-price-complaint-1",
            first_seen_at="2026-04-23T15:00:00+08:00",
            last_seen_at="2026-04-23T15:00:00+08:00",
            canonical_title="福能股份：节能风电和你同样都是一半的绿电！别人市盈率42倍！你9倍！就这么样别人涨停！你大跌的原因是什么？",
            summary="问题：节能风电和你同样都是一半的绿电！别人市盈率42倍！你9倍！就这么样别人涨停！你大跌的原因是什么？ 回复：感谢您对公司的关注！公司股价走势受行业周期、市场资金偏好、市场风格切换等多重因素综合影响，请理性看待。",
            source="sse_einteractive",
            published_at="2026-04-23T15:00:00+08:00",
            url="https://example.com/sse-stock-price-complaint-1",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-sse-stock-price-complaint-2",
            first_seen_at="2026-04-23T15:01:00+08:00",
            last_seen_at="2026-04-23T15:01:00+08:00",
            canonical_title="福能股份：今日！上涨板块，电力排名第二，福能股份电力板块跌幅倒数第一！请董秘给个解释！谢谢！",
            summary="问题：今日！上涨板块，电力排名第二，福能股份电力板块跌幅倒数第一！请董秘给个解释！谢谢！ 回复：感谢您对公司的关注！公司股价走势受行业周期、市场资金偏好、市场风格切换等多重因素综合影响，请理性看待。",
            source="sse_einteractive",
            published_at="2026-04-23T15:01:00+08:00",
            url="https://example.com/sse-stock-price-complaint-2",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-keep-substantive-reply",
            first_seen_at="2026-04-23T15:02:00+08:00",
            last_seen_at="2026-04-23T15:02:00+08:00",
            canonical_title="长光华芯：硅光集成产线预计2026年底通线 光通信订单起量",
            summary="问题：硅光集成产线预计何时通线，订单何时起量？ 回复：公司硅光集成产线预计2026年底通线，光通信订单正在逐步起量。",
            source="sse_einteractive",
            published_at="2026-04-23T15:02:00+08:00",
            url="https://example.com/sse-keep-substantive-reply",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-sse-stock-price-complaint-csb-1",
            first_seen_at="2026-04-30T18:36:00+08:00",
            last_seen_at="2026-04-30T18:36:00+08:00",
            canonical_title="中国船舶：公司提出所谓 “长期、稳定、可持续” 的股东回报,真是令人啼笑皆非。贵公司在二级市场融资千亿，然分红寥寥。好不容易盼到船市转好，公司旗下半数船厂效率低下，净利率远低于市场水平。以至于被二级市场厌弃，公司能否拿出实际行动出来增持公司股份，做好市值管理，给二级市场信心？",
            summary="问题：公司提出所谓 “长期、稳定、可持续” 的股东回报,真是令人啼笑皆非。贵公司在二级市场融资千亿，然分红寥寥。好不容易盼到船市转好，公司旗下半数船厂效率低下，净利率远低于市场水平。以至于被二级市场厌弃，公司能否拿出实际行动出来增持公司股份，做好市值管理，给二级市场信心？ 回复：您好，感谢您的关注和建议。公司已披露2025年年度报告及2026年第一季度报告。2025年，公司实现归母净利润78.48亿元，同比增长86.00%。2026年一季度，公司实现归母净利润48.32亿元，同比增长251.64%。有关分红方面，2025年，公司每10股派发现金红利3.65元（含税），即派发红利总额2,746,851,770.12元（含税），占公司当年度实现归属于母公司股东净利润的比例达到35.00%，现金分红金额较上年增长145.71%。此外，公司拟综合考虑盈利状况、经营发展、合理回报股东等情况，制定2026年中期现金分红方案，中期现金分红总额预计不低于2026年上半年实现的归属于上市公司股东的净利润的35%，以实际行动切实提升投资者获得感与回报水平，与投资者共享高质量发展成果。谢谢！",
            source="sse_einteractive",
            published_at="2026-04-30T18:36:00+08:00",
            url="https://example.com/sse-stock-price-complaint-csb-1",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-sse-stock-price-complaint-csb-2",
            first_seen_at="2026-04-30T18:35:00+08:00",
            last_seen_at="2026-04-30T18:35:00+08:00",
            canonical_title="中国船舶：尊敬的董秘您好，贵司市值被低估相信贵集团领导也感同身受，当前几乎所有卖方及机构投资者都用订单市值比来对公司进行估值，但这种估值方法似乎只统计公司民船资产的价值，即P/O法估值的分母仅包括民船，所以现在市场对公司军工资产估值似乎为零，投资者理解公司有些信息不能披露，但公司这十几年来涨幅落后于其他军工集团及航运企业，分红和回购力度亦不及其余央企，希望公司不仅要有强军担当，亦要在资本市场做好表率。",
            summary="问题：尊敬的董秘您好，贵司市值被低估相信贵集团领导也感同身受，当前几乎所有卖方及机构投资者都用订单市值比来对公司进行估值，但这种估值方法似乎只统计公司民船资产的价值，即P/O法估值的分母仅包括民船，所以现在市场对公司军工资产估值似乎为零，投资者理解公司有些信息不能披露，但公司这十几年来涨幅落后于其他军工集团及航运企业，分红和回购力度亦不及其余央企，希望公司不仅要有强军担当，亦要在资本市场做好表率。 回复：您好，感谢您的关注和理解。股价涨跌受诸多方面影响，公司高度关注二级市场股价走势，历来重视价值创造、价值经营和价值实现的相关工作，持续强化经营管理，提升核心技术和核心竞争力。我们结合船舶行业景气度上升周期，组织开展了业绩说明会、中小股东开放日活动、“走出去”和“请进来”的路演与反路演、积极开展分红等措施，全力向市场阐述好公司经济价值、功能价值和战略价值，努力推动上市公司市场价值与内在价值相匹配。2025年，公司每10股派发现金红利3.65元（含税），即派发红利总额2,746,851,770.12元（含税），占公司当年度实现归属于母公司股东净利润的比例达到35.00%，现金分红金额较上年增长145.71%。此外，公司拟综合考虑盈利状况、经营发展、合理回报股东等情况，制定2026年中期现金分红方案，中期现金分红总额预计不低于2026年上半年实现的归属于上市公司股东的净利润的35%，以实际行动切实提升投资者获得感与回报水平，与投资者共享高质量发展成果。谢谢！",
            source="sse_einteractive",
            published_at="2026-04-30T18:35:00+08:00",
            url="https://example.com/sse-stock-price-complaint-csb-2",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-sse-stock-price-complaint-antong-1",
            first_seen_at="2026-05-07T18:22:00+08:00",
            last_seen_at="2026-05-07T18:22:00+08:00",
            canonical_title="安通控股：强烈质疑公司管理层不作为：股价连跌，投资者要求回购、降薪、增持，公司只说“二级市场多重因素”，无实质行动",
            summary="问题：强烈质疑公司管理层不作为：股价连跌，投资者要求回购、降薪、增持，公司只说“二级市场多重因素”，无实质行动 回复：尊敬的投资者，您好！公司股价受到宏观经济环境、行业周期以及二级市场波动等诸多因素的综合影响，存在不确定性，公司提醒广大投资者理性投资，注意投资风险！同时，公司管理层也始终重视投资者的利益，将继续专注主业，增强业务优势，坚持以提升公司经营业绩和企业价值作为长期工作重点，力争以优良的业绩回报广大投资者。感谢您的关注！",
            source="sse_einteractive",
            published_at="2026-05-07T18:22:00+08:00",
            url="https://example.com/sse-stock-price-complaint-antong-1",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-stock-price-complaint-antong-2",
            first_seen_at="2026-05-07T18:22:00+08:00",
            last_seen_at="2026-05-07T18:22:00+08:00",
            canonical_title="安通控股：公司如此二级市场存在财务虚报配合股东压价增持让无信息资源小散投资者接盘？安通控股一季度营业收入约21.20亿元，同比增长3.83%；净利润约2.54亿元，同比增长5.12%。",
            summary="问题：公司如此二级市场存在财务虚报配合股东压价增持让无信息资源小散投资者接盘？安通控股一季度营业收入约21.20亿元，同比增长3.83%；净利润约2.54亿元，同比增长5.12%。 回复：尊敬的投资者，您好！公司的经营管理情况一切正常，公司股价受到宏观经济环境、行业周期以及二级市场波动等诸多因素的综合影响，存在不确定性。有关公司的经营业绩，请关注公司发布的定期报告。感谢您的关注！",
            source="sse_einteractive",
            published_at="2026-05-07T18:22:00+08:00",
            url="https://example.com/sse-stock-price-complaint-antong-2",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-sse-stock-price-complaint-jinggong-1",
            first_seen_at="2026-05-07T18:22:00+08:00",
            last_seen_at="2026-05-07T18:22:00+08:00",
            canonical_title="精工钢构：2020年高调提出的“十年千亿产值”按时间节点严重不及预期；“大力拓展EPc营收占比”严重不达预期；“努力提升公司估值”效果更加不达预期；2023年至今连续3年扣非净利润下滑，“业绩向好”从何说起；2022年每股净资产较目前低许多，公司能以均价4.39元回购1亿元，如今4元以下却无动于衷，管理层知行合一在哪里？……请问：这里面哪一个不是基于客观事实的反馈？",
            summary="问题：2020年高调提出的“十年千亿产值”按时间节点严重不及预期；“大力拓展EPc营收占比”严重不达预期；“努力提升公司估值”效果更加不达预期；2023年至今连续3年扣非净利润下滑，“业绩向好”从何说起；2022年每股净资产较目前低许多，公司能以均价4.39元回购1亿元，如今4元以下却无动于衷，管理层知行合一在哪里？……请问：这里面哪一个不是基于客观事实的反馈？ 回复：尊敬的投资者您好，公司始终尊重并重视投资者的反馈，感谢您的关注。",
            source="sse_einteractive",
            published_at="2026-05-07T18:22:00+08:00",
            url="https://example.com/sse-stock-price-complaint-jinggong-1",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-sse-investor-relations-complaint-1",
            first_seen_at="2026-05-08T18:28:00+08:00",
            last_seen_at="2026-05-08T18:28:00+08:00",
            canonical_title="航天晨光：关注到公司近期在资本市场的口碑受前期 IR 回复效率及减持信披一致性的影响有所波动。作为长期关注公司的投资者，想请问：公司是否意识到前期投资者沟通工作中存在的疏漏？对于高点发布减持后又未实施的情况，公司管理层如何向市场传达信披的权威性与一致性？",
            summary="问题：关注到公司近期在资本市场的口碑受前期 IR 回复效率及减持信披一致性的影响有所波动。作为长期关注公司的投资者，想请问：公司是否意识到前期投资者沟通工作中存在的疏漏？对于高点发布减持后又未实施的情况，公司管理层如何向市场传达信披的权威性与一致性？ 回复：您好，公司将继续强化投资者关系管理工作，与投资者建立良好的双向互动关系。公司高管发布减持计划或者是否实施均符合相关监管规定，感谢您的监督和建议。",
            source="sse_einteractive",
            published_at="2026-05-08T18:28:00+08:00",
            url="https://example.com/sse-investor-relations-complaint-1",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-investor-relations-complaint-2",
            first_seen_at="2026-05-08T18:26:00+08:00",
            last_seen_at="2026-05-08T18:26:00+08:00",
            canonical_title="航天晨光：请问公司面对投资者质疑董秘无力履职，对于投资者提问选择投诉，是否合规？",
            summary="问题：请问公司面对投资者质疑董秘无力履职，对于投资者提问选择投诉，是否合规？ 回复：您好，公司将继续强化投资者关系管理工作，加强与投资者沟通与服务，保护投资者合法权益。谢谢关注。",
            source="sse_einteractive",
            published_at="2026-05-08T18:26:00+08:00",
            url="https://example.com/sse-investor-relations-complaint-2",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-keep-substantive-jinggong-1",
            first_seen_at="2026-05-07T18:22:00+08:00",
            last_seen_at="2026-05-07T18:22:00+08:00",
            canonical_title="精工钢构：您好，请问贵公司的业务是否涉及数据中心及火箭发射厂的基础设施建设，业务体量如何，目前国内低空经济，算力设施，深空深海深地等建设均离不开基础设施，贵公司是如何把握机会的",
            summary="问题：您好，请问贵公司的业务是否涉及数据中心及火箭发射厂的基础设施建设，业务体量如何，目前国内低空经济，算力设施，深空深海深地等建设均离不开基础设施，贵公司是如何把握机会的 回复：尊敬的投资者，您好。公司业务已覆盖数据中心、火箭发射厂等基础设施建设，主要负责钢结构相关业务，属于公司主营业务范畴。后续公司将持续关注国家政策导向，积极关注新兴赛道建设需求，依托钢结构主业技术优势与工程经验，主动挖掘业务合作机会，培育新的业绩增长点。",
            source="sse_einteractive",
            published_at="2026-05-07T18:22:00+08:00",
            url="https://example.com/sse-keep-substantive-jinggong-1",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-sse-stock-price-complaint-1", direction="neutral", impact_score=99.9, reasoning="rule", themes=["绿电"], triggered=True),
        EventAnalysis(event_id="event-sse-stock-price-complaint-2", direction="neutral", impact_score=99.9, reasoning="rule", themes=["电力"], triggered=True),
        EventAnalysis(event_id="event-sse-keep-substantive-reply", direction="bullish", impact_score=99.9, reasoning="rule", themes=["光通信"], triggered=True),
        EventAnalysis(event_id="event-sse-stock-price-complaint-csb-1", direction="bullish", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-stock-price-complaint-csb-2", direction="bullish", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-stock-price-complaint-antong-1", direction="bearish", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-stock-price-complaint-antong-2", direction="bullish", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-stock-price-complaint-jinggong-1", direction="bearish", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-investor-relations-complaint-1", direction="bullish", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-investor-relations-complaint-2", direction="bullish", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-keep-substantive-jinggong-1", direction="bullish", impact_score=99.9, reasoning="rule", themes=["算力"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "大跌的原因是什么" not in content
    assert "请董秘给个解释" not in content
    assert "二级市场融资千亿" not in content
    assert "贵司市值被低估" not in content
    assert "强烈质疑公司管理层不作为" not in content
    assert "财务虚报配合股东压价增持" not in content
    assert "十年千亿产值" not in content
    assert "IR 回复效率及减持信披一致性" not in content
    assert "质疑董秘无力履职" not in content
    assert "业务是否涉及数据中心及火箭发射厂" in content


def test_write_text_report_filters_current_live_equity_incentive_review_opinion_without_hiding_exercise_notice(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-equity-incentive-review-opinion-current",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="中文在线：第六届董事会薪酬与考核委员会关于公司股权激励计划相关事项的核查意见",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/equity-incentive-review-opinion-current",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-keep-equity-incentive-exercise-current",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="上海电力股份有限公司关于首期股票期权激励计划预留授予部分股票期权第二个行权期自主行权实施公告",
            summary="summary",
            source="sse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/keep-equity-incentive-exercise-current",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-equity-incentive-review-opinion-current", direction="neutral", impact_score=100.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-equity-incentive-exercise-current", direction="bullish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "股权激励计划相关事项的核查意见" not in content
    assert "第二个行权期自主行权实施公告" in content


def test_write_text_report_filters_cls_investment_sentiment_roundup_without_hiding_substantive_order_progress(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-investment-sentiment-roundup",
            first_seen_at="2026-04-23T16:00:00+08:00",
            last_seen_at="2026-04-23T16:00:00+08:00",
            canonical_title="今日投资舆情热点",
            summary=(
                "【今日投资舆情热点】 1）芯片产业链：三星、海力士称光刻胶等产品原材料的采购环节已出现中断；"
                "近期，氦气、靶材、掩模版等上游材料价格持续走高。"
                " 2）电力：工信部表示，正在开展算电协同政策研究和标准制定。"
                " 3）算力租赁：今年以来，高端GPU租约价格持续上涨，头部算租厂商营收与订单双爆发。"
                " 4）业绩超预期：4月底，上市公司大规模披露业绩，部分超预期个股受到市场关注。"
            ),
            source="cls",
            published_at="2026-04-23T16:00:00+08:00",
            url="https://example.com/cls-investment-sentiment-roundup",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-cls-venture-financing-weekly-roundup",
            first_seen_at="2026-05-09T10:40:01+08:00",
            last_seen_at="2026-05-09T10:40:01+08:00",
            canonical_title="财联社创投通：一级市场本周融资总额约356.34亿元 大模型融资额居前",
            summary=(
                "【财联社创投通：一级市场本周融资总额约356.34亿元 大模型融资额居前】"
                "《科创板日报》9日讯，据财联社创投通数据，本周国内统计口径内共发生66起投融资事件，"
                "已披露的融资总额合计约356.34亿元。从投资事件数量来看，先进制造、人工智能、医疗健康、"
                "集成电路、企业服务等领域较活跃；从融资总额来看，人工智能披露的融资总额最多。"
            ),
            source="cls",
            published_at="2026-05-09T10:40:01+08:00",
            url="https://example.com/cls-venture-financing-weekly-roundup",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-keep-substantive-dbs-progress",
            first_seen_at="2026-04-23T16:01:00+08:00",
            last_seen_at="2026-04-23T16:01:00+08:00",
            canonical_title="乐普医疗：请公司介绍下DBS产品订单情况、入院数量、医保落地进展情况等，谢谢。",
            summary=(
                "问题：请公司介绍下DBS产品订单情况、入院数量、医保落地进展情况等，谢谢。"
                " 回复：DBS目前处于商业化初期，公司正积极推动该产品的入院及临床植入工作。"
            ),
            source="irm_cninfo",
            published_at="2026-04-23T16:01:00+08:00",
            url="https://example.com/keep-substantive-dbs-progress",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cls-investment-sentiment-roundup",
            direction="bullish",
            impact_score=99.3,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-venture-financing-weekly-roundup",
            direction="neutral",
            impact_score=99.3,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-substantive-dbs-progress",
            direction="bullish",
            impact_score=98.6,
            reasoning="rule",
            themes=["脑机接口"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "今日投资舆情热点" not in content
    assert "一级市场本周融资总额" not in content
    assert "DBS产品订单情况、入院数量、医保落地进展情况" in content


def test_write_text_report_filters_current_live_restructuring_impairment_audit_report_without_hiding_revocation(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-restructuring-impairment-audit-report",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="会计师事务所关于电投水电重大资产重组标的减值测试报告的专项审核报告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/restructuring-impairment-audit-report",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-keep-delisting-revocation",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="*ST荣控：荣丰控股集团关于申请撤销对公司股票交易实施退市风险警示的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/keep-delisting-revocation-2",
            event_type="hard_event",
            event_subtype="delisting_risk",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-restructuring-impairment-audit-report", direction="neutral", impact_score=80.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-delisting-revocation", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "会计师事务所关于电投水电重大资产重组标的减值测试报告的专项审核报告" not in content
    assert "*ST荣控：荣丰控股集团关于申请撤销对公司股票交易实施退市风险警示的公告" in content


def test_write_text_report_filters_current_live_equity_incentive_unmet_exercise_condition_notice(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-asia-tech-unmet-exercise-condition",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="亚太科技：关于第一期股票期权和限制性股票激励计划第三个行权期行权条件未成就及注销部分股票期权的公告",
            summary="亚太科技：关于第一期股票期权和限制性股票激励计划第三个行权期行权条件未成就及注销部分股票期权的公告",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/asia-tech-unmet-exercise-condition",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-keep-delisting-risk-asia-tech-window",
            first_seen_at="2026-04-21T00:01:00+08:00",
            last_seen_at="2026-04-21T00:01:00+08:00",
            canonical_title="奥特迅：关于股票交易被实施退市风险警示暨股票停牌的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:01:00+08:00",
            url="https://example.com/keep-delisting-risk-asia-tech-window",
            event_type="hard_event",
            event_subtype="delisting_risk",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-asia-tech-unmet-exercise-condition", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-delisting-risk-asia-tech-window", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "亚太科技：关于第一期股票期权和限制性股票激励计划第三个行权期行权条件未成就及注销部分股票期权的公告" not in content
    assert "奥特迅：关于股票交易被实施退市风险警示暨股票停牌的公告" in content


def test_write_text_report_filters_current_live_equity_incentive_committee_verification_notice(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-gltc-equity-incentive-verification",
            first_seen_at="2026-04-21T00:00:00+08:00",
            last_seen_at="2026-04-21T00:00:00+08:00",
            canonical_title="光大同创：董事会薪酬与考核委员会关于2024年限制性股票激励计划有关事项的核查意见",
            summary="光大同创：董事会薪酬与考核委员会关于2024年限制性股票激励计划有关事项的核查意见",
            source="szse",
            published_at="2026-04-21T00:00:00+08:00",
            url="https://example.com/gltc-equity-incentive-verification",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-keep-delisting-risk-gltc-window",
            first_seen_at="2026-04-21T00:01:00+08:00",
            last_seen_at="2026-04-21T00:01:00+08:00",
            canonical_title="奥特迅：关于股票交易被实施退市风险警示暨股票停牌的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-21T00:01:00+08:00",
            url="https://example.com/keep-delisting-risk-gltc-window",
            event_type="hard_event",
            event_subtype="delisting_risk",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-gltc-equity-incentive-verification", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-delisting-risk-gltc-window", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "光大同创：董事会薪酬与考核委员会关于2024年限制性股票激励计划有关事项的核查意见" not in content
    assert "奥特迅：关于股票交易被实施退市风险警示暨股票停牌的公告" in content


def test_write_text_report_filters_restructuring_performance_commitment_audit_report_without_hiding_delisting_risk(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-szse-restructuring-performance-audit",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="维业股份：关于重大资产重组业绩承诺实现情况说明专项审核报告维业-信会师报字[2026]第ZM10552号",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-restructuring-performance-audit",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-keep-delisting-risk",
            first_seen_at="2026-04-15T00:01:00+08:00",
            last_seen_at="2026-04-15T00:01:00+08:00",
            canonical_title="ST中青宝：关于撤销其他风险警示暨股票停复牌的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:01:00+08:00",
            url="https://example.com/keep-delisting-risk",
            event_type="hard_event",
            event_subtype="delisting_risk",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-szse-restructuring-performance-audit",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-delisting-risk",
            direction="bearish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "ST中青宝：关于撤销其他风险警示暨股票停复牌的公告" in content
    assert "维业股份：关于重大资产重组业绩承诺实现情况说明专项审核报告维业-信会师报字[2026]第ZM10552号" not in content


def test_write_text_report_keeps_cls_morning_brief_column_for_global_news_collection(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-morning-brief",
            first_seen_at="2026-04-14T21:24:04+08:00",
            last_seen_at="2026-04-14T21:24:04+08:00",
            canonical_title="【财联社早知道】重大突破！我国最大规模科学智能计算集群投入使用，机构称AI应用持续发展正推动算力需求维持高位，这家公司子公司运营着全国最大C端AI算力云平台",
            summary="①重大突破！我国最大规模科学智能计算集群投入使用；②国办发布健全药品价格形成机制的若干意见；③这家公司截至目前算力业务规模已超过4000P。",
            source="cls",
            published_at="2026-04-14T21:24:04+08:00",
            url="https://www.cls.cn/detail/2343479",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-cls-keep-acquisition",
            first_seen_at="2026-04-14T21:14:22+08:00",
            last_seen_at="2026-04-14T21:14:22+08:00",
            canonical_title="杭可科技：拟1.79亿元增资杭可仪器获51%股权",
            summary="财联社4月14日电，公司拟增资杭可仪器并将其纳入合并报表范围。",
            source="cls",
            published_at="2026-04-14T21:14:22+08:00",
            url="https://www.cls.cn/detail/2344008",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cls-morning-brief",
            direction="bullish",
            impact_score=99.3,
            reasoning="rule",
            themes=["算力", "AI应用"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-keep-acquisition",
            direction="neutral",
            impact_score=99.3,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "杭可科技：拟1.79亿元增资杭可仪器获51%股权" in content
    assert "【财联社早知道】重大突破！我国最大规模科学智能计算集群投入使用" in content


def test_write_text_report_filters_cls_morning_brief_anonymous_pick_column_without_hiding_substantive_item(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-morning-brief-anonymous-pick",
            first_seen_at="2026-04-20T21:21:14+08:00",
            last_seen_at="2026-04-20T21:21:14+08:00",
            canonical_title="【财联社早知道】机构预估2026年全球AI光收发模块市场规模达260亿美元，关键零部件吃紧成扩产瓶颈，分析师称AI爆炸式增长为光模块带来了长期的增长动力，这家公司为头部客户提供CPO光互连解决方案",
            summary="①机构预估2026年全球AI光收发模块市场规模达260亿美元；②机构称AI应用即将在2026年迎来商业化拐点，这家公司在多个业务场景深化AI应用落地；③这家公司深耕电子元器件领域60余年。",
            source="cls",
            published_at="2026-04-20T21:21:14+08:00",
            url="https://example.com/cls-morning-brief-anonymous-pick",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-keep-policy-signal-column-test",
            first_seen_at="2026-04-20T20:24:07+08:00",
            last_seen_at="2026-04-20T20:24:07+08:00",
            canonical_title="广东：要用好产业引导基金 加大对集成电路、具身智能、算电协同等领域的投资",
            summary="summary",
            source="cls",
            published_at="2026-04-20T20:24:07+08:00",
            url="https://example.com/keep-policy-signal-column-test",
            event_type="fast_news",
            event_subtype="policy_signal",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-cls-morning-brief-anonymous-pick", direction="bullish", impact_score=99.3, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-keep-policy-signal-column-test", direction="bullish", impact_score=99.3, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "【财联社早知道】机构预估2026年全球AI光收发模块市场规模达260亿美元" not in content
    assert "广东：要用好产业引导基金 加大对集成电路、具身智能、算电协同等领域的投资" in content


def test_write_text_report_keeps_cls_overseas_aviation_fuel_story_for_global_news_collection(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-aviation-fuel-story",
            first_seen_at="2026-04-14T21:16:23+08:00",
            last_seen_at="2026-04-14T21:16:23+08:00",
            canonical_title="五一假期国际航班遭大规模取消？专家：燃油成本大涨为主因 国际低成本航司压力更大",
            summary="财联社4月14日电，多位网友称飞往东南亚及大洋洲航班被取消。专家表示核心原因在于航空燃油成本大幅攀升，国际低成本航司压力更大。",
            source="cls",
            published_at="2026-04-14T21:16:23+08:00",
            url="https://www.cls.cn/detail/2344010",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-cls-keep-acquisition",
            first_seen_at="2026-04-14T21:14:22+08:00",
            last_seen_at="2026-04-14T21:14:22+08:00",
            canonical_title="杭可科技：拟1.79亿元增资杭可仪器获51%股权",
            summary="财联社4月14日电，公司拟增资杭可仪器并将其纳入合并报表范围。",
            source="cls",
            published_at="2026-04-14T21:14:22+08:00",
            url="https://www.cls.cn/detail/2344008",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cls-aviation-fuel-story",
            direction="neutral",
            impact_score=74.3,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-keep-acquisition",
            direction="neutral",
            impact_score=99.3,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "杭可科技：拟1.79亿元增资杭可仪器获51%股权" in content
    assert "五一假期国际航班遭大规模取消？专家：燃油成本大涨为主因 国际低成本航司压力更大" in content


def test_write_text_report_keeps_cls_foreign_index_fast_news_for_global_news_collection(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-us-index-open",
            first_seen_at="2026-04-14T21:30:50+08:00",
            last_seen_at="2026-04-14T21:30:50+08:00",
            canonical_title="美股三大指数小幅高开",
            summary="财联社4月14日电，美股三大指数小幅高开，道指涨0.1%，纳指涨0.71%，标普500指数涨0.32%。GoPro大涨超19%；美国航空涨超7%。",
            source="cls",
            published_at="2026-04-14T21:30:50+08:00",
            url="https://www.cls.cn/detail/2344018",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-cls-china-concept-index-open",
            first_seen_at="2026-04-14T21:31:37+08:00",
            last_seen_at="2026-04-14T21:31:37+08:00",
            canonical_title="利弗莫尔中概股龙头指数盘初涨1%",
            summary="财联社4月14日电，利弗莫尔中概股龙头指数盘初涨幅扩大至1%，报9648.25点。成分股中，金山云涨4.54%，京东涨3.33%。",
            source="cls",
            published_at="2026-04-14T21:31:37+08:00",
            url="https://www.cls.cn/detail/2344020",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-cls-keep-acquisition",
            first_seen_at="2026-04-14T21:14:22+08:00",
            last_seen_at="2026-04-14T21:14:22+08:00",
            canonical_title="杭可科技：拟1.79亿元增资杭可仪器获51%股权",
            summary="财联社4月14日电，公司拟增资杭可仪器并将其纳入合并报表范围。",
            source="cls",
            published_at="2026-04-14T21:14:22+08:00",
            url="https://www.cls.cn/detail/2344008",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cls-us-index-open",
            direction="neutral",
            impact_score=74.3,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-china-concept-index-open",
            direction="neutral",
            impact_score=74.3,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-keep-acquisition",
            direction="neutral",
            impact_score=99.3,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "杭可科技：拟1.79亿元增资杭可仪器获51%股权" in content
    assert "美股三大指数小幅高开" in content
    assert "利弗莫尔中概股龙头指数盘初涨1%" in content


def test_write_text_report_keeps_cls_single_stock_market_move_for_global_news_collection(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-cls-foreign-single-stock-move",
            first_seen_at="2026-04-14T21:33:57+08:00",
            last_seen_at="2026-04-14T21:33:57+08:00",
            canonical_title="财联社4月14日电，富国银行股价下跌6%，创一个月来最大跌幅。",
            summary="财联社4月14日电，富国银行股价下跌6%，创一个月来最大跌幅。",
            source="cls",
            published_at="2026-04-14T21:33:57+08:00",
            url="https://www.cls.cn/detail/2344024",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-cls-keep-acquisition",
            first_seen_at="2026-04-14T21:14:22+08:00",
            last_seen_at="2026-04-14T21:14:22+08:00",
            canonical_title="杭可科技：拟1.79亿元增资杭可仪器获51%股权",
            summary="财联社4月14日电，公司拟增资杭可仪器并将其纳入合并报表范围。",
            source="cls",
            published_at="2026-04-14T21:14:22+08:00",
            url="https://www.cls.cn/detail/2344008",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-cls-foreign-single-stock-move",
            direction="neutral",
            impact_score=74.3,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-keep-acquisition",
            direction="neutral",
            impact_score=99.3,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "杭可科技：拟1.79亿元增资杭可仪器获51%股权" in content
    assert "富国银行股价下跌6%" in content


def test_write_text_report_filters_latest_live_exchange_noise_variants(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-sse-equity-unlock-listing",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="华润双鹤关于公司2021年限制性股票激励计划首次授予部分第三个解除限售期解锁暨限制性股票上市公告",
            summary="summary",
            source="sse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/sse-equity-unlock-listing",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-sse-order-signing-brief",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="上海建工2026年一季度新签合同情况公告",
            summary="summary",
            source="sse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/sse-order-signing-brief",
            event_type="hard_event",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-szse-restructuring-risk-tip",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="永达股份：关于披露重组报告书暨一般风险提示性公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-restructuring-risk-tip",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-szse-restructuring-review-opinion",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="永达股份：国金证券股份有限公司关于本次交易符合《上市公司重大资产重组管理办法》第十一条、第四十三条及第四十四条规定的核查意见",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-restructuring-review-opinion",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-keep-delisting-revocation",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="*ST中地：关于申请撤销公司股票退市风险警示的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/keep-delisting-revocation",
            event_type="hard_event",
            event_subtype="delisting_risk",
        ),
        Event(
            event_id="event-szse-option-cancel",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="纳思达：关于注销2024年股票期权激励计划部分股票期权的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-option-cancel",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-equity-grant",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="哈尔斯：关于向激励对象授予限制性股票的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-equity-grant",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-compliance-opinion",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="永达股份：国金证券股份有限公司关于本次交易符合《关于加强证券公司在投资银行类业务中聘请第三方等廉洁从业风险防控的意见》相关规定的核查意见",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-compliance-opinion",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-etf-flow",
            first_seen_at="2026-04-15T07:16:10+08:00",
            last_seen_at="2026-04-15T07:16:10+08:00",
            canonical_title="ETF资金流向分化 公募策略趋于多元",
            summary="summary",
            source="stcn",
            published_at="2026-04-15T07:16:10+08:00",
            url="https://example.com/stcn-etf-flow",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-szse-reorganization-investment-agreement",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="美年健康：关于签署《重整投资协议》的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/szse-reorganization-investment-agreement",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-sse-equity-unlock-listing",
            direction="bearish",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-sse-order-signing-brief",
            direction="neutral",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-restructuring-risk-tip",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-restructuring-review-opinion",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-delisting-revocation",
            direction="bullish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-option-cancel",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-equity-grant",
            direction="bearish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-compliance-opinion",
            direction="bearish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-stcn-etf-flow",
            direction="neutral",
            impact_score=74.0,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-szse-reorganization-investment-agreement",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "华润双鹤关于公司2021年限制性股票激励计划首次授予部分第三个解除限售期解锁暨限制性股票上市公告" not in content
    assert "上海建工2026年一季度新签合同情况公告" not in content
    assert "永达股份：关于披露重组报告书暨一般风险提示性公告" not in content
    assert "永达股份：国金证券股份有限公司关于本次交易符合《上市公司重大资产重组管理办法》第十一条、第四十三条及第四十四条规定的核查意见" not in content
    assert "纳思达：关于注销2024年股票期权激励计划部分股票期权的公告" not in content
    assert "哈尔斯：关于向激励对象授予限制性股票的公告" not in content
    assert "永达股份：国金证券股份有限公司关于本次交易符合《关于加强证券公司在投资银行类业务中聘请第三方等廉洁从业风险防控的意见》相关规定的核查意见" not in content
    assert "ETF资金流向分化 公募策略趋于多元" not in content
    assert "美年健康：关于签署《重整投资协议》的公告" not in content


def test_write_text_report_deprioritizes_cls_global_information_below_direct_catalysts(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-control-change",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告",
            summary="公司推进控制权收购事项。",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/control-change",
            event_type="hard_event",
            event_subtype="control_change",
        ),
        Event(
            event_id="event-cls-industry-data",
            first_seen_at="2026-04-15T12:48:23+08:00",
            last_seen_at="2026-04-15T12:48:23+08:00",
            canonical_title="韩国3月汽车出口额为63.7亿美元 同比增长2.2%",
            summary="summary",
            source="cls",
            published_at="2026-04-15T12:48:23+08:00",
            url="https://example.com/cls-industry-data",
            event_type="fast_news",
            event_subtype="industry_data",
        ),
        Event(
            event_id="event-cls-general-fast-news",
            first_seen_at="2026-04-15T13:07:55+08:00",
            last_seen_at="2026-04-15T13:07:55+08:00",
            canonical_title="财联社4月15日电，韩国总统府官员称，已从海外确保获得2.73亿桶原油供应。",
            summary="summary",
            source="cls",
            published_at="2026-04-15T13:07:55+08:00",
            url="https://example.com/cls-general-fast-news",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-delisting-risk",
            first_seen_at="2026-04-15T00:00:00+08:00",
            last_seen_at="2026-04-15T00:00:00+08:00",
            canonical_title="*ST中地：关于申请撤销公司股票退市风险警示的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-15T00:00:00+08:00",
            url="https://example.com/delisting-risk",
            event_type="hard_event",
            event_subtype="delisting_risk",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-control-change",
            direction="bullish",
            impact_score=100.0,
            reasoning="rule",
            themes=["半导体"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-industry-data",
            direction="bullish",
            impact_score=99.3,
            reasoning="rule",
            themes=["新能源车"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-cls-general-fast-news",
            direction="neutral",
            impact_score=79.3,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-delisting-risk",
            direction="bullish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    control_change_pos = content.index("盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告")
    delisting_risk_pos = content.index("*ST中地：关于申请撤销公司股票退市风险警示的公告")
    cls_industry_data_pos = content.index("韩国3月汽车出口额为63.7亿美元 同比增长2.2%")
    cls_general_fast_news_pos = content.index("财联社4月15日电，韩国总统府官员称，已从海外确保获得2.73亿桶原油供应。")

    assert control_change_pos < delisting_risk_pos
    assert delisting_risk_pos < cls_industry_data_pos
    assert delisting_risk_pos < cls_general_fast_news_pos
    assert "*ST中地：关于申请撤销公司股票退市风险警示的公告" in content


def test_write_text_report_appends_social_signal_section_without_affecting_main_entries(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-1",
            first_seen_at="2026-04-22T09:30:00+08:00",
            last_seen_at="2026-04-22T09:30:00+08:00",
            canonical_title="吉利将于2026北京车展发布中国首台原生Robotaxi原型车",
            summary="summary",
            source="stcn",
            published_at="2026-04-22T09:30:00+08:00",
            url="https://example.com/robotaxi",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-1",
            direction="bullish",
            impact_score=88.0,
            reasoning="rule",
            themes=["智能驾驶"],
            triggered=True,
        ),
    ]
    social_signals = [
        SocialSignal(
            event_id="event-1",
            platform="weibo",
            captured_at="2026-04-22T09:35:00+08:00",
            heat_score=82.0,
            heat_delta=18.0,
            co_mentioned_themes=["Robotaxi", "智能驾驶"],
            sample_posts=["北京车展 Robotaxi 关注度升温"],
        )
    ]

    write_text_report(paths, events, analyses, social_signals=social_signals)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "[关注] 吉利将于2026北京车展发布中国首台原生Robotaxi原型车" in content
    assert "[社交热度观察]" in content
    assert "平台: weibo" in content
    assert "热度: 82.0" in content
    assert "增速: +18.0" in content
    assert "共现题材: Robotaxi, 智能驾驶" in content


def test_write_text_report_groups_entries_into_global_multisource_sections(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-ashare",
            first_seen_at="2026-04-22T09:30:00+08:00",
            last_seen_at="2026-04-22T09:30:00+08:00",
            canonical_title="中科曙光签署算力合作协议公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-22T09:30:00+08:00",
            url="https://example.com/ashare",
            event_type="hard_event",
            event_subtype="cooperation_agreement",
        ),
        Event(
            event_id="event-domestic-policy",
            first_seen_at="2026-04-22T09:31:00+08:00",
            last_seen_at="2026-04-22T09:31:00+08:00",
            canonical_title="工业和信息化部发布节能装备实施方案",
            summary="summary",
            source="miit",
            published_at="2026-04-22T09:31:00+08:00",
            url="https://example.com/domestic-policy",
            event_type="policy",
            event_subtype="policy_update",
        ),
        Event(
            event_id="event-global-policy",
            first_seen_at="2026-04-22T09:32:00+08:00",
            last_seen_at="2026-04-22T09:32:00+08:00",
            canonical_title="Federal Reserve releases supervisory update",
            summary="summary",
            source="fed",
            published_at="2026-04-22T09:32:00+08:00",
            url="https://example.com/global-policy",
            event_type="policy",
            event_subtype="policy_update",
        ),
        Event(
            event_id="event-global-market",
            first_seen_at="2026-04-22T09:33:00+08:00",
            last_seen_at="2026-04-22T09:33:00+08:00",
            canonical_title="WTI crude rises above $86 per barrel",
            summary="summary",
            source="investing_news",
            published_at="2026-04-22T09:33:00+08:00",
            url="https://example.com/global-market",
            event_type="fast_news",
            event_subtype="market_move",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-ashare",
            direction="bullish",
            impact_score=92.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-domestic-policy",
            direction="bullish",
            impact_score=85.0,
            reasoning="rule",
            themes=["节能装备"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-global-policy",
            direction="bullish",
            impact_score=83.0,
            reasoning="rule",
            themes=["金融监管"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-global-market",
            direction="bullish",
            impact_score=81.0,
            reasoning="rule",
            themes=["油气"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    ashare_section = content.index("[A股强催化]")
    domestic_section = content.index("[国内政策与监管]")
    global_policy_section = content.index("[全球政策与监管]")
    global_market_section = content.index("[全球市场与商品]")

    assert ashare_section < domestic_section < global_policy_section < global_market_section
    assert content.index("中科曙光签署算力合作协议公告") > ashare_section
    assert content.index("工业和信息化部发布节能装备实施方案") > domestic_section
    assert content.index("Federal Reserve releases supervisory update") > global_policy_section
    assert content.index("WTI crude rises above $86 per barrel") > global_market_section


def test_write_text_report_keeps_social_section_after_mainline_sections(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-ashare",
            first_seen_at="2026-04-22T09:30:00+08:00",
            last_seen_at="2026-04-22T09:30:00+08:00",
            canonical_title="长亮科技中标某股份制银行新网贷服务平台项目",
            summary="summary",
            source="stcn",
            published_at="2026-04-22T09:30:00+08:00",
            url="https://example.com/order",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-ashare",
            direction="bullish",
            impact_score=88.0,
            reasoning="rule",
            themes=["金融科技"],
            triggered=True,
        ),
    ]
    social_signals = [
        SocialSignal(
            event_id="event-ashare",
            platform="weibo",
            captured_at="2026-04-22T09:35:00+08:00",
            heat_score=82.0,
            heat_delta=18.0,
            co_mentioned_themes=["金融科技"],
            sample_posts=["银行IT项目热度升温"],
        )
    ]

    write_text_report(paths, events, analyses, social_signals=social_signals)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert content.index("[A股强催化]") < content.index("[社交热度观察]")


def test_write_text_report_filters_investor_qa_and_exchange_material_within_ashare_section(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-order",
            first_seen_at="2026-04-22T09:30:00+08:00",
            last_seen_at="2026-04-22T09:30:00+08:00",
            canonical_title="长亮科技中标某股份制银行新网贷服务平台项目",
            summary="summary",
            source="stcn",
            published_at="2026-04-22T09:30:00+08:00",
            url="https://example.com/order",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-legal",
            first_seen_at="2026-04-22T09:31:00+08:00",
            last_seen_at="2026-04-22T09:31:00+08:00",
            canonical_title="ST岭南：关于重大诉讼的进展公告",
            summary="summary",
            source="szse",
            published_at="2026-04-22T09:31:00+08:00",
            url="https://example.com/legal",
            event_type="hard_event",
            event_subtype="legal_dispute",
        ),
        Event(
            event_id="event-irm",
            first_seen_at="2026-04-22T09:32:00+08:00",
            last_seen_at="2026-04-22T09:32:00+08:00",
            canonical_title="快可电子：董秘您好，有看到公司在招聘网站上招聘光模块技术人员，请问公司目前有哪些光模块产品，谢谢",
            summary="summary",
            source="irm_cninfo",
            published_at="2026-04-22T09:32:00+08:00",
            url="https://example.com/irm",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-material",
            first_seen_at="2026-04-22T09:33:00+08:00",
            last_seen_at="2026-04-22T09:33:00+08:00",
            canonical_title="北京市大龙伟业房地产开发股份有限公司2025年年度股东会会议资料",
            summary="summary",
            source="sse",
            published_at="2026-04-22T09:33:00+08:00",
            url="https://example.com/material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-order",
            direction="bullish",
            impact_score=88.0,
            reasoning="rule",
            themes=["金融科技"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-legal",
            direction="bearish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-irm",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["算力"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-material",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["房地产"],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "长亮科技中标某股份制银行新网贷服务平台项目" in content
    assert "ST岭南：关于重大诉讼的进展公告" in content
    assert "快可电子：董秘您好，有看到公司在招聘网站上招聘光模块技术人员，请问公司目前有哪些光模块产品，谢谢" not in content
    assert "北京市大龙伟业房地产开发股份有限公司2025年年度股东会会议资料" not in content


def test_write_text_report_filters_live_weak_investor_qa_variants_without_hiding_substantive_catalyst(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-keep-order",
            first_seen_at="2026-04-22T09:30:00+08:00",
            last_seen_at="2026-04-22T09:30:00+08:00",
            canonical_title="长亮科技中标某股份制银行新网贷服务平台项目",
            summary="summary",
            source="stcn",
            published_at="2026-04-22T09:30:00+08:00",
            url="https://example.com/order",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-disclosure",
            first_seen_at="2026-04-22T14:24:02+08:00",
            last_seen_at="2026-04-22T14:24:02+08:00",
            canonical_title="强达电路：董秘您好，贵公司南通强达电路工厂已开工投产，为什么一直不正式公告披露呢？还一直回复预计Q2投产，我朋友南通强达普工已经开工PCB打样了。",
            summary="summary",
            source="irm_cninfo",
            published_at="2026-04-22T14:24:02+08:00",
            url="https://example.com/irm-disclosure",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-recruitment",
            first_seen_at="2026-04-22T14:22:02+08:00",
            last_seen_at="2026-04-22T14:22:02+08:00",
            canonical_title="快可电子：董秘您好，有看到公司在招聘网站上招聘光模块技术人员，请问公司目前有哪些光模块产品，谢谢",
            summary="summary",
            source="irm_cninfo",
            published_at="2026-04-22T14:22:02+08:00",
            url="https://example.com/irm-recruitment",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-sample",
            first_seen_at="2026-04-22T14:20:02+08:00",
            last_seen_at="2026-04-22T14:20:02+08:00",
            canonical_title="精锻科技：请问机器人样品送这么久了，发展到哪一步了？",
            summary="summary",
            source="irm_cninfo",
            published_at="2026-04-22T14:20:02+08:00",
            url="https://example.com/irm-sample",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-cooperation",
            first_seen_at="2026-04-21T18:15:00+08:00",
            last_seen_at="2026-04-21T18:15:00+08:00",
            canonical_title="合锻智能：董秘您好，查询发现公司子公司合肥汇智主要产品为光模块核心结构件，请问该光模块产品与哪些厂商有合作？",
            summary="summary",
            source="sse_einteractive",
            published_at="2026-04-21T18:15:00+08:00",
            url="https://example.com/sse-cooperation",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-keep-order", direction="bullish", impact_score=88.0, reasoning="rule", themes=["金融科技"], triggered=True),
        EventAnalysis(event_id="event-irm-disclosure", direction="neutral", impact_score=100.0, reasoning="rule", themes=["PCB"], triggered=True),
        EventAnalysis(event_id="event-irm-recruitment", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-sample", direction="neutral", impact_score=100.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-sse-cooperation", direction="neutral", impact_score=99.9, reasoning="rule", themes=["算力"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "长亮科技中标某股份制银行新网贷服务平台项目" in content
    assert "为什么一直不正式公告披露呢" not in content
    assert "招聘网站上招聘光模块技术人员" not in content
    assert "样品送这么久了" not in content
    assert "哪些厂商有合作" not in content


def test_write_text_report_filters_live_exchange_material_variants_without_hiding_substantive_events(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-22T09:31:00+08:00",
            last_seen_at="2026-04-22T09:31:00+08:00",
            canonical_title="天威视讯：天威视讯关于全资子公司深圳市广电网络有限公司收购深圳市长泰传媒有限公司49%股权的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-22T09:31:00+08:00",
            url="https://example.com/keep-acquisition",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-order-material",
            first_seen_at="2026-04-22T00:00:00+08:00",
            last_seen_at="2026-04-22T00:00:00+08:00",
            canonical_title="持续关连交易：养护工程合同",
            summary="summary",
            source="sse",
            published_at="2026-04-22T00:00:00+08:00",
            url="https://example.com/order-material",
            event_type="hard_event",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-restructuring-material",
            first_seen_at="2026-04-22T00:00:00+08:00",
            last_seen_at="2026-04-22T00:00:00+08:00",
            canonical_title="天源资产评估有限公司关于对《关于浙江东望时代科技股份有限公司股权收购相关事项的监管工作函》之评估相关问题的回复",
            summary="summary",
            source="sse",
            published_at="2026-04-22T00:00:00+08:00",
            url="https://example.com/restructuring-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-meeting-material",
            first_seen_at="2026-04-22T00:00:00+08:00",
            last_seen_at="2026-04-22T00:00:00+08:00",
            canonical_title="北京市大龙伟业房地产开发股份有限公司2025年年度股东会会议资料",
            summary="summary",
            source="sse",
            published_at="2026-04-22T00:00:00+08:00",
            url="https://example.com/meeting-material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-bond-notice",
            first_seen_at="2026-04-22T00:00:00+08:00",
            last_seen_at="2026-04-22T00:00:00+08:00",
            canonical_title="万科A：关于在交易商协会披露《关于2023年度第一期中期票据本息偿付安排的公告》的提示性公告",
            summary="summary",
            source="szse",
            published_at="2026-04-22T00:00:00+08:00",
            url="https://example.com/bond-notice",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-rent-contract",
            first_seen_at="2026-04-22T00:00:00+08:00",
            last_seen_at="2026-04-22T00:00:00+08:00",
            canonical_title="光线传媒：关于签署房屋租赁合同暨关联交易的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-22T00:00:00+08:00",
            url="https://example.com/rent-contract",
            event_type="hard_event",
            event_subtype="order_contract",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-keep-acquisition", direction="bullish", impact_score=88.0, reasoning="rule", themes=["传媒"], triggered=True),
        EventAnalysis(event_id="event-order-material", direction="neutral", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-restructuring-material", direction="neutral", impact_score=78.5, reasoning="rule", themes=["房地产"], triggered=True),
        EventAnalysis(event_id="event-meeting-material", direction="neutral", impact_score=100.0, reasoning="rule", themes=["房地产"], triggered=True),
        EventAnalysis(event_id="event-bond-notice", direction="neutral", impact_score=100.0, reasoning="rule", themes=["房地产"], triggered=True),
        EventAnalysis(event_id="event-rent-contract", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "天威视讯：天威视讯关于全资子公司深圳市广电网络有限公司收购深圳市长泰传媒有限公司49%股权的公告" in content
    assert "持续关连交易：养护工程合同" not in content
    assert "评估相关问题的回复" not in content
    assert "年度股东会会议资料" not in content
    assert "本息偿付安排的公告》的提示性公告" not in content
    assert "房屋租赁合同暨关联交易" not in content


def test_write_text_report_filters_second_batch_live_investor_qa_variants_without_hiding_substantive_cls_updates(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-keep-cls",
            first_seen_at="2026-04-22T19:12:31+08:00",
            last_seen_at="2026-04-22T19:12:31+08:00",
            canonical_title="永鼎股份：100G EML及硅光高功率芯片具备批量生产能力 启动扩产计划",
            summary="summary",
            source="cls",
            published_at="2026-04-22T19:12:31+08:00",
            url="https://example.com/keep-cls",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-order",
            first_seen_at="2026-04-22T18:15:03+08:00",
            last_seen_at="2026-04-22T18:15:03+08:00",
            canonical_title="地铁设计：中标雄安项目了？",
            summary="问题：中标雄安项目了？ 回复：您好，公司建立了华南、华东、中南、东南、西北、西南、华北七大业务区域以及海外事业部，在境内外50多个城市开展轨道交通、市政、建筑等领域的勘察设计、规划咨询、工程总承包业务以及数智技术、低碳技术服务等业务。有关项目中标情况请以相关公示信息为准。感谢您的关注！",
            source="irm_cninfo",
            published_at="2026-04-22T18:15:03+08:00",
            url="https://example.com/irm-order",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-irm-robot-progress",
            first_seen_at="2026-04-22T17:33:33+08:00",
            last_seen_at="2026-04-22T17:33:33+08:00",
            canonical_title="震裕科技：贵公司在泰国的机器人零部件生产基地项目进展如何，一期二期产能预计如何？主要生产哪方面的机器人零部件？",
            summary="问题：贵公司在泰国的机器人零部件生产基地项目进展如何，一期二期产能预计如何？主要生产哪方面的机器人零部件？ 回复：您好，公司海外相关项目的具体进展请以公司后续发布的定期报告或临时公告为准。感谢您对公司的关注！",
            source="irm_cninfo",
            published_at="2026-04-22T17:33:33+08:00",
            url="https://example.com/irm-robot-progress",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-robot-application",
            first_seen_at="2026-04-22T17:33:03+08:00",
            last_seen_at="2026-04-22T17:33:03+08:00",
            canonical_title="震裕科技：贵公司研发生产的机器人零部件主要应用于机器人的哪个部分？手部还是关节？麻烦详细介绍下",
            summary="问题：贵公司研发生产的机器人零部件主要应用于机器人的哪个部分？手部还是关节？麻烦详细介绍下 回复：请详见公司同类问题的回复。",
            source="irm_cninfo",
            published_at="2026-04-22T17:33:03+08:00",
            url="https://example.com/irm-robot-application",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-rumor",
            first_seen_at="2026-04-22T19:18:18+08:00",
            last_seen_at="2026-04-22T19:18:18+08:00",
            canonical_title="华丰科技：董秘您好，对于4月22日早盘贵公司股票盘中极速跳水逾10%一事，有消息称是贵公司订单被抢，请董秘履行保护投资者责任，尽快调查核实此消息是否为谣传，谢谢！",
            summary="问题：董秘您好，对于4月22日早盘贵公司股票盘中极速跳水逾10%一事，有消息称是贵公司订单被抢，请董秘履行保护投资者责任，尽快调查核实此消息是否为谣传，谢谢！ 回复：尊敬的投资者，您好！公司目前生产经营一切正常，核心业务、在手订单及客户合作均保持稳定。公司严格按照监管要求履行信息披露义务，所有重大事项均以官方披露为准，敬请广大投资者理性判断、审慎投资。感谢您的关注！",
            source="sse_einteractive",
            published_at="2026-04-22T19:18:18+08:00",
            url="https://example.com/sse-rumor",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-sse-rant",
            first_seen_at="2026-04-22T19:18:18+08:00",
            last_seen_at="2026-04-22T19:18:18+08:00",
            canonical_title="华丰科技：不要总是踩竞争对手，这么大的市场空间，应该是一起合作做大。不要总是讲竞争的逻辑，要讲生态逻辑，只有参与的玩家多了，市场才会越做越大。记住，中国是全球开源大模型最大贡献者，国产算力超节点生态将成为全球标准，这么大的市场逻辑，好好想想怎么讲吧。",
            summary="问题：不要总是踩竞争对手，这么大的市场空间，应该是一起合作做大。不要总是讲竞争的逻辑，要讲生态逻辑，只有参与的玩家多了，市场才会越做越大。记住，中国是全球开源大模型最大贡献者，国产算力超节点生态将成为全球标准，这么大的市场逻辑，好好想想怎么讲吧。 回复：尊敬的投资者，您好！公司高度认同生态协同、共同做大产业的理念。公司将立足主业，深化产业链上下游合作，坚持开放共赢的发展思路，与行业伙伴一道助力国产算力生态建设。感谢您的关注！",
            source="sse_einteractive",
            published_at="2026-04-22T19:18:18+08:00",
            url="https://example.com/sse-rant",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-keep-cls", direction="bullish", impact_score=99.3, reasoning="rule", themes=["算力", "半导体"], triggered=True),
        EventAnalysis(event_id="event-irm-order", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-robot-progress", direction="bullish", impact_score=100.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-irm-robot-application", direction="neutral", impact_score=100.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-sse-rumor", direction="neutral", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-rant", direction="neutral", impact_score=99.9, reasoning="rule", themes=["算力"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "永鼎股份：100G EML及硅光高功率芯片具备批量生产能力 启动扩产计划" in content
    assert "地铁设计：中标雄安项目了？" not in content
    assert "机器人零部件生产基地项目进展如何" not in content
    assert "主要应用于机器人的哪个部分" not in content
    assert "有消息称是贵公司订单被抢" not in content
    assert "不要总是踩竞争对手" not in content


def test_write_text_report_filters_second_batch_live_exchange_material_variants_without_hiding_real_risk(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-keep-risk",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="*ST和科：关于申请撤销对公司股票交易实施退市风险警示的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/keep-risk",
            event_type="hard_event",
            event_subtype="delisting_risk",
        ),
        Event(
            event_id="event-renew-contract",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="汉桑科技：关于续签日常关联交易合同的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/renew-contract",
            event_type="hard_event",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-credit-guarantee",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="万孚生物：关于公司向银行申请综合授信并为经销商和子公司订单融资提供担保的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/credit-guarantee",
            event_type="hard_event",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-framework",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="金 螳 螂：关于签署《框架协议》的自愿性披露公告",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/framework",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-buyback-plan",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="乖宝宠物：关于以集中竞价交易方式回购公司股份的预案",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/buyback-plan",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-risk-note",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="光迅科技：武汉光迅科技股份有限公司关于对信科（北京）财务有限公司的持续风险评估说明的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/risk-note",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-pledge-buyback",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="湖北能源：湖北能源集团股份有限公司关于持股5%以上股东股票质押式回购交易提前购回的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/pledge-buyback",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-keep-risk", direction="bullish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-renew-contract", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-credit-guarantee", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-framework", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-buyback-plan", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-risk-note", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-pledge-buyback", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "*ST和科：关于申请撤销对公司股票交易实施退市风险警示的公告" in content
    assert "续签日常关联交易合同" not in content
    assert "申请综合授信并为经销商和子公司订单融资提供担保" not in content
    assert "签署《框架协议》的自愿性披露公告" not in content
    assert "回购公司股份的预案" not in content
    assert "持续风险评估说明" not in content
    assert "股票质押式回购交易提前购回" not in content


def test_write_text_report_filters_weak_acquisition_followup_and_low_signal_increase_plan_and_stcn_buyback_flash(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-keep-buyback",
            first_seen_at="2026-04-22T19:15:23+08:00",
            last_seen_at="2026-04-22T19:15:23+08:00",
            canonical_title="乖宝宠物：拟1亿元—2亿元回购股份",
            summary="人民财讯4月22日电，乖宝宠物(301498)4月22日公告，公司拟以1亿元—2亿元回购股份，用于股权激励或员工持股计划。",
            source="stcn",
            published_at="2026-04-22T19:15:23+08:00",
            url="https://example.com/keep-buyback",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-acquisition-followup",
            first_seen_at="2026-04-22T17:29:33+08:00",
            last_seen_at="2026-04-22T17:29:33+08:00",
            canonical_title="飞亚达：请问董秘，公司最近股价异动是否是收购长空齿轮股权有进展的原因？如果不是 那么收购为什么还不提上日程？",
            summary="问题：请问董秘，公司最近股价异动是否是收购长空齿轮股权有进展的原因？如果不是 那么收购为什么还不提上日程？ 回复：您好，感谢您对飞亚达公司的关注！公司收购长空齿轮控股权项目正在推进国有资产评估备案相关工作，备案通过并确认交易方案后将履行审批程序及披露义务。谢谢！",
            source="irm_cninfo",
            published_at="2026-04-22T17:29:33+08:00",
            url="https://example.com/irm-acquisition-followup",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-exec-increase-plan",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="乖宝宠物：关于实际控制人兼董事长、董事兼总裁及部分高级管理人员增持股份计划的公告",
            summary="summary",
            source="szse",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/exec-increase-plan",
            event_type="hard_event",
            event_subtype="executive_change",
        ),
        Event(
            event_id="event-equity-invalid",
            first_seen_at="2026-04-23T00:00:00+08:00",
            last_seen_at="2026-04-23T00:00:00+08:00",
            canonical_title="莲花控股股份有限公司关于2024年股票期权与限制性股票激励计划预留权益失效的公告",
            summary="summary",
            source="cninfo",
            published_at="2026-04-23T00:00:00+08:00",
            url="https://example.com/equity-invalid",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-keep-buyback", direction="neutral", impact_score=74.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-acquisition-followup", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-exec-increase-plan", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-equity-invalid", direction="bearish", impact_score=80.0, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "乖宝宠物：拟1亿元—2亿元回购股份" not in content
    assert "收购长空齿轮股权有进展的原因" not in content
    assert "部分高级管理人员增持股份计划" not in content
    assert "预留权益失效" not in content


def test_write_text_report_filters_cninfo_minority_shareholder_acquisition_progress_without_hiding_real_acquisition(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-24T00:00:00+08:00",
            last_seen_at="2026-04-24T00:00:00+08:00",
            canonical_title="盈新发展：关于收购广东长兴半导体科技有限公司控制权的公告",
            summary="公司披露收购半导体公司控制权。",
            source="cninfo",
            published_at="2026-04-24T00:00:00+08:00",
            url="https://example.com/keep-acquisition",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-minority-shareholder-progress",
            first_seen_at="2026-04-24T00:00:00+08:00",
            last_seen_at="2026-04-24T00:00:00+08:00",
            canonical_title="艾迪药业关于公司收购控股子公司少数股东股权进展的公告",
            summary="公司披露收购控股子公司少数股东股权的进展情况。",
            source="cninfo",
            published_at="2026-04-24T00:00:00+08:00",
            url="https://example.com/minority-shareholder-progress",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-keep-acquisition", direction="bullish", impact_score=88.0, reasoning="rule", themes=["半导体"], triggered=True),
        EventAnalysis(event_id="event-minority-shareholder-progress", direction="neutral", impact_score=80.0, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "盈新发展：关于收购广东长兴半导体科技有限公司控制权的公告" in content
    assert "艾迪药业关于公司收购控股子公司少数股东股权进展的公告" not in content


def test_write_text_report_filters_related_party_contract_renewal_and_supplement_material_without_hiding_real_acquisition(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-25T00:00:00+08:00",
            last_seen_at="2026-04-25T00:00:00+08:00",
            canonical_title="华大基因：关于收购重庆新一产生命科技有限公司100%股权暨关联交易的公告",
            summary="公司披露收购目标公司100%股权。",
            source="szse",
            published_at="2026-04-25T00:00:00+08:00",
            url="https://example.com/keep-acquisition",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-supplement-contract",
            first_seen_at="2026-04-25T00:00:00+08:00",
            last_seen_at="2026-04-25T00:00:00+08:00",
            canonical_title="亚太药业：关于签署《技术开发合同补充协议》暨关联交易的公告",
            summary="公司披露签署技术开发合同补充协议暨关联交易事项。",
            source="szse",
            published_at="2026-04-25T00:00:00+08:00",
            url="https://example.com/supplement-contract",
            event_type="hard_event",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-renew-business-cooperation",
            first_seen_at="2026-04-25T00:00:00+08:00",
            last_seen_at="2026-04-25T00:00:00+08:00",
            canonical_title="万润股份：关于与烟台万海舟化工有限公司续签《业务合作协议》暨关联交易的公告",
            summary="公司披露续签业务合作协议暨关联交易事项。",
            source="szse",
            published_at="2026-04-25T00:00:00+08:00",
            url="https://example.com/renew-business-cooperation",
            event_type="hard_event",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-keep-acquisition",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-supplement-contract",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-renew-business-cooperation",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "华大基因：关于收购重庆新一产生命科技有限公司100%股权暨关联交易的公告" in content
    assert "亚太药业：关于签署《技术开发合同补充协议》暨关联交易的公告" not in content
    assert "万润股份：关于与烟台万海舟化工有限公司续签《业务合作协议》暨关联交易的公告" not in content


def test_write_text_report_filters_exchange_governance_and_equity_material_variants_without_hiding_real_acquisition(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-25T00:00:00+08:00",
            last_seen_at="2026-04-25T00:00:00+08:00",
            canonical_title="华大基因：关于收购重庆新一产生命科技有限公司100%股权暨关联交易的公告",
            summary="公司披露收购目标公司100%股权。",
            source="szse",
            published_at="2026-04-25T00:00:00+08:00",
            url="https://example.com/keep-acquisition-2",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-governance-rule",
            first_seen_at="2026-04-25T00:00:00+08:00",
            last_seen_at="2026-04-25T00:00:00+08:00",
            canonical_title="英飞特：《投资性房地产管理办法》（2026年4月修订）",
            summary="公司披露制度修订文件。",
            source="szse",
            published_at="2026-04-25T00:00:00+08:00",
            url="https://example.com/governance-rule",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-real-estate-self-check",
            first_seen_at="2026-04-25T00:00:00+08:00",
            last_seen_at="2026-04-25T00:00:00+08:00",
            canonical_title="川润股份：关于2026年度向特定对象发行A股股票之房地产业务专项自查报告",
            summary="公司披露房地产业务专项自查报告。",
            source="szse",
            published_at="2026-04-25T00:00:00+08:00",
            url="https://example.com/real-estate-self-check",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-equity-review-opinion",
            first_seen_at="2026-04-25T00:00:00+08:00",
            last_seen_at="2026-04-25T00:00:00+08:00",
            canonical_title="奥尼电子：董事会薪酬与考核委员会关于公司2025年限制性股票激励计划第一个解除限售期解除限售及第一个归属期归属相关事项的核查意见",
            summary="公司披露股权激励归属核查意见。",
            source="szse",
            published_at="2026-04-25T00:00:00+08:00",
            url="https://example.com/equity-review-opinion",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-equity-capital-reduction",
            first_seen_at="2026-04-25T00:00:00+08:00",
            last_seen_at="2026-04-25T00:00:00+08:00",
            canonical_title="明阳电路：关于回购注销限制性股票的减资公告",
            summary="公司披露回购注销限制性股票减资事项。",
            source="szse",
            published_at="2026-04-25T00:00:00+08:00",
            url="https://example.com/equity-capital-reduction",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-keep-acquisition",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-governance-rule",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["房地产"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-real-estate-self-check",
            direction="neutral",
            impact_score=100.0,
            reasoning="rule",
            themes=["房地产"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-equity-review-opinion",
            direction="bearish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-equity-capital-reduction",
            direction="bearish",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "华大基因：关于收购重庆新一产生命科技有限公司100%股权暨关联交易的公告" in content
    assert "英飞特：《投资性房地产管理办法》（2026年4月修订）" not in content
    assert "川润股份：关于2026年度向特定对象发行A股股票之房地产业务专项自查报告" not in content
    assert "奥尼电子：董事会薪酬与考核委员会关于公司2025年限制性股票激励计划第一个解除限售期解除限售及第一个归属期归属相关事项的核查意见" not in content
    assert "明阳电路：关于回购注销限制性股票的减资公告" not in content


def test_write_text_report_filters_disclosure_and_cooperation_exchange_variants_without_hiding_real_acquisition(
    tmp_path,
) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-25T00:00:00+08:00",
            last_seen_at="2026-04-25T00:00:00+08:00",
            canonical_title="华大基因：关于收购重庆新一产生命科技有限公司100%股权暨关联交易的公告",
            summary="公司披露收购目标公司100%股权。",
            source="szse",
            published_at="2026-04-25T00:00:00+08:00",
            url="https://example.com/keep-acquisition-3",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-land-intention",
            first_seen_at="2026-04-25T00:00:00+08:00",
            last_seen_at="2026-04-25T00:00:00+08:00",
            canonical_title="强瑞技术：关于拟购买土地使用权并建设人工智能产业研发智造总部并签署投资合作意向书的公告",
            summary="公司披露购买土地使用权并签署投资合作意向书事项。",
            source="szse",
            published_at="2026-04-25T00:00:00+08:00",
            url="https://example.com/land-intention",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-dilution-risk",
            first_seen_at="2026-04-25T00:00:00+08:00",
            last_seen_at="2026-04-25T00:00:00+08:00",
            canonical_title="川润股份：关于2026年度向特定对象发行股票摊薄即期回报的风险提示及填补回报措施和相关主体承诺的公告",
            summary="公司披露摊薄即期回报的风险提示及填补回报措施和相关主体承诺。",
            source="szse",
            published_at="2026-04-25T00:00:00+08:00",
            url="https://example.com/dilution-risk",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-related-deposit-plan",
            first_seen_at="2026-04-25T00:00:00+08:00",
            last_seen_at="2026-04-25T00:00:00+08:00",
            canonical_title="荃银高科：安徽荃银高科种业股份有限公司在中化集团财务有限责任公司关联存款风险处置预案",
            summary="公司披露关联存款风险处置预案。",
            source="szse",
            published_at="2026-04-25T00:00:00+08:00",
            url="https://example.com/related-deposit-plan",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-cooperation-exchange",
            first_seen_at="2026-04-24T22:58:34+08:00",
            last_seen_at="2026-04-24T22:58:34+08:00",
            canonical_title="内蒙古能源集团与华润电力围绕战略合作等交流座谈",
            summary="双方围绕战略合作、管理提升、人才交流、科技协同等进行了深入交流，并表示在重大项目合作、项目共建等领域深化务实合作。",
            source="stcn",
            published_at="2026-04-24T22:58:34+08:00",
            url="https://example.com/cooperation-exchange",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-keep-acquisition", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-land-intention", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-dilution-risk", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-related-deposit-plan", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-cooperation-exchange", direction="neutral", impact_score=74.0, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "华大基因：关于收购重庆新一产生命科技有限公司100%股权暨关联交易的公告" in content
    assert "强瑞技术：关于拟购买土地使用权并建设人工智能产业研发智造总部并签署投资合作意向书的公告" not in content
    assert "川润股份：关于2026年度向特定对象发行股票摊薄即期回报的风险提示及填补回报措施和相关主体承诺的公告" not in content
    assert "荃银高科：安徽荃银高科种业股份有限公司在中化集团财务有限责任公司关联存款风险处置预案" not in content
    assert "内蒙古能源集团与华润电力围绕战略合作等交流座谈" not in content


def test_write_text_report_filters_domestic_commodity_night_session_variant(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-night-session-roundup",
            first_seen_at="2026-04-24T23:05:21+08:00",
            last_seen_at="2026-04-24T23:05:21+08:00",
            canonical_title="国内商品期市夜盘收盘 合成橡胶跌超1%",
            summary="人民财讯4月24日电，国内商品期市夜盘收盘，合成橡胶跌超1%。",
            source="stcn",
            published_at="2026-04-24T23:05:21+08:00",
            url="https://example.com/night-session-roundup",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-keep-acquisition",
            first_seen_at="2026-04-25T00:00:00+08:00",
            last_seen_at="2026-04-25T00:00:00+08:00",
            canonical_title="华大基因：关于收购重庆新一产生命科技有限公司100%股权暨关联交易的公告",
            summary="公司披露收购目标公司100%股权。",
            source="szse",
            published_at="2026-04-25T00:00:00+08:00",
            url="https://example.com/keep-acquisition-4",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-night-session-roundup", direction="neutral", impact_score=74.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-acquisition", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "国内商品期市夜盘收盘 合成橡胶跌超1%" not in content
    assert "华大基因：关于收购重庆新一产生命科技有限公司100%股权暨关联交易的公告" in content


def test_write_text_report_filters_latest_low_signal_live_head_noise(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-keep-delisting-risk",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="*ST新研：关于申请撤销公司股票退市风险警示的公告",
            summary="公司申请撤销公司股票退市风险警示。",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/keep-delisting-risk",
            event_type="hard_event",
            event_subtype="delisting_risk",
        ),
        Event(
            event_id="event-cls-overseas-optical-market-move",
            first_seen_at="2026-04-28T21:37:28+08:00",
            last_seen_at="2026-04-28T21:37:28+08:00",
            canonical_title="美股光通信板块开盘普跌 Coherent跌超4%",
            summary="财联社4月28日电，美股光通信板块开盘普跌，Coherent跌超4%。",
            source="cls",
            published_at="2026-04-28T21:37:28+08:00",
            url="https://example.com/cls-overseas-optical-market-move",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-cls-world-bank-energy-forecast",
            first_seen_at="2026-04-28T21:34:02+08:00",
            last_seen_at="2026-04-28T21:34:02+08:00",
            canonical_title="世界银行：如果中东战争的最严重干扰在五月结束 预计2026年能源价格将上涨24%",
            summary="财联社4月28日电，世界银行发布能源价格预测。",
            source="cls",
            published_at="2026-04-28T21:34:02+08:00",
            url="https://example.com/cls-world-bank-energy-forecast",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-cls-morning-brief-anonymous-pick",
            first_seen_at="2026-04-28T21:30:30+08:00",
            last_seen_at="2026-04-28T21:30:30+08:00",
            canonical_title="【财联社早知道】我国最大规模科学智能集群接入全国一体化算力网，分析师称AI算力仍将是科技巨头竞相争抢的战略性稀缺资源，这家公司的算力网调度与市场运营平台已实现东数西算枢纽等供给方的标准化接入",
            summary="①我国最大规模科学智能集群接入全国一体化算力网；②分析师称AI算力仍是战略性稀缺资源；③这家公司算力网调度与市场运营平台已实现供给方标准化接入。",
            source="cls",
            published_at="2026-04-28T21:30:30+08:00",
            url="https://example.com/cls-morning-brief-anonymous-pick-latest",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-cninfo-investor-qa",
            first_seen_at="2026-04-28T21:31:33+08:00",
            last_seen_at="2026-04-28T21:31:33+08:00",
            canonical_title="中工国际：您好、国机集团领导来公司调研、其中提出算电协同出海、麻烦请解答：公司对于算电协同出海有哪些理解与认识？如何落实落地？公司在算电协同有哪些先发优势？",
            summary="问题：公司对于算电协同出海有哪些理解与认识？ 回复：感谢您的关注，公司将围绕主营业务推进相关工作。",
            source="irm_cninfo",
            published_at="2026-04-28T21:31:33+08:00",
            url="https://example.com/irm-cninfo-investor-qa",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-szse-option-cancel",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="直真科技：关于注销2023年股票期权激励计划部分已授予的股票期权的公告",
            summary="公司注销2023年股票期权激励计划部分已授予的股票期权。",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/szse-option-cancel",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-shareholder-reduction",
            first_seen_at="2026-04-28T00:00:00+08:00",
            last_seen_at="2026-04-28T00:00:00+08:00",
            canonical_title="视觉中国：关于实际控制人减持股份触及1%及5%整数倍的公告",
            summary="公司披露实际控制人减持股份触及1%及5%整数倍。",
            source="szse",
            published_at="2026-04-28T00:00:00+08:00",
            url="https://example.com/szse-shareholder-reduction",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-risk-control-rules",
            first_seen_at="2026-04-28T00:00:00+08:00",
            last_seen_at="2026-04-28T00:00:00+08:00",
            canonical_title="宁波华翔：董事会风险控制委员会工作细则",
            summary="公司披露董事会风险控制委员会工作细则。",
            source="szse",
            published_at="2026-04-28T00:00:00+08:00",
            url="https://example.com/szse-risk-control-rules",
            event_type="hard_event",
            event_subtype="board_resolution",
        ),
        Event(
            event_id="event-szse-transfer-progress-supplement",
            first_seen_at="2026-04-28T00:00:00+08:00",
            last_seen_at="2026-04-28T00:00:00+08:00",
            canonical_title="祖名股份：关于与北京市香香唯一食品厂及其一致行动人签署股权转让协议的交易进展及签署补充协议的公告",
            summary="公司披露股权转让协议交易进展及签署补充协议。",
            source="szse",
            published_at="2026-04-28T00:00:00+08:00",
            url="https://example.com/szse-transfer-progress-supplement",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-cninfo-equity-incentive-price-adjustment",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="江苏微导纳米科技股份有限公司关于调整2023年限制性股票激励计划授予价格的公告",
            summary="公司调整2023年限制性股票激励计划授予价格。",
            source="cninfo",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/cninfo-equity-incentive-price-adjustment",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-stcn-private-robot-financing",
            first_seen_at="2026-04-29T09:24:51+08:00",
            last_seen_at="2026-04-29T09:24:51+08:00",
            canonical_title="擎天租完成数亿元Pre-A轮融资 提升平台在多城市、多场景、多品类机器人应用中的交付能力",
            summary="擎天租完成数亿元Pre-A轮融资，提升平台在多城市、多场景、多品类机器人应用中的交付能力。",
            source="stcn",
            published_at="2026-04-29T09:24:51+08:00",
            url="https://example.com/stcn-private-robot-financing",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-szse-cumulative-litigation",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="雅博股份：关于累计新增诉讼、仲裁情况的公告",
            summary="公司披露累计新增诉讼、仲裁情况。",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/szse-cumulative-litigation",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-stcn-business-registration-ai-robotics",
            first_seen_at="2026-04-29T13:54:06+08:00",
            last_seen_at="2026-04-29T13:54:06+08:00",
            canonical_title="民爆光电成立精密科技公司 含AI及机器人业务",
            summary="人民财讯4月29日电，企查查APP显示，民爆光电成立精密科技公司，经营范围含AI及机器人业务。",
            source="stcn",
            published_at="2026-04-29T13:54:06+08:00",
            url="https://example.com/stcn-business-registration-ai-robotics",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-stcn-business-registration-real-estate",
            first_seen_at="2026-05-09T14:36:45+08:00",
            last_seen_at="2026-05-09T14:36:45+08:00",
            canonical_title="昊华科技成立置业公司 含房地产开发经营业务",
            summary="人民财讯5月9日电，企查查APP显示，近日，成都棠茂置业有限公司成立，法定代表人为李佳，注册资本为3000万元，经营范围包含：房地产开发经营；住宅室内装饰装修；物业管理；房地产经纪；非居住房地产租赁。企查查股权穿透显示，该公司由昊华科技间接全资持股。",
            source="stcn",
            published_at="2026-05-09T14:36:45+08:00",
            url="https://example.com/stcn-business-registration-real-estate",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-stcn-world-bank-energy-forecast",
            first_seen_at="2026-04-29T13:45:13+08:00",
            last_seen_at="2026-04-29T13:45:13+08:00",
            canonical_title="世界银行：今年全球能源价格或上涨24%",
            summary="人民财讯4月29日电，世界银行称今年全球能源价格或上涨24%。",
            source="stcn",
            published_at="2026-04-29T13:45:13+08:00",
            url="https://example.com/stcn-world-bank-energy-forecast",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-cninfo-lithium-capacity-qa",
            first_seen_at="2026-04-29T13:58:47+08:00",
            last_seen_at="2026-04-29T13:58:47+08:00",
            canonical_title="超频三：董秘您好：公司发布的一季度业报告中绩扣非净利润799万，同比提升了30倍。主要原因是电池材料涨价的原因吗？四月以来碳酸锂价格一直居高不下公司是否有扩大产能利用率的计划。公司现在碳酸锂产能利用率达到了多少。谢谢",
            summary="问题：公司是否有扩大产能利用率的计划，公司现在碳酸锂产能利用率达到了多少。",
            source="irm_cninfo",
            published_at="2026-04-29T13:58:47+08:00",
            url="https://example.com/irm-cninfo-lithium-capacity-qa",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-cninfo-storage-reits-suggestion",
            first_seen_at="2026-04-29T13:58:47+08:00",
            last_seen_at="2026-04-29T13:58:47+08:00",
            canonical_title="智光电气：4月28日，由财通证券资产管理有限公司担任计划管理人及独家销售机构的“财通资管-阿特斯持有型不动产资产支持专项计划（碳中和）”成功设立。这是全国首单以储能电站作为基础资产的机构间REITs产品，构建了“储能投资-REITs退出-新项目开发”的完整闭环。 希望智光的管理层考虑研究一下是否可以将独立储能电站项目资产化，来提前回笼资金，解决高负债、项目研发费用以及工程垫资问题。",
            summary="问题：建议公司考虑研究是否可以将独立储能电站项目资产化，提前回笼资金。",
            source="irm_cninfo",
            published_at="2026-04-29T13:58:47+08:00",
            url="https://example.com/irm-cninfo-storage-reits-suggestion",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-cninfo-semiconductor-tech-disclosure-qa",
            first_seen_at="2026-04-29T14:10:52+08:00",
            last_seen_at="2026-04-29T14:10:52+08:00",
            canonical_title="国林科技：公司能否学习一下臻宝科技，它并非半导体主机设备厂，而是跟公司一样是半导体设备零部件及系统供应商。其在招股说明书中披露了它的半导体产品已经批量供应于20nm及以下DRAM先进工艺存储芯片制造，存储类200层及以上堆叠先进工艺3d nand闪存芯片制造。公司不愿意披露客户信息，但像上述技术实力是可以披露的。请问，公司半导体系统已经批量供应于多少nm以下dram存储芯片及多少层以上nand闪存芯片制造？",
            summary="问题：请问公司半导体系统已经批量供应于多少nm以下dram存储芯片及多少层以上nand闪存芯片制造？",
            source="irm_cninfo",
            published_at="2026-04-29T14:10:52+08:00",
            url="https://example.com/irm-cninfo-semiconductor-tech-disclosure-qa",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-cninfo-supplier-ipo-equity-plan-qa",
            first_seen_at="2026-04-29T14:10:52+08:00",
            last_seen_at="2026-04-29T14:10:52+08:00",
            canonical_title="苏试试验：董秘你好！最近商业航天重要的科技公司中科宇航完成IPO辅导，公司作为该企业测试供应商，有没有对该公司参股的计划？ 谢谢！",
            summary="问题：中科宇航完成IPO辅导，公司作为该企业测试供应商，有没有对该公司参股的计划？",
            source="irm_cninfo",
            published_at="2026-04-29T14:10:52+08:00",
            url="https://example.com/irm-cninfo-supplier-ipo-equity-plan-qa",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-einteractive-server-power-order-expectation-qa",
            first_seen_at="2026-04-29T19:37:48+08:00",
            last_seen_at="2026-04-29T19:37:48+08:00",
            canonical_title="科威尔：董秘你好，公司在服务器电源测试领域都有哪些客户导入和订单预期？谢谢",
            summary="问题：公司在服务器电源测试领域都有哪些客户导入和订单预期？ 回复：已实现部分小批量订单交付，今年该板块业务开局良好。",
            source="sse_einteractive",
            published_at="2026-04-29T19:37:48+08:00",
            url="https://example.com/sse-einteractive-server-power-order-expectation-qa",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-sse-einteractive-st-zhenlei-executive-stock-drop-qa",
            first_seen_at="2026-04-29T19:37:48+08:00",
            last_seen_at="2026-04-29T19:37:48+08:00",
            canonical_title="ST臻镭：股市股东因公司高管的错误行为股价大跌，公司高管有无增持或增资计划？上市公司如何让还没走的股东利益受损降低！",
            summary="问题：股价大跌，公司高管有无增持或增资计划？ 回复：如有相关计划会严格按照相关法律法规要求履行信息披露义务。",
            source="sse_einteractive",
            published_at="2026-04-29T19:37:48+08:00",
            url="https://example.com/sse-einteractive-st-zhenlei-executive-stock-drop-qa",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-sse-einteractive-st-zhenlei-order-expansion-qa",
            first_seen_at="2026-04-29T19:37:48+08:00",
            last_seen_at="2026-04-29T19:37:48+08:00",
            canonical_title="ST臻镭：公司今年上半年订单总额是否可公开给大家，未来几年有没有扩产计划？",
            summary="问题：公司今年上半年订单总额是否可公开，未来几年有没有扩产计划？ 回复：关于公司业绩情况请关注公司公告。",
            source="sse_einteractive",
            published_at="2026-04-29T19:37:48+08:00",
            url="https://example.com/sse-einteractive-st-zhenlei-order-expansion-qa",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-cninfo-luxin-profit-distribution-plan",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="鲁信创投2025年度利润分配方案公告",
            summary="鲁信创投2025年度利润分配方案公告",
            source="cninfo",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/cninfo-luxin-profit-distribution-plan",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-irm-cninfo-robot-equity-stake-qa",
            first_seen_at="2026-04-29T18:37:30+08:00",
            last_seen_at="2026-04-29T18:37:30+08:00",
            canonical_title="彩讯股份：董秘您好，贵公司是否参股银河通用机器人？",
            summary="董秘您好，贵公司是否参股银河通用机器人？",
            source="irm_cninfo",
            published_at="2026-04-29T18:37:30+08:00",
            url="https://example.com/irm-cninfo-robot-equity-stake-qa",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-cninfo-stock-drop-buyback-qa",
            first_seen_at="2026-04-29T18:37:30+08:00",
            last_seen_at="2026-04-29T18:37:30+08:00",
            canonical_title="光线传媒：股价跌这么厉害，公司账上趴着35亿可用资金，为什么不回购股份！？市值管理不是说说而已，要付诸行动！",
            summary="股价跌这么厉害，为什么不回购股份，市值管理要付诸行动。",
            source="irm_cninfo",
            published_at="2026-04-29T18:37:30+08:00",
            url="https://example.com/irm-cninfo-stock-drop-buyback-qa",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-szse-shareholder-meeting-resolution-with-theme",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="四川黄金：2025年年度股东会决议公告",
            summary="四川黄金：2025年年度股东会决议公告",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/szse-shareholder-meeting-resolution-with-theme",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-stock-appreciation-right-legal-opinion",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="上海新阳：北京市隆安律师事务所上海分所关于上海新阳半导体材料股份有限公司2024年股票增值权第二个行权期行权条件成就事项的法律意见书",
            summary="上海新阳披露股票增值权第二个行权期行权条件成就事项的法律意见书。",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/szse-stock-appreciation-right-legal-opinion",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-reduction-period-expired",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="麦克奥迪：关于公司股东减持股份计划期限届满的公告",
            summary="麦克奥迪披露公司股东减持股份计划期限届满。",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/szse-reduction-period-expired",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-restricted-stock-repurchase-cancel-2022",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="隆基机械：关于回购注销2022年限制性股票激励计划部分限制性股票的公告",
            summary="隆基机械披露回购注销2022年限制性股票激励计划部分限制性股票。",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/szse-restricted-stock-repurchase-cancel-2022",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-szse-director-manager-reduction-result",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="盈趣科技：关于部分董事、高级管理人员股份减持计划实施结果的公告",
            summary="盈趣科技披露部分董事、高级管理人员股份减持计划实施结果。",
            source="szse",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/szse-director-manager-reduction-result",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-irm-cninfo-memory-order-visibility-qa",
            first_seen_at="2026-04-29T19:37:33+08:00",
            last_seen_at="2026-04-29T19:37:33+08:00",
            canonical_title="江波龙：董秘你好：1. 当前存储行业整体处于涨价周期，公司近期的业绩高增长主要来自出货量的提升，还是产品价格的上涨？两者对增长的贡献比例大致如何？ 2. 目前公司的订单能见度大概能看到几个月（比如是否已排到2026年下半年）？蔡总对不同产品线（嵌入式、消费级、企业级等）的未来价格走势，公司内部有怎样的预判？ 3. 在下游客户普遍预期涨价的背景下，是否存在渠道过度囤货的现象？公司目前的渠道库存周转天数是多少",
            summary="问题：订单能见度大概能看到几个月？ 回复：产销数据、订单情况、库存规模等财务信息请以定期报告为准。",
            source="irm_cninfo",
            published_at="2026-04-29T19:37:33+08:00",
            url="https://example.com/irm-cninfo-memory-order-visibility-qa",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-cls-overseas-pharma-acquisition",
            first_seen_at="2026-04-29T19:23:56+08:00",
            last_seen_at="2026-04-29T19:23:56+08:00",
            canonical_title="意大利制药公司Chiesi同意以约19亿美元收购美国上市公司KalVista制药",
            summary="意大利制药公司Chiesi同意以约19亿美元收购美国上市公司KalVista制药。",
            source="cls",
            published_at="2026-04-29T19:23:56+08:00",
            url="https://example.com/cls-overseas-pharma-acquisition",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-stcn-hk-broker-ant-acquisition",
            first_seen_at="2026-04-29T19:39:38+08:00",
            last_seen_at="2026-04-29T19:39:38+08:00",
            canonical_title="耀才证券：蚂蚁控股收购交易完成，专注香港客户，尚无涉足代币化资产的计划",
            summary="香港上市券商耀才证券宣布蚂蚁财富控股收购交易全部完成，专注香港客户。",
            source="stcn",
            published_at="2026-04-29T19:39:38+08:00",
            url="https://example.com/stcn-hk-broker-ant-acquisition",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-sse-financial-insurance-framework",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="关于公司与中国华能集团有限公司签订金融保险服务框架协议的公告",
            summary="公司与中国华能集团有限公司签订金融保险服务框架协议。",
            source="sse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/sse-financial-insurance-framework",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-szse-convertible-bond-trustee-report",
            first_seen_at="2026-04-29T00:00:00+08:00",
            last_seen_at="2026-04-29T00:00:00+08:00",
            canonical_title="ST岭南：岭南生态文旅股份有限公司向不特定对象发行可转换公司债券2026年度第十一次临时受托管理事务报告",
            summary="公司披露可转换公司债券临时受托管理事务报告。",
            source="szse",
            published_at="2026-04-29T00:00:00+08:00",
            url="https://example.com/szse-convertible-bond-trustee-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-sse-einteractive-tailings-extraction-qa",
            first_seen_at="2026-04-28T18:23:00+08:00",
            last_seen_at="2026-04-28T18:23:00+08:00",
            canonical_title="恒誉环保：请问公司60万吨尾矿制备富钛材料示范项目除了提取钛材料和铁以外尾矿中剩余其它金属是否计划进行开发提取？谢谢",
            summary="问题：尾矿中剩余其它金属是否计划进行开发提取？ 回复：若矿石中剩余有价元素含量高，可进一步处置。",
            source="sse_einteractive",
            published_at="2026-04-28T18:23:00+08:00",
            url="https://example.com/sse-einteractive-tailings-extraction-qa",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-einteractive-tailings-scope-qa",
            first_seen_at="2026-04-28T18:21:00+08:00",
            last_seen_at="2026-04-28T18:21:00+08:00",
            canonical_title="恒誉环保：请问公司的尾矿处理技术除了可用于钛铁尾矿还可以用于哪些尾矿？谢谢",
            summary="问题：尾矿处理技术还可以用于哪些尾矿？ 回复：目前还可以用于处理其他贵金属伴生铁矿。",
            source="sse_einteractive",
            published_at="2026-04-28T18:21:00+08:00",
            url="https://example.com/sse-einteractive-tailings-scope-qa",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-sse-einteractive-satellite-internet-order-qa",
            first_seen_at="2026-04-28T18:20:00+08:00",
            last_seen_at="2026-04-28T18:20:00+08:00",
            canonical_title="成都华微：尊敬的董秘： 您好！近日上海市发布《国家数字经济创新发展试验区（上海）实施方案》，提出加快千帆星座建设、推动卫星互联网商用试点。请问： 1. 公司产品是否已应用或对接千帆星座（G60星链）相关项目？目前订单或合作进展如何？ ​ 2. 卫星互联网业务商用化提速，对公司特种集成电路业务的订单、收入预期有何积极影响？",
            summary="问题：公司产品是否已应用或对接千帆星座相关项目，目前订单或合作进展如何？ 回复：公司将密切关注前沿技术发展趋势。",
            source="sse_einteractive",
            published_at="2026-04-28T18:20:00+08:00",
            url="https://example.com/sse-einteractive-satellite-internet-order-qa",
            event_type="fast_news",
            event_subtype="policy_signal",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-keep-delisting-risk", direction="bullish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-cls-overseas-optical-market-move", direction="neutral", impact_score=99.3, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-cls-world-bank-energy-forecast", direction="neutral", impact_score=99.3, reasoning="rule", themes=["油气"], triggered=True),
        EventAnalysis(event_id="event-cls-morning-brief-anonymous-pick", direction="bullish", impact_score=99.3, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-cninfo-investor-qa", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-szse-option-cancel", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-shareholder-reduction", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-risk-control-rules", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-transfer-progress-supplement", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-cninfo-equity-incentive-price-adjustment", direction="bearish", impact_score=80.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-stcn-private-robot-financing", direction="neutral", impact_score=79.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-szse-cumulative-litigation", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-stcn-business-registration-ai-robotics", direction="neutral", impact_score=99.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-stcn-business-registration-real-estate", direction="neutral", impact_score=99.0, reasoning="rule", themes=["房地产"], triggered=True),
        EventAnalysis(event_id="event-stcn-world-bank-energy-forecast", direction="bullish", impact_score=99.0, reasoning="rule", themes=["油气"], triggered=True),
        EventAnalysis(event_id="event-irm-cninfo-lithium-capacity-qa", direction="bullish", impact_score=100.0, reasoning="rule", themes=["锂电池"], triggered=True),
        EventAnalysis(event_id="event-irm-cninfo-storage-reits-suggestion", direction="bullish", impact_score=100.0, reasoning="rule", themes=["储能"], triggered=True),
        EventAnalysis(event_id="event-irm-cninfo-semiconductor-tech-disclosure-qa", direction="neutral", impact_score=100.0, reasoning="rule", themes=["半导体"], triggered=True),
        EventAnalysis(event_id="event-irm-cninfo-supplier-ipo-equity-plan-qa", direction="neutral", impact_score=100.0, reasoning="rule", themes=["商业航天"], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-server-power-order-expectation-qa", direction="neutral", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-st-zhenlei-executive-stock-drop-qa", direction="neutral", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-st-zhenlei-order-expansion-qa", direction="neutral", impact_score=74.9, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-cninfo-luxin-profit-distribution-plan", direction="neutral", impact_score=100.0, reasoning="rule", themes=["信创"], triggered=True),
        EventAnalysis(event_id="event-irm-cninfo-robot-equity-stake-qa", direction="neutral", impact_score=100.0, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-irm-cninfo-stock-drop-buyback-qa", direction="neutral", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-shareholder-meeting-resolution-with-theme", direction="neutral", impact_score=100.0, reasoning="rule", themes=["黄金"], triggered=True),
        EventAnalysis(event_id="event-szse-stock-appreciation-right-legal-opinion", direction="neutral", impact_score=100.0, reasoning="rule", themes=["半导体"], triggered=True),
        EventAnalysis(event_id="event-szse-reduction-period-expired", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-restricted-stock-repurchase-cancel-2022", direction="bearish", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-szse-director-manager-reduction-result", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-irm-cninfo-memory-order-visibility-qa", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-cls-overseas-pharma-acquisition", direction="neutral", impact_score=74.3, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-stcn-hk-broker-ant-acquisition", direction="bullish", impact_score=74.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-sse-financial-insurance-framework", direction="neutral", impact_score=100.0, reasoning="rule", themes=["保险"], triggered=True),
        EventAnalysis(event_id="event-szse-convertible-bond-trustee-report", direction="neutral", impact_score=100.0, reasoning="rule", themes=["文旅"], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-tailings-extraction-qa", direction="neutral", impact_score=99.9, reasoning="rule", themes=["黄金"], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-tailings-scope-qa", direction="neutral", impact_score=99.9, reasoning="rule", themes=["黄金"], triggered=True),
        EventAnalysis(event_id="event-sse-einteractive-satellite-internet-order-qa", direction="bullish", impact_score=99.9, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "*ST新研：关于申请撤销公司股票退市风险警示的公告" in content
    assert "美股光通信板块开盘普跌 Coherent跌超4%" not in content
    assert "世界银行：如果中东战争的最严重干扰在五月结束" not in content
    assert "【财联社早知道】我国最大规模科学智能集群接入全国一体化算力网" not in content
    assert "中工国际：您好、国机集团领导来公司调研" not in content
    assert "直真科技：关于注销2023年股票期权激励计划部分已授予的股票期权的公告" not in content
    assert "视觉中国：关于实际控制人减持股份触及1%及5%整数倍的公告" not in content
    assert "宁波华翔：董事会风险控制委员会工作细则" not in content
    assert "祖名股份：关于与北京市香香唯一食品厂及其一致行动人签署股权转让协议的交易进展及签署补充协议的公告" not in content
    assert "江苏微导纳米科技股份有限公司关于调整2023年限制性股票激励计划授予价格的公告" not in content
    assert "擎天租完成数亿元Pre-A轮融资" not in content
    assert "雅博股份：关于累计新增诉讼、仲裁情况的公告" not in content
    assert "民爆光电成立精密科技公司 含AI及机器人业务" not in content
    assert "昊华科技成立置业公司 含房地产开发经营业务" not in content
    assert "世界银行：今年全球能源价格或上涨24%" not in content
    assert "超频三：董秘您好" not in content
    assert "智光电气：4月28日" not in content
    assert "公司半导体系统已经批量供应于多少nm以下dram存储芯片" not in content
    assert "中科宇航完成IPO辅导" not in content
    assert "服务器电源测试领域都有哪些客户导入和订单预期" not in content
    assert "高管的错误行为股价大跌" not in content
    assert "上半年订单总额是否可公开给大家" not in content
    assert "鲁信创投2025年度利润分配方案公告" not in content
    assert "是否参股银河通用机器人" not in content
    assert "为什么不回购股份" not in content
    assert "2025年年度股东会决议公告" not in content
    assert "股票增值权第二个行权期行权条件成就事项的法律意见书" not in content
    assert "公司股东减持股份计划期限届满" not in content
    assert "回购注销2022年限制性股票激励计划部分限制性股票" not in content
    assert "部分董事、高级管理人员股份减持计划实施结果" not in content
    assert "当前存储行业整体处于涨价周期" not in content
    assert "Chiesi同意以约19亿美元收购美国上市公司KalVista制药" not in content
    assert "耀才证券：蚂蚁控股收购交易完成" not in content
    assert "关于公司与中国华能集团有限公司签订金融保险服务框架协议的公告" not in content
    assert "临时受托管理事务报告" not in content
    assert "尾矿中剩余其它金属是否计划进行开发提取" not in content
    assert "尾矿处理技术除了可用于钛铁尾矿还可以用于哪些尾矿" not in content
    assert "千帆星座" not in content


def test_write_text_report_filters_latest_interactive_ai_and_exchange_material_noise(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-keep-real-guidance",
            first_seen_at="2026-04-29T20:10:05+08:00",
            last_seen_at="2026-04-29T20:10:05+08:00",
            canonical_title="林洋能源：2026年储能力争开发不少于10GWh独立储能项目 拟中期分红不低于50%",
            summary="林洋能源披露储能开发规划。",
            source="cls",
            published_at="2026-04-29T20:10:05+08:00",
            url="https://example.com/keep-real-guidance",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-irm-ai-fit",
            first_seen_at="2026-04-29T20:15:33+08:00",
            last_seen_at="2026-04-29T20:15:33+08:00",
            canonical_title="紫光股份：公司在Ai算力方面与DeepSeek-V4适配吗？",
            summary="问题：公司在Ai算力方面与DeepSeek-V4适配吗？ 回复：您好，公司控股子公司新华三与DeepSeek在大模型训练、推理优化、解决方案及一体机部署等领域保持持续深度的常态化沟通和技术合作，目前在政府、企业、运营商、电力能源、教育、医疗等多个重点行业落地了可复制的解决方案。",
            source="irm_cninfo",
            published_at="2026-04-29T20:15:33+08:00",
            url="https://example.com/irm-ai-fit",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-ai-outlook",
            first_seen_at="2026-04-29T20:13:34+08:00",
            last_seen_at="2026-04-29T20:13:34+08:00",
            canonical_title="紫光股份：贵公司在算力方面发展前景如何，是否有加大力度，谢谢",
            summary="问题：贵公司在算力方面发展前景如何，是否有加大力度，谢谢 回复：您好，具体情况请您关注公司已披露的《2025年年度报告》。",
            source="irm_cninfo",
            published_at="2026-04-29T20:13:34+08:00",
            url="https://example.com/irm-ai-outlook",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-irm-optical-latest",
            first_seen_at="2026-04-29T20:11:33+08:00",
            last_seen_at="2026-04-29T20:11:33+08:00",
            canonical_title="紫光股份：在光交换机方面的最新消息",
            summary="问题：在光交换机方面的最新消息 回复：您好，公司紧跟行业向800G或1.6T可插拔光模块以及OCI、CPX等新兴技术发展趋势，对应产品及全生态连接解决方案正在准备中。",
            source="irm_cninfo",
            published_at="2026-04-29T20:11:33+08:00",
            url="https://example.com/irm-optical-latest",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-quarterly-report",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="万科A：2026年一季度报告",
            summary="万科A：2026年一季度报告",
            source="szse",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/quarterly-report",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-reduction-complete",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="大族激光：关于控股股东减持股份计划实施完成的公告",
            summary="大族激光：关于控股股东减持股份计划实施完成的公告",
            source="szse",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/reduction-complete",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-listed-transfer",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="万科A：关于公开挂牌转让环山集团股份有限公司股权的公告",
            summary="万科A：关于公开挂牌转让环山集团股份有限公司股权的公告",
            source="szse",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/listed-transfer",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-buyback-cancel-complete",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="科伦药业：关于部分回购股份注销完成暨股份变动的公告",
            summary="科伦药业：关于部分回购股份注销完成暨股份变动的公告",
            source="szse",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/buyback-cancel-complete",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-option-exercise",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="希荻微关于2024年股票期权激励计划首次授予部分第二个行权期采用自主行权的提示性公告",
            summary="希荻微关于2024年股票期权激励计划首次授予部分第二个行权期采用自主行权的提示性公告",
            source="cninfo",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/option-exercise",
            event_type="hard_event",
            event_subtype="equity_incentive",
        ),
        Event(
            event_id="event-share-increase-legal-opinion",
            first_seen_at="2026-05-01T00:00:00+08:00",
            last_seen_at="2026-05-01T00:00:00+08:00",
            canonical_title="北京市君致律师事务所关于漳州片仔癀药业股份有限公司控股股东增持公司股份的法律意见书",
            summary="片仔癀披露控股股东增持公司股份法律意见书。",
            source="cninfo",
            published_at="2026-05-01T00:00:00+08:00",
            url="https://example.com/share-increase-legal-opinion",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-no-penalty-cert",
            first_seen_at="2026-05-01T00:00:00+08:00",
            last_seen_at="2026-05-01T00:00:00+08:00",
            canonical_title="关于最近五年未被证券监管部门和证券交易所采取监管措施或处罚情况的公告",
            summary="公司披露最近五年未被证券监管部门和证券交易所采取监管措施或处罚情况。",
            source="cninfo",
            published_at="2026-05-01T00:00:00+08:00",
            url="https://example.com/no-penalty-cert",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-hk-ipo-tabled",
            first_seen_at="2026-04-30T20:53:32+08:00",
            last_seen_at="2026-04-30T20:53:32+08:00",
            canonical_title="港股IPO：山推工程机械股份有限公司表港交所",
            summary="利弗莫尔证券显示，山推工程机械股份有限公司向港交所提交上市申请书，独家保荐人为中金公司。",
            source="cls",
            published_at="2026-04-30T20:53:32+08:00",
            url="https://example.com/hk-ipo-tabled",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-overseas-robot-acquisition",
            first_seen_at="2026-04-30T21:10:54+08:00",
            last_seen_at="2026-04-30T21:10:54+08:00",
            canonical_title="财联社4月30日电，谷歌合作伙伴NovaCore Labs与Aibotics推进收购事宜，并扩大机器人在牙买加全境的部署。",
            summary="财联社4月30日电，谷歌合作伙伴NovaCore Labs与Aibotics推进收购事宜，并扩大机器人在牙买加全境的部署。",
            source="cls",
            published_at="2026-04-30T21:10:54+08:00",
            url="https://example.com/overseas-robot-acquisition",
            event_type="fast_news",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-irm-memory-order-visibility-question-only",
            first_seen_at="2026-04-29T19:39:04+08:00",
            last_seen_at="2026-04-29T19:39:04+08:00",
            canonical_title="江波龙：董秘你好：1. 当前存储行业整体处于涨价周期，公司近期的业绩高增长主要来自出货量的提升，还是产品价格的上涨？两者对增长的贡献比例大致如何？ 2. 目前公司的订单能见度大概能看到几个月（比如是否已排到2026年下半年）？蔡总对不同产品线（嵌入式、消费级、企业级等）的未来价格走势，公司内部有怎样的预判？ 3. 在下游客户普遍预期涨价的背景下，是否存在渠道过度囤货的现象？公司目前的渠道库存周转天数是多少",
            summary="董秘你好：1. 当前存储行业整体处于涨价周期，公司近期的业绩高增长主要来自出货量的提升，还是产品价格的上涨？两者对增长的贡献比例大致如何？ 2. 目前公司的订单能见度大概能看到几个月？",
            source="irm_cninfo",
            published_at="2026-04-29T19:39:04+08:00",
            url="https://example.com/irm-memory-order-visibility-question-only",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-keep-real-guidance", direction="bullish", impact_score=99.3, reasoning="rule", themes=["储能"], triggered=True),
        EventAnalysis(event_id="event-irm-ai-fit", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-ai-outlook", direction="bullish", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-irm-optical-latest", direction="bullish", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-quarterly-report", direction="neutral", impact_score=100.0, reasoning="rule", themes=["房地产"], triggered=True),
        EventAnalysis(event_id="event-reduction-complete", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-listed-transfer", direction="neutral", impact_score=100.0, reasoning="rule", themes=["房地产"], triggered=True),
        EventAnalysis(event_id="event-buyback-cancel-complete", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-option-exercise", direction="neutral", impact_score=80.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-share-increase-legal-opinion", direction="neutral", impact_score=80.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-no-penalty-cert", direction="bearish", impact_score=80.0, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-hk-ipo-tabled", direction="neutral", impact_score=99.3, reasoning="rule", themes=["工程机械"], triggered=True),
        EventAnalysis(event_id="event-overseas-robot-acquisition", direction="bullish", impact_score=99.3, reasoning="rule", themes=["机器人"], triggered=True),
        EventAnalysis(event_id="event-irm-memory-order-visibility-question-only", direction="bullish", impact_score=75.2, reasoning="rule", themes=[], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "林洋能源：2026年储能力争开发不少于10GWh独立储能项目" in content
    assert "公司在Ai算力方面与DeepSeek-V4适配吗" not in content
    assert "贵公司在算力方面发展前景如何" not in content
    assert "在光交换机方面的最新消息" not in content
    assert "万科A：2026年一季度报告" not in content
    assert "大族激光：关于控股股东减持股份计划实施完成的公告" not in content
    assert "万科A：关于公开挂牌转让环山集团股份有限公司股权的公告" not in content
    assert "科伦药业：关于部分回购股份注销完成暨股份变动的公告" not in content
    assert "第二个行权期采用自主行权" not in content
    assert "北京市君致律师事务所关于漳州片仔癀药业股份有限公司控股股东增持公司股份的法律意见书" not in content
    assert "关于最近五年未被证券监管部门和证券交易所采取监管措施或处罚情况的公告" not in content
    assert "港股IPO：山推工程机械股份有限公司表港交所" not in content
    assert "财联社4月30日电，谷歌合作伙伴NovaCore Labs与Aibotics推进收购事宜" not in content
    assert "当前存储行业整体处于涨价周期" not in content


def test_write_text_report_filters_latest_live_head_noise_cluster_without_hiding_real_catalysts(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-yingtang-material",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="英唐智控：中审众环关于公司重大资产重组前发生业绩异常或存在拟置出资产情形的专项核查意见",
            summary="英唐智控披露重大资产重组专项核查意见。",
            source="szse",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/yingtang-material",
            event_type="hard_event",
            event_subtype="acquisition_restructuring",
        ),
        Event(
            event_id="event-aisen-order-question",
            first_seen_at="2026-04-30T18:35:00+08:00",
            last_seen_at="2026-04-30T18:35:00+08:00",
            canonical_title="艾森股份：第二个问题，据媒体报道，贵司官微今日4.22发布消息，自研低温PSPI获得行业知名客户订单。请再详细介绍一下有关情况。这个客户是近日上市的盛合晶微吗？感谢！",
            summary="问题：第二个问题，据媒体报道，贵司官微今日4.22发布消息，自研低温PSPI获得行业知名客户订单。请再详细介绍一下有关情况。这个客户是近日上市的盛合晶微吗？感谢！ 回复：尊敬的投资者您好，公司低温PSPI可作为核心绝缘和介电材料，应用于扇出型晶圆级封装、2.5D/3D封装等，作为RDL绝缘层、TSV侧壁钝化与填充、晶圆级封装(WLP)中的钝化层、缓冲层和保护膜。低温PSPI是AI芯片先进封装的关键材料之一，目前仍由美日企业高度垄断，国产替代潜力巨大。感谢您的关注与支持！",
            source="sse_einteractive",
            published_at="2026-04-30T18:35:00+08:00",
            url="https://example.com/aisen-order-question",
            event_type="fast_news",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-ruihuatai-supply-chain-question",
            first_seen_at="2026-04-30T18:37:00+08:00",
            last_seen_at="2026-04-30T18:37:00+08:00",
            canonical_title="瑞华泰：PI膜作为PCB、FPC的核心材料，目前国产替代的比例还很少，瑞华泰作为国产PI的龙头，是否已经进入生益科技这些头部企业的供应链？谢谢！",
            summary="问题：PI膜作为PCB、FPC的核心材料，目前国产替代的比例还很少，瑞华泰作为国产PI的龙头，是否已经进入生益科技这些头部企业的供应链？谢谢！ 回复：尊敬的投资者您好！公司生产的电子基材用PI薄膜，具备良好的介电性能及尺寸稳定性，可广泛应用于消费电子、5G通信、汽车电子等领域，适配折叠屏手机、可穿戴设备等产品的高精密柔性电路需求，产品已进入生益科技、联茂等知名厂商的供应体系。感谢您对公司的关注。",
            source="sse_einteractive",
            published_at="2026-04-30T18:37:00+08:00",
            url="https://example.com/ruihuatai-supply-chain-question",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-lianhua-progress",
            first_seen_at="2026-05-01T00:00:00+08:00",
            last_seen_at="2026-05-01T00:00:00+08:00",
            canonical_title="莲花控股股份有限公司关于转型算力业务相关进展情况的公告",
            summary="莲花控股股份有限公司关于转型算力业务相关进展情况的公告",
            source="sse",
            published_at="2026-05-01T00:00:00+08:00",
            url="https://example.com/lianhua-progress",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-em-best-month",
            first_seen_at="2026-05-01T06:51:56+08:00",
            last_seen_at="2026-05-01T06:51:56+08:00",
            canonical_title="新兴市场股市录得2022年以来最佳单月表现 AI热潮与油价风险交织",
            summary="【新兴市场股市录得2022年以来最佳单月表现 AI热潮与油价风险交织】财联社5月1日电，新兴市场股市录得自2022年以来最佳单月表现，得益于亚洲科技股因人工智能需求前景乐观而大涨，尽管美伊围绕霍尔木兹海峡对峙之际，石油供应冲击仍在持续。MSCI新兴市场指数4月上涨14.5%，收复战争爆发后出现的跌幅。",
            source="cls",
            published_at="2026-05-01T06:51:56+08:00",
            url="https://example.com/em-best-month",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-stcn-institution-research-roundup",
            first_seen_at="2026-05-01T20:19:51+08:00",
            last_seen_at="2026-05-01T20:19:51+08:00",
            canonical_title="近一周机构调研个股超700只 迈瑞医疗和金盘科技调研机构数最多",
            summary="人民财讯5月1日电，近一周机构调研个股有700多只，迈瑞医疗和金盘科技调研机构数最多。迈瑞医疗有219家机构调研。金盘科技数据中心领域实现销售订单17.35亿元，同比增长278.45%。从市场表现来看，近一周机构调研股平均上涨1.16%。",
            source="stcn",
            published_at="2026-05-01T20:19:51+08:00",
            url="https://example.com/stcn-institution-research-roundup",
            event_type="fast_news",
            event_subtype="business_guidance",
        ),
        Event(
            event_id="event-keep-risk",
            first_seen_at="2026-05-01T00:00:00+08:00",
            last_seen_at="2026-05-01T00:00:00+08:00",
            canonical_title="佳通轮胎股份有限公司关于收到中国证券监督管理委员会立案告知书的公告",
            summary="佳通轮胎披露收到中国证监会立案告知书。",
            source="sse",
            published_at="2026-05-01T00:00:00+08:00",
            url="https://example.com/keep-risk",
            event_type="hard_event",
            event_subtype="legal_dispute",
        ),
        Event(
            event_id="event-keep-cooperation",
            first_seen_at="2026-05-01T07:42:21+08:00",
            last_seen_at="2026-05-01T07:42:21+08:00",
            canonical_title="腾云智算与华为达成深度合作 共筑福建智算新生态",
            summary="财联社5月1日电，腾云智算与华为达成深度合作，共筑福建智算新生态。",
            source="cls",
            published_at="2026-05-01T07:42:21+08:00",
            url="https://example.com/keep-cooperation",
            event_type="fast_news",
            event_subtype="cooperation_agreement",
        ),
    ]
    analyses = [
        EventAnalysis(event_id="event-yingtang-material", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-aisen-order-question", direction="bullish", impact_score=99.9, reasoning="rule", themes=["半导体"], triggered=True),
        EventAnalysis(event_id="event-ruihuatai-supply-chain-question", direction="neutral", impact_score=99.9, reasoning="rule", themes=["PCB"], triggered=True),
        EventAnalysis(event_id="event-lianhua-progress", direction="neutral", impact_score=100.0, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-em-best-month", direction="bearish", impact_score=74.3, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-stcn-institution-research-roundup", direction="bullish", impact_score=99.0, reasoning="rule", themes=["算力", "保险"], triggered=True),
        EventAnalysis(event_id="event-keep-risk", direction="bearish", impact_score=78.5, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-cooperation", direction="neutral", impact_score=99.3, reasoning="rule", themes=["算力"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "重大资产重组前发生业绩异常或存在拟置出资产情形的专项核查意见" not in content
    assert "自研低温PSPI获得行业知名客户订单" not in content
    assert "是否已经进入生益科技这些头部企业的供应链" not in content
    assert "莲花控股股份有限公司关于转型算力业务相关进展情况的公告" not in content
    assert "新兴市场股市录得2022年以来最佳单月表现" not in content
    assert "近一周机构调研个股超700只 迈瑞医疗和金盘科技调研机构数最多" not in content
    assert "佳通轮胎股份有限公司关于收到中国证券监督管理委员会立案告知书的公告" in content
    assert "腾云智算与华为达成深度合作 共筑福建智算新生态" in content


def test_write_text_report_filters_unhcr_logistics_disruption_story_from_live_head(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-unhcr-logistics",
            first_seen_at="2026-05-02T14:53:15+08:00",
            last_seen_at="2026-05-02T14:56:10+08:00",
            canonical_title="联合国难民署：中东局势致物资运输成本上升 交付推迟",
            summary="【联合国难民署：中东局势致物资运输成本上升 交付推迟】财联社5月2日电，联合国难民署5月1日表示，受中东局势影响，包括霍尔木兹海峡通行受阻，部分援助物资的运输成本上升，援助物资的交付被推迟。相关路线的援助物资运输成本翻了一番多。联合国难民署还表示，包括沙特阿拉伯吉达在内的主要港口因拥堵问题，以及大幅上涨的战争风险保险费等因素，都加剧了运输压力，阻碍援助物资的及时交付。",
            source="cls",
            published_at="2026-05-02T14:53:15+08:00",
            url="https://example.com/unhcr-logistics",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-keep-risk",
            first_seen_at="2026-05-01T00:00:00+08:00",
            last_seen_at="2026-05-01T00:00:00+08:00",
            canonical_title="佳通轮胎股份有限公司关于收到中国证券监督管理委员会立案告知书的公告",
            summary="佳通轮胎披露收到中国证监会立案告知书。",
            source="sse",
            published_at="2026-05-01T00:00:00+08:00",
            url="https://example.com/keep-risk",
            event_type="hard_event",
            event_subtype="legal_dispute",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-unhcr-logistics",
            direction="bearish",
            impact_score=99.3,
            reasoning="rule",
            themes=["保险"],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-risk",
            direction="bearish",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "联合国难民署：中东局势致物资运输成本上升 交付推迟" not in content
    assert "佳通轮胎股份有限公司关于收到中国证券监督管理委员会立案告知书的公告" in content


def test_write_text_report_filters_contract_area_progress_notice_without_theme(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
        Event(
            event_id="event-contract-area-progress",
            first_seen_at="2026-04-30T00:00:00+08:00",
            last_seen_at="2026-04-30T00:00:00+08:00",
            canonical_title="潜能恒信：渤海0917合同区进展公告",
            summary="潜能恒信：渤海0917合同区进展公告",
            source="szse",
            published_at="2026-04-30T00:00:00+08:00",
            url="https://example.com/contract-area-progress",
            event_type="hard_event",
            event_subtype="order_contract",
        ),
        Event(
            event_id="event-keep-risk",
            first_seen_at="2026-05-01T00:00:00+08:00",
            last_seen_at="2026-05-01T00:00:00+08:00",
            canonical_title="佳通轮胎股份有限公司关于收到中国证券监督管理委员会立案告知书的公告",
            summary="佳通轮胎披露收到中国证监会立案告知书。",
            source="sse",
            published_at="2026-05-01T00:00:00+08:00",
            url="https://example.com/keep-risk",
            event_type="hard_event",
            event_subtype="legal_dispute",
        ),
    ]
    analyses = [
        EventAnalysis(
            event_id="event-contract-area-progress",
            direction="neutral",
            impact_score=78.2,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
        EventAnalysis(
            event_id="event-keep-risk",
            direction="bearish",
            impact_score=78.5,
            reasoning="rule",
            themes=[],
            triggered=True,
        ),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")

    assert "潜能恒信：渤海0917合同区进展公告" not in content
    assert "佳通轮胎股份有限公司关于收到中国证券监督管理委员会立案告知书的公告" in content
