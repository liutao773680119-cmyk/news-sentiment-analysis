from __future__ import annotations

from datetime import datetime, timedelta

from news_sentiment.history.matcher import match_historical_events
from news_sentiment.mapping.stock_mapper import map_themes_to_stocks
from news_sentiment.models import Event, EventAnalysis
from news_sentiment.settings import ProjectPaths


REPORT_WINDOW_DAYS = 2
LOW_SIGNAL_EXCHANGE_HARD_EVENT_SOURCES = {"cninfo", "hkex", "sse", "szse"}
HARD_EVENT_CATALYST_KEYWORDS = (
    "受理",
    "签署",
    "合作",
    "获批",
    "中标",
    "订单",
    "合同",
    "回购",
    "增持",
    "减持",
    "定增",
    "重组",
    "收购",
    "激励",
)
FAST_NEWS_CATALYST_KEYWORDS = (
    "战略合作",
    "合作协议",
    "签署协议",
    "签订合同",
    "获批上市",
    "获批",
    "上市申请",
    "中标",
    "订单",
    "收购",
    "重组",
    "回购",
    "增持",
    "减持",
    "股权激励",
)
FAST_NEWS_MARKET_MOVE_KEYWORDS = (
    "涨停",
    "跌停",
    "涨幅扩大",
    "跌幅扩大",
    "涨超",
    "跌超",
    "大涨",
    "大跌",
    "跳水",
)
EVENT_SUBTYPE_LABELS = {
    "policy_support": "产业政策",
    "policy_update": "政策动态",
    "control_change": "控制权变更",
    "reorganization_risk": "重整风险",
    "delisting_risk": "退市风险",
    "legal_dispute": "法律争议",
    "financing_acceptance": "融资受理",
    "equity_incentive": "股权激励",
    "order_contract": "订单合同",
    "cooperation_agreement": "合作协议",
    "acquisition_restructuring": "并购重组",
    "board_resolution": "董事会决议",
    "executive_change": "高管变动",
    "corporate_disclosure": "一般公告",
    "market_move": "市场异动",
    "regulatory_approval": "监管获批",
    "policy_signal": "政策信号",
    "tech_breakthrough": "技术突破",
    "industry_data": "行业数据",
    "business_guidance": "经营指引",
    "company_update": "公司动态",
    "general_fast_news": "一般快讯",
    "general": "一般事件",
}
LOW_PRIORITY_CNINFO_SUBTYPES = {
    "corporate_disclosure",
    "board_resolution",
    "equity_incentive",
}
LOW_SIGNAL_CNINFO_DISCLOSURE_KEYWORDS = (
    "实施进展",
    "进展公告",
    "通知债权人",
    "责任保险",
    "行政处罚事先告知书",
    "述职报告",
    "业绩说明会",
    "风险评估报告",
    "风险持续评估报告",
    "环境、社会与公司治理（ESG）报告",
    "鉴证报告",
    "资产评估报告",
    "增持公司股份结果公告",
    "增持股份结果",
    "增持公司股份计划",
    "增持计划实施完成",
    "减持股份预披露",
    "减持股份的预披露公告",
    "减持股份预披露公告",
    "股东计划减持公司股份的预披露公告",
    "减持股份计划公告",
    "减持计划的预披露公告",
    "减持计划完成",
    "减持计划实施完成",
    "减持计划期限届满暨实施情况",
    "减持股份计划期限届满暨实施情况",
    "减持期限届满未减持股份",
    "减持股份结果",
    "股份减持完成",
    "减持公司股份比例触及",
    "终止股份减持计划",
    "提前终止股份减持计划",
    "回购实施结果",
    "回购股份用途并注销",
    "回购股份的用途并注销",
    "一般风险提示暨公司股票复牌",
    "变更股份回购用途",
    "回购股份用途",
    "库存股减少公司注册资本",
    "注销回购股份并减少注册资本",
    "关联交易进展",
    "考核管理办法",
    "回购报告书",
    "信用评级报告",
    "股东质询建议函",
    "金融服务协议及相关风险控制措施执行情况的核查意见",
    "金融服务协议",
    "履职情况评估报告",
    "利润分配预案",
    "营业收入扣除事项的专项核查意见",
    "股票交易异常波动公告",
    "股票交易风险提示暨停牌核查",
    "使用暂时闲置自有资金进行现金管理",
    "国债逆回购",
    "结构性存款",
    "中短期低风险金融理财产品",
    "申请综合授信额度",
    "受让协议",
    "未弥补的亏损达实收股本总额三分之一",
    "募集资金存放、管理与实际使用情况的专项报告",
    "年度薪酬方案",
    "提质增效重回报",
    "回购股份价格上限",
    "互动易平台信息发布及回复内部审核制度",
    "风险管理制度",
    "行政处罚决定书",
    "年度报告摘要",
    "年度报告",
    "独立董事候选人声明与承诺",
    "独立董事提名人声明与承诺",
    "内部控制审计报告",
    "年度审计报告",
    "监管措施或处罚及整改情况",
    "上市投资风险特别公告",
    "风险提示公告",
    "不存在被证券监管部门和交易所采取处罚或监管措施",
    "附条件生效的股份认购协议",
    "股权委托管理协议",
    "相关规定的核查意见",
    "重整投资协议",
    "问询函回复",
    "专项说明",
    "诉讼事项的进展",
    "重大诉讼、仲裁情况进展",
    "累计诉讼",
    "失信被执行人",
    "轮候冻结",
)
LOW_SIGNAL_CNINFO_EQUITY_INCENTIVE_KEYWORDS = (
    "考核管理办法",
    "独立财务顾问报告",
    "法律意见书",
    "（草案）",
    "（草案）摘要",
    "草案摘要",
    "注销首期股票期权激励计划部分股票期权",
    "注销2024年股票期权激励计划部分股票期权",
    "解锁条件成就",
    "解除限售条件",
    "符合行权条件",
    "首次授予限制性股票",
    "向激励对象授予限制性股票",
    "授予登记完成",
    "归属结果暨股份上市",
    "解除限售期解锁暨限制性股票上市公告",
    "行权条件成就",
    "期权数量、行权价格并注销部分已获授但未行权的股票期权",
    "回购注销限制性股票减资暨通知债权人",
    "暨通知债权人",
    "回购注销部分限制性股票",
    "尚未解除限售的限制性股票",
    "尚未归属的限制性股票",
    "归属条件未成就",
    "激励对象名单",
    "股票期权注销事项的核查意见",
    "股票增值权激励计划第一个行权期的行权名单的核查意见",
    "作废处理部分限制性股票的法律意见",
    "作废部分已授予尚未归属的限制性股票相关事项的核查意见",
    "限制性股票相关事项的核查意见",
    "限制性股票激励计划相关事项的核查意见",
    "激励对象买卖公司股票情况的自查报告",
    "内幕信息知情人买卖公司股票情况的自查报告",
    "符合归属条件的公告",
    "归属条件成就",
)
LOW_SIGNAL_CNINFO_BOARD_RESOLUTION_KEYWORDS = (
    "履行监督职责情况的报告",
    "审计与风险管理委员会",
    "审计与风险委员会",
    "独立性情况的专项意见",
    "授权董事会审议股份回购事项",
    "股票价格波动情况的说明",
)
LOW_SIGNAL_CNINFO_RESTRUCTURING_KEYWORDS = (
    "实施情况之法律意见书",
    "重大资产重组实施情况之法律意见书",
    "重大资产重组业绩承诺期满标的资产减值测试情况",
    "减值测试报告",
    "重大资产重组业绩承诺实现情况说明专项审核报告",
    "持续督导意见",
    "第四条规定的说明",
    "进展公告",
    "一般风险提示性公告",
    "一般风险提示暨公司股票复牌",
    "并购重组审核委员会审核通过",
    "管理办法》第十一条、第四十三条及第四十四条规定的核查意见",
)
LOW_SIGNAL_EXCHANGE_ORDER_CONTRACT_PROGRESS_KEYWORDS = (
    "中标项目签订协议的进展公告",
    "新签合同情况公告",
)
LOW_SIGNAL_EXCHANGE_RESTRUCTURING_RESULT_KEYWORDS = (
    "拟",
    "完成",
    "获批",
    "复牌",
    "控制权变更",
    "要约",
)
LOW_SIGNAL_CONTROL_CHANGE_MATERIAL_KEYWORDS = (
    "业绩承诺实现情况",
    "专项说明",
)
LOW_SIGNAL_EXCHANGE_TEMPLATE_COOPERATION_STRONG_KEYWORDS = (
    "战略",
    "项目",
    "订单",
    "合同",
    "中标",
    "金额",
    "落地",
    "交付",
)
LOW_SIGNAL_CNINFO_RESTRUCTURING_MATERIAL_KEYWORDS = (
    "审核问询函回复",
    "报告书（修订稿）",
    "报告书(修订稿)",
)
LOW_SIGNAL_CNINFO_RESTRUCTURING_CONTEXT_KEYWORDS = (
    "发行股份购买资产",
    "关联交易",
    "重大资产重组",
    "并购重组",
)
LOW_SIGNAL_HKEX_DISCLOSURE_TITLE_KEYWORDS = (
    "An announcement has just been published by the Company on the HKEXnews website",
    "Current Listed Company Information",
    "Next Day Disclosure Return",
    "Monthly Return of Equity Issuer",
    "Proxy Form",
    "Reply Form",
    "Notification Letter",
    "Notice of Annual General Meeting",
    "Notice of Extraordinary General Meeting",
    "Annual General Meeting",
    "Extraordinary General Meeting",
    "Circular",
    "Date of Board Meeting",
    "Notice of Board Meeting",
    "Annual Report",
    "Environmental, Social and Governance Report",
    "ESG Report",
    "Sustainability Report",
    "List of Directors and their Roles and Functions",
)
LOW_SIGNAL_EXCHANGE_OPERATIONAL_DISCLOSURE_KEYWORDS = (
    "销售情况简报",
    "获得房地产项目",
    "股票回购贷款承诺函",
    "谅解备忘录",
)
LOW_SIGNAL_FOREIGN_INDEX_FAST_NEWS_KEYWORDS = (
    "欧洲主要股指",
    "美股三大指数",
    "美股跌幅扩大",
    "恒生科技指数",
    "恒生指数",
    "日韩股市",
    "KOSPI指数",
    "纳斯达克中国金龙指数",
    "纳指",
    "道指",
    "标普500指数",
    "欧洲斯托克50指数",
    "英国富时100指数",
    "法国CAC40指数",
    "德国DAX30指数",
    "意大利富时MIB指数",
)
LOW_SIGNAL_CLS_GENERAL_FAST_NEWS_MARKET_BRIEF_KEYWORDS = (
    "现货白银",
    "美股光通信股走势分化",
)
LOW_SIGNAL_DOMESTIC_FUTURES_MARKET_MOVE_KEYWORDS = (
    "国内期货市场夜盘收盘",
    "国内商品期货夜盘收盘",
    "国内期货夜盘收盘涨跌不一",
    "国内期市开盘多数下跌",
    "国内期货开盘涨跌不一",
    "国内期货收盘涨跌不一",
    "国内商品期货多数收跌",
    "国内商品期货多数收涨",
)
LOW_SIGNAL_STCN_MARKET_ROUNDUP_TITLE_KEYWORDS = (
    "开评：三大指数",
    "收评：三大指数",
    "午评：三大指数",
    "早盘：三大指数",
)
LOW_SIGNAL_STCN_MARKET_ROUNDUP_TITLE_PREFIXES = (
    "开评：",
    "收评：",
    "午评：",
    "早盘：",
)
LOW_SIGNAL_STCN_SINGLE_STOCK_MARKET_MOVE_TITLE_KEYWORDS = (
    "股价创下历史新高",
    "股价创历史新高",
)
A_SHARE_CORE_INDEX_KEYWORDS = (
    "沪指",
    "深证成指",
    "创业板指",
)
LOW_SIGNAL_HK_LISTING_APPLICATION_KEYWORDS = (
    "向港交所提交上市申请书",
    "再次向港交所提交上市申请书",
    "向港交所递交上市申请",
    "港交所提交上市申请书",
    "港交所上市申请书",
)
LOW_SIGNAL_SHAREHOLDER_REDUCTION_FAST_NEWS_KEYWORDS = (
    "拟合计减持",
    "减持不超",
    "拟减持",
)
LOW_SIGNAL_STCN_BROKER_COMMENTARY_ORGS = (
    "瑞银",
    "中信建投",
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
LOW_SIGNAL_STCN_BROKER_COMMENTARY_MACRO_KEYWORDS = (
    "非农",
    "联储",
    "通胀",
    "就业市场",
    "货币政策",
    "降息",
    "加息",
    "平衡型配置",
    "资产配置",
    "财富管理",
    "投资总监办公室",
    "市场情绪回升",
    "建议积极关注",
)
LOW_SIGNAL_STCN_FUND_MANAGER_COMMENTARY_TITLE_KEYWORDS = (
    "基金经理",
    "对冲组合风险",
    "配置逻辑出现新变化",
)
LOW_SIGNAL_STCN_ETF_ALLOCATION_COMMENTARY_TITLE_KEYWORDS = (
    "ETF资金流向分化",
    "公募策略趋于多元",
)
LOW_SIGNAL_STCN_OPERATIONAL_UPDATE_KEYWORDS = (
    "目前生产经营正常",
    "订单情况整体稳定",
    "经营正常",
)
LOW_SIGNAL_STCN_MACRO_LIQUIDITY_TITLE_KEYWORDS = (
    "逆回购操作",
)
LOW_SIGNAL_STCN_OVERSEAS_LIVELIHOOD_KEYWORDS = (
    "日本",
    "温泉",
    "被迫停业",
)
LOW_SIGNAL_STCN_OVERSEAS_AVIATION_FUEL_TITLE_KEYWORDS = (
    "国际航协",
    "航油价格翻倍",
)
LOW_SIGNAL_STCN_OVERSEAS_AVIATION_FUEL_BODY_KEYWORDS = (
    "航空业承压",
    "削减航班",
)
LOW_SIGNAL_STCN_PUBLIC_AFFAIRS_TITLE_KEYWORDS = (
    "鼓励非高峰使用公共交通",
    "延长签证宽限期",
    "跨区域人员流动量预计",
    "暴雨黄色预警信号",
    "取消部分化肥关税",
    "外立面遭防空系统拦截碎片击中",
    "调研先进制造业发展",
)
LOW_SIGNAL_MIIT_POLICY_MEETING_TITLE_KEYWORDS = (
    "座谈会",
    "行业会议",
    "全体会议",
    "工作会议",
    "推进会",
    "会见",
    "并座谈",
    "活动",
    "部署会",
    "报告会",
    "开班式",
    "新闻发布会",
    "领导小组会议",
    "总体组",
    "咨询组",
)
LOW_SIGNAL_MIIT_POLICY_MEETING_BODY_KEYWORDS = (
    "召开",
    "研究部署",
    "出席会议",
    "交流发言",
    "参加会议",
    "参加会见",
    "深化务实合作",
    "参加活动",
    "开展活动",
    "开班讲话",
    "参加学习",
    "动员部署会",
    "工作方案",
    "学习教育走深走实",
)
LOW_SIGNAL_MIIT_POLICY_ACTIVITY_TITLE_KEYWORDS = (
    "学习教育",
)
LOW_SIGNAL_MIIT_POLICY_PUBLICATION_TITLE_KEYWORDS = (
    "出版发行",
)
LOW_SIGNAL_MIIT_POLICY_PUBLICATION_BODY_KEYWORDS = (
    "出版发行",
    "组织编写",
    "报告",
)
LOW_SIGNAL_MIIT_POLICY_SUPERVISION_TITLE_KEYWORDS = (
    "统计督察意见",
    "督察意见反馈",
)
LOW_SIGNAL_MIIT_POLICY_SUPERVISION_BODY_KEYWORDS = (
    "督察发现",
    "反馈问题整改",
    "统计数据质量",
    "从严从实推进督察反馈问题整改",
)


def _parse_event_timestamp(event: Event) -> datetime | None:
    timestamp = event.published_at or event.first_seen_at or event.last_seen_at
    if not timestamp:
        return None
    return datetime.fromisoformat(timestamp)


def _is_market_relevant(event: Event, analysis: EventAnalysis) -> bool:
    text = f"{event.canonical_title} {event.summary}"
    if _is_low_signal_foreign_index_fast_news(event, text):
        return False
    if _is_low_signal_domestic_futures_market_move(event.canonical_title, event):
        return False
    if _is_low_signal_stcn_market_roundup(event.canonical_title, event, analysis):
        return False
    if _is_low_signal_stcn_single_stock_market_move(event.canonical_title, event, analysis):
        return False
    if _is_low_signal_hk_listing_application_fast_news(event.canonical_title, event):
        return False
    if _is_low_signal_stcn_broker_macro_commentary(event, text):
        return False
    if _is_low_signal_stcn_fund_manager_allocation_commentary(event):
        return False
    if _is_low_signal_stcn_operational_update(event, text):
        return False
    if _is_low_signal_stcn_macro_liquidity_update(event):
        return False
    if _is_low_signal_stcn_overseas_livelihood_story(event, text):
        return False
    if _is_low_signal_stcn_overseas_aviation_fuel_story(event, text):
        return False
    if _is_low_signal_stcn_public_affairs_story(event):
        return False
    if _is_low_signal_miit_policy_meeting(event, analysis, text):
        return False
    if _is_low_signal_miit_policy_publication(event, analysis, text):
        return False
    if _is_low_signal_miit_policy_supervision_feedback(event, analysis, text):
        return False
    if _is_low_signal_cninfo_hard_event(event, text):
        return False
    if _is_low_signal_exchange_template_cooperation_agreement(event, analysis):
        return False
    if _is_low_signal_cls_fund_suspend_resume_notice(event):
        return False
    if _is_low_signal_cls_central_bank_gold_reserve_brief(event, text):
        return False
    if _is_low_signal_cls_news_broadcast_roundup(event):
        return False
    if _is_low_signal_cls_telegraph_interpretation_column(event):
        return False
    if _is_low_signal_cls_gold_memo_column(event):
        return False
    if _is_low_signal_cls_wind_research_column(event):
        return False
    if _is_low_signal_cls_wind_research_insight_column(event):
        return False
    if _is_low_signal_cls_after_hours_earnings_digest(event):
        return False
    if _is_low_signal_cls_general_fast_news_market_brief(event):
        return False
    if analysis.themes:
        return True
    if _is_low_signal_shareholder_reduction_fast_news(event.canonical_title, event):
        return False
    if event.event_type == "fast_news":
        return _has_fast_news_title_catalyst(event.canonical_title) or any(
            keyword in text for keyword in FAST_NEWS_MARKET_MOVE_KEYWORDS
        )
    if analysis.direction != "neutral":
        return True
    if event.event_type == "hard_event":
        return any(keyword in text for keyword in HARD_EVENT_CATALYST_KEYWORDS)
    return False


def _is_low_signal_cninfo_hard_event(event: Event, text: str) -> bool:
    if not (
        event.source in LOW_SIGNAL_EXCHANGE_HARD_EVENT_SOURCES
        and event.event_type == "hard_event"
    ):
        return False

    if event.event_subtype == "corporate_disclosure":
        if event.source == "hkex":
            return _is_low_signal_hkex_disclosure_title(event.canonical_title)
        return (
            any(keyword in text for keyword in LOW_SIGNAL_CNINFO_DISCLOSURE_KEYWORDS)
            or _is_low_signal_cninfo_cancel_shareholder_meeting(event.canonical_title)
            or _is_low_signal_exchange_shareholder_meeting_notice(event.canonical_title)
            or _is_low_signal_exchange_shareholder_meeting_legal_opinion(event.canonical_title)
            or _is_low_signal_exchange_halt_check_risk_notice(event.canonical_title)
            or _is_low_signal_exchange_operational_disclosure(event.canonical_title, event)
            or _is_low_signal_cninfo_restructuring_material(event.canonical_title)
            or _is_low_signal_exchange_inquiry_transfer_verification_report(event.canonical_title)
        )

    if event.event_subtype == "equity_incentive":
        return any(keyword in text for keyword in LOW_SIGNAL_CNINFO_EQUITY_INCENTIVE_KEYWORDS)

    if event.event_subtype == "board_resolution":
        return any(keyword in text for keyword in LOW_SIGNAL_CNINFO_BOARD_RESOLUTION_KEYWORDS)

    if event.event_subtype == "acquisition_restructuring":
        return any(keyword in text for keyword in LOW_SIGNAL_CNINFO_RESTRUCTURING_KEYWORDS) or (
            _is_low_signal_exchange_share_purchase_agreement_material(event.canonical_title, event)
        )

    if event.event_subtype == "order_contract":
        return event.source in {"sse", "szse"} and any(
            keyword in event.canonical_title
            for keyword in LOW_SIGNAL_EXCHANGE_ORDER_CONTRACT_PROGRESS_KEYWORDS
        )

    if event.event_subtype == "control_change":
        return event.source in {"sse", "szse"} and all(
            keyword in event.canonical_title for keyword in LOW_SIGNAL_CONTROL_CHANGE_MATERIAL_KEYWORDS
        )

    if event.event_subtype == "delisting_risk":
        return _is_low_signal_repeated_delisting_risk_notice(event.canonical_title)

    return False


def _is_low_signal_cninfo_restructuring_material(title: str) -> bool:
    return (
        any(keyword in title for keyword in LOW_SIGNAL_CNINFO_RESTRUCTURING_MATERIAL_KEYWORDS)
        and any(keyword in title for keyword in LOW_SIGNAL_CNINFO_RESTRUCTURING_CONTEXT_KEYWORDS)
    )


def _is_low_signal_cninfo_cancel_shareholder_meeting(title: str) -> bool:
    return "取消" in title and any(keyword in title for keyword in ("临时股东会", "股东大会"))


def _is_low_signal_exchange_shareholder_meeting_notice(title: str) -> bool:
    return "关于召开" in title and any(keyword in title for keyword in ("股东会", "股东大会"))


def _is_low_signal_exchange_shareholder_meeting_legal_opinion(title: str) -> bool:
    return "法律意见书" in title and any(keyword in title for keyword in ("股东会", "股东大会"))


def _is_low_signal_exchange_halt_check_risk_notice(title: str) -> bool:
    return "停牌核查" in title and any(keyword in title for keyword in ("股票交易风险", "风险提示"))


def _is_low_signal_repeated_delisting_risk_notice(title: str) -> bool:
    return (
        "第" in title
        and any(keyword in title for keyword in ("风险提示公告", "提示性公告"))
        and any(
            keyword in title
            for keyword in ("股票交易风险", "可能被终止上市", "可能被实施退市风险警示", "退市风险警示")
        )
    )


def _is_low_signal_hkex_disclosure_title(title: str) -> bool:
    return any(keyword in title for keyword in LOW_SIGNAL_HKEX_DISCLOSURE_TITLE_KEYWORDS)


def _is_low_signal_exchange_operational_disclosure(title: str, event: Event) -> bool:
    if event.source not in {"sse", "szse"}:
        return False

    return any(keyword in title for keyword in LOW_SIGNAL_EXCHANGE_OPERATIONAL_DISCLOSURE_KEYWORDS)


def _is_low_signal_exchange_share_purchase_agreement_material(title: str, event: Event) -> bool:
    if event.source not in {"sse", "szse"}:
        return False

    return (
        "收购股权" in title
        and "股份购买协议" in title
        and not any(keyword in title for keyword in LOW_SIGNAL_EXCHANGE_RESTRUCTURING_RESULT_KEYWORDS)
    )


def _is_low_signal_exchange_inquiry_transfer_verification_report(title: str) -> bool:
    return "询价转让股份" in title and "核查报告" in title


def _is_low_signal_exchange_template_cooperation_agreement(event: Event, analysis: EventAnalysis) -> bool:
    if not (
        event.source in {"sse", "szse"}
        and event.event_type == "hard_event"
        and event.event_subtype == "cooperation_agreement"
        and not analysis.themes
    ):
        return False

    title = event.canonical_title
    if not any(keyword in title for keyword in ("签订", "签署")):
        return False

    if "框架协议" in title:
        return True

    return "合作协议书" in title and not any(
        keyword in title for keyword in LOW_SIGNAL_EXCHANGE_TEMPLATE_COOPERATION_STRONG_KEYWORDS
    )


def _is_low_signal_foreign_index_fast_news(event: Event, text: str) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
    ):
        return False

    return any(keyword in text for keyword in LOW_SIGNAL_FOREIGN_INDEX_FAST_NEWS_KEYWORDS)


