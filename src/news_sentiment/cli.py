from __future__ import annotations

import argparse
from dataclasses import dataclass
import sys
from typing import Sequence

from news_sentiment.analysis import score_event
from news_sentiment.collectors import (
    CollectFailure,
    CollectorError,
    get_registered_collectors,
)
from news_sentiment.config_loader import load_scoring_config, load_source_definitions
from news_sentiment.event_merge import merge_news_items
from news_sentiment.models import Event, EventAnalysis, NormalizedNews, RawNews, SocialSignal
from news_sentiment.normalize import normalize_news_items
from news_sentiment.reporting import write_text_report
from news_sentiment.settings import ProjectPaths
from news_sentiment.social_collectors import collect_social_signals
from news_sentiment.storage import JsonlStore


COMMANDS = (
    "collect",
    "normalize",
    "merge-events",
    "analyze-events",
    "audit-suspicious",
    "live-smoke",
    "collect-social",
    "report",
    "run-once",
)

HARD_EVENT_RISK_REVIEW_KEYWORDS = (
    "申请重整",
    "预重整",
    "商标争议",
    "诉讼",
    "仲裁",
    "冻结",
    "查封",
    "被执行",
    "失信",
    "立案",
    "问询函",
)
LOW_SIGNAL_CNINFO_RESTRUCTURING_MATERIAL_KEYWORDS = (
    "审核问询函回复",
    "审核问询函的专项核查意见",
    "审核问询函之回复",
    "问询函回复",
    "审核问询函中有关财务会计问题的专项说明",
    "报告书（修订稿）",
    "报告书(修订稿)",
)
LOW_SIGNAL_CNINFO_RESTRUCTURING_CONTEXT_KEYWORDS = (
    "发行股份购买资产",
    "关联交易",
    "重大资产重组",
    "重大资产出售",
    "并购重组",
)
LOW_SIGNAL_FINANCING_MATERIAL_CONTEXT_KEYWORDS = (
    "向不特定对象发行可转换公司债券",
    "发行可转换公司债券",
    "可转换公司债券",
    "募集配套资金",
    "向特定对象发行股票",
    "申请向特定对象发行股票",
)
LOW_SIGNAL_HARD_EVENT_RISK_DISCLOSURE_KEYWORDS = (
    "年报问询函回复",
    "问询函有关问题的专项说明",
    "年报的问询函相关事项的专项说明",
    "诉讼事项的进展",
    "仲裁事项的进展",
    "涉及诉讼进展",
    "诉讼进展公告",
    "提起诉讼的进展公告",
    "进展暨公司涉及诉讼事项的公告",
    "累计诉讼",
    "累计新增诉讼",
    "重大诉讼公告",
    "重大诉讼的公告",
    "重大诉讼、仲裁情况进展",
    "失信被执行人",
    "轮候冻结",
    "解除司法冻结",
    "强制执行完成",
)
FAST_NEWS_LEGAL_REVIEW_KEYWORDS = (
    "商标争议",
    "侵害发明专利权纠纷",
    "专利权纠纷",
    "诉讼",
    "仲裁",
)
SUSPICIOUS_MARKET_ROUNDUP_PREFIXES = (
    "开评：",
    "收评：",
    "午评：",
    "早盘：",
)
LOW_SIGNAL_MARKET_ROUNDUP_KEYWORDS = ("涨停分析",)
LOW_SIGNAL_STCN_PUBLIC_AFFAIRS_TITLE_KEYWORDS = (
    "鼓励非高峰使用公共交通",
    "延长签证宽限期",
    "跨区域人员流动量预计",
    "暴雨黄色预警信号",
    "取消部分化肥关税",
    "外立面遭防空系统拦截碎片击中",
    "调研先进制造业发展",
    "人形机器人半马",
    "文旅经济发展大会召开",
    "看望慰问“五一”假期在岗一线劳动者并调研重点工作进展情况",
)
LOW_SIGNAL_STCN_CHARGING_INFRASTRUCTURE_TITLE_KEYWORDS = (
    "广汽自营充电桩突破",
)
LOW_SIGNAL_STCN_WTI_GENERAL_FAST_NEWS_TITLE_PREFIX = (
    "国际油价持续回落 WTI原油期货价格涨幅收窄至"
)
LOW_SIGNAL_STCN_BRENT_UPWARD_VOLATILITY_FAST_NEWS_TITLE_PREFIX = (
    "国际原油短线快速拉升 布伦特原油期货涨逾"
)
LOW_SIGNAL_STCN_PRECIOUS_METAL_SPOT_MOVE_TITLE_PREFIXES = (
    "现货白银",
    "现货黄金",
)
LOW_SIGNAL_STCN_PRECIOUS_METAL_SPOT_MOVE_TITLE_KEYWORDS = (
    "涨近",
    "跌近",
    "涨超",
    "跌超",
    "震荡走高",
    "震荡走低",
)
LOW_SIGNAL_STCN_FUND_MANAGER_COMMENTARY_EXTRA_TITLE_KEYWORDS = (
    "投资机会",
)


