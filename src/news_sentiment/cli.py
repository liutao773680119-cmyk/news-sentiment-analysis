from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
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
    "watchdog-once",
    "watchdog-summary",
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
    "问询函》的回复公告",
    "审核问询函中有关财务会计问题的专项说明",
    "审核问询函中有关财务事项的说明",
    "审核问询函有关财务事项的说明",
    "问询函中有关财务事项的说明",
    "问询函中有关财务会计问题的专项说明",
    "报告书（修订稿）",
    "报告书(修订稿)",
    "独立财务顾问主办人",
)
LOW_SIGNAL_CNINFO_RESTRUCTURING_CONTEXT_KEYWORDS = (
    "发行股份购买资产",
    "发行股份及支付现金购买资产",
    "重大资产购买",
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
    "向特定对象发行优先股",
    "发行优先股",
    "向特定对象发行股票",
    "申请向特定对象发行股票",
    "向特定对象发行A股股票",
    "申请向特定对象发行A股股票",
)
LOW_SIGNAL_HARD_EVENT_RISK_DISCLOSURE_KEYWORDS = (
    "年报问询函回复",
    "问询函有关问题的专项说明",
    "年报的问询函相关事项的专项说明",
    "年报有关事项问询函",
    "年报有关事项的问询函",
    "年报问询函之回复",
    "年报问询函的回复",
    "年报问询函》的回复",
    "年报问询函》之回复",
    "年报的问询函的回复",
    "年报问询函的专项说明",
    "年报问询函审计相关事项的专项说明",
    "年报的问询函相关事项的法律意见书",
    "股价波动事项的问询函",
    "延期回复深圳证券交易所审核问询函的公告",
    "涉及评估问题的回复",
    "年报问询函》回复",
    "监管问询函的回复",
    "信息披露监管问询函回复",
    "信息披露监管问询函之回复",
    "信息披露监管问询函》的回复",
    "信息披露监管问询函》的回复公告",
    "信息披露监管问询函的回复",
    "信息披露监管问询函的回复公告",
    "信息披露监管问询函专项说明",
    "信息披露监管问询函的专项说明",
    "年度报告信息披露监管问询函专说明",
    "采矿权评估发表意见",
    "股票交易异常波动问询函",
    "股票交易异常波动有关事项的问询函",
    "问询函相关问题之专项核查意见",
    "立案调查进展暨风险提示公告",
    "申请仲裁的进展公告",
    "涉及仲裁的进展公告",
    "注销已回购股份暨股份变动",
    "以集中竞价交易方式首次回购股份",
    "限制性股票激励计划首次授予结果",
    "诉讼事项的进展",
    "仲裁事项的进展",
    "涉及诉讼进展",
    "诉讼进展公告",
    "关于诉讼的进展公告",
    "提起诉讼的进展公告",
    "进展暨公司涉及诉讼事项的公告",
    "累计诉讼",
    "累计新增诉讼",
    "新增诉讼的公告",
    "提起诉讼的公告",
    "新增诉讼及进展情况",
    "重大诉讼公告",
    "重大诉讼的公告",
    "重大诉讼、仲裁情况进展",
    "追偿权纠纷诉讼的进展公告",
    "失信被执行人",
    "轮候冻结",
    "部分债务逾期和部分银行账户被冻结",
    "公司部分银行账户被冻结",
    "银行账户部分资金被冻结",
    "募集资金账户被冻结",
    "股东所持部分股份冻结",
    "控股股东股份被冻结",
    "控股股东部分股份冻结",
    "冻结股份被动减持计划",
    "解除司法冻结",
    "持股5%以上股东股份解除冻结",
    "一致行动人部分股份解除冻结",
    "控股股东所持公司部分股份解除冻结",
    "控股子公司部分银行账户资金解除冻结",
    "诉讼案件进展",
    "诉讼案件进展情况",
    "强制执行完成",
    "关于仲裁进展的公告",
    "子公司提起仲裁的公告",
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
    "集成电路领域企业家座谈",
    "油气储存企业部级专家指导服务",
    "看望慰问“五一”假期在岗一线劳动者并调研重点工作进展情况",
    "加强新能源汽车安全管理工作视频会",
    "专题调研集成电路产业发展工作",
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
    "日内跌幅达",
    "震荡走高",
    "震荡走低",
    "站上",
)
LOW_SIGNAL_STCN_FUND_MANAGER_COMMENTARY_EXTRA_TITLE_KEYWORDS = (
    "投资机会",
)
LOW_SIGNAL_STCN_GLOBAL_CAPITAL_A_SHARE_ALLOCATION_TITLE_KEYWORDS = (
    "增配A股",
    "黄金窗口期",
)
LOW_SIGNAL_STCN_GLOBAL_CAPITAL_A_SHARE_ALLOCATION_BODY_KEYWORDS = (
    "全球投资者大会",
    "中国资产",
    "低配状态",
)
LOW_SIGNAL_STCN_STOCK_SCREEN_OBSERVATION_TITLE_KEYWORDS = (
    "滞涨",
    "融资客重仓",
)
LOW_SIGNAL_STCN_STOCK_SCREEN_OBSERVATION_BODY_KEYWORDS = (
    "融资余额",
    "累计涨幅低于",
    "按照融资余额增幅排序",
)
LOW_SIGNAL_STCN_STORAGE_LITHIUM_PRICE_OBSERVATION_TITLE_KEYWORDS = (
    "海外储能需求",
    "锂价传导机制",
)
LOW_SIGNAL_STCN_STORAGE_LITHIUM_PRICE_OBSERVATION_BODY_KEYWORDS = (
    "记者采访获悉",
    "全球储能需求增速",
    "价格联动",
)
LOW_SIGNAL_STCN_NIGHT_SESSION_COMMODITY_MOVE_TITLE_KEYWORDS = (
    "涨近",
    "跌近",
    "涨超",
    "跌超",
)
MARKET_REFERENCE_GLOBAL_INDEX_SECTOR_MOVE_TITLE_PREFIXES = (
    "纳斯达克综合指数",
    "道琼斯指数",
    "标普500指数",
)
MARKET_REFERENCE_GLOBAL_INDEX_SECTOR_MOVE_CONTEXT_KEYWORDS = (
    "股票集体上涨",
    "股票集体下跌",
    "板块集体上涨",
    "板块集体下跌",
)
MARKET_REFERENCE_A_SHARE_CONCEPT_MOVE_CONTEXT_KEYWORDS = (
    "股价创新高",
    "涨停",
    "连板",
    "涨逾",
    "涨近",
    "大涨",
    "涨幅居前",
)
MARKET_REFERENCE_A_SHARE_INDEX_SECTOR_ACTIVE_TITLE_KEYWORDS = (
    "创业板指",
    "深证成指",
    "沪指",
)
MARKET_REFERENCE_HK_THEME_MOVE_CONTEXT_KEYWORDS = (
    "拉升",
    "涨逾",
    "涨幅扩大",
    "涨近",
)


