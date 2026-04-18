from __future__ import annotations

from datetime import datetime

from news_sentiment.config_loader import load_source_priority_map
from news_sentiment.models import Event, NormalizedNews

BROKER_COMMENTARY_ORGS = (
    "瑞银",
    "华泰证券",
    "中信证券",
    "中金公司",
    "国泰海通",
    "国联民生",
    "银河证券",
    "招商证券",
    "申万宏源",
    "广发证券",
)
MARKET_MOVE_ASSETS = (
    "现货黄金",
    "现货白银",
    "布伦特原油期货",
    "WTI原油期货",
    "沪金",
    "沪银",
    "沪指",
    "深证成指",
    "创业板指",
)
MARKET_MOVE_WINDOW_SECONDS = 15 * 60
STRUCTURED_CATALYST_WINDOW_SECONDS = 12 * 60 * 60
STRUCTURED_CATALYST_SUBTYPES = {
    "financing_acceptance",
    "control_change",
    "equity_incentive",
    "order_contract",
    "cooperation_agreement",
    "acquisition_restructuring",
    "reorganization_risk",
    "delisting_risk",
}
LEGAL_DISPUTE_KEYWORDS = (
    "商标争议",
    "侵害发明专利权纠纷",
    "专利权纠纷",
    "ARBITRATION PROCEEDINGS",
)
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
HKEX_FINANCIAL_RESULT_KEYWORDS = (
    "PROFIT WARNING",
    "PROFIT ALERT",
)
HKEX_TRANSACTION_KEYWORDS = (
    "CONNECTED TRANSACTION",
    "Connected Transaction",
    "CONTINUING CONNECTED TRANSACTIONS",
    "Continuing Connected Transactions",
    "MAJOR TRANSACTION",
    "Major Transaction",
    "VERY SUBSTANTIAL",
    "Very Substantial",
    "DISCLOSEABLE TRANSACTION",
    "Discloseable Transaction",
    "DISPOSAL OF",
    "Disposal of",
    "ACQUISITION OF",
    "Acquisition of",
)
HKEX_EXECUTIVE_CHANGE_KEYWORDS = (
    "CHANGE OF DIRECTORS",
    "RE-DESIGNATION OF DIRECTOR",
    "RESIGNATION OF CHIEF EXECUTIVE OFFICER",
    "APPOINTMENT OF CHIEF EXECUTIVE OFFICER",
    "CHANGE OF COMPANY SECRETARY",
)


def merge_news_items(items: list[NormalizedNews]) -> list[Event]:
    if not items:
        return []

    source_priorities = load_source_priority_map()
    groups: list[list[NormalizedNews]] = []
    for item in items:
        target_group = None
        for group in groups:
            if _should_merge(item, group[0]):
                target_group = group
                break
        if target_group is None:
            groups.append([item])
        else:
            target_group.append(item)

    events: list[Event] = []
    for index, group in enumerate(groups, start=1):
        first = min(group, key=lambda item: item.published_at)
        last = max(group, key=lambda item: item.published_at)
        authoritative = max(
            group,
            key=lambda item: (
                source_priorities.get(item.source, 0),
                item.published_at,
            ),
        )
        authority_priority = source_priorities.get(authoritative.source, 0)
        events.append(
            Event(
                event_id=f"event-{index:03d}",
                first_seen_at=first.published_at,
                last_seen_at=last.published_at,
                canonical_title=authoritative.title,
                summary=authoritative.content,
                source=authoritative.source,
                published_at=authoritative.published_at,
                url=authoritative.url,
                member_news_ids=[item.news_id for item in group],
                event_type=authoritative.source_type,
                event_subtype=_classify_event_subtype(
                    authoritative.source_type,
                    authoritative.title,
                    authoritative.content,
                ),
                primary_entities=[],
                source_authority_score=authority_priority / 100.0,
            )
        )
    return events


def _is_similar(left: str, right: str) -> bool:
    left_chars = {char for char in left if not char.isspace()}
    right_chars = {char for char in right if not char.isspace()}
    if not left_chars or not right_chars:
        return False
    overlap = len(left_chars & right_chars)
    base = min(len(left_chars), len(right_chars))
    return overlap / base >= 0.7