@dataclass(frozen=True)
class CollectResult:
    rows: list[RawNews]
    failed_sources: list[CollectFailure]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="news-sentiment")
    subparsers = parser.add_subparsers(dest="command")
    collect_parser = subparsers.add_parser("collect")
    collect_parser.add_argument("--source", default="fixture")
    subparsers.add_parser("normalize")
    subparsers.add_parser("merge-events")
    subparsers.add_parser("analyze-events")
    audit_parser = subparsers.add_parser("audit-suspicious")
    audit_parser.add_argument("--limit", type=int, default=10)
    live_smoke_parser = subparsers.add_parser("live-smoke")
    live_smoke_parser.add_argument("--source", default="all")
    collect_social_parser = subparsers.add_parser("collect-social")
    collect_social_parser.add_argument("--platform", default="fixture")
    subparsers.add_parser("report")
    run_once_parser = subparsers.add_parser("run-once")
    run_once_parser.add_argument("--source", default="fixture")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    paths = ProjectPaths.discover()

    if args.command == "collect":
        result = run_collect(paths, args.source)
        if result.failed_sources:
            print(
                f"warning: failed_sources={format_collect_failures(result.failed_sources)}",
                file=sys.stderr,
            )
        return 0
    if args.command == "normalize":
        return run_normalize(paths)
    if args.command == "merge-events":
        return run_merge_events(paths)
    if args.command == "analyze-events":
        return run_analyze_events(paths)
    if args.command == "audit-suspicious":
        return run_audit_suspicious(paths, args.limit)
    if args.command == "live-smoke":
        return run_live_smoke(paths, args.source)
    if args.command == "collect-social":
        try:
            return run_collect_social(paths, args.platform)
        except CollectorError as exc:
            print(
                f"warning: social_platform_failed={exc.source}:{exc.kind}:{exc.message}",
                file=sys.stderr,
            )
            return 0
    if args.command == "report":
        return run_report(paths)
    if args.command == "run-once":
        run_collect(paths, args.source)
        run_normalize(paths)
        run_merge_events(paths)
        run_analyze_events(paths)
        return run_report(paths)
    return 0


def run_collect(paths: ProjectPaths, source: str) -> CollectResult:
    store = JsonlStore(paths.raw_news_path, RawNews)
    result = collect_from_source(source)
    store.write_many(result.rows)
    return result


def collect_from_source(source: str) -> CollectResult:
    if source != "all":
        return CollectResult(rows=_collect_rows(source), failed_sources=[])

    rows: list[RawNews] = []
    failed_sources: list[CollectFailure] = []
    for source_definition in load_source_definitions():
        if not source_definition.enabled:
            continue
        try:
            rows.extend(_collect_rows(source_definition.source_id))
        except CollectorError as exc:
            failed_sources.append(
                CollectFailure(
                    source=exc.source,
                    kind=exc.kind,
                    message=exc.message,
                )
            )
        except Exception as exc:
            failed_sources.append(
                CollectFailure(
                    source=source_definition.source_id,
                    kind="unexpected_error",
                    message=str(exc) or exc.__class__.__name__,
                )
            )
    return CollectResult(rows=rows, failed_sources=failed_sources)