@dataclass(frozen=True)
class CollectResult:
    rows: list[RawNews]
    failed_sources: list[CollectFailure]


@dataclass(frozen=True)
class LiveSmokeStatus:
    raw_count: int
    normalized_count: int
    event_count: int
    analysis_count: int
    failed_sources: list[CollectFailure]
    report_path: Path


@dataclass(frozen=True)
class SuspiciousCandidate:
    reason: str
    event: Event
    analysis: EventAnalysis


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
    watchdog_parser = subparsers.add_parser("watchdog-once")
    watchdog_parser.add_argument("--source", default="all")
    watchdog_parser.add_argument("--limit", type=int, default=10)
    watchdog_summary_parser = subparsers.add_parser("watchdog-summary")
    watchdog_summary_parser.add_argument("--hours", type=int, default=6)
    watchdog_summary_parser.add_argument("--now")
    watchdog_summary_parser.add_argument("--log-path", type=Path)
    watchdog_summary_parser.add_argument("--log-timezone", choices=("local", "utc"), default="local")
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
    if args.command == "watchdog-once":
        from news_sentiment.watchdog import run_watchdog_once

        return run_watchdog_once(paths, args.source, args.limit)
    if args.command == "watchdog-summary":
        from news_sentiment.watchdog_summary import run_watchdog_summary

        return run_watchdog_summary(
            paths,
            hours=args.hours,
            now=args.now,
            log_path=args.log_path,
            log_timezone=args.log_timezone,
        )
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
    candidates = collect_suspicious_candidates(paths)
    print(f"suspicious_count={len(candidates)}")
    for candidate in candidates[: max(limit, 0)]:
        event = candidate.event
        analysis = candidate.analysis
        themes = ",".join(analysis.themes) if analysis.themes else "无"
        print(
            " | ".join(
                [
                    f"reason={candidate.reason}",
                    f"subtype={event.event_subtype}",
                    f"direction={analysis.direction}",
                    f"score={analysis.impact_score:.1f}",
                    f"themes={themes}",
                    f"title={event.canonical_title}",
                ]
            )
        )
    return 0