def _is_low_signal_domestic_futures_market_move(title: str, event: Event) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "market_move"
    ):
        return False

    return any(keyword in title for keyword in LOW_SIGNAL_DOMESTIC_FUTURES_MARKET_MOVE_KEYWORDS)


def _is_low_signal_hk_listing_application_fast_news(title: str, event: Event) -> bool:
    if not (
        event.source in {"stcn", "cls"}
        and event.event_type == "fast_news"
    ):
        return False

    return any(keyword in title for keyword in LOW_SIGNAL_HK_LISTING_APPLICATION_KEYWORDS)


def _is_low_signal_stcn_market_roundup(title: str, event: Event, analysis: EventAnalysis) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "market_move"
    ):
        return False

    if any(keyword in title for keyword in LOW_SIGNAL_STCN_MARKET_ROUNDUP_TITLE_KEYWORDS):
        return True

    return (
        any(title.startswith(prefix) for prefix in LOW_SIGNAL_STCN_MARKET_ROUNDUP_TITLE_PREFIXES)
        and any(keyword in title for keyword in A_SHARE_CORE_INDEX_KEYWORDS)
    )


def _is_low_signal_stcn_single_stock_market_move(title: str, event: Event, analysis: EventAnalysis) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "market_move"
        and not analysis.themes
    ):
        return False

    return any(keyword in title for keyword in LOW_SIGNAL_STCN_SINGLE_STOCK_MARKET_MOVE_TITLE_KEYWORDS)


