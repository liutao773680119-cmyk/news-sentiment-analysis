from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from news_sentiment.config_loader import load_theme_registry
from news_sentiment.models import Event

COMPANY_THEME_EVENT_SUBTYPES = {
    "financing_acceptance",
    "control_change",
    "equity_incentive",
    "executive_change",
    "order_contract",
    "cooperation_agreement",
    "acquisition_restructuring",
}
FAST_NEWS_FINANCIAL_RESULT_KEYWORDS = (
    "净利润",
    "营业收入",
    "营收",
    "年报",
    "季报",
    "一季报",
    "半年报",
    "三季报",
    "业绩",
    "扭亏为盈",
    "亏损",
)


def detect_themes(text: str) -> list[str]:
    return list(_detect_theme_hits(text).keys())


def _detect_theme_hits(text: str, *, include_theme_name: bool = True) -> dict[str, int]:
    registry = load_theme_registry()
    matches: dict[str, int] = {}
    normalized_text = text.lower()
    for theme in registry.themes:
        tokens = list(theme.aliases)
        if include_theme_name and theme.match_name:
            tokens.insert(0, theme.name)
        hit_count = sum(1 for token in tokens if token.lower() in normalized_text)
        if hit_count:
            matches[theme.name] = hit_count
    return matches


def detect_event_themes(event: Event) -> list[str]:
    title_matches = detect_themes(event.canonical_title)
    if event.event_type == "policy":
        if title_matches:
            matches = title_matches
        else:
            summary_hits = _detect_theme_hits(event.summary, include_theme_name=False)
            matches = [theme for theme, hit_count in summary_hits.items() if hit_count >= 2]
    elif event.event_type == "fast_news":
        if title_matches:
            if _is_company_update_title_theme_spillover(event, title_matches):
                matches = []
            else:
                matches = title_matches
        elif event.event_subtype == "market_move":
            matches = []
        elif event.event_subtype == "general_fast_news":
            matches = []
        elif _is_company_update_summary_theme_spillover(event):
            matches = []
        elif _is_financial_result_business_guidance(event):
            matches = []
        elif _is_regional_industry_data_theme_spillover(event):
            matches = []
        else:
            matches = detect_themes(f"{event.canonical_title} {event.summary}")
    else:
        matches = detect_themes(f"{event.canonical_title} {event.summary}")
    stock_code = _extract_stock_code_from_url(event.url)
    if stock_code and event.event_subtype in COMPANY_THEME_EVENT_SUBTYPES:
        matches.extend(_load_company_theme_map().get(stock_code, []))
    return list(dict.fromkeys(matches))


def detect_direction(text: str) -> str:
    bullish_tokens = ("支持", "推进", "发布", "突破", "增长")
    bearish_tokens = (
        "限制",
        "处罚",
        "重大诉讼",
        "涉及诉讼",
        "诉讼进展",
        "立案通知书",
        "立案告知书",
        "被立案调查",
        "中国证券监督管理委员会立案",
        "中国证监会立案",
        "下滑",
        "收缩",
        "风险",
        "PROFIT WARNING",
        "WINDING UP PETITION",
        "申请重整",
        "预重整",
        "申请破产清算",
        "破产清算",
        "商标争议",
        "侵害发明专利权纠纷",
        "专利权纠纷",
        "ARBITRATION PROCEEDINGS",
    )
    if _is_bullish_profit_alert(text):
        return "bullish"
    if _is_bullish_risk_warning_revocation(text):
        return "bullish"
    if _is_bullish_control_change(text):
        return "bullish"
    if any(token in text for token in bullish_tokens):
        return "bullish"
    if any(token in text for token in bearish_tokens):
        return "bearish"
    return "neutral"


def _is_bullish_profit_alert(text: str) -> bool:
    return "POSITIVE PROFIT ALERT" in text


def _is_bullish_risk_warning_revocation(text: str) -> bool:
    return any(
        phrase in text
        for phrase in (
            "撤销其他风险警示",
            "撤销退市风险警示",
            "申请撤销退市风险警示",
            "申请撤销公司股票退市风险警示",
            "申请撤销对公司股票交易实施退市风险警示",
            "申请撤销其他风险警示",
        )
    )