def collect_suspicious_candidates(paths: ProjectPaths) -> list[SuspiciousCandidate]:
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
        candidates.append(SuspiciousCandidate(reason=reason, event=event, analysis=analysis))

    candidates.sort(
        key=lambda candidate: (candidate.analysis.impact_score, candidate.event.published_at),
        reverse=True,
    )
    return candidates


def _is_st_title(title: str) -> bool:
    normalized_title = title.lstrip()
    return normalized_title.startswith("*ST") or normalized_title.startswith("ST")


def _suspicious_reason(event: Event, analysis: EventAnalysis) -> str | None:
    title = event.canonical_title
    text = f"{event.canonical_title} {event.summary}"
    if _is_st_title(title):
        return None
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
        if _is_market_reference_global_index_sector_move_candidate(event):
            return None
        if _is_market_reference_a_share_index_sector_active_candidate(event):
            return None
        if _is_market_reference_stcn_overseas_storage_project_candidate(event):
            return None
        if _is_market_reference_a_share_concept_move_candidate(event):
            return None
        if _is_market_reference_hk_theme_move_candidate(event):
            return None
        if _is_market_reference_stcn_interactive_theme_chain_candidate(event):
            return None
        if _is_market_reference_stcn_insurance_asset_management_regulation_candidate(event):
            return None
        if _is_low_signal_stcn_wti_general_fast_news_candidate(event):
            return None
        if _is_low_signal_stcn_crude_low_general_fast_news_candidate(event):
            return None
        if _is_low_signal_stcn_crude_main_contract_percent_move_candidate(event):
            return None
        if _is_low_signal_stcn_brent_upward_volatility_general_fast_news_candidate(event):
            return None
        if _is_low_signal_stcn_precious_metal_spot_move_candidate(event):
            return None
        if _is_low_signal_stcn_central_bank_gold_reserve_brief_candidate(event):
            return None
        if _is_low_signal_stcn_phase_one_clinical_trial_start_candidate(event):
            return None
        if _is_low_signal_stcn_sector_fund_flow_observation_candidate(event):
            return None
        if _is_stcn_project_cooperation_catalyst_candidate(event):
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
        if _is_low_signal_stcn_global_capital_a_share_allocation_commentary_candidate(event):
            return None
        if _is_low_signal_stcn_stock_screen_observation_candidate(event):
            return None
        if _is_low_signal_stcn_financing_balance_recap_candidate(event):
            return None
        if _is_low_signal_stcn_storage_lithium_price_observation_candidate(event):
            return None
        if _is_low_signal_stcn_night_session_commodity_move_candidate(event):
            return None
        if _is_low_signal_stcn_industry_prosperity_story_candidate(event):
            return None
        if _is_low_signal_stcn_storage_grid_connection_story_candidate(event):
            return None
        if _is_low_signal_stcn_storage_collection_station_commissioning_story_candidate(event):
            return None
        if _is_low_signal_stcn_storage_system_delivery_progress_candidate(event):
            return None
        if _is_low_signal_stcn_overseas_storage_landing_validation_story_candidate(event):
            return None
        if _is_low_signal_stcn_space_compute_innovation_center_meeting_story_candidate(event):
            return None
        if _is_low_signal_stcn_space_compute_research_institute_establishment_story_candidate(event):
            return None
        if _is_low_signal_stcn_overseas_satellite_orbit_maintenance_story_candidate(event):
            return None
        if _is_low_signal_investing_economic_colombia_runoff_story_candidate(event):
            return None
        if _is_low_signal_investing_news_glp1_access_program_story_candidate(event):
            return None
        if _is_low_signal_stcn_undersea_data_center_story_candidate(event):
            return None
        if _is_low_signal_stcn_largest_storage_station_story_candidate(event):
            return None
        if _is_low_signal_stcn_company_visit_exchange_story_candidate(event):
            return None
        if _is_low_signal_stcn_foreign_mayor_delegation_exchange_story_candidate(event):
            return None
        if _is_low_signal_stcn_chairman_meeting_exchange_story_candidate(event):
            return None
        if _is_low_signal_stcn_storage_president_appointment_story_candidate(event):
            return None
        if _is_low_signal_stcn_space_compute_ecosystem_plan_story_candidate(event):
            return None
        if _is_low_signal_stcn_etf_premium_risk_suspension_notice(event):
            return None
        if _is_low_signal_robot_competition_story_candidate(event):
            return None
        if _is_low_signal_stcn_electric_robot_validation_platform_candidate(event):
            return None
        if _is_low_signal_stcn_robotaxi_internal_test_story_candidate(event):
            return None
        if _is_low_signal_private_robot_financing_story_candidate(event):
            return None
        if _is_low_signal_overseas_pharma_antitrust_lawsuit_candidate(event):
            return None
        return "general_fast_news_with_theme"
    if (
        event.event_type == "fast_news"
        and event.event_subtype == "company_update"
        and _contains_any(title, FAST_NEWS_LEGAL_REVIEW_KEYWORDS)
    ):
        if _is_low_signal_irm_cninfo_legal_question_only(event, text):
            return None
        if _is_low_signal_irm_cninfo_mna_litigation_governance_question(event, text):
            return None
        if _is_low_signal_irm_cninfo_legal_schedule_follow_up_question(event, text):
            return None
        if _is_low_signal_irm_cninfo_legal_litigation_follow_up_question(event, text):
            return None
        if _is_low_signal_irm_cninfo_legal_arbitration_follow_up_question(event, text):
            return None
        if _is_low_signal_irm_cninfo_subsidiary_risk_question(event, text):
            return None
        if _is_low_signal_irm_cninfo_legal_complaint_question_only(event, text):
            return None
        if _is_low_signal_cls_overseas_legal_response_candidate(event, text):
            return None
        if _is_low_signal_sse_einteractive_litigation_disposal_suggestion(event, text):
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
    ) or (
        "生物医药" in title
        and "完成" in title
        and "C轮融资" in title
    )