def _is_low_signal_shareholder_reduction_fast_news(title: str, event: Event) -> bool:
    if not (
        event.source in {"stcn", "cls"}
        and event.event_type == "fast_news"
    ):
        return False

    return any(keyword in title for keyword in LOW_SIGNAL_SHAREHOLDER_REDUCTION_FAST_NEWS_KEYWORDS)


def _is_low_signal_cls_fund_suspend_resume_notice(event: Event) -> bool:
    if not (
        event.source == "cls"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
    ):
        return False

    title = event.canonical_title
    return "LOF" in title and "停牌" in title and "复牌" in title


def _is_low_signal_cls_central_bank_gold_reserve_brief(event: Event, text: str) -> bool:
    if not (
        event.source == "cls"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
    ):
        return False

    return "央行数据" in text and "黄金储备" in text


def _is_low_signal_cls_news_broadcast_roundup(event: Event) -> bool:
    if not (
        event.source == "cls"
        and event.event_type == "fast_news"
        and event.event_subtype in {"general_fast_news", "company_update"}
    ):
        return False

    title = event.canonical_title
    return "《新闻联播》要闻" in title


def _is_low_signal_cls_telegraph_interpretation_column(event: Event) -> bool:
    if not (
        event.source == "cls"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
    ):
        return False

    return "【电报解读】" in event.canonical_title