def _should_merge(left: NormalizedNews, right: NormalizedNews) -> bool:
    if left.source in {"hkex", "fed"} or right.source in {"hkex", "fed"}:
        return _is_same_market_move_asset(left, right) or _is_same_structured_catalyst(left, right)

    if _is_similar(left.title, right.title):
        return True

    return _is_same_market_move_asset(left, right) or _is_same_structured_catalyst(left, right)


def _is_same_market_move_asset(left: NormalizedNews, right: NormalizedNews) -> bool:
    if left.source_type != "fast_news" or right.source_type != "fast_news":
        return False

    left_asset = _extract_market_move_asset(f"{left.title} {left.content}")
    right_asset = _extract_market_move_asset(f"{right.title} {right.content}")
    if not left_asset or left_asset != right_asset:
        return False

    left_time = datetime.fromisoformat(left.published_at)
    right_time = datetime.fromisoformat(right.published_at)
    return abs((left_time - right_time).total_seconds()) <= MARKET_MOVE_WINDOW_SECONDS


def _extract_market_move_asset(text: str) -> str:
    if not _contains_any(
        text,
        ("涨幅扩大", "跌幅扩大", "涨超", "跌超", "跌破", "突破", "向上触及", "向下触及", "高开", "低开", "开盘"),
    ):
        return ""
    for asset in MARKET_MOVE_ASSETS:
        if asset in text:
            return asset
    return ""


def _is_same_structured_catalyst(left: NormalizedNews, right: NormalizedNews) -> bool:
    if left.source_type != "hard_event" or right.source_type != "hard_event":
        return False

    left_subtype = _classify_event_subtype(left.source_type, left.title, left.content)
    right_subtype = _classify_event_subtype(right.source_type, right.title, right.content)
    if left_subtype != right_subtype or left_subtype not in STRUCTURED_CATALYST_SUBTYPES:
        return False

    left_stock_code = _extract_stock_code_from_url(left.url)
    right_stock_code = _extract_stock_code_from_url(right.url)
    if not left_stock_code or left_stock_code != right_stock_code:
        return False

    left_time = datetime.fromisoformat(left.published_at)
    right_time = datetime.fromisoformat(right.published_at)
    return abs((left_time - right_time).total_seconds()) <= STRUCTURED_CATALYST_WINDOW_SECONDS