def _is_low_signal_stcn_robotaxi_internal_test_story_candidate(event: Event) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
    ):
        return False

    text = f"{event.canonical_title} {event.summary}"
    return (
        "Robotaxi" in text
        and "内测" in text
        and "服务商" in text
        and not _contains_any(text, ("订单", "中标", "合同", "量产", "交付"))
    )


def _is_low_signal_stcn_electric_robot_validation_platform_candidate(event: Event) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
    ):
        return False

    text = f"{event.canonical_title} {event.summary}"
    return (
        "电力具身智能机器人中试验证平台" in text
        and "对外提供服务" in text
        and "国网北京市电力公司" in text
        and not _contains_any(text, ("订单", "中标", "合同", "量产", "交付"))
    )


def _is_low_signal_overseas_pharma_antitrust_lawsuit_candidate(event: Event) -> bool:
    if not (
        event.source == "investing_news"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
    ):
        return False

    text = f"{event.canonical_title} {event.summary}".lower()
    return (
        _contains_any(text, ("antitrust", "lawsuit", "jury"))
        and _contains_any(text, ("takeda", "generic", "drug", "pharma", "pharmaceutical"))
    )


def _is_low_signal_cls_overseas_legal_response_candidate(event: Event, text: str) -> bool:
    return (
        event.source == "cls"
        and event.event_type == "fast_news"
        and event.event_subtype == "company_update"
        and "OpenAI" in text
        and "苹果公司" in text
        and "诉讼案" in text
        and "未发现任何证据" in text
        and "合理依据" in text
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


def _is_low_signal_stcn_night_session_commodity_move_candidate(event: Event) -> bool:
    title = event.canonical_title
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and ("国内商品期货夜盘开盘" in title or "国内商品期货夜盘收盘" in title)
        and _contains_any(title, LOW_SIGNAL_STCN_NIGHT_SESSION_COMMODITY_MOVE_TITLE_KEYWORDS)
    )


def _is_market_reference_global_index_sector_move_candidate(event: Event) -> bool:
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and event.canonical_title.startswith(
            MARKET_REFERENCE_GLOBAL_INDEX_SECTOR_MOVE_TITLE_PREFIXES
        )
        and _contains_any(
            event.canonical_title,
            MARKET_REFERENCE_GLOBAL_INDEX_SECTOR_MOVE_CONTEXT_KEYWORDS,
        )
    )


def _is_market_reference_a_share_concept_move_candidate(event: Event) -> bool:
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and (
            "概念走强" in event.canonical_title
            or "概念活跃" in event.canonical_title
            or "板块震荡走强" in event.canonical_title
            or "概念震荡回升" in event.canonical_title
            or "板块震荡回升" in event.canonical_title
            or ("概念" in event.canonical_title and "涨幅居前" in event.canonical_title)
        )
        and _contains_any(
            f"{event.canonical_title} {event.summary}",
            MARKET_REFERENCE_A_SHARE_CONCEPT_MOVE_CONTEXT_KEYWORDS,
        )
    )