def _is_low_signal_cls_gold_memo_column(event: Event) -> bool:
    if not (
        event.source == "cls"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
    ):
        return False

    return "【金牌纪要库】" in event.canonical_title


def _is_low_signal_cls_wind_research_column(event: Event) -> bool:
    if not (
        event.source == "cls"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
    ):
        return False

    return "【风口研报·公司】" in event.canonical_title


def _is_low_signal_cls_wind_research_insight_column(event: Event) -> bool:
    if not (
        event.source == "cls"
        and event.event_type == "fast_news"
        and event.event_subtype == "company_update"
    ):
        return False

    return "【风口研报·洞察】" in event.canonical_title


def _is_low_signal_cls_after_hours_earnings_digest(event: Event) -> bool:
    if not (
        event.source == "cls"
        and event.event_type == "fast_news"
        and event.event_subtype == "business_guidance"
    ):
        return False

    return "盘后A股上市公司重点业绩公告精选" in event.canonical_title


def _is_low_signal_cls_general_fast_news_market_brief(event: Event) -> bool:
    if not (
        event.source == "cls"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
    ):
        return False

    return any(
        keyword in event.canonical_title
        for keyword in LOW_SIGNAL_CLS_GENERAL_FAST_NEWS_MARKET_BRIEF_KEYWORDS
    )