def format_collect_failures(failures: list[CollectFailure]) -> str:
    if not failures:
        return "none"
    return ",".join(f"{failure.source}:{failure.kind}" for failure in failures)


def _collect_rows(source: str) -> list[RawNews]:
    collector = get_registered_collectors().get(source)
    if collector is not None:
        return collector()
    raise ValueError(f"Unsupported source: {source}")


def run_normalize(paths: ProjectPaths) -> int:
    raw_store = JsonlStore(paths.raw_news_path, RawNews)
    normalized_store = JsonlStore(paths.normalized_news_path, NormalizedNews)
    normalized_store.write_many(normalize_news_items(raw_store.read_all()))
    return 0


def run_merge_events(paths: ProjectPaths) -> int:
    normalized_store = JsonlStore(paths.normalized_news_path, NormalizedNews)
    events_store = JsonlStore(paths.events_path, Event)
    events_store.write_many(merge_news_items(normalized_store.read_all()))
    return 0


def run_analyze_events(paths: ProjectPaths) -> int:
    events_store = JsonlStore(paths.events_path, Event)
    analyses_store = JsonlStore(paths.analyses_path, EventAnalysis)
    scoring_config = load_scoring_config()
    analyses_store.write_many(
        [score_event(event, scoring_config=scoring_config) for event in events_store.read_all()]
    )
    return 0


def run_report(paths: ProjectPaths) -> int:
    events_store = JsonlStore(paths.events_path, Event)
    analyses_store = JsonlStore(paths.analyses_path, EventAnalysis)
    social_signals_store = JsonlStore(paths.social_signals_path, SocialSignal)
    write_text_report(
        paths,
        events_store.read_all(),
        analyses_store.read_all(),
        social_signals=social_signals_store.read_all(),
    )
    return 0


def run_collect_social(paths: ProjectPaths, platform: str) -> int:
    social_signals_store = JsonlStore(paths.social_signals_path, SocialSignal)
    social_signals_store.write_many(collect_social_signals(paths, platform))
    return 0


def run_audit_suspicious(paths: ProjectPaths, limit: int) -> int:
    events_store = JsonlStore(paths.events_path, Event)
    analyses_store = JsonlStore(paths.analyses_path, EventAnalysis)
    analyses = {analysis.event_id: analysis for analysis in analyses_store.read_all()}
    candidates = []
    for event in events_store.read_all():
        analysis = analyses.get(event.event_id)
        if analysis is None or not analysis.triggered:
            continue
        reason = _suspicious_reason(event, analysis)
        if reason is None:
            continue
        candidates.append((analysis.impact_score, event.published_at, reason, event, analysis))

    candidates.sort(key=lambda row: (row[0], row[1]), reverse=True)
    print(f"suspicious_count={len(candidates)}")
    for _, _, reason, event, analysis in candidates[: max(limit, 0)]:
        themes = ",".join(analysis.themes) if analysis.themes else "无"
        print(
            " | ".join(
                [
                    f"reason={reason}",
                    f"subtype={event.event_subtype}",
                    f"direction={analysis.direction}",
                    f"score={analysis.impact_score:.1f}",
                    f"themes={themes}",
                    f"title={event.canonical_title}",
                ]
            )
        )
    return 0