def _is_market_reference_a_share_index_sector_active_candidate(event: Event) -> bool:
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "板块活跃" in event.canonical_title
        and _contains_any(
            event.canonical_title,
            MARKET_REFERENCE_A_SHARE_INDEX_SECTOR_ACTIVE_TITLE_KEYWORDS,
        )
        and _contains_any(
            event.canonical_title,
            ("涨逾", "涨近", "大涨"),
        )
    )


def _is_market_reference_stcn_overseas_storage_project_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "Solarpro Holding" in event.canonical_title
        and "宁德时代" in text
        and "储能项目" in event.canonical_title
        and _contains_any(text, ("并网投运", "投运", "长期合作意向"))
    )


def _is_market_reference_hk_theme_move_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "港股" in text
        and _contains_any(text, ("AI应用", "大模型"))
        and _contains_any(text, MARKET_REFERENCE_HK_THEME_MOVE_CONTEXT_KEYWORDS)
    )


def _is_market_reference_stcn_interactive_theme_chain_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and event.canonical_title.startswith("【淘金互动易】")
        and _contains_any(text, ("产业链", "机构持续看好"))
        and _contains_any(text, ("将应用于", "已应用于", "规模化落地", "最新布局"))
    )


def _is_market_reference_stcn_insurance_asset_management_regulation_candidate(
    event: Event,
) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "保险资管" in text
        and "监管要求" in event.canonical_title
        and "金融监管总局" in text
        and "四个支柱" in text
        and _contains_any(text, ("投资者保护", "系统性风险", "宏观审慎"))
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


def _is_low_signal_stcn_crude_low_general_fast_news_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "原油期价" in event.canonical_title
        and "新低" in event.canonical_title
        and _contains_any(text, ("轻质原油期货价格", "纽约商品交易所"))
        and not _contains_any(text, ("供应中断", "制裁", "战争", "减产", "库存"))
    )


def _is_low_signal_stcn_crude_main_contract_percent_move_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "上期所原油主力合约" in text
        and _contains_any(text, ("涨幅扩大至", "跌幅扩大至"))
        and "报" in text
        and not _contains_any(text, ("供应中断", "制裁", "战争", "减产", "库存"))
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


def _is_low_signal_stcn_central_bank_gold_reserve_brief_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "央行数据" in text
        and "黄金储备" in text
        and "增持黄金" in text
    )


def _is_low_signal_stcn_phase_one_clinical_trial_start_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "I期临床试验" in text
        and _contains_any(text, ("启动", "正式启动"))
        and _contains_any(text, ("临床前研究", "联合研发"))
        and not _contains_any(text, ("获批上市", "批准上市", "商业化", "销售收入", "订单"))
    )


def _is_low_signal_stcn_sector_fund_flow_observation_candidate(event: Event) -> bool:
    title = event.canonical_title
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "指数" in title
        and "主力资金" in title
        and _contains_any(text, ("概念指数", "成份股", "主力资金净流入"))
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "采购", "获批"))
    )


def _is_stcn_project_cooperation_catalyst_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "项目合作" in event.canonical_title
        and _contains_any(text, ("签约", "签署", "合作"))
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


def _is_low_signal_stcn_global_capital_a_share_allocation_commentary_candidate(
    event: Event,
) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and _contains_any(
            event.canonical_title,
            LOW_SIGNAL_STCN_GLOBAL_CAPITAL_A_SHARE_ALLOCATION_TITLE_KEYWORDS,
        )
        and _contains_any(text, LOW_SIGNAL_STCN_GLOBAL_CAPITAL_A_SHARE_ALLOCATION_BODY_KEYWORDS)
    )


def _is_low_signal_stcn_stock_screen_observation_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and _contains_any(event.canonical_title, LOW_SIGNAL_STCN_STOCK_SCREEN_OBSERVATION_TITLE_KEYWORDS)
        and _contains_any(text, LOW_SIGNAL_STCN_STOCK_SCREEN_OBSERVATION_BODY_KEYWORDS)
    )


def _is_low_signal_stcn_financing_balance_recap_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and _contains_any(event.canonical_title, ("融资资金", "融资客"))
        and _contains_any(text, ("融资余额", "融资净买入", "融资净偿还"))
        and _contains_any(text, ("据证券时报·数据宝统计", "数据宝统计"))
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "获批", "投产"))
    )