def _is_low_signal_stcn_broker_macro_commentary(event: Event, text: str) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
    ):
        return False

    title = event.canonical_title
    return any(org in title for org in LOW_SIGNAL_STCN_BROKER_COMMENTARY_ORGS) and any(
        keyword in text for keyword in LOW_SIGNAL_STCN_BROKER_COMMENTARY_MACRO_KEYWORDS
    )


def _is_low_signal_stcn_fund_manager_allocation_commentary(event: Event) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
    ):
        return False

    return all(
        keyword in event.canonical_title
        for keyword in LOW_SIGNAL_STCN_FUND_MANAGER_COMMENTARY_TITLE_KEYWORDS
    ) or all(
        keyword in event.canonical_title
        for keyword in LOW_SIGNAL_STCN_ETF_ALLOCATION_COMMENTARY_TITLE_KEYWORDS
    )


def _is_low_signal_stcn_operational_update(event: Event, text: str) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
    ):
        return False

    return any(keyword in text for keyword in LOW_SIGNAL_STCN_OPERATIONAL_UPDATE_KEYWORDS)


def _is_low_signal_stcn_macro_liquidity_update(event: Event) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
    ):
        return False

    return any(keyword in event.canonical_title for keyword in LOW_SIGNAL_STCN_MACRO_LIQUIDITY_TITLE_KEYWORDS)