def _suspicious_reason(event: Event, analysis: EventAnalysis) -> str | None:
    title = event.canonical_title
    text = f"{event.canonical_title} {event.summary}"
    if _is_cls_editorial_roundup_column(event):
        return None
    if _is_low_signal_market_roundup_candidate(event):
        return None
    if (
        event.source in {"cninfo", "sse", "szse"}
        and event.event_type == "hard_event"
        and event.event_subtype in {"corporate_disclosure", "acquisition_restructuring"}
        and _is_low_signal_cninfo_restructuring_material(title)
    ):
        return None
    if (
        event.event_type == "hard_event"
        and event.event_subtype == "corporate_disclosure"
        and any(keyword in title for keyword in HARD_EVENT_RISK_REVIEW_KEYWORDS)
        and not _is_low_signal_hard_event_risk_disclosure(title)
    ):
        return "hard_event_risk_keyword"
    if (
        event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and event.source != "cls"
        and bool(analysis.themes)
    ):
        if _is_low_signal_stcn_wti_general_fast_news_candidate(event):
            return None
        if _is_low_signal_stcn_brent_upward_volatility_general_fast_news_candidate(event):
            return None
        if _is_low_signal_stcn_precious_metal_spot_move_candidate(event):
            return None
        if (
            event.source == "stcn"
            and any(keyword in title for keyword in LOW_SIGNAL_STCN_PUBLIC_AFFAIRS_TITLE_KEYWORDS)
        ):
            return None
        if _is_low_signal_stcn_charging_infrastructure_candidate(event):
            return None
        if _is_low_signal_stcn_fund_manager_commentary_candidate(event):
            return None
        if _is_low_signal_stcn_industry_prosperity_story_candidate(event):
            return None
        if _is_low_signal_robot_competition_story_candidate(event):
            return None
        if _is_low_signal_private_robot_financing_story_candidate(event):
            return None
        return "general_fast_news_with_theme"
    if (
        event.event_type == "fast_news"
        and event.event_subtype == "company_update"
        and _contains_any(title, FAST_NEWS_LEGAL_REVIEW_KEYWORDS)
    ):
        if _is_low_signal_irm_cninfo_legal_question_only(event, text):
            return None
        return "company_update_legal_keyword"
    if (
        event.event_type == "fast_news"
        and event.event_subtype == "market_move"
        and any(title.startswith(prefix) for prefix in SUSPICIOUS_MARKET_ROUNDUP_PREFIXES)
    ):
        return "market_roundup_candidate"
    return None


def _is_cls_editorial_roundup_column(event: Event) -> bool:
    return (
        event.source == "cls"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "【公告全知道】" in event.canonical_title
    )


def _is_low_signal_market_roundup_candidate(event: Event) -> bool:
    if not (
        event.source in {"stcn", "cls"}
        and event.event_type == "fast_news"
        and event.event_subtype == "market_move"
    ):
        return False

    title = event.canonical_title
    return any(title.startswith(prefix) for prefix in SUSPICIOUS_MARKET_ROUNDUP_PREFIXES) or any(
        keyword in title for keyword in LOW_SIGNAL_MARKET_ROUNDUP_KEYWORDS
    )


def _is_low_signal_robot_competition_story_candidate(event: Event) -> bool:
    if not (
        event.source in {"cls", "stcn"}
        and event.event_type == "fast_news"
        and event.event_subtype in {"general_fast_news", "company_update"}
    ):
        return False

    title = event.canonical_title
    text = f"{event.canonical_title} {event.summary}"
    return (
        "机器人半马" in title
        or ("半程马拉松" in text and any(keyword in text for keyword in ("率先冲线", "鸣枪开跑", "净成绩")))
        or (
            any(keyword in text for keyword in ("半程马拉松", "机器人半马"))
            and any(keyword in text for keyword in ("夺冠", "冠军"))
            and any(keyword in text for keyword in ("结构件", "供应商", "批量交付", "量产"))
        )
        or (
            any(keyword in text for keyword in ("人形机器人马拉松", "排位赛"))
            and any(keyword in text for keyword in ("世界纪录", "按比例计算"))
        )
    )


def _is_low_signal_private_robot_financing_story_candidate(event: Event) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
    ):
        return False

    title = event.canonical_title
    return (
        "Pre-A轮融资" in title
        and "机器人应用" in title
        and "交付能力" in title
    )