def _is_low_signal_stcn_storage_lithium_price_observation_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and _contains_any(
            event.canonical_title,
            LOW_SIGNAL_STCN_STORAGE_LITHIUM_PRICE_OBSERVATION_TITLE_KEYWORDS,
        )
        and _contains_any(text, LOW_SIGNAL_STCN_STORAGE_LITHIUM_PRICE_OBSERVATION_BODY_KEYWORDS)
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "采购"))
    )


def _is_low_signal_stcn_undersea_data_center_story_candidate(event: Event) -> bool:
    title = event.canonical_title
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "海底数据中心" in title
        and "落户" in title
        and "东海" in title
    )


def _is_low_signal_stcn_largest_storage_station_story_candidate(event: Event) -> bool:
    title = event.canonical_title
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "智能组串式储能电站" in title
        and "落地" in title
        and "内蒙古" in title
    )


def _is_low_signal_stcn_company_visit_exchange_story_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "拜访" in event.canonical_title
        and "交流" in event.canonical_title
        and _contains_any(text, ("持续推进交流对接", "进行了交流"))
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "采购"))
    )


def _is_low_signal_stcn_foreign_mayor_delegation_exchange_story_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "市长率团" in event.canonical_title
        and _contains_any(text, ("率团访问", "访蓉", "代表团参访"))
        and _contains_any(text, ("座谈", "交流", "参访"))
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "采购"))
    )


def _is_low_signal_investing_economic_colombia_runoff_story_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "investing_economic"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "Colombia" in text
        and "runoff" in text
        and _contains_any(text, ("De La Espriella", "Cepeda"))
    )


def _is_low_signal_investing_news_glp1_access_program_story_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "investing_news"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "GLP-1" in text
        and "Older Americans" in text
        and "program" in text
        and not _contains_any(text, ("FDA approval", "trial", "earnings", "guidance"))
    )


def _is_low_signal_stcn_chairman_meeting_exchange_story_candidate(event: Event) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "会见" in event.canonical_title
        and ("董事" in event.canonical_title or "友邦保险" in text)
        and "主席" in event.canonical_title
        and _contains_any(
            text,
            (
                "进行交流",
                "进行了交流",
                "交换意见",
                "合作等话题",
                "深化互利合作",
                "加大投资布局",
                "互利共赢",
            ),
        )
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "采购"))
    )


def _is_low_signal_stcn_storage_president_appointment_story_candidate(event: Event) -> bool:
    title = event.canonical_title
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "晶澳科技" in text
        and "王君生" in text
        and "任命" in title
        and "储能公司总裁" in title
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "采购"))
    )


def _is_low_signal_stcn_space_compute_ecosystem_plan_story_candidate(event: Event) -> bool:
    title = event.canonical_title
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "优刻得" in text
        and "加入" in title
        and "太空算力产业生态伙伴计划" in text
        and _contains_any(text, ("成立大会", "产业生态建设", "协同创新"))
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "采购"))
    )


def _is_low_signal_stcn_space_compute_research_institute_establishment_story_candidate(
    event: Event,
) -> bool:
    title = event.canonical_title
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "太空" in title
        and "研究院" in title
        and "成立" in title
        and _contains_any(
            text,
            (
                "注册成立",
                "试验星",
                "天地一体化网络",
                "星载算力芯片",
                "星间激光通信",
                "太空能源与散热",
                "空间安全标准",
            ),
        )
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "采购"))
    )


def _is_low_signal_stcn_storage_grid_connection_story_candidate(event: Event) -> bool:
    title = event.canonical_title
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "储能电站" in title
        and "全容量并网" in title
        and _contains_any(text, ("项目预计", "消纳绿电", "节约标准煤", "减排二氧化碳"))
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "采购"))
    )


def _is_low_signal_stcn_storage_collection_station_commissioning_story_candidate(
    event: Event,
) -> bool:
    title = event.canonical_title
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "储能电站" in title
        and "汇集站" in title
        and "投运" in title
        and _contains_any(text, ("顺利完成各项测试", "正式并网投运", "配套短板", "源网荷储一体化"))
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "采购"))
    )


def _is_low_signal_stcn_storage_system_delivery_progress_candidate(event: Event) -> bool:
    title = event.canonical_title
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "储能系统" in title
        and "交付" in title
        and "完成" in title
        and _contains_any(text, ("设备交付", "液冷储能系统", "新能源基地项目", "高比例并网"))
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "采购"))
    )


def _is_low_signal_stcn_overseas_storage_landing_validation_story_candidate(
    event: Event,
) -> bool:
    title = event.canonical_title
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "液冷储能" in title
        and "欧洲" in title
        and "落地验证" in title
        and _contains_any(text, ("欧洲市场", "工商业储能", "接连落地储能项目"))
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "采购"))
    )