def _classify_event_subtype(source_type: str, title: str, content: str) -> str:
    text = f"{title} {content}"

    if source_type == "policy":
        if _contains_any(text, ("实施方案", "行动方案", "行动计划", "发展规划", "支持", "通知", "意见")):
            return "policy_support"
        return "policy_update"

    if source_type == "hard_event":
        if _contains_any(text, ("控制权", "股份转让协议", "实控人变更")):
            return "control_change"
        if _contains_any(text, ("申请重整", "预重整", "庭外重组", "申请破产清算", "破产清算", "WINDING UP PETITION")):
            return "reorganization_risk"
        if _contains_any(text, ("退市风险警示", "退市风险提示", "其他风险警示")):
            return "delisting_risk"
        if _contains_any(text, LEGAL_DISPUTE_KEYWORDS):
            return "legal_dispute"
        if _contains_any(text, HKEX_FINANCIAL_RESULT_KEYWORDS):
            return "business_guidance"
        if _contains_any(text, ("受理", "向特定对象发行", "定增", "发行股票申请")):
            return "financing_acceptance"
        if _contains_any(text, ("激励计划", "限制性股票", "归属")):
            return "equity_incentive"
        if _is_order_contract_fast_news(text):
            return "order_contract"
        if _contains_any(text, ("合作协议", "战略合作", "签署协议", "签订协议", "签署合作", "授权许可协议")):
            return "cooperation_agreement"
        if _contains_any(text, ("收购", "重组")) or _contains_any(text, HKEX_TRANSACTION_KEYWORDS):
            return "acquisition_restructuring"
        if _contains_any(text, ("董事会", "监事会", "股东大会", "会议决议")):
            return "board_resolution"
        if _contains_any(text, ("聘任", "辞任", "离任", "首席执行官", "总经理", "董事长")) or _contains_any(
            text,
            HKEX_EXECUTIVE_CHANGE_KEYWORDS,
        ):
            return "executive_change"
        return "corporate_disclosure"

    if source_type == "fast_news":
        if _is_broker_commentary_fast_news(title, text):
            return "general_fast_news"
        if _is_editorial_roundup_fast_news(title):
            return "general_fast_news"
        if _is_market_move_fast_news(title, text):
            return "market_move"
        if _is_policy_document_fast_news(title, text):
            return "policy_signal"
        if _is_policy_measure_fast_news(title, text):
            return "policy_signal"
        if _is_authority_statement_fast_news(title, text):
            return "policy_signal"
        if _is_industry_project_release_fast_news(text):
            return "policy_signal"
        if _contains_any(text, ("科学家", "研究人员", "研究团队", "科研")) and _contains_any(
            text,
            ("实现", "突破", "测试", "开发出", "新途径"),
        ):
            return "tech_breakthrough"
        if _is_financial_result_fast_news(title):
            return "business_guidance"
        if _is_industry_data_fast_news(text):
            return "industry_data"
        if _is_geopolitical_fast_news(text):
            return "general_fast_news"
        if _contains_any(text, LEGAL_DISPUTE_KEYWORDS):
            return "legal_dispute"
        if _is_equity_investment_fast_news(text):
            return "company_update"
        if _is_company_setup_fast_news(text):
            return "company_update"
        if _is_response_or_clarification_fast_news(title, text):
            return "company_update"
        if _contains_any(text, ("电话会议", "销售目标", "业绩指引", "收入", "利润", "盈利")):
            return "business_guidance"
        if _contains_any(title, ("获批上市", "获批", "上市申请", "药监局批准", "药品注册证书")):
            return "regulatory_approval"
        if _is_order_contract_fast_news(text):
            return "order_contract"
        if _is_cooperation_agreement_fast_news(text):
            return "cooperation_agreement"
        if _contains_any(text, ("收购", "重组")):
            return "acquisition_restructuring"
        if "：" in title or _contains_any(text, ("发布", "上线", "推出", "回应")):
            return "company_update"
        return "general_fast_news"

    return "general"


def _is_market_move_fast_news(title: str, text: str) -> bool:
    if _is_industry_price_data_fast_news(text):
        return False
    if _extract_market_move_asset(text):
        return True
    return _contains_any(title, ("涨停", "跌停", "涨超", "跌超", "大涨", "大跌", "跳水"))


def _is_editorial_roundup_fast_news(title: str) -> bool:
    return _contains_any(title, ("隔夜全球要闻", "新闻精选", "你需要知道"))


def _is_policy_document_fast_news(title: str, text: str) -> bool:
    if _contains_any(text, ("行动方案", "行动计划", "实施方案", "发展规划")):
        return True
    return _contains_any(title, ("通知", "意见", "印发"))


def _is_authority_statement_fast_news(title: str, text: str) -> bool:
    if "：" not in title:
        return False

    if not _contains_any(text, ("表示", "指出", "强调", "提出", "称", "说", "要求")):
        return False

    authority_markers = (
        "国务院",
        "国防科技工业局",
        "国家发改委",
        "发改委",
        "工信部",
        "财政部",
        "商务部",
        "证监会",
        "国家能源局",
        "国家药监局",
        "国家数据局",
        "司副司长",
        "副司长",
        "司长",
        "副局长",
        "局长",
        "副部长",
        "部长",
        "副主任",
        "主任",
        "负责人",
    )
    return _contains_any(text, authority_markers)


def _is_policy_measure_fast_news(title: str, text: str) -> bool:
    if not _contains_any(text, ("措施", "若干措施")):
        return False

    return _contains_any(
        text,
        (
            "有关部门",
            "北京市",
            "上海市",
            "深圳市",
            "广州市",
            "省政府",
            "市政府",
            "发改委",
            "卫健委",
            "药监局",
        ),
    ) or _contains_any(title, ("高质量发展措施",))