def _is_bullish_control_change(text: str) -> bool:
    if "控制权" not in text:
        return False

    return any(keyword in text for keyword in ("收购", "取得", "获得"))


def _extract_stock_code_from_url(url: str) -> str:
    if not url:
        return ""
    query = parse_qs(urlparse(url).query)
    return query.get("stockCode", [""])[0]


def _is_financial_result_business_guidance(event: Event) -> bool:
    return (
        event.event_subtype == "business_guidance"
        and any(keyword in event.canonical_title for keyword in FAST_NEWS_FINANCIAL_RESULT_KEYWORDS)
    )


def _is_company_update_title_theme_spillover(event: Event, title_matches: list[str]) -> bool:
    if event.event_subtype != "company_update" or len(title_matches) != 1:
        return False

    return (
        title_matches == ["算力"]
        and "数据中心" in event.canonical_title
        and "电力供应领域" in f"{event.canonical_title} {event.summary}"
    )


def _is_company_update_summary_theme_spillover(event: Event) -> bool:
    if event.event_subtype != "company_update":
        return False

    if _is_foreign_relief_summary_theme_spillover(event):
        return True

    if _is_expert_interview_summary_theme_spillover(event):
        return True

    summary_hits = _detect_theme_hits(event.summary)
    if _is_company_setup_registry_summary_theme_spillover(event, summary_hits):
        return True

    if _is_background_track_summary_theme_spillover(event, summary_hits):
        return True

    if _is_application_field_summary_theme_spillover(event.summary, summary_hits):
        return True

    if len(summary_hits) < 2:
        return False

    return any(keyword in event.summary for keyword in ("应用场景", "下游应用领域"))


def _is_regional_industry_data_theme_spillover(event: Event) -> bool:
    if event.event_subtype != "industry_data":
        return False

    if event.canonical_title.startswith("主力资金监控："):
        return True

    if "：" not in event.canonical_title:
        return False

    if not any(keyword in event.canonical_title for keyword in ("先导产业", "产值", "工业增加值", "制造业增加值")):
        return False

    summary_hits = _detect_theme_hits(event.summary)
    return len(summary_hits) >= 2


def _is_foreign_relief_summary_theme_spillover(event: Event) -> bool:
    if event.source != "cls":
        return False

    if not any(keyword in event.canonical_title for keyword in ("纾困计划", "应对能源价格高企")):
        return False

    return all(keyword in event.summary for keyword in ("政府", "声明", "企业"))


def _is_expert_interview_summary_theme_spillover(event: Event) -> bool:
    if "教授" not in event.canonical_title:
        return False

    if not _detect_theme_hits(event.summary):
        return False

    return all(keyword in event.summary for keyword in ("专访", "表示"))


def _is_application_field_summary_theme_spillover(summary: str, summary_hits: dict[str, int]) -> bool:
    if len(summary_hits) != 1:
        return False

    return "领域" in summary and any(keyword in summary for keyword in ("应用于", "应用在", "用于"))


def _is_company_setup_registry_summary_theme_spillover(event: Event, summary_hits: dict[str, int]) -> bool:
    if len(summary_hits) != 1:
        return False

    if "成立" not in event.canonical_title or "公司" not in event.canonical_title:
        return False

    summary = event.summary
    return all(keyword in summary for keyword in ("企查查APP显示", "经营范围包含", "股权穿透显示"))


def _is_background_track_summary_theme_spillover(event: Event, summary_hits: dict[str, int]) -> bool:
    if len(summary_hits) != 1:
        return False

    if "项目定点" not in event.canonical_title:
        return False

    return "业绩说明会" in event.summary and any(
        keyword in event.summary for keyword in ("赛道之一", "量产交付", "预研发")
    )


@lru_cache(maxsize=1)
def _load_company_theme_map() -> dict[str, list[str]]:
    path = Path(__file__).resolve().parents[3] / "data" / "reference" / "company_theme_map.csv"
    if not path.exists():
        return {}

    rows: dict[str, list[str]] = {}
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.setdefault(row["stock_code"], []).append(row["theme_name"])
    return rows