def _is_low_signal_stcn_space_compute_innovation_center_meeting_story_candidate(
    event: Event,
) -> bool:
    title = event.canonical_title
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "太空算力" in title
        and "座谈会" in title
        and "创新中心" in title
        and "建设工作" in title
        and _contains_any(text, ("研究部署", "打造太空算力产业高地", "产业高地"))
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "采购"))
    )


def _is_low_signal_stcn_overseas_satellite_orbit_maintenance_story_candidate(
    event: Event,
) -> bool:
    title = event.canonical_title
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and _contains_any(text, ("美国航空航天局", "NASA"))
        and _contains_any(text, ("天文卫星", "天文台"))
        and _contains_any(text, ("抬升", "轨道高度", "延长其使用寿命", "延长工作寿命"))
        and not _contains_any(text, ("签署", "中标", "订单", "合同", "采购"))
        and title.startswith("美发射商业航天器")
    )


def _is_low_signal_stcn_etf_premium_risk_suspension_notice(event: Event) -> bool:
    title = event.canonical_title
    text = f"{event.canonical_title} {event.summary}"
    return (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
        and "ETF" in title
        and "停牌" in title
        and "基金" in text
        and "溢价幅度" in text
        and _contains_any(text, ("警示风险", "临时停牌至收盘"))
    )


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _is_low_signal_cninfo_restructuring_material(title: str) -> bool:
    return _is_numbered_inquiry_reply_exemption_material(title) or (
        _contains_any(title, LOW_SIGNAL_CNINFO_RESTRUCTURING_MATERIAL_KEYWORDS)
        or ("审核问询函" in title and _contains_any(title, ("回复", "之回复")))
        or _is_restructuring_review_process_material(title)
    ) and (
        _contains_any(title, LOW_SIGNAL_CNINFO_RESTRUCTURING_CONTEXT_KEYWORDS)
        or _contains_any(title, LOW_SIGNAL_FINANCING_MATERIAL_CONTEXT_KEYWORDS)
    )


def _is_restructuring_review_process_material(title: str) -> bool:
    return (
        ("审核问询函" in title and _contains_any(title, ("收到", "申请")))
        or ("申请文件" in title and _contains_any(title, ("受理", "获得深圳证券交易所受理")))
    )


def _is_numbered_inquiry_reply_exemption_material(title: str) -> bool:
    return (
        "审核问询函的回复" in title
        and "豁免版" in title
        and _contains_any(title, ("发行人及保荐机构", "会计师"))
    )


def _is_low_signal_hard_event_risk_disclosure(title: str) -> bool:
    return _contains_any(title, LOW_SIGNAL_HARD_EVENT_RISK_DISCLOSURE_KEYWORDS) or (
        "被司法强制执行实施结果" in title
        and "解除质押及冻结" in title
        and "权益变动触及1%整数倍" in title
    ) or (
        "司法拍卖" in title
        and _contains_any(title, ("过户完成", "完成过户", "过户登记"))
        and (
            ("解除质押" in title and "解除司法再冻结" in title and "司法冻结" in title)
            or ("股份质押与冻结变动情况" in title and "触及1%整数倍" in title)
        )
    )


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


def _is_low_signal_irm_cninfo_mna_litigation_governance_question(
    event: Event, text: str
) -> bool:
    title = event.canonical_title
    return (
        event.source in {"irm_cninfo", "sse_einteractive"}
        and "诉讼" in title
        and "减持" in title
        and "回避表决" in title
        and "并购重组的子公司" in text
        and "不存在任何关联关系" in text
        and "经营一切正常有序开展" in text
    )


def _is_low_signal_irm_cninfo_legal_schedule_follow_up_question(
    event: Event, text: str
) -> bool:
    title = event.canonical_title
    return (
        event.source in {"irm_cninfo", "sse_einteractive"}
        and "简易判决动议" in title
        and "预计 7 月宣布开庭" in title
        and "后续相关公告" in text
    )


def _is_low_signal_irm_cninfo_legal_litigation_follow_up_question(
    event: Event, text: str
) -> bool:
    title = event.canonical_title
    return (
        event.source in {"irm_cninfo", "sse_einteractive"}
        and event.event_type == "fast_news"
        and event.event_subtype == "company_update"
        and "诉讼" in title
        and all(marker not in text for marker in ("回复：", "回复:"))
        and (
            ("进行到什么程度" in title or "进展如何" in title or "目前进展如何" in title)
            and _contains_any(title, ("什么时候开庭", "何时开庭", "庭外和解", "能庭外和解", "能和解吗"))
        )
    )