def _is_industry_project_release_fast_news(text: str) -> bool:
    return _contains_any(text, ("重点攻关项目", "攻关合作")) and _contains_any(
        text,
        ("产业大会", "专业委员会", "产业界"),
    )


def _is_cooperation_agreement_fast_news(text: str) -> bool:
    if not _contains_any(text, ("战略合作", "合作协议", "签署协议", "签订协议")):
        return False
    if _contains_any(text, ("违约", "终止", "破裂", "纠纷", "诉求")):
        return False
    return True


def _is_order_contract_fast_news(text: str) -> bool:
    if not _contains_any(text, ("中标", "订单", "合同")):
        return False
    if _contains_any(text, ("未能履行", "违约", "终止", "破裂", "纠纷", "诉求")):
        return False
    if _contains_any(text, ("订单数据", "保密协议", "不便公开披露")):
        return False
    return True


def _is_industry_data_fast_news(text: str) -> bool:
    if _contains_any(text, ("周活跃用户", "月活跃用户", "WAU", "MAU", "数据显示")):
        return True

    if _contains_any(text, ("库存", "较前周")) and _contains_any(
        text,
        ("原油", "汽油", "馏分油", "柴油"),
    ):
        return True

    if _contains_any(text, ("模型调用排行榜", "调用量")) and _contains_any(
        text,
        ("日榜", "Token", "排行榜"),
    ):
        return True

    if _is_industry_price_data_fast_news(text):
        return True

    if _contains_any(text, ("产值", "工业增加值", "制造业增加值")) and _contains_any(
        text,
        ("增长", "同比增长", "同比", "增速"),
    ):
        return True

    return _contains_any(text, ("出口", "销量", "产量")) and _contains_any(
        text,
        ("同比增长", "同比", "环比", "累计", "年增"),
    )


def _is_financial_result_fast_news(title: str) -> bool:
    return _contains_any(title, FAST_NEWS_FINANCIAL_RESULT_KEYWORDS)


def _is_industry_price_data_fast_news(text: str) -> bool:
    return _contains_any(text, ("价格涨幅", "价格涨幅达", "提价")) and _contains_any(
        text,
        ("景气度", "行业"),
    )


def _is_response_or_clarification_fast_news(title: str, text: str) -> bool:
    if not _contains_any(title, ("回应", "澄清", "否认", "辟谣", "说明")):
        return False

    if not _contains_any(text, ("合作协议", "战略合作", "订单", "合同", "通知", "意见", "印发")):
        return False

    return _contains_any(
        text,
        ("传闻", "回应记者", "框架合作协议", "框架协议", "不涉及", "不存在", "未披露"),
    )


def _is_company_setup_fast_news(text: str) -> bool:
    if not _contains_any(text, ("成立", "投资成立")):
        return False
    return _contains_any(text, ("公司", "有限公司", "科技公司", "新公司"))


def _is_equity_investment_fast_news(text: str) -> bool:
    if not _contains_any(text, ("入股", "新增股东", "工商变更")):
        return False
    return _contains_any(text, ("注册资本", "股东", "有限公司"))


def _is_broker_commentary_fast_news(title: str, text: str) -> bool:
    if "：" not in title:
        return False
    if not _contains_any(title, BROKER_COMMENTARY_ORGS):
        return False
    return _contains_any(
        text,
        ("平衡型配置", "资产配置", "大幅调仓", "投资总监办公室", "财富管理"),
    )


def _is_geopolitical_fast_news(text: str) -> bool:
    if not _contains_any(text, ("朝鲜", "韩国军方", "日本防卫省", "韩联社", "共同社")):
        return False
    return _contains_any(text, ("导弹", "发射", "防卫省", "军方"))


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def _extract_stock_code_from_url(url: str) -> str:
    if "stockCode=" not in url:
        return ""
    return url.split("stockCode=", maxsplit=1)[1].split("&", maxsplit=1)[0]
