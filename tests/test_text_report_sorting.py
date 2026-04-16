from news_sentiment.models import Event, EventAnalysis
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
            first_seen_at="2026-04-12T19:16:02+08:00",
            last_seen_at="2026-04-12T19:16:02+08:00",
            canonical_title="中信建投：A股迎修复行情 围绕景气行业布局",
            summary="券商观点认为当前市场正在修复，建议围绕景气行业进行资产配置。",
            source="stcn",
            published_at="2026-04-12T19:16:02+08:00",
            url="https://example.com/stcn-csc-commentary",
            event_type="fast_news",
            event_subtype="company_update",
        ),
        Event(
            event_id="event-stcn-coop-keep",
            first_seen_at="2026-04-12T19:14:50+08:00",
            last_seen_at="2026-04-12T19:14:50+08:00",
            canonical_title="迅策：与深圳数据交易所签署战略合作协议",
            summary="summary",
            source="stcn",
            published_at="2026-04-12T19:14:50+08:00",
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
            first_seen_at="2026-04-13T07:20:50+08:00",
            last_seen_at="2026-04-13T07:20:50+08:00",
            canonical_title="基金经理布局创新药对冲组合风险 公募对创新药配置逻辑出现新变化",
            summary="伴随各类事件催化进入密集兑现周期，不少基金经理开始切换布局创新药对冲组合风险，反映公募对创新药配置逻辑出现了新的变化。",
            source="stcn",
            published_at="2026-04-13T07:20:50+08:00",
            url="https://example.com/stcn-fund-manager-commentary",
            event_type="fast_news",
            event_subtype="market_move",
        ),
        Event(
            event_id="event-stcn-order-keep",
            first_seen_at="2026-04-13T07:28:53+08:00",
            last_seen_at="2026-04-13T07:28:53+08:00",
            canonical_title="上海电气中标人造卫星装备一体化自动项目",
            summary="summary",
            source="stcn",
            published_at="2026-04-13T07:28:53+08:00",
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
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "千问3.6Plus大模型登顶全球模型调用排行榜首，日调用量破万亿" in content
    assert "能源供应趋紧 韩国鼓励非高峰使用公共交通" not in content
    assert "南非新政延长签证宽限期 将刺激旅游市场" not in content
    assert "清明假期第一天 全社会跨区域人员流动量预计约2.96亿人次" not in content
    assert "深圳市暴雨黄色预警信号扩展至全市" not in content
    assert "农业成本因伊朗战事上升 土耳其取消部分化肥关税" not in content
    assert "迪拜甲骨文大楼外立面遭防空系统拦截碎片击中 无人员伤亡" not in content


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
            event_id="event-stcn-keep-hkex-filter",
            first_seen_at="2026-04-10T20:01:00+08:00",
            last_seen_at="2026-04-10T20:01:00+08:00",
            canonical_title="国产EDA工具链和先进封装产线建设提速",
            summary="summary",
            source="stcn",
            published_at="2026-04-10T20:01:00+08:00",
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


def test_write_text_report_filters_exchange_low_signal_project_sales_and_mou_announcements(tmp_path) -> None:
    paths = ProjectPaths(tmp_path)
    events = [
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
            event_id="event-stcn-keep-low-signal-exchange",
            first_seen_at="2026-04-10T20:01:00+08:00",
            last_seen_at="2026-04-10T20:01:00+08:00",
            canonical_title="国产EDA工具链和先进封装产线建设提速",
            summary="summary",
            source="stcn",
            published_at="2026-04-10T20:01:00+08:00",
            url="https://example.com/stcn-keep-low-signal-exchange",
            event_type="fast_news",
            event_subtype="company_update",
        ),
    ]
    analyses = [
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
    assert "保利发展控股集团股份有限公司关于本公司获得房地产项目的公告" not in content
    assert "保利发展控股集团股份有限公司2026年3月份销售情况简报" not in content
    assert "中国东方航空股份有限公司关于取得金融机构股票回购贷款承诺函的公告" not in content
    assert "建发股份关于控股子公司签署《谅解备忘录》暨关联交易的公告" not in content


def test_write_text_report_filters_exchange_buyback_result_and_purpose_cancellation_without_hiding_buyback_plan(
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
    assert "贵州茅台关于以集中竞价交易方式回购股份方案的公告" in content
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
        EventAnalysis(event_id="event-szse-reduction-expire-no-sale", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-acquisition", direction="neutral", impact_score=100.0, reasoning="rule", themes=["半导体"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告" in content
    assert "上海电力股份有限公司董事会审计与风险委员会2025年度履职情况报告" not in content
    assert "哈尔斯：董事会薪酬与考核委员会关于2024年股票增值权激励计划第一个行权期的行权名单的核查意见" not in content
    assert "广东建工：关于重大资产重组业绩承诺期满标的资产减值测试情况的公告" not in content
    assert "凯瑞德：关于持股5%以上股东减持期限届满未减持股份的公告" not in content


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
            first_seen_at="2026-04-16T20:15:59+08:00",
            last_seen_at="2026-04-16T20:15:59+08:00",
            canonical_title="【风口研报·公司】积极拓展智算服务+数据智能，这家公司加码扩充万卡级算力、租赁服务需求可期，多路径布局AI算力和应用产品线；这家光通信芯片公司在数据中心侧芯片实现从追赶到并跑的突破",
            summary="summary",
            source="cls",
            published_at="2026-04-16T20:15:59+08:00",
            url="https://example.com/cls-wind-research",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-szse-share-reduction-plan",
            first_seen_at="2026-04-17T00:00:00+08:00",
            last_seen_at="2026-04-17T00:00:00+08:00",
            canonical_title="和胜股份：关于股东计划减持公司股份的预披露公告",
            summary="summary",
            source="szse",
            published_at="2026-04-17T00:00:00+08:00",
            url="https://example.com/szse-share-reduction-plan",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
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
        EventAnalysis(event_id="event-cls-wind-research", direction="neutral", impact_score=79.3, reasoning="rule", themes=["算力"], triggered=True),
        EventAnalysis(event_id="event-szse-share-reduction-plan", direction="neutral", impact_score=78.2, reasoning="rule", themes=[], triggered=True),
        EventAnalysis(event_id="event-keep-catalyst", direction="bullish", impact_score=99.3, reasoning="rule", themes=["锂电池"], triggered=True),
    ]

    write_text_report(paths, events, analyses)
    content = paths.latest_report_path.read_text(encoding="utf-8")
    assert "云天化：引入当升科技为合作方 预计总投资约44.93亿元建设磷酸铁锂等新能源电池材料项目" in content
    assert "【风口研报·公司】积极拓展智算服务+数据智能" not in content
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