def _is_low_signal_irm_cninfo_legal_arbitration_follow_up_question(
    event: Event, text: str
) -> bool:
    title = event.canonical_title
    substantive_markers = (
        "目前案件正在依法推进",
        "正在依法推进",
        "已聘请律师",
        "已立案",
        "已开庭",
        "庭审",
        "判决",
        "裁定",
        "达成和解",
        "和解协议",
        "仲裁委员会",
        "仲裁裁决",
    )
    return (
        event.source in {"irm_cninfo", "sse_einteractive"}
        and event.event_type == "fast_news"
        and event.event_subtype == "company_update"
        and "仲裁" in title
        and _contains_any(
            title,
            (
                "目前案件进展如何",
                "目前进展如何",
                "案件进展如何",
                "仲裁进展如何",
                "仲裁进展如何了",
                "进展如何",
                "进展如何了",
            ),
        )
        and any(
            keyword in title
            for keyword in ("公司不存在与", "上市公司主体", "控股的子公司", "子公司存在仲裁案件", "全资子公司")
        )
        and (
            all(marker not in text for marker in ("回复：", "回复:"))
            or (
                _contains_any(
                    text,
                    (
                        "公司不存在与",
                        "以公司在指定信息披露网站公开披露的信息为准",
                    ),
                )
                and not _contains_any(text, substantive_markers)
            )
        )
    )


def _is_low_signal_irm_cninfo_subsidiary_risk_question(event: Event, text: str) -> bool:
    title = event.canonical_title
    return (
        event.source in {"irm_cninfo", "sse_einteractive"}
        and event.event_type == "fast_news"
        and event.event_subtype == "company_update"
        and "子公司" in title
        and any(keyword in title for keyword in ("商誉减值", "资产减值", "减值"))
        and any(
            keyword in title
            for keyword in ("诉讼败诉", "风险隐瞒", "持续经营能力", "资产质量", "经营失控", "今日闪崩")
        )
        and any(marker in text for marker in ("回复：", "回复:"))
    )


def _is_low_signal_irm_cninfo_legal_complaint_question_only(event: Event, text: str) -> bool:
    return (
        event.source in {"irm_cninfo", "sse_einteractive"}
        and all(marker not in text for marker in ("回复：", "回复:"))
        and _contains_any(text, ("诉讼", "查账诉讼"))
        and _contains_any(text, ("请问公司", "可否", "是否考虑"))
        and _contains_any(text, ("具体的解决方案", "尽快彻底解决", "不要因为这个事情毁掉"))
    )


def _is_low_signal_sse_einteractive_litigation_disposal_suggestion(event: Event, text: str) -> bool:
    title = event.canonical_title
    return (
        event.source == "sse_einteractive"
        and event.event_type == "fast_news"
        and event.event_subtype == "company_update"
        and "诉讼" in title
        and "建议" in title
        and _contains_any(title, ("挂牌转让", "剥离交割", "转达董事长"))
        and _contains_any(text, ("您的建议我们已收悉", "如实转达"))
    )


def run_live_smoke(paths: ProjectPaths, source: str) -> int:
    status = execute_live_smoke(paths, source)
    print(format_live_smoke_status(status))
    return 0


def execute_live_smoke(paths: ProjectPaths, source: str) -> LiveSmokeStatus:
    collect_result = run_collect(paths, source)
    run_normalize(paths)
    run_merge_events(paths)
    run_analyze_events(paths)
    run_report(paths)

    return LiveSmokeStatus(
        raw_count=len(JsonlStore(paths.raw_news_path, RawNews).read_all()),
        normalized_count=len(JsonlStore(paths.normalized_news_path, NormalizedNews).read_all()),
        event_count=len(JsonlStore(paths.events_path, Event).read_all()),
        analysis_count=len(JsonlStore(paths.analyses_path, EventAnalysis).read_all()),
        failed_sources=collect_result.failed_sources,
        report_path=paths.latest_report_path,
    )


def format_live_smoke_status(status: LiveSmokeStatus) -> str:
    return " ".join(
        [
            f"raw_news={status.raw_count}",
            f"normalized_news={status.normalized_count}",
            f"events={status.event_count}",
            f"analyses={status.analysis_count}",
            f"failed_sources={format_collect_failures(status.failed_sources)}",
            f"report={status.report_path}",
        ]
    )