def _is_low_signal_stcn_charging_infrastructure_candidate(event: Event) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
    ):
        return False

    return any(
        keyword in event.canonical_title
        for keyword in LOW_SIGNAL_STCN_CHARGING_INFRASTRUCTURE_TITLE_KEYWORDS
    )


def _is_low_signal_stcn_fund_manager_commentary_candidate(event: Event) -> bool:
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and "基金经理" in event.canonical_title
        and any(
            keyword in event.canonical_title
            for keyword in LOW_SIGNAL_STCN_FUND_MANAGER_COMMENTARY_EXTRA_TITLE_KEYWORDS
        )
    )


def _is_low_signal_stcn_wti_general_fast_news_candidate(event: Event) -> bool:
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and event.canonical_title.startswith(
            LOW_SIGNAL_STCN_WTI_GENERAL_FAST_NEWS_TITLE_PREFIX
        )
    )


def _is_low_signal_stcn_brent_upward_volatility_general_fast_news_candidate(
    event: Event,
) -> bool:
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and event.canonical_title.startswith(
            LOW_SIGNAL_STCN_BRENT_UPWARD_VOLATILITY_FAST_NEWS_TITLE_PREFIX
        )
    )


def _is_low_signal_stcn_precious_metal_spot_move_candidate(event: Event) -> bool:
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and event.canonical_title.startswith(LOW_SIGNAL_STCN_PRECIOUS_METAL_SPOT_MOVE_TITLE_PREFIXES)
        and any(
            keyword in event.canonical_title
            for keyword in LOW_SIGNAL_STCN_PRECIOUS_METAL_SPOT_MOVE_TITLE_KEYWORDS
        )
    )


def _is_low_signal_stcn_industry_prosperity_story_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "高景气延续" in event.canonical_title
        and "重点布局方向" in event.canonical_title
        and "机构分析认为" in text
        and "有望获益" in text
    )


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _is_low_signal_cninfo_restructuring_material(title: str) -> bool:
    return (
        _contains_any(title, LOW_SIGNAL_CNINFO_RESTRUCTURING_MATERIAL_KEYWORDS)
        or ("审核问询函" in title and _contains_any(title, ("回复", "之回复")))
    ) and (
        _contains_any(title, LOW_SIGNAL_CNINFO_RESTRUCTURING_CONTEXT_KEYWORDS)
        or _contains_any(title, LOW_SIGNAL_FINANCING_MATERIAL_CONTEXT_KEYWORDS)
    )


def _is_low_signal_hard_event_risk_disclosure(title: str) -> bool:
    return _contains_any(title, LOW_SIGNAL_HARD_EVENT_RISK_DISCLOSURE_KEYWORDS)


def _is_low_signal_irm_cninfo_legal_question_only(event: Event, text: str) -> bool:
    return (
        event.source in {"irm_cninfo", "sse_einteractive"}
        and "未决诉讼事项" in event.canonical_title
        and "会计处理政策" in event.canonical_title
        and (
            (
                "披露义务" in event.canonical_title
                and all(marker not in text for marker in ("回复：", "回复:"))
            )
            or "履行信息披露义务" in text
        )
    )


def run_live_smoke(paths: ProjectPaths, source: str) -> int:
    collect_result = run_collect(paths, source)
    run_normalize(paths)
    run_merge_events(paths)
    run_analyze_events(paths)
    run_report(paths)

    raw_count = len(JsonlStore(paths.raw_news_path, RawNews).read_all())
    normalized_count = len(JsonlStore(paths.normalized_news_path, NormalizedNews).read_all())
    event_count = len(JsonlStore(paths.events_path, Event).read_all())
    analysis_count = len(JsonlStore(paths.analyses_path, EventAnalysis).read_all())
    print(
        " ".join(
            [
                f"raw_news={raw_count}",
                f"normalized_news={normalized_count}",
                f"events={event_count}",
                f"analyses={analysis_count}",
                f"failed_sources={format_collect_failures(collect_result.failed_sources)}",
                f"report={paths.latest_report_path}",
            ]
        )
    )
    return 0
