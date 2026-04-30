from news_sentiment.analysis.scoring import score_event
from news_sentiment.collectors.eia_wpsr import parse_eia_wpsr_release
from news_sentiment.config_loader import load_scoring_config
from news_sentiment.event_merge.core import merge_news_items
from news_sentiment.models import Event, NormalizedNews


def test_score_event_flags_policy_event_as_triggered() -> None:
    event = Event(
        event_id="event-001",
        first_seen_at="2026-04-01T09:30:00+08:00",
        last_seen_at="2026-04-01T09:32:00+08:00",
        canonical_title="工信部发布算力政策",
        summary="工信部发布文件支持算力基础设施建设。",
        source="miit",
        published_at="2026-04-01T09:30:00+08:00",
        url="https://example.com/policy",
        member_news_ids=["n1"],
        event_type="policy",
        primary_entities=["工信部"],
        source_authority_score=0.95,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.triggered is True
    assert analysis.direction == "bullish"


def test_score_event_detects_rare_earth_magnet_theme_for_market_move() -> None:
    event = Event(
        event_id="event-001r",
        first_seen_at="2026-04-09T13:11:38+08:00",
        last_seen_at="2026-04-09T13:11:38+08:00",
        canonical_title="稀土永磁概念走高 英洛华等涨停",
        summary="人民财讯4月9日电，稀土永磁概念午后走高，英洛华涨停，华宏科技、天通股份此前涨停。",
        source="stcn",
        published_at="2026-04-09T13:11:38+08:00",
        url="https://example.com/rare-earth-magnet",
        member_news_ids=["n1r"],
        event_type="fast_news",
        event_subtype="market_move",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == ["稀土永磁"]
    assert analysis.triggered is True


def test_score_event_keeps_eia_wpsr_as_neutral_oil_signal() -> None:
    page_html = """
    <html>
      <body>
        <span>Data for week ending Apr. 10, 2026</span>
        <span class="responsive-container"><span class="label">Release Date:</span> <span class="date">Apr. 15, 2026</span></span>
      </body>
    </html>
    """
    table1_csv = '''"STUB_1","4/10/26","4/3/26","Difference","Percent Change"
"Commercial (Excluding SPR)","463.804","464.717","-0.913","-0.200"
"Total Motor Gasoline","232.944","239.272","-6.328","-2.600"
"Distillate Fuel Oil","111.559","114.681","-3.123","-2.700"
'''

    row = parse_eia_wpsr_release(page_html, table1_csv)[0]
    event = merge_news_items(
        [
            NormalizedNews(
                news_id=row.news_id,
                source=row.source,
                source_type=row.source_type,
                published_at=row.published_at,
                captured_at=row.captured_at,
                title=row.title,
                content=row.content,
                url=row.url,
            )
        ]
    )[0]

    analysis = score_event(event, scoring_config=load_scoring_config())

    assert event.event_subtype == "industry_data"
    assert analysis.direction == "neutral"
    assert analysis.themes == ["油气"]


def test_score_event_detects_compute_infra_theme_for_optical_communication_market_move() -> None:
    event = Event(
        event_id="event-001s",
        first_seen_at="2026-04-09T14:09:26+08:00",
        last_seen_at="2026-04-09T14:09:26+08:00",
        canonical_title="光通信概念反复活跃 特发信息等涨停",
        summary="人民财讯4月9日电，光通信概念反复活跃，特发信息、太辰光、华脉科技涨停，新易盛、天孚通信等跟涨。",
        source="stcn",
        published_at="2026-04-09T14:09:26+08:00",
        url="https://example.com/optical-communication",
        member_news_ids=["n1s"],
        event_type="fast_news",
        event_subtype="market_move",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == ["算力"]
    assert analysis.triggered is True


def test_score_event_does_not_treat_expert_interview_example_as_company_theme() -> None:
    event = Event(
        event_id="event-001t",
        first_seen_at="2026-04-09T14:12:07+08:00",
        last_seen_at="2026-04-09T14:12:07+08:00",
        canonical_title="北京大学光华管理学院教授刘俏：服务业的效率提升是“慢变量”，但蕴藏的潜力巨大",
        summary="人民财讯4月9日电，证券时报“人民财讯·大观”栏目专访北京大学光华管理学院教授刘俏。刘俏表示，哈尔滨、云南等地区的文旅经济发展，看似短期对全要素生产率的贡献不明显，但从长期来看有助于服务业专业化、规模化发展。",
        source="stcn",
        published_at="2026-04-09T14:12:07+08:00",
        url="https://example.com/expert-interview",
        member_news_ids=["n1t"],
        event_type="fast_news",
        event_subtype="company_update",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == []


def test_score_event_does_not_treat_data_center_power_supply_field_as_compute_infra_theme() -> None:
    event = Event(
        event_id="event-001u",
        first_seen_at="2026-04-09T18:58:21+08:00",
        last_seen_at="2026-04-09T18:58:21+08:00",
        canonical_title="密封科技：部分大缸径产品被应用于数据中心的电力供应领域",
        summary="人民财讯4月9日电，密封科技表示，公司目前部分大缸径产品被应用于数据中心的电力供应领域，但相关收入占比较小。",
        source="stcn",
        published_at="2026-04-09T18:58:21+08:00",
        url="https://example.com/power-supply-field",
        member_news_ids=["n1u"],
        event_type="fast_news",
        event_subtype="company_update",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == []


def test_score_event_detects_energy_saving_equipment_theme_for_policy_support() -> None:
    event = Event(
        event_id="event-001a",
        first_seen_at="2026-03-20T00:00:00+08:00",
        last_seen_at="2026-03-20T00:00:00+08:00",
        canonical_title="工业和信息化部举行《节能装备高质量发展实施方案（2026—2028年）》新闻发布会",
        summary="工业和信息化部举行《节能装备高质量发展实施方案（2026—2028年）》新闻发布会。",
        source="miit",
        published_at="2026-03-20T00:00:00+08:00",
        url="https://example.com/miit-energy-saving-equipment",
        member_news_ids=["n1a"],
        event_type="policy",
        event_subtype="policy_support",
        primary_entities=["工业和信息化部"],
        source_authority_score=0.9,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert "节能装备" in analysis.themes
    assert analysis.triggered is True


def test_score_event_detects_xinchuang_theme_for_miit_policy_update() -> None:
    event = Event(
        event_id="event-001b",
        first_seen_at="2026-03-20T00:00:00+08:00",
        last_seen_at="2026-03-20T00:00:00+08:00",
        canonical_title="李乐成调研信息技术创新应用和未来产业发展研究工作",
        summary="李乐成调研信息技术创新应用和未来产业发展研究工作。",
        source="miit",
        published_at="2026-03-20T00:00:00+08:00",
        url="https://example.com/miit-xinchuang",
        member_news_ids=["n1b"],
        event_type="policy",
        event_subtype="policy_update",
        primary_entities=["工业和信息化部"],
        source_authority_score=0.9,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert "信创" in analysis.themes
    assert analysis.triggered is True


def test_score_event_detects_data_security_theme_for_app_sdk_notice() -> None:
    event = Event(
        event_id="event-001c",
        first_seen_at="2026-03-10T00:00:00+08:00",
        last_seen_at="2026-03-10T00:00:00+08:00",
        canonical_title="关于侵害用户权益行为的APP（SDK）通报（2026年第2批，总第55批）",
        summary="关于侵害用户权益行为的APP（SDK）通报（2026年第2批，总第55批）。",
        source="miit",
        published_at="2026-03-10T00:00:00+08:00",
        url="https://example.com/miit-app-sdk-notice",
        member_news_ids=["n1c"],
        event_type="policy",
        event_subtype="policy_update",
        primary_entities=["工业和信息化部"],
        source_authority_score=0.9,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert "数据安全" in analysis.themes
    assert analysis.triggered is True


def test_score_event_detects_new_material_theme_for_miit_roundtable_summary() -> None:
    event = Event(
        event_id="event-001d",
        first_seen_at="2026-03-19T00:00:00+08:00",
        last_seen_at="2026-03-19T00:00:00+08:00",
        canonical_title="工业和信息化部召开新材料领域中小企业圆桌会",
        summary="工业和信息化部将以先进基础材料、关键战略材料、前沿新材料、人工智能+材料为主攻方向，全链条推动新材料创新发展。",
        source="miit",
        published_at="2026-03-19T00:00:00+08:00",
        url="https://example.com/miit-new-material",
        member_news_ids=["n1d"],
        event_type="policy",
        event_subtype="policy_support",
        primary_entities=["工业和信息化部"],
        source_authority_score=0.9,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert "新材料" in analysis.themes
    assert analysis.triggered is True


def test_score_event_prefers_policy_title_theme_over_summary_spillover() -> None:
    event = Event(
        event_id="event-001e",
        first_seen_at="2026-03-20T00:00:00+08:00",
        last_seen_at="2026-03-20T00:00:00+08:00",
        canonical_title="工业和信息化部举行《节能装备高质量发展实施方案（2026—2028年）》新闻发布会",
        summary="会议提出统筹推进算力基础设施和新型电力系统建设。",
        source="miit",
        published_at="2026-03-20T00:00:00+08:00",
        url="https://example.com/miit-policy-spillover",
        member_news_ids=["n1e"],
        event_type="policy",
        event_subtype="policy_support",
        primary_entities=["工业和信息化部"],
        source_authority_score=0.9,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == ["节能装备"]


def test_score_event_does_not_treat_policy_update_summary_catalog_as_themes() -> None:
    event = Event(
        event_id="event-001f",
        first_seen_at="2026-03-05T00:00:00+08:00",
        last_seen_at="2026-03-05T00:00:00+08:00",
        canonical_title="实录丨李乐成在“部长通道”谈现代化产业体系、人工智能产业",
        summary="新能源汽车产销量创新高，人形机器人组团炫技，脑机接口和6G等前沿领域发展迅速。",
        source="miit",
        published_at="2026-03-05T00:00:00+08:00",
        url="https://example.com/miit-policy-catalog",
        member_news_ids=["n1f"],
        event_type="policy",
        event_subtype="policy_support",
        primary_entities=["工业和信息化部"],
        source_authority_score=0.9,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == []


def test_score_event_does_not_treat_golden_period_phrase_as_gold_theme_for_policy() -> None:
    event = Event(
        event_id="event-001g",
        first_seen_at="2026-03-17T00:00:00+08:00",
        last_seen_at="2026-03-17T00:00:00+08:00",
        canonical_title="柯吉欣会见香港特别行政区政府创新科技及工业局局长孙东",
        summary="今年是香港对接国家战略的黄金期，将主动对接工业和信息化领域规划。",
        source="miit",
        published_at="2026-03-17T00:00:00+08:00",
        url="https://example.com/miit-golden-period",
        member_news_ids=["n1g"],
        event_type="policy",
        event_subtype="policy_update",
        primary_entities=["工业和信息化部"],
        source_authority_score=0.9,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == []


def test_score_event_does_not_treat_breeding_chip_breakthrough_as_semiconductor() -> None:
    event = Event(
        event_id="event-001h",
        first_seen_at="2026-04-03T13:56:01+08:00",
        last_seen_at="2026-04-03T13:56:01+08:00",
        canonical_title="我国白羽肉鸡自主育种跑出加速度 中国种源竞争力持续增强",
        summary="AI智能系统同步对B超、X光检测影像进行分析，应用京芯一号育种芯片，让育种周期缩短2到3个世代。",
        source="stcn",
        published_at="2026-04-03T13:56:01+08:00",
        url="https://example.com/breeding-chip",
        member_news_ids=["n1h"],
        event_type="fast_news",
        event_subtype="tech_breakthrough",
        primary_entities=[],
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == []


def test_score_event_detects_ai_application_theme_for_qwen_model_usage_rank() -> None:
    event = Event(
        event_id="event-001i",
        first_seen_at="2026-04-04T10:44:37+08:00",
        last_seen_at="2026-04-04T10:44:37+08:00",
        canonical_title="千问3.6Plus大模型登顶全球模型调用排行榜首，日调用量破万亿",
        summary="发布仅1天的千问新模型Qwen3.6-Plus，冲上全球知名大模型API调用平台OpenRouter的日榜榜首，日调用量突破1.4万亿Token。",
        source="stcn",
        published_at="2026-04-04T10:44:37+08:00",
        url="https://example.com/qwen-usage-rank",
        member_news_ids=["n1i"],
        event_type="fast_news",
        event_subtype="industry_data",
        primary_entities=[],
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert "AI应用" in analysis.themes


def test_score_event_marks_reorganization_risk_as_bearish() -> None:
    event = Event(
        event_id="event-001k",
        first_seen_at="2026-04-09T00:00:00+08:00",
        last_seen_at="2026-04-09T00:00:00+08:00",
        canonical_title="美克家居关于被债权人申请重整及预重整的专项自查报告",
        summary="美克家居关于被债权人申请重整及预重整的专项自查报告",
        source="cninfo",
        published_at="2026-04-09T00:00:00+08:00",
        url="https://example.com/cninfo-reorganization-risk",
        member_news_ids=["n1k"],
        event_type="hard_event",
        event_subtype="reorganization_risk",
        primary_entities=[],
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bearish"
    assert analysis.triggered is True


def test_score_event_marks_bankruptcy_liquidation_application_as_bearish() -> None:
    event = Event(
        event_id="event-001kb",
        first_seen_at="2026-04-13T00:00:00+08:00",
        last_seen_at="2026-04-13T00:00:00+08:00",
        canonical_title="关于公司下属公司申请破产清算的公告",
        summary="公司下属公司申请破产清算，相关事项存在不确定性。",
        source="sse",
        published_at="2026-04-13T00:00:00+08:00",
        url="https://example.com/sse-bankruptcy-liquidation",
        member_news_ids=["n1kb"],
        event_type="hard_event",
        event_subtype="reorganization_risk",
        primary_entities=[],
        source_authority_score=0.95,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bearish"
    assert analysis.triggered is True


def test_score_event_marks_legal_dispute_as_bearish() -> None:
    event = Event(
        event_id="event-001l",
        first_seen_at="2026-04-09T00:00:00+08:00",
        last_seen_at="2026-04-09T00:00:00+08:00",
        canonical_title="天奈科技关于商标争议事项进展的公告",
        summary="天奈科技关于商标争议事项进展的公告",
        source="cninfo",
        published_at="2026-04-09T00:00:00+08:00",
        url="https://example.com/cninfo-legal-dispute",
        member_news_ids=["n1l"],
        event_type="hard_event",
        event_subtype="legal_dispute",
        primary_entities=[],
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bearish"
    assert analysis.triggered is True


def test_score_event_marks_csrs_filing_notice_as_bearish() -> None:
    event = Event(
        event_id="event-001lr",
        first_seen_at="2026-04-21T00:00:00+08:00",
        last_seen_at="2026-04-21T00:00:00+08:00",
        canonical_title="上海太和水科技发展股份有限公司关于收到中国证券监督管理委员会立案告知书的公告",
        summary="公司收到中国证券监督管理委员会立案告知书。",
        source="sse",
        published_at="2026-04-21T00:00:00+08:00",
        url="https://example.com/sse-regulatory-risk",
        member_news_ids=["n1lr"],
        event_type="hard_event",
        event_subtype="legal_dispute",
        primary_entities=[],
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bearish"
    assert analysis.triggered is True


def test_score_event_marks_patent_infringement_dispute_as_bearish() -> None:
    event = Event(
        event_id="event-001lp",
        first_seen_at="2026-04-08T19:51:57+08:00",
        last_seen_at="2026-04-08T19:51:57+08:00",
        canonical_title="佰维存储：作为被告涉及两起侵害发明专利权纠纷案件 涉案金额合计5000万元",
        summary="公司作为被告涉及两起侵害发明专利权纠纷案件，涉案金额合计5000万元。",
        source="stcn",
        published_at="2026-04-08T19:51:57+08:00",
        url="https://example.com/stcn-patent-dispute",
        member_news_ids=["n1lp"],
        event_type="fast_news",
        event_subtype="legal_dispute",
        primary_entities=[],
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bearish"
    assert analysis.triggered is True


def test_score_event_marks_major_litigation_progress_as_bearish() -> None:
    event = Event(
        event_id="event-001lm",
        first_seen_at="2026-04-22T00:00:00+08:00",
        last_seen_at="2026-04-22T00:00:00+08:00",
        canonical_title="ST岭南：关于重大诉讼的进展公告",
        summary="ST岭南：关于重大诉讼的进展公告",
        source="szse",
        published_at="2026-04-22T00:00:00+08:00",
        url="https://example.com/szse-major-litigation",
        member_news_ids=["n1lm"],
        event_type="hard_event",
        event_subtype="legal_dispute",
        primary_entities=[],
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bearish"
    assert analysis.triggered is True


def test_score_event_marks_case_filing_notice_as_bearish() -> None:
    event = Event(
        event_id="event-001ln",
        first_seen_at="2026-04-22T00:00:00+08:00",
        last_seen_at="2026-04-22T00:00:00+08:00",
        canonical_title="ST岭南：关于收到万安县住房和城乡建设局立案通知书的公告",
        summary="ST岭南：关于收到万安县住房和城乡建设局立案通知书的公告",
        source="szse",
        published_at="2026-04-22T00:00:00+08:00",
        url="https://example.com/szse-filing-notice",
        member_news_ids=["n1ln"],
        event_type="hard_event",
        event_subtype="legal_dispute",
        primary_entities=[],
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bearish"
    assert analysis.triggered is True


def test_score_event_marks_asset_seizure_notice_as_bearish() -> None:
    event = Event(
        event_id="event-001ls",
        first_seen_at="2026-04-30T00:00:00+08:00",
        last_seen_at="2026-04-30T00:00:00+08:00",
        canonical_title="ST泉为：关于部分资产被查封的公告",
        summary="ST泉为：关于部分资产被查封的公告",
        source="szse",
        published_at="2026-04-30T00:00:00+08:00",
        url="https://example.com/szse-asset-seizure",
        member_news_ids=["n1ls"],
        event_type="hard_event",
        event_subtype="legal_dispute",
        primary_entities=[],
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bearish"
    assert analysis.triggered is True


def test_score_event_marks_share_judicial_freeze_notice_as_bearish() -> None:
    event = Event(
        event_id="event-001freeze",
        first_seen_at="2026-04-30T00:00:00+08:00",
        last_seen_at="2026-04-30T00:00:00+08:00",
        canonical_title="元道通信：关于控股股东部分股份被司法冻结的公告",
        summary="元道通信：关于控股股东部分股份被司法冻结的公告",
        source="szse",
        published_at="2026-04-30T00:00:00+08:00",
        url="https://example.com/szse-share-freeze",
        member_news_ids=["n1freeze"],
        event_type="hard_event",
        event_subtype="legal_dispute",
        primary_entities=[],
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bearish"
    assert analysis.triggered is True


def test_score_event_marks_hkex_profit_warning_as_bearish() -> None:
    event = Event(
        event_id="event-hk-pw",
        first_seen_at="2026-04-17T20:00:00+08:00",
        last_seen_at="2026-04-17T20:00:00+08:00",
        canonical_title="PROFIT WARNING",
        summary="PROFIT WARNING",
        source="hkex",
        published_at="2026-04-17T20:00:00+08:00",
        url="https://example.com/hkex-profit-warning",
        member_news_ids=["n-hk-pw"],
        event_type="hard_event",
        event_subtype="business_guidance",
        primary_entities=[],
        source_authority_score=0.93,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bearish"
    assert analysis.triggered is True


def test_score_event_marks_hkex_positive_profit_alert_as_bullish() -> None:
    event = Event(
        event_id="event-hk-ppa",
        first_seen_at="2026-04-16T21:28:00+08:00",
        last_seen_at="2026-04-16T21:28:00+08:00",
        canonical_title="INSIDE INFORMATION - POSITIVE PROFIT ALERT",
        summary="INSIDE INFORMATION - POSITIVE PROFIT ALERT",
        source="hkex",
        published_at="2026-04-16T21:28:00+08:00",
        url="https://example.com/hkex-positive-profit-alert",
        member_news_ids=["n-hk-ppa"],
        event_type="hard_event",
        event_subtype="business_guidance",
        primary_entities=[],
        source_authority_score=0.93,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bullish"
    assert analysis.triggered is True


def test_score_event_marks_delisting_risk_as_bearish() -> None:
    event = Event(
        event_id="event-001ld",
        first_seen_at="2026-04-09T00:00:00+08:00",
        last_seen_at="2026-04-09T00:00:00+08:00",
        canonical_title="关于公司股票交易可能被实施退市风险警示的提示性公告",
        summary="公司股票交易可能被实施退市风险警示。",
        source="cninfo",
        published_at="2026-04-09T00:00:00+08:00",
        url="https://example.com/cninfo-delisting-risk",
        member_news_ids=["n1ld"],
        event_type="hard_event",
        event_subtype="delisting_risk",
        primary_entities=[],
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bearish"
    assert analysis.triggered is True


def test_score_event_marks_risk_warning_revocation_as_bullish() -> None:
    event = Event(
        event_id="event-001ldr",
        first_seen_at="2026-04-15T00:00:00+08:00",
        last_seen_at="2026-04-15T00:00:00+08:00",
        canonical_title="ST中青宝：关于撤销其他风险警示暨股票停复牌的公告",
        summary="公司撤销其他风险警示的申请已获得深交所审核同意，股票将停牌一天后复牌并撤销其他风险警示。",
        source="szse",
        published_at="2026-04-15T00:00:00+08:00",
        url="https://example.com/szse-risk-warning-revocation",
        member_news_ids=["n1ldr"],
        event_type="hard_event",
        event_subtype="delisting_risk",
        primary_entities=[],
        source_authority_score=0.94,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bullish"
    assert analysis.triggered is True


def test_score_event_marks_control_change_acquisition_as_bullish() -> None:
    event = Event(
        event_id="event-001cc",
        first_seen_at="2026-04-15T00:00:00+08:00",
        last_seen_at="2026-04-15T00:00:00+08:00",
        canonical_title="盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告",
        summary="公司拟通过本次交易收购标的公司控制权。",
        source="szse",
        published_at="2026-04-15T00:00:00+08:00",
        url="https://example.com/szse-control-change-acquisition",
        member_news_ids=["n1cc"],
        event_type="hard_event",
        event_subtype="control_change",
        primary_entities=[],
        source_authority_score=0.94,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bullish"
    assert analysis.triggered is True


def test_score_event_marks_delisting_risk_revocation_application_as_bullish() -> None:
    event = Event(
        event_id="event-001cc2",
        first_seen_at="2026-04-15T00:00:00+08:00",
        last_seen_at="2026-04-15T00:00:00+08:00",
        canonical_title="*ST中地：关于申请撤销公司股票退市风险警示的公告",
        summary="公司已向深交所提交申请撤销公司股票退市风险警示的材料。",
        source="szse",
        published_at="2026-04-15T00:00:00+08:00",
        url="https://example.com/szse-delisting-risk-revocation-application",
        member_news_ids=["n1cc2"],
        event_type="hard_event",
        event_subtype="delisting_risk",
        primary_entities=[],
        source_authority_score=0.94,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bullish"


def test_score_event_marks_delisting_risk_revocation_application_with_stock_trading_wording_as_bullish() -> None:
    event = Event(
        event_id="event-001cc3",
        first_seen_at="2026-04-17T00:00:00+08:00",
        last_seen_at="2026-04-17T00:00:00+08:00",
        canonical_title="*ST荣控：荣丰控股集团关于申请撤销对公司股票交易实施退市风险警示的公告",
        summary="公司已向深交所提交申请撤销对公司股票交易实施退市风险警示的材料。",
        source="szse",
        published_at="2026-04-17T00:00:00+08:00",
        url="https://example.com/szse-delisting-risk-revocation-application-2",
        member_news_ids=["n1cc3"],
        event_type="hard_event",
        event_subtype="delisting_risk",
        primary_entities=[],
        source_authority_score=0.94,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "bullish"


def test_score_event_does_not_treat_generic_model_api_rank_as_ai_application() -> None:
    event = Event(
        event_id="event-001j",
        first_seen_at="2026-04-04T10:44:37+08:00",
        last_seen_at="2026-04-04T10:44:37+08:00",
        canonical_title="某模型API平台发布最新模型调用排行榜",
        summary="平台披露多家模型厂商调用量变化，但未提及具体产品名称或场景化应用。",
        source="stcn",
        published_at="2026-04-04T10:44:37+08:00",
        url="https://example.com/generic-model-api-rank",
        member_news_ids=["n1j"],
        event_type="fast_news",
        event_subtype="industry_data",
        primary_entities=[],
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert "AI应用" not in analysis.themes


def test_score_event_flags_hard_event_as_triggered() -> None:
    event = Event(
        event_id="event-002",
        first_seen_at="2026-04-02T11:46:27+08:00",
        last_seen_at="2026-04-02T11:46:27+08:00",
        canonical_title="关于聘任窦昌林博士为公司首席执行官兼首席科学家的公告",
        summary="公司公告。",
        source="cninfo",
        published_at="2026-04-02T11:46:27+08:00",
        url="https://example.com/hard-event",
        member_news_ids=["n2"],
        event_type="hard_event",
        primary_entities=["安科生物"],
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.triggered is True


def test_score_event_flags_fast_news_as_triggered() -> None:
    event = Event(
        event_id="event-003",
        first_seen_at="2026-04-02T12:14:33+08:00",
        last_seen_at="2026-04-02T12:14:33+08:00",
        canonical_title="国家药监局发布生物制品分段生产操作指南",
        summary="快讯报道监管部门发布操作指南。",
        source="stcn",
        published_at="2026-04-02T12:14:33+08:00",
        url="https://example.com/fast-news",
        member_news_ids=["n3"],
        event_type="fast_news",
        primary_entities=["国家药监局"],
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.triggered is True


def test_score_event_uses_company_theme_map_for_cninfo_hard_event() -> None:
    event = Event(
        event_id="event-004",
        first_seen_at="2026-04-02T11:44:27+08:00",
        last_seen_at="2026-04-02T11:44:27+08:00",
        canonical_title="关于2025年度向特定对象发行A股股票申请获得深圳证券交易所受理的公告",
        summary="关于2025年度向特定对象发行A股股票申请获得深圳证券交易所受理的公告",
        source="cninfo",
        published_at="2026-04-02T11:44:27+08:00",
        url="https://www.cninfo.com.cn/new/disclosure/detail?stockCode=300005&announcementId=1225073837",
        member_news_ids=["n4"],
        event_type="hard_event",
        event_subtype="financing_acceptance",
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert "户外经济" in analysis.themes
    assert analysis.triggered is True


def test_score_event_does_not_use_company_theme_map_for_generic_disclosure() -> None:
    event = Event(
        event_id="event-005",
        first_seen_at="2026-04-02T11:44:27+08:00",
        last_seen_at="2026-04-02T11:44:27+08:00",
        canonical_title="探路者控股集团股份有限公司最近一年的财务报告及其审计报告以及最近一期的财务报告",
        summary="探路者控股集团股份有限公司最近一年的财务报告及其审计报告以及最近一期的财务报告",
        source="cninfo",
        published_at="2026-04-02T11:44:27+08:00",
        url="https://www.cninfo.com.cn/new/disclosure/detail?stockCode=300005&announcementId=1225073841",
        member_news_ids=["n5"],
        event_type="hard_event",
        event_subtype="corporate_disclosure",
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert "户外经济" not in analysis.themes


def test_score_event_does_not_trigger_low_signal_cninfo_esg_disclosure() -> None:
    event = Event(
        event_id="event-005a",
        first_seen_at="2026-04-17T00:00:00+08:00",
        last_seen_at="2026-04-17T00:00:00+08:00",
        canonical_title="青岛食品2025年度环境、社会和公司治理报告",
        summary="青岛食品2025年度环境、社会和公司治理报告。",
        source="cninfo",
        published_at="2026-04-17T00:00:00+08:00",
        url="https://example.com/cninfo-esg-report",
        member_news_ids=["n5a"],
        event_type="hard_event",
        event_subtype="corporate_disclosure",
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == []
    assert analysis.triggered is False


def test_score_event_does_not_trigger_low_signal_cninfo_earnings_briefing_notice() -> None:
    event = Event(
        event_id="event-005b",
        first_seen_at="2026-04-17T00:00:00+08:00",
        last_seen_at="2026-04-17T00:00:00+08:00",
        canonical_title="关于举行2025年度业绩网上说明会的公告",
        summary="关于举行2025年度业绩网上说明会的公告。",
        source="cninfo",
        published_at="2026-04-17T00:00:00+08:00",
        url="https://example.com/cninfo-earnings-briefing",
        member_news_ids=["n5b"],
        event_type="hard_event",
        event_subtype="corporate_disclosure",
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == []
    assert analysis.triggered is False


def test_score_event_keeps_thematic_related_party_capex_disclosure_triggered() -> None:
    event = Event(
        event_id="event-005c",
        first_seen_at="2026-04-16T00:00:00+08:00",
        last_seen_at="2026-04-16T00:00:00+08:00",
        canonical_title="公告2026-017-中远海能关于投资建造两艘巴拿马型原油轮暨关联交易的公告",
        summary="summary",
        source="sse",
        published_at="2026-04-16T00:00:00+08:00",
        url="https://example.com/thematic-related-party-capex",
        member_news_ids=["n5c"],
        event_type="hard_event",
        event_subtype="corporate_disclosure",
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == ["油气"]
    assert analysis.triggered is True


def test_score_event_does_not_trigger_low_signal_cninfo_director_liability_insurance_notice() -> None:
    event = Event(
        event_id="event-005d",
        first_seen_at="2026-04-17T00:00:00+08:00",
        last_seen_at="2026-04-17T00:00:00+08:00",
        canonical_title="关于拟购买董事及高级管理人员责任保险的公告",
        summary="关于拟购买董事及高级管理人员责任保险的公告。",
        source="cninfo",
        published_at="2026-04-17T00:00:00+08:00",
        url="https://example.com/cninfo-director-liability-insurance",
        member_news_ids=["n5d"],
        event_type="hard_event",
        event_subtype="corporate_disclosure",
        source_authority_score=1.0,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert "保险" in analysis.themes
    assert analysis.triggered is False


def test_score_event_does_not_treat_summary_theme_as_market_move_theme() -> None:
    event = Event(
        event_id="event-006",
        first_seen_at="2026-04-02T21:32:39+08:00",
        last_seen_at="2026-04-02T21:32:39+08:00",
        canonical_title="美股三大指数集体低开 特斯拉跌超3%",
        summary="美股三大指数集体低开。存储芯片板块大跌，闪迪跌超5%，美光科技跌超5%。",
        source="stcn",
        published_at="2026-04-02T21:32:39+08:00",
        url="https://example.com/us-market-move",
        member_news_ids=["n6"],
        event_type="fast_news",
        event_subtype="market_move",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert "半导体" not in analysis.themes


def test_score_event_prefers_title_theme_for_fast_news_over_summary_spillover() -> None:
    event = Event(
        event_id="event-007",
        first_seen_at="2026-04-02T20:14:34+08:00",
        last_seen_at="2026-04-02T20:14:34+08:00",
        canonical_title="【调研风向标】功率半导体行业维持高景气，这家公司一季度业绩预增，客户下单意愿显著增强",
        summary="受益于AI算力爆发、新能源汽车、储能及工控等下游应用领域的强劲需求，人形机器人等新场景持续跟进。",
        source="stcn",
        published_at="2026-04-02T20:14:34+08:00",
        url="https://example.com/power-semiconductor",
        member_news_ids=["n7"],
        event_type="fast_news",
        event_subtype="business_guidance",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == ["半导体"]


def test_score_event_does_not_treat_general_fast_news_summary_theme_as_event_theme() -> None:
    event = Event(
        event_id="event-007a",
        first_seen_at="2026-04-09T12:55:10+08:00",
        last_seen_at="2026-04-09T12:55:10+08:00",
        canonical_title="玻璃基板爆发在即 潜力股有这些",
        summary="机构称AI算力需求带动相关材料景气度提升，部分公司同步受益。",
        source="stcn",
        published_at="2026-04-09T12:55:10+08:00",
        url="https://example.com/glass-substrate",
        member_news_ids=["n7a"],
        event_type="fast_news",
        event_subtype="general_fast_news",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == []


def test_score_event_uses_lower_boost_for_general_fast_news_with_theme() -> None:
    event = Event(
        event_id="event-007a1",
        first_seen_at="2026-04-15T06:20:13+08:00",
        last_seen_at="2026-04-15T06:20:13+08:00",
        canonical_title="光通信进入可持续景气周期 产业链多环节成长空间打开",
        summary="有研究机构认为，2026年是AI光互联的大年，光互联将持续向算力连接环节不断渗透。",
        source="cls",
        published_at="2026-04-15T06:20:13+08:00",
        url="https://www.cls.cn/detail/2344212",
        member_news_ids=["n7a1"],
        event_type="fast_news",
        event_subtype="general_fast_news",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == ["算力"]
    assert analysis.impact_score == 79.0
    assert analysis.triggered is True


def test_score_event_marks_editorial_roundup_general_fast_news_as_neutral() -> None:
    event = Event(
        event_id="event-007a2",
        first_seen_at="2026-04-15T06:31:03+08:00",
        last_seen_at="2026-04-15T06:31:03+08:00",
        canonical_title="周三你需要知道的隔夜全球要闻：国际原油下挫 美股纳指十连涨",
        summary="霍尔木兹海峡恢复部分通航，国际原油期货收盘下挫，美股三大指数集体收涨。",
        source="cls",
        published_at="2026-04-15T06:31:03+08:00",
        url="https://www.cls.cn/detail/2344207",
        member_news_ids=["n7a2"],
        event_type="fast_news",
        event_subtype="general_fast_news",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "neutral"


def test_score_event_marks_general_fast_news_feature_story_as_neutral() -> None:
    event = Event(
        event_id="event-007a3",
        first_seen_at="2026-04-15T06:20:13+08:00",
        last_seen_at="2026-04-15T06:20:13+08:00",
        canonical_title="光通信进入可持续景气周期 产业链多环节成长空间打开",
        summary="美国光通信龙头表示需求正在加速增长，公司预计两个季度内将售罄2028年产能。光互联将持续向算力连接环节不断渗透，为未来几年打开更大的成长空间。",
        source="cls",
        published_at="2026-04-15T06:20:13+08:00",
        url="https://www.cls.cn/detail/2344212",
        member_news_ids=["n7a3"],
        event_type="fast_news",
        event_subtype="general_fast_news",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.direction == "neutral"


def test_score_event_does_not_treat_advanced_storage_equipment_as_compute_infra() -> None:
    event = Event(
        event_id="event-007b",
        first_seen_at="2026-04-09T12:43:03+08:00",
        last_seen_at="2026-04-09T12:43:03+08:00",
        canonical_title="华海清科面向先进存储的新型12英寸晶圆减薄装备首台出机",
        summary="发往国内集成电路制造龙头企业，该机型可满足三维集成技术对超精密加工的要求。",
        source="stcn",
        published_at="2026-04-09T12:43:03+08:00",
        url="https://example.com/advanced-storage-equipment",
        member_news_ids=["n7b"],
        event_type="fast_news",
        event_subtype="company_update",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == ["半导体"]


def test_score_event_does_not_treat_company_update_downstream_scene_list_as_themes() -> None:
    event = Event(
        event_id="event-007c",
        first_seen_at="2026-04-09T13:09:46+08:00",
        last_seen_at="2026-04-09T13:09:46+08:00",
        canonical_title="天齐锂业：预计2026年上半年锂矿供应将持续偏紧",
        summary="长远来看，新能源行业发展空间广阔；同时，储能、机器人等新兴应用场景不断涌现，对锂盐及相关关键材料需求持续提升。",
        source="stcn",
        published_at="2026-04-09T13:09:46+08:00",
        url="https://example.com/lithium-supply-outlook",
        member_news_ids=["n7c"],
        event_type="fast_news",
        event_subtype="company_update",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == []


def test_score_event_does_not_treat_company_setup_registry_scope_as_theme() -> None:
    event = Event(
        event_id="event-007c2",
        first_seen_at="2026-04-17T15:13:06+08:00",
        last_seen_at="2026-04-17T15:13:06+08:00",
        canonical_title="中国电建成立绿能科技服务公司",
        summary="人民财讯4月17日电，企查查APP显示，近日，广东丰汇绿能科技服务有限公司成立，法定代表人为王晓明，经营范围包含：新兴能源技术研发；集中式快速充电站；储能技术服务；太阳能发电技术服务；合同能源管理等。企查查股权穿透显示，该公司由中国电建间接全资持股。",
        source="stcn",
        published_at="2026-04-17T15:13:06+08:00",
        url="https://example.com/company-setup-registry-scope",
        member_news_ids=["n7c2"],
        event_type="fast_news",
        event_subtype="company_update",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == []


def test_score_event_does_not_treat_background_track_commentary_as_project_theme() -> None:
    event = Event(
        event_id="event-007d",
        first_seen_at="2026-04-09T23:11:26+08:00",
        last_seen_at="2026-04-09T23:11:26+08:00",
        canonical_title="豪恩汽电：已获得国内低空飞行器企业的项目定点",
        summary="人民财讯4月9日电，豪恩汽电4月9日在业绩说明会上表示，机器人领域是公司除主营业务外最重要的赛道之一，目前感知类产品已实现量产交付，域控产品已开发，同时公司还在不断地进行新产品的预研发。低空经济端，目前公司已获得国内低空飞行器企业的项目定点，相关产品将于2026年实现规模化量产交付。",
        source="stcn",
        published_at="2026-04-09T23:11:26+08:00",
        url="https://example.com/low-altitude-project-designation",
        member_news_ids=["n7d"],
        event_type="fast_news",
        event_subtype="company_update",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == []


def test_score_event_keeps_summary_theme_for_fast_news_when_title_has_no_theme() -> None:
    event = Event(
        event_id="event-008",
        first_seen_at="2026-04-02T20:59:03+08:00",
        last_seen_at="2026-04-02T20:59:03+08:00",
        canonical_title="中国能建与华北电力大学签署战略合作协议",
        summary="双方将围绕构建新型能源体系和新型电力系统深化合作。",
        source="stcn",
        published_at="2026-04-02T20:59:03+08:00",
        url="https://example.com/power-theme",
        member_news_ids=["n8"],
        event_type="fast_news",
        event_subtype="cooperation_agreement",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == ["电力资源"]


def test_score_event_keeps_semiconductor_theme_for_fast_news_when_title_has_no_theme() -> None:
    event = Event(
        event_id="event-009",
        first_seen_at="2026-04-02T21:10:03+08:00",
        last_seen_at="2026-04-02T21:10:03+08:00",
        canonical_title="企业与研究机构签署合作协议",
        summary="双方将围绕国产EDA工具链和先进封装产线建设深化合作。",
        source="stcn",
        published_at="2026-04-02T21:10:03+08:00",
        url="https://example.com/chip-edge-theme",
        member_news_ids=["n9"],
        event_type="fast_news",
        event_subtype="cooperation_agreement",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == ["半导体"]


def test_score_event_keeps_energy_storage_theme_for_fast_news_when_title_has_no_theme() -> None:
    event = Event(
        event_id="event-010",
        first_seen_at="2026-04-09T12:02:57+08:00",
        last_seen_at="2026-04-09T12:02:57+08:00",
        canonical_title="隆基与华为数字能源达成战略合作",
        summary="双方将在储能系统集成、智能组串式PCS以及清洁能源大基地解决方案等方面展开深度合作。",
        source="stcn",
        published_at="2026-04-09T12:02:57+08:00",
        url="https://example.com/energy-storage-theme",
        member_news_ids=["n10"],
        event_type="fast_news",
        event_subtype="cooperation_agreement",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert analysis.themes == ["储能"]


def test_score_event_does_not_treat_generic_clean_energy_cooperation_as_energy_storage() -> None:
    event = Event(
        event_id="event-011",
        first_seen_at="2026-04-09T12:02:57+08:00",
        last_seen_at="2026-04-09T12:02:57+08:00",
        canonical_title="企业与合作方达成清洁能源战略合作",
        summary="双方将在清洁能源大基地解决方案、绿色电力协同和零碳园区建设方面展开合作。",
        source="stcn",
        published_at="2026-04-09T12:02:57+08:00",
        url="https://example.com/generic-clean-energy-theme",
        member_news_ids=["n11"],
        event_type="fast_news",
        event_subtype="cooperation_agreement",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert "储能" not in analysis.themes


def test_score_event_does_not_treat_financial_result_summary_theme_as_fast_news_theme() -> None:
    event = Event(
        event_id="event-010",
        first_seen_at="2026-04-02T23:19:19+08:00",
        last_seen_at="2026-04-02T23:19:19+08:00",
        canonical_title="*ST金刚：2025年净利润2.03亿元同比扭亏为盈，拟申请撤销退市风险警示",
        summary="公司紧抓算力行业发展机遇，成功开拓并落地算力服务业务；此外拟定增募资用于人工智能智算中心项目。",
        source="stcn",
        published_at="2026-04-02T23:19:19+08:00",
        url="https://example.com/earnings-summary-theme",
        member_news_ids=["n10"],
        event_type="fast_news",
        event_subtype="business_guidance",
        source_authority_score=0.8,
    )
    analysis = score_event(event, scoring_config=load_scoring_config())
    assert "算力" not in analysis.themes