def _is_low_signal_stcn_overseas_livelihood_story(event: Event, text: str) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "general_fast_news"
    ):
        return False

    return all(keyword in text for keyword in LOW_SIGNAL_STCN_OVERSEAS_LIVELIHOOD_KEYWORDS)


def _is_low_signal_stcn_overseas_aviation_fuel_story(event: Event, text: str) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "company_update"
    ):
        return False

    title = event.canonical_title
    return (
        any(keyword in title for keyword in LOW_SIGNAL_STCN_OVERSEAS_AVIATION_FUEL_TITLE_KEYWORDS)
        and any(keyword in text for keyword in LOW_SIGNAL_STCN_OVERSEAS_AVIATION_FUEL_BODY_KEYWORDS)
    )
def _is_low_signal_stcn_public_affairs_story(event: Event) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype in {"general_fast_news", "company_update"}
    ):
        return False

    return any(keyword in event.canonical_title for keyword in LOW_SIGNAL_STCN_PUBLIC_AFFAIRS_TITLE_KEYWORDS)


def _is_low_signal_miit_policy_meeting(event: Event, analysis: EventAnalysis, text: str) -> bool:
    if not (
        event.source == "miit"
        and event.event_type == "policy"
        and not analysis.themes
    ):
        return False

    title = event.canonical_title
    if "新闻发布会" in title:
        return True

    return (
        (
            any(keyword in title for keyword in LOW_SIGNAL_MIIT_POLICY_MEETING_TITLE_KEYWORDS)
            or any(keyword in title for keyword in LOW_SIGNAL_MIIT_POLICY_ACTIVITY_TITLE_KEYWORDS)
        )
        and any(keyword in text for keyword in LOW_SIGNAL_MIIT_POLICY_MEETING_BODY_KEYWORDS)
    )


