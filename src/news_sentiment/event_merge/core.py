from __future__ import annotations

from news_sentiment.config_loader import load_source_priority_map
from news_sentiment.models import Event, NormalizedNews


def merge_news_items(items: list[NormalizedNews]) -> list[Event]:
    if not items:
        return []

    source_priorities = load_source_priority_map()
    groups: list[list[NormalizedNews]] = []
    for item in items:
        target_group = None
        for group in groups:
            if _is_similar(item.title, group[0].title):
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


def _classify_event_subtype(source_type: str, title: str, content: str) -> str:
    text = f"{title} {content}"

    if source_type == "policy":
        if _contains_any(text, ("实施方案", "行动方案", "行动计划", "发展规划", "支持", "通知", "意见")):
            return "policy_support"
        return "policy_update"

    if source_type == "hard_event":
        if _contains_any(text, ("控制权", "股份转让协议", "实控人变更")):
            return "control_change"
        if _contains_any(text, ("受理", "向特定对象发行", "定增", "发行股票申请")):
            return "financing_acceptance"
        if _contains_any(text, ("激励计划", "限制性股票", "归属")):
            return "equity_incentive"
        if _contains_any(text, ("中标", "订单", "合同")):
            return "order_contract"
        if _contains_any(text, ("合作协议", "战略合作", "签署协议", "签订协议", "签署合作")):
            return "cooperation_agreement"
        if _contains_any(text, ("收购", "重组")):
            return "acquisition_restructuring"
        if _contains_any(text, ("董事会", "监事会", "股东大会", "会议决议")):
            return "board_resolution"
        if _contains_any(text, ("聘任", "辞任", "首席执行官", "总经理", "董事长")):
            return "executive_change"
        return "corporate_disclosure"

    if source_type == "fast_news":
        if _contains_any(text, ("涨停", "跌停", "涨幅扩大", "跌幅扩大", "涨超", "跌超", "大涨", "大跌", "跳水")):
            return "market_move"
        if _contains_any(text, ("行动方案", "行动计划", "实施方案", "发展规划", "通知", "意见", "印发")):
            return "policy_signal"
        if _contains_any(text, ("科学家", "研究人员", "研究团队", "科研")) and _contains_any(
            text,
            ("实现", "突破", "测试", "开发出", "新途径"),
        ):
            return "tech_breakthrough"
        if _contains_any(text, ("周活跃用户", "月活跃用户", "WAU", "MAU", "数据显示")):
            return "industry_data"
        if _contains_any(text, ("电话会议", "销售目标", "业绩指引", "收入", "利润", "盈利")):
            return "business_guidance"
        if _contains_any(title, ("获批上市", "获批", "上市申请", "药监局批准")):
            return "regulatory_approval"
        if _contains_any(text, ("中标", "订单", "合同")):
            return "order_contract"
        if _contains_any(text, ("战略合作", "合作协议", "签署协议", "签订协议")):
            return "cooperation_agreement"
        if "：" in title or _contains_any(text, ("发布", "上线", "推出")):
            return "company_update"
        return "general_fast_news"

    return "general"


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)