def _is_low_signal_miit_policy_publication(event: Event, analysis: EventAnalysis, text: str) -> bool:
    if not (
        event.source == "miit"
        and event.event_type == "policy"
        and not analysis.themes
    ):
        return False

    title = event.canonical_title
    return any(keyword in title for keyword in LOW_SIGNAL_MIIT_POLICY_PUBLICATION_TITLE_KEYWORDS) and any(
        keyword in text for keyword in LOW_SIGNAL_MIIT_POLICY_PUBLICATION_BODY_KEYWORDS
    )


def _is_low_signal_miit_policy_supervision_feedback(
    event: Event, analysis: EventAnalysis, text: str
) -> bool:
    if not (
        event.source == "miit"
        and event.event_type == "policy"
        and not analysis.themes
    ):
        return False

    title = event.canonical_title
    return any(keyword in title for keyword in LOW_SIGNAL_MIIT_POLICY_SUPERVISION_TITLE_KEYWORDS) and any(
        keyword in text for keyword in LOW_SIGNAL_MIIT_POLICY_SUPERVISION_BODY_KEYWORDS
    )


def _has_fast_news_title_catalyst(title: str) -> bool:
    return any(keyword in title for keyword in FAST_NEWS_CATALYST_KEYWORDS)


def _report_priority(event: Event, analysis: EventAnalysis) -> int:
    if (
        event.source == "cls"
        and event.event_type == "fast_news"
        and event.event_subtype in {"industry_data", "general_fast_news"}
    ):
        return 0
    if analysis.themes:
        return 2
    if _is_ashare_core_index_market_move(event, analysis):
        return 0
    if (
        event.source == "cninfo"
        and event.event_type == "hard_event"
        and event.event_subtype in LOW_PRIORITY_CNINFO_SUBTYPES
    ):
        return 0
    return 1


def _report_status(event: Event, analysis: EventAnalysis) -> str:
    if _is_ashare_core_index_market_move(event, analysis):
        return "温度"
    return "关注"


def _is_ashare_core_index_market_move(event: Event, analysis: EventAnalysis) -> bool:
    if not (
        event.source == "stcn"
        and event.event_type == "fast_news"
        and event.event_subtype == "market_move"
        and not analysis.themes
    ):
        return False

    title = event.canonical_title
    return any(keyword in title for keyword in A_SHARE_CORE_INDEX_KEYWORDS)


def write_text_report(
    paths: ProjectPaths,
    events: list[Event],
    analyses: list[EventAnalysis],
) -> None:
    event_map = {event.event_id: event for event in events}
    lines: list[str] = []
    event_times = {
        event.event_id: parsed
        for event in events
        for parsed in [_parse_event_timestamp(event)]
        if parsed is not None
    }
    latest_batch_time = max(event_times.values(), default=None)
    cutoff_time = (
        latest_batch_time - timedelta(days=REPORT_WINDOW_DAYS)
        if latest_batch_time is not None
        else None
    )
    ranked_analyses = sorted(
        [
            analysis
            for analysis in analyses
            if analysis.triggered
            and analysis.event_id in event_map
            and _is_market_relevant(event_map[analysis.event_id], analysis)
            and (
                cutoff_time is None
                or analysis.event_id not in event_times
                or event_times[analysis.event_id] >= cutoff_time
            )
        ],
        key=lambda analysis: (
            _report_priority(event_map[analysis.event_id], analysis),
            analysis.impact_score,
        ),
        reverse=True,
    )
    for analysis in ranked_analyses:
        event = event_map[analysis.event_id]
        theme_matches = map_themes_to_stocks(analysis.themes)
        historical = match_historical_events(analysis.themes)
        status = _report_status(event, analysis)
        lines.extend(
            [
                f"[{status}] {event.canonical_title}",
                f"事件类型: {EVENT_SUBTYPE_LABELS.get(event.event_subtype, event.event_subtype)}",
                f"来源: {event.source or '未知'}",
                f"发布时间: {event.published_at or event.first_seen_at or '未知'}",
                f"URL: {event.url or '无'}",
                f"方向: {analysis.direction}",
                f"强度: {analysis.impact_score:.1f}",
                f"题材: {', '.join(analysis.themes) if analysis.themes else '无'}",
                f"个股: {', '.join(match.stock_code for match in theme_matches[:3]) if theme_matches else '无'}",
                f"历史: {historical[0]['historical_event_id'] if historical else '无'}",
                "",
            ]
        )

    paths.latest_report_path.parent.mkdir(parents=True, exist_ok=True)
    content = "\n".join(lines).strip()
    paths.latest_report_path.write_text((content + "\n") if content else "", encoding="utf-8")
