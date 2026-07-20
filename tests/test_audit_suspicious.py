from news_sentiment.cli import main
from news_sentiment.models import Event, EventAnalysis
from news_sentiment.settings import ProjectPaths
from news_sentiment.storage import JsonlStore


def test_audit_suspicious_prints_flagged_candidates(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-risk",
                first_seen_at="2026-04-09T00:00:00+08:00",
                last_seen_at="2026-04-09T00:00:00+08:00",
                canonical_title="美克家居关于被债权人申请重整及预重整的专项自查报告",
                summary="summary",
                source="cninfo",
                published_at="2026-04-09T00:00:00+08:00",
                url="https://example.com/risk",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-theme-fast",
                first_seen_at="2026-04-08T14:39:37+08:00",
                last_seen_at="2026-04-08T14:39:37+08:00",
                canonical_title="琏升科技成立数字科技公司 含AI及卫星相关业务",
                summary="summary",
                source="stcn",
                published_at="2026-04-08T14:39:37+08:00",
                url="https://example.com/theme-fast",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-fast-legal",
                first_seen_at="2026-04-08T19:51:57+08:00",
                last_seen_at="2026-04-08T19:51:57+08:00",
                canonical_title="佰维存储：作为被告涉及两起侵害发明专利权纠纷案件 涉案金额合计5000万元",
                summary="summary",
                source="stcn",
                published_at="2026-04-08T19:51:57+08:00",
                url="https://example.com/fast-legal",
                event_type="fast_news",
                event_subtype="company_update",
            ),
            Event(
                event_id="event-keep",
                first_seen_at="2026-04-08T18:59:25+08:00",
                last_seen_at="2026-04-08T18:59:25+08:00",
                canonical_title="内蒙古：建设全国领先的绿色智能算力保障基地 持续提升智能算力规模",
                summary="summary",
                source="stcn",
                published_at="2026-04-08T18:59:25+08:00",
                url="https://example.com/keep",
                event_type="fast_news",
                event_subtype="policy_signal",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-risk",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-theme-fast",
                direction="neutral",
                impact_score=99.0,
                reasoning="rule",
                themes=["AI应用"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-fast-legal",
                direction="neutral",
                impact_score=99.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-keep",
                direction="bullish",
                impact_score=99.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=3" in output
    assert "hard_event_risk_keyword" in output
    assert "general_fast_news_with_theme" in output
    assert "company_update_legal_keyword" in output
    assert "美克家居关于被债权人申请重整及预重整的专项自查报告" in output
    assert "琏升科技成立数字科技公司 含AI及卫星相关业务" in output
    assert "佰维存储：作为被告涉及两起侵害发明专利权纠纷案件 涉案金额合计5000万元" in output
    assert "内蒙古：建设全国领先的绿色智能算力保障基地 持续提升智能算力规模" not in output


def test_audit_suspicious_skips_cninfo_restructuring_material_reply(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-restructuring-reply",
                direction="bullish",
                impact_score=100.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "中芯国际关于发行股份购买资产暨关联交易的审核问询函回复的提示性公告" not in output


def test_audit_suspicious_skips_cninfo_numbered_inquiry_reply_exemption_material(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-numbered-inquiry-reply-exemption",
                first_seen_at="2026-07-01T11:56:28+08:00",
                last_seen_at="2026-07-01T11:56:28+08:00",
                canonical_title="7-2 会计师关于审核问询函的回复（豁免版）",
                summary="7-2 会计师关于审核问询函的回复（豁免版）",
                source="cninfo",
                published_at="2026-07-01T11:56:28+08:00",
                url="https://example.com/cninfo-numbered-inquiry-reply-exemption",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-numbered-inquiry-reply-exemption",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "7-2 会计师关于审核问询函的回复（豁免版）" not in output


def test_audit_suspicious_skips_sse_einteractive_litigation_disposal_suggestion(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    title = (
        "泉阳泉：董秘你好：园林 1.23 亿工程款诉讼尚未落地，持有越久，坏账计提、负债风险越大，"
        "越早挂牌转让越能锁定资产价值。 希望证券部把我的建议完整转达董事长、经营层和大股东森工集团，"
        "恳请管理层成立专项小组对接国资审批，简化流程、主动对接意向受让方，争取今年内完成全部剥离交割工作。"
    )
    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-sse-einteractive-litigation-disposal-suggestion",
                first_seen_at="2026-07-09T10:51:00+08:00",
                last_seen_at="2026-07-09T10:51:00+08:00",
                canonical_title=title,
                summary=(
                    f"问题：{title} "
                    "回复：尊敬的投资者，您的建议我们已收悉，我们将如实转达，并将积极推进有关工作。谢谢！"
                ),
                source="sse_einteractive",
                published_at="2026-07-09T10:51:00+08:00",
                url="https://sns.sseinfo.com/qadetail.do?weiboId=1767015",
                event_type="fast_news",
                event_subtype="company_update",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-sse-einteractive-litigation-disposal-suggestion",
                direction="bullish",
                impact_score=74.9,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "泉阳泉：董秘你好：园林 1.23 亿工程款诉讼尚未落地" not in output


def test_audit_suspicious_skips_stcn_financing_balance_statistical_recap(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    title = "近一周融资资金加码多只光模块龙头股 撤离存储等赛道"
    summary = (
        "据证券时报·数据宝统计，近一周A股融资余额有所下降，交易所披露的最新数据为29341.64亿元。"
        "A股融资资金近一周总体呈现净偿还态势，融资净买入方面，新易盛、东山精密净买入额居前。"
    )
    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-financing-balance-recap",
                first_seen_at="2026-07-12T19:11:25+08:00",
                last_seen_at="2026-07-12T19:11:25+08:00",
                canonical_title=title,
                summary=summary,
                source="stcn",
                published_at="2026-07-12T19:11:25+08:00",
                url="https://www.stcn.com/article/detail/4013181.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-financing-balance-recap",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert title not in output


def test_audit_suspicious_skips_stcn_crude_main_contract_percent_move(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    title = "上期所原油主力合约涨幅扩大至9%"
    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-crude-main-contract-percent-move",
                first_seen_at="2026-07-14T11:22:10+08:00",
                last_seen_at="2026-07-14T11:22:10+08:00",
                canonical_title=title,
                summary="人民财讯7月14日电，上期所原油主力合约涨幅扩大至9%，报514.8元/桶。",
                source="stcn",
                published_at="2026-07-14T11:22:10+08:00",
                url="https://www.stcn.com/article/detail/4016708.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-crude-main-contract-percent-move",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["油气"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert title not in output


def test_audit_suspicious_skips_stcn_electric_robot_validation_platform(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    title = "北京电力具身智能机器人中试验证平台正式对外服务"
    summary = (
        "人民财讯7月14日电，近日，由北京市经济和信息化局指导，国网北京市电力公司牵头建设的"
        "北京电力具身智能机器人中试验证平台建成并对外提供服务。该平台位于大兴区磁各庄国网北京市"
        "电力公司实验实训基地，占地面积5000余平方米，包含输变电真型实验平台、配网真型实验平台、"
        "电力具身智能研发验证区等多个区域，重点聚焦输变配巡检、带电作业等电网核心业务场景，打造"
        "电力具身智能机器人自主巡视、状态检测、现场操作等中试验证能力。"
    )
    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-electric-robot-validation-platform",
                first_seen_at="2026-07-14T11:13:39+08:00",
                last_seen_at="2026-07-14T11:13:39+08:00",
                canonical_title=title,
                summary=summary,
                source="stcn",
                published_at="2026-07-14T11:13:39+08:00",
                url="https://www.stcn.com/article/detail/4016695.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-electric-robot-validation-platform",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["机器人"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert title not in output


def test_audit_suspicious_skips_stcn_a_share_concept_rebound_recap(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    title = "科技股反弹，MLCC、PCB概念等涨幅居前"
    summary = (
        "人民财讯7月14日电，科技股反弹，MLCC、PCB概念、复合铜箔、CPO概念等涨幅居前。"
        "个股方面，博杰股份、沪电股份、金安国纪等一批个股涨停。"
    )
    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-a-share-concept-rebound-recap",
                first_seen_at="2026-07-14T13:28:22+08:00",
                last_seen_at="2026-07-14T13:28:22+08:00",
                canonical_title=title,
                summary=summary,
                source="stcn",
                published_at="2026-07-14T13:28:22+08:00",
                url="https://www.stcn.com/article/detail/4016933.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-a-share-concept-rebound-recap",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["PCB"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert title not in output


def test_audit_suspicious_skips_restructuring_review_process_materials(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-restructuring-review-inquiry-received",
                first_seen_at="2026-07-02T00:00:00+08:00",
                last_seen_at="2026-07-02T00:00:00+08:00",
                canonical_title="关于收到深圳证券交易所《关于紫光国芯微电子股份有限公司发行股份及支付现金购买资产并募集配套资金申请的审核问询函》的公告",
                summary="关于收到深圳证券交易所《关于紫光国芯微电子股份有限公司发行股份及支付现金购买资产并募集配套资金申请的审核问询函》的公告",
                source="cninfo",
                published_at="2026-07-02T00:00:00+08:00",
                url="https://example.com/cninfo-restructuring-review-inquiry-received",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-szse-restructuring-application-accepted",
                first_seen_at="2026-07-02T00:00:00+08:00",
                last_seen_at="2026-07-02T00:00:00+08:00",
                canonical_title="盈方微：关于发行股份及支付现金购买资产并募集配套资金暨关联交易申请文件获得深圳证券交易所受理的公告",
                summary="盈方微：关于发行股份及支付现金购买资产并募集配套资金暨关联交易申请文件获得深圳证券交易所受理的公告",
                source="szse",
                published_at="2026-07-02T00:00:00+08:00",
                url="https://example.com/szse-restructuring-application-accepted",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-restructuring-review-inquiry-received",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-szse-restructuring-application-accepted",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "紫光国芯微电子股份有限公司发行股份及支付现金购买资产" not in output
    assert "盈方微：关于发行股份及支付现金购买资产并募集配套资金暨关联交易申请文件获得深圳证券交易所受理的公告" not in output


def test_audit_suspicious_skips_cninfo_restructuring_revised_report(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-restructuring-revised-report",
                direction="bullish",
                impact_score=100.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "中芯国际集成电路制造有限公司发行股份购买资产暨关联交易报告书（修订稿）" not in output


def test_audit_suspicious_skips_cninfo_restructuring_revised_report_without_theme(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
            )
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-restructuring-revised-report-no-theme",
                direction="neutral",
                impact_score=75.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "中芯国际集成电路制造有限公司发行股份购买资产暨关联交易报告书（修订稿）" not in output


def test_audit_suspicious_ignores_all_st_titles_while_keeps_non_st_risk(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-st-west-dev",
                first_seen_at="2026-05-27T14:00:00+08:00",
                last_seen_at="2026-05-27T14:00:00+08:00",
                canonical_title="*ST西发：关于回复《深圳证券交易所对公司重大资产购买的问询函》的公告",
                summary="summary",
                source="cninfo",
                published_at="2026-05-27T14:00:00+08:00",
                url="https://example.com/st-west-dev",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-non-st-risk",
                first_seen_at="2026-05-27T14:05:00+08:00",
                last_seen_at="2026-05-27T14:05:00+08:00",
                canonical_title="美克家居关于被债权人申请重整及预重整的专项自查报告",
                summary="summary",
                source="cninfo",
                published_at="2026-05-27T14:05:00+08:00",
                url="https://example.com/non-st-risk",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-st-west-dev",
                direction="neutral",
                impact_score=83.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-non-st-risk",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=1" in output
    assert "美克家居关于被债权人申请重整及预重整的专项自查报告" in output
    assert "*ST西发：关于回复《深圳证券交易所对公司重大资产购买的问询函》的公告" not in output


def test_audit_suspicious_skips_cninfo_restructuring_material_reply_without_theme(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
            )
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-restructuring-reply-no-theme",
                direction="neutral",
                impact_score=75.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "中芯国际关于发行股份购买资产暨关联交易的审核问询函回复的提示性公告" not in output


def test_audit_suspicious_skips_cninfo_restructuring_special_audit_verification_opinion(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-restructuring-special-audit-opinion",
                first_seen_at="2026-05-05T18:45:00+08:00",
                last_seen_at="2026-05-05T18:45:00+08:00",
                canonical_title="欧菲光：中兴华会计师事务所（特殊普通合伙）关于欧菲光集团股份有限公司发行股份购买资产的审核问询函的专项核查意见",
                summary="summary",
                source="cninfo",
                published_at="2026-05-05T18:45:00+08:00",
                url="https://www.cninfo.com.cn/new/disclosure/detail?stockCode=002456&announcementId=123456789",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-restructuring-special-audit-opinion",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "欧菲光：中兴华会计师事务所（特殊普通合伙）关于欧菲光集团股份有限公司发行股份购买资产的审核问询函的专项核查意见" not in output


def test_audit_suspicious_skips_cninfo_inquiry_reply_related_batch_8_titles(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    titles = [
        "正平股份关于收到上海证券交易所对公司2025年年报有关事项问询函的公告",
        "会计师事务所关于招商局蛇口工业区控股股份有限公司申请向特定对象发行优先股审核问询函回复的专项说明（修订稿）（2025年度财务数据更新版）",
        "关于绿康生化股份有限公司2025年年报问询函相关问题之专项核查意见",
        "信永中和关于对佳沃食品有限公司2025年年报问询函之回复",
        "容诚会计师事务所（特殊普通合伙）关于必易微2025年年度报告信息披露监管问询函的回复",
        "*ST绿康：关于持股5%以上股东股份解除冻结的公告",
        "ST龙大：关于控股股东所持公司部分股份解除冻结的公告",
        "国安股份：关于诉讼案件进展情况的公告",
    ]
    now = "2026-05-11T10:00:00+08:00"
    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id=f"event-cninfo-batch8-{idx}",
                first_seen_at=now,
                last_seen_at=now,
                canonical_title=title,
                summary="summary",
                source="cninfo",
                published_at=now,
                url=f"https://example.com/cninfo-batch8-{idx}",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            )
            for idx, title in enumerate(titles)
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id=f"event-cninfo-batch8-{idx}",
                direction="neutral",
                impact_score=75.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            )
            for idx in range(len(titles))
        ]
    )

    assert main(["audit-suspicious", "--limit", "20"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    for title in titles:
        assert title not in output


def test_audit_suspicious_skips_cninfo_annual_inquiry_reply_with_quote_style(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    title = "*ST佳沃：关于深圳证券交易所《关于对佳沃食品股份有限公司的2025年年报问询函》回复的公告"

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-annual-inquiry-quote-style",
                first_seen_at="2026-05-11T11:00:00+08:00",
                last_seen_at="2026-05-11T11:00:00+08:00",
                canonical_title=title,
                summary="summary",
                source="cninfo",
                published_at="2026-05-11T11:00:00+08:00",
                url="https://example.com/cninfo-annual-inquiry-quote-style",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            )
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-annual-inquiry-quote-style",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert title not in output


def test_audit_suspicious_skips_exchange_generic_annual_inquiry_reply_and_acting_party_unfreeze(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    titles = [
        "关于上海证券交易所对公司2025年年度报告的信息披露监管问询函回复的公告",
        "关于控股股东的一致行动人部分股份解除冻结的公告",
    ]
    now = "2026-07-07T00:00:00+08:00"
    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id=f"event-sse-generic-disclosure-{idx}",
                first_seen_at=now,
                last_seen_at=now,
                canonical_title=title,
                summary=title,
                source="sse",
                published_at=now,
                url=f"https://example.com/sse-generic-disclosure-{idx}",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            )
            for idx, title in enumerate(titles)
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id=f"event-sse-generic-disclosure-{idx}",
                direction="neutral",
                impact_score=78.5,
                reasoning="rule",
                themes=[],
                triggered=True,
            )
            for idx, _title in enumerate(titles)
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    for title in titles:
        assert title not in output


def test_audit_suspicious_skips_cninfo_accountant_annual_inquiry_special_explanation(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    title = "天健会计师事务所(特殊普通合伙)关于合盛硅业股份有限公司2025年年度报告的信息披露监管问询函专项说明"
    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-accountant-annual-inquiry-special-explanation",
                first_seen_at="2026-07-04T00:00:00+08:00",
                last_seen_at="2026-07-04T00:00:00+08:00",
                canonical_title=title,
                summary=title,
                source="cninfo",
                published_at="2026-07-04T00:00:00+08:00",
                url="https://example.com/cninfo-accountant-annual-inquiry-special-explanation",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-accountant-annual-inquiry-special-explanation",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert title not in output


def test_audit_suspicious_skips_cninfo_accountant_annual_inquiry_special_explanation_with_de_particle(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    title = "天健会计师事务所（特殊普通合伙）关于安达智能2025年年度报告信息披露监管问询函的专项说明"
    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-accountant-annual-inquiry-special-explanation-with-de",
                first_seen_at="2026-07-13T00:00:00+08:00",
                last_seen_at="2026-07-13T00:00:00+08:00",
                canonical_title=title,
                summary=title,
                source="cninfo",
                published_at="2026-07-13T00:00:00+08:00",
                url="https://example.com/cninfo-accountant-annual-inquiry-special-explanation-with-de",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-accountant-annual-inquiry-special-explanation-with-de",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert title not in output


def test_audit_suspicious_skips_cninfo_accountant_annual_inquiry_special_explanation_without_de_particle(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    title = "大华会计师事务所关于洲际油气股份有限公司2025年年度报告信息披露监管问询函专说明"
    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-accountant-annual-inquiry-special-explanation-without-de",
                first_seen_at="2026-07-06T00:00:00+08:00",
                last_seen_at="2026-07-06T00:00:00+08:00",
                canonical_title=title,
                summary=title,
                source="cninfo",
                published_at="2026-07-06T00:00:00+08:00",
                url="https://example.com/cninfo-accountant-annual-inquiry-special-explanation-without-de",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-accountant-annual-inquiry-special-explanation-without-de",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert title not in output


def test_audit_suspicious_skips_cninfo_added_litigation_progress_update_without_themes(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    title = "瑞茂通关于公司及子公司新增诉讼及进展情况的公告"

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-added-litigation-progress-update",
                first_seen_at="2026-05-12T00:00:00+08:00",
                last_seen_at="2026-05-12T00:00:00+08:00",
                canonical_title=title,
                summary=title,
                source="cninfo",
                published_at="2026-05-12T00:00:00+08:00",
                url="https://www.cninfo.com.cn/new/disclosure/detail?stockCode=600180&announcementId=1225292957&orgId=gssh0600180&announcementTime=2026-05-12",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            )
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-added-litigation-progress-update",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule_based_scoring",
                themes=[],
                triggered=True,
            )
        ]
    )

    assert main(["audit-suspicious", "--limit", "20"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert title not in output


def test_audit_suspicious_skips_exchange_inquiry_reply_and_special_explanation(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
                event_id="event-szse-audit-inquiry-special-explanation",
                first_seen_at="2026-04-30T00:00:00+08:00",
                last_seen_at="2026-04-30T00:00:00+08:00",
                canonical_title="ST炼石：年度审计机构对公司2025年年报的问询函相关事项的专项说明",
                summary="summary",
                source="szse",
                published_at="2026-04-30T00:00:00+08:00",
                url="https://example.com/szse-audit-inquiry-special-explanation",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
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
                event_id="event-szse-audit-inquiry-special-explanation",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "*ST仁东：关于对深圳证券交易所2025年年报问询函回复的公告" not in output
    assert "*ST仁东：评估机构关于仁东控股年报问询函有关问题的专项说明" not in output
    assert "ST炼石：年度审计机构对公司2025年年报的问询函相关事项的专项说明" not in output


def test_audit_suspicious_skips_exchange_stock_volatility_reply_and_annual_inquiry_special_note(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stock-volatility-inquiry-reply",
                first_seen_at="2026-05-12T00:00:00+08:00",
                last_seen_at="2026-05-12T00:00:00+08:00",
                canonical_title="控股股东关于《上海网达软件股份有限公司股票交易异常波动问询函》的回函",
                summary="summary",
                source="sse",
                published_at="2026-05-12T00:00:00+08:00",
                url="https://example.com/stock-volatility-inquiry-reply",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-annual-inquiry-special-note",
                first_seen_at="2026-05-12T00:00:00+08:00",
                last_seen_at="2026-05-12T00:00:00+08:00",
                canonical_title="*ST凯鑫：中兴华会计师事务所（特殊普通合伙）关于上海凯鑫分离技术股份有限公司2025年度年报问询函的专项说明",
                summary="summary",
                source="szse",
                published_at="2026-05-12T00:00:00+08:00",
                url="https://example.com/annual-inquiry-special-note",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stock-volatility-inquiry-reply",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-annual-inquiry-special-note",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "股票交易异常波动问询函" not in output
    assert "2025年度年报问询函的专项说明" not in output


def test_audit_suspicious_skips_exchange_stock_volatility_matter_reply_and_generic_filing_risk_notice(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stock-volatility-matter-inquiry-reply",
                first_seen_at="2026-07-06T00:00:00+08:00",
                last_seen_at="2026-07-06T00:00:00+08:00",
                canonical_title="关于《亚士创能科技（上海）股份有限公司股票交易异常波动有关事项的问询函》的回函",
                summary="关于《亚士创能科技（上海）股份有限公司股票交易异常波动有关事项的问询函》的回函",
                source="cninfo",
                published_at="2026-07-06T00:00:00+08:00",
                url="https://example.com/stock-volatility-matter-inquiry-reply",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-generic-filing-risk-progress-notice",
                first_seen_at="2026-07-06T00:00:00+08:00",
                last_seen_at="2026-07-06T00:00:00+08:00",
                canonical_title="关于立案调查进展暨风险提示公告",
                summary="关于立案调查进展暨风险提示公告",
                source="cninfo",
                published_at="2026-07-06T00:00:00+08:00",
                url="https://example.com/generic-filing-risk-progress-notice",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stock-volatility-matter-inquiry-reply",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-generic-filing-risk-progress-notice",
                direction="bearish",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "股票交易异常波动有关事项的问询函" not in output
    assert "立案调查进展暨风险提示公告" not in output


def test_audit_suspicious_skips_exchange_litigation_progress_and_dishonest_person_notices(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
                event_id="event-szse-generic-litigation-progress",
                first_seen_at="2026-04-18T00:00:00+08:00",
                last_seen_at="2026-04-18T00:00:00+08:00",
                canonical_title="ST中迪：中迪投资关于公司全资子公司重庆中美恒置业有限公司诉讼进展公告",
                summary="summary",
                source="szse",
                published_at="2026-04-18T00:00:00+08:00",
                url="https://example.com/szse-generic-litigation-progress",
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
                event_id="event-szse-subsidiary-bank-account-funds-unfreeze",
                first_seen_at="2026-07-08T00:00:00+08:00",
                last_seen_at="2026-07-08T00:00:00+08:00",
                canonical_title="三羊马：关于控股子公司部分银行账户资金解除冻结的公告",
                summary="三羊马：关于控股子公司部分银行账户资金解除冻结的公告",
                source="szse",
                published_at="2026-07-08T00:00:00+08:00",
                url="https://example.com/szse-subsidiary-bank-account-funds-unfreeze",
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
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
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
                event_id="event-szse-generic-litigation-progress",
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
                event_id="event-szse-subsidiary-bank-account-funds-unfreeze",
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
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "合力泰：关于诉讼事项的进展暨公司部分银行账户及子公司股权解除冻结的公告" not in output
    assert "麦趣尔：关于公司被纳入失信被执行人的公告" not in output
    assert "幸福蓝海：关于累计诉讼、仲裁案件情况的公告" not in output
    assert "ST中迪：中迪投资关于公司全资子公司重庆中美恒置业有限公司诉讼进展公告" not in output
    assert "*ST美谷：关于担保事项涉及诉讼进展暨银行账户解除冻结的公告" not in output
    assert "龙大美食：关于控股股东所持公司1000万股股份被强制执行完成暨解除冻结的公告" not in output
    assert "三羊马：关于控股子公司部分银行账户资金解除冻结的公告" not in output
    assert "泰达股份：天津泰达资源循环集团股份有限公司关于重大资产出售暨关联交易问询函回复的公告" not in output


def test_audit_suspicious_skips_judicial_execution_unpledge_percent_disclosure(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-judicial-execution-unpledge-percent",
                first_seen_at="2026-05-09T00:00:00+08:00",
                last_seen_at="2026-05-09T00:00:00+08:00",
                canonical_title="欢瑞世纪：关于公司持股5%以上股东所持部分股份被司法强制执行实施结果、权益变动触及1%整数倍暨解除质押及冻结的公告",
                summary="summary",
                source="cninfo",
                published_at="2026-05-09T00:00:00+08:00",
                url="https://example.com/judicial-execution-unpledge-percent",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-judicial-execution-unpledge-percent",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "被司法强制执行实施结果" not in output


def test_audit_suspicious_skips_annual_report_inquiry_reply_and_mixed_judicial_freeze_change_notices(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-sse-annual-report-regulatory-inquiry-reply",
                first_seen_at="2026-06-06T00:00:00+08:00",
                last_seen_at="2026-06-06T00:00:00+08:00",
                canonical_title="返利网数字科技股份有限公司关于对上海证券交易所《关于返利网数字科技股份有限公司 2025 年年度报告的信息披露监管问询函》的回复公告",
                summary="返利网数字科技股份有限公司关于对上海证券交易所《关于返利网数字科技股份有限公司 2025 年年度报告的信息披露监管问询函》的回复公告",
                source="sse",
                published_at="2026-06-06T00:00:00+08:00",
                url="https://example.com/sse-annual-report-regulatory-inquiry-reply",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-szse-mixed-judicial-freeze-change",
                first_seen_at="2026-06-06T00:00:00+08:00",
                last_seen_at="2026-06-06T00:00:00+08:00",
                canonical_title="万马科技：关于股东部分股份司法拍卖完成过户登记、解除质押、解除司法再冻结及司法冻结的公告",
                summary="万马科技：关于股东部分股份司法拍卖完成过户登记、解除质押、解除司法再冻结及司法冻结的公告",
                source="szse",
                published_at="2026-06-06T00:00:00+08:00",
                url="https://example.com/szse-mixed-judicial-freeze-change",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-szse-mixed-judicial-freeze-change-percent",
                first_seen_at="2026-06-06T00:00:00+08:00",
                last_seen_at="2026-06-06T00:00:00+08:00",
                canonical_title="深水海纳：关于控股股东、实际控制人所持公司部分股份司法拍卖过户完成、股份变动触及1%整数倍暨股份质押与冻结变动情况的公告",
                summary="深水海纳：关于控股股东、实际控制人所持公司部分股份司法拍卖过户完成、股份变动触及1%整数倍暨股份质押与冻结变动情况的公告",
                source="szse",
                published_at="2026-06-06T00:00:00+08:00",
                url="https://example.com/szse-mixed-judicial-freeze-change-percent",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-cninfo-keep-litigation",
                first_seen_at="2026-06-06T00:00:00+08:00",
                last_seen_at="2026-06-06T00:00:00+08:00",
                canonical_title="正平股份关于公司及子公司诉讼事项进展及新增诉讼事项的公告",
                summary="正平股份关于公司及子公司诉讼事项进展及新增诉讼事项的公告",
                source="cninfo",
                published_at="2026-06-06T00:00:00+08:00",
                url="https://example.com/cninfo-keep-litigation",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-stcn-keep-strategic-investment",
                first_seen_at="2026-06-06T21:30:34+08:00",
                last_seen_at="2026-06-06T21:30:34+08:00",
                canonical_title="赛意信息战略投资七号智算 健全企业全栈AI业务布局",
                summary="人民财讯6月6日电，记者获悉，近日，赛意信息与广东七号智算技术有限公司签署战略投资协议，并已完成工商股权变更登记，公司正式成为七号智算在册股东。",
                source="stcn",
                published_at="2026-06-06T21:30:34+08:00",
                url="https://example.com/stcn-keep-strategic-investment",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-sse-annual-report-regulatory-inquiry-reply",
                direction="neutral",
                impact_score=78.5,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-szse-mixed-judicial-freeze-change",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-szse-mixed-judicial-freeze-change-percent",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-cninfo-keep-litigation",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-stcn-keep-strategic-investment",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=2" in output
    assert "返利网数字科技股份有限公司关于对上海证券交易所《关于返利网数字科技股份有限公司 2025 年年度报告的信息披露监管问询函》的回复公告" not in output
    assert "万马科技：关于股东部分股份司法拍卖完成过户登记、解除质押、解除司法再冻结及司法冻结的公告" not in output
    assert "深水海纳：关于控股股东、实际控制人所持公司部分股份司法拍卖过户完成、股份变动触及1%整数倍暨股份质押与冻结变动情况的公告" not in output
    assert "正平股份关于公司及子公司诉讼事项进展及新增诉讼事项的公告" in output
    assert "赛意信息战略投资七号智算 健全企业全栈AI业务布局" in output


def test_audit_suspicious_skips_exchange_major_litigation_and_filing_progress_notices(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
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
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "关于控股子公司提起诉讼的进展公告" not in output
    assert "长药退：重大诉讼公告" not in output


def test_audit_suspicious_skips_exchange_short_litigation_material_notices(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-szse-new-litigation-short-notice",
                first_seen_at="2026-05-14T00:00:00+08:00",
                last_seen_at="2026-05-14T00:00:00+08:00",
                canonical_title="*ST海源：关于新增诉讼的公告",
                summary="*ST海源：关于新增诉讼的公告",
                source="szse",
                published_at="2026-05-14T00:00:00+08:00",
                url="https://example.com/szse-new-litigation-short-notice",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-szse-filed-litigation-short-notice",
                first_seen_at="2026-05-14T00:00:00+08:00",
                last_seen_at="2026-05-14T00:00:00+08:00",
                canonical_title="海南海药：关于公司提起诉讼的公告",
                summary="海南海药：关于公司提起诉讼的公告",
                source="szse",
                published_at="2026-05-14T00:00:00+08:00",
                url="https://example.com/szse-filed-litigation-short-notice",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-szse-new-litigation-short-notice",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-szse-filed-litigation-short-notice",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "*ST海源：关于新增诉讼的公告" not in output
    assert "海南海药：关于公司提起诉讼的公告" not in output


def test_audit_suspicious_skips_exchange_waiting_freeze_notice(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-szse-share-freeze-waiting",
                direction="neutral",
                impact_score=78.5,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "关于持股5%以上股东及其一致行动人股份被轮候冻结的公告" not in output


def test_audit_suspicious_skips_fundraising_account_freeze_material_notice(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-sse-fundraising-account-freeze",
                first_seen_at="2026-05-14T00:00:00+08:00",
                last_seen_at="2026-05-14T00:00:00+08:00",
                canonical_title="联美量子股份有限公司关于子公司募集资金账户被冻结的公告",
                summary="联美量子股份有限公司关于子公司募集资金账户被冻结的公告",
                source="sse",
                published_at="2026-05-14T00:00:00+08:00",
                url="https://example.com/sse-fundraising-account-freeze",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-sse-fundraising-account-freeze",
                direction="neutral",
                impact_score=78.5,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "联美量子股份有限公司关于子公司募集资金账户被冻结的公告" not in output


def test_audit_suspicious_skips_bank_account_partial_fund_freeze_material_notice(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-bank-account-partial-fund-freeze",
                first_seen_at="2026-05-22T00:00:00+08:00",
                last_seen_at="2026-05-22T00:00:00+08:00",
                canonical_title="关于公司银行账户部分资金被冻结的公告",
                summary="关于公司银行账户部分资金被冻结的公告",
                source="cninfo",
                published_at="2026-05-22T00:00:00+08:00",
                url="https://example.com/cninfo-bank-account-partial-fund-freeze",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-bank-account-partial-fund-freeze",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "关于公司银行账户部分资金被冻结的公告" not in output


def test_audit_suspicious_skips_company_partial_bank_account_freeze_material_notice(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-company-partial-bank-account-freeze",
                first_seen_at="2026-06-17T00:00:00+08:00",
                last_seen_at="2026-06-17T00:00:00+08:00",
                canonical_title="永安林业：关于公司部分银行账户被冻结的公告",
                summary="永安林业：关于公司部分银行账户被冻结的公告",
                source="cninfo",
                published_at="2026-06-17T00:00:00+08:00",
                url="https://example.com/cninfo-company-partial-bank-account-freeze",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-company-partial-bank-account-freeze",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "永安林业：关于公司部分银行账户被冻结的公告" not in output


def test_audit_suspicious_skips_mixed_debt_overdue_and_bank_account_freeze_material_notice(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-szse-mixed-debt-overdue-bank-freeze",
                first_seen_at="2026-05-23T00:00:00+08:00",
                last_seen_at="2026-05-23T00:00:00+08:00",
                canonical_title="ST三木：关于公司部分债务逾期和部分银行账户被冻结的公告",
                summary="ST三木：关于公司部分债务逾期和部分银行账户被冻结的公告",
                source="szse",
                published_at="2026-05-23T00:00:00+08:00",
                url="https://example.com/szse-mixed-debt-overdue-bank-freeze",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-szse-mixed-debt-overdue-bank-freeze",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "ST三木：关于公司部分债务逾期和部分银行账户被冻结的公告" not in output


def test_audit_suspicious_skips_shareholder_partial_share_freeze_material_notice(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-sse-shareholder-partial-share-freeze",
                first_seen_at="2026-05-20T00:00:00+08:00",
                last_seen_at="2026-05-20T00:00:00+08:00",
                canonical_title="中农发种业集团股份有限公司关于股东所持部分股份冻结的公告",
                summary="中农发种业集团股份有限公司关于股东所持部分股份冻结的公告",
                source="sse",
                published_at="2026-05-20T00:00:00+08:00",
                url="https://example.com/sse-shareholder-partial-share-freeze",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-sse-shareholder-partial-share-freeze",
                direction="neutral",
                impact_score=78.5,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "中农发种业集团股份有限公司关于股东所持部分股份冻结的公告" not in output


def test_audit_suspicious_skips_control_share_freeze_notice(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-control-share-freeze",
                first_seen_at="2026-05-26T00:00:00+08:00",
                last_seen_at="2026-05-26T00:00:00+08:00",
                canonical_title="西安曲江文化旅游股份有限公司关于控股股东部分股份冻结公告",
                summary="西安曲江文化旅游股份有限公司关于控股股东部分股份冻结公告",
                source="cninfo",
                published_at="2026-05-26T00:00:00+08:00",
                url="https://www.cninfo.com.cn/new/disclosure/detail?stockCode=600706&announcementId=1225329931&orgId=gssh0600706&announcementTime=2026-05-26",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-control-share-freeze",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "西安曲江文化旅游股份有限公司关于控股股东部分股份冻结公告" not in output


def test_audit_suspicious_skips_frozen_share_passive_reduction_plan_notice(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-sse-frozen-share-passive-reduction-plan",
                first_seen_at="2026-05-25T00:00:00+08:00",
                last_seen_at="2026-05-25T00:00:00+08:00",
                canonical_title="上海皓元医药股份有限公司关于股东冻结股份被动减持计划公告",
                summary="上海皓元医药股份有限公司关于股东冻结股份被动减持计划公告",
                source="sse",
                published_at="2026-05-25T00:00:00+08:00",
                url="https://example.com/sse-frozen-share-passive-reduction-plan",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-sse-frozen-share-passive-reduction-plan",
                direction="neutral",
                impact_score=78.5,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "上海皓元医药股份有限公司关于股东冻结股份被动减持计划公告" not in output


def test_audit_suspicious_skips_convertible_bond_inquiry_reply_revision(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cb-inquiry-reply-revision",
                first_seen_at="2026-04-14T00:00:00+08:00",
                last_seen_at="2026-04-14T00:00:00+08:00",
                canonical_title="三鑫医疗：关于江西三鑫医疗科技股份有限公司申请向不特定对象发行可转换公司债券的审核问询函之回复（修订稿）",
                summary="summary",
                source="szse",
                published_at="2026-04-14T00:00:00+08:00",
                url="https://example.com/cb-inquiry-reply-revision",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cb-inquiry-reply-revision",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "三鑫医疗：关于江西三鑫医疗科技股份有限公司申请向不特定对象发行可转换公司债券的审核问询函之回复（修订稿）" not in output


def test_audit_suspicious_skips_financing_inquiry_reply_material(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
                event_id="event-directed-offering-inquiry-update",
                first_seen_at="2026-04-30T00:00:00+08:00",
                last_seen_at="2026-04-30T00:00:00+08:00",
                canonical_title="盈趣科技：关于向特定对象发行股票的审核问询函回复等文件更新的提示性公告",
                summary="summary",
                source="szse",
                published_at="2026-04-30T00:00:00+08:00",
                url="https://example.com/directed-offering-inquiry-update",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-directed-offering-accounting-explanation",
                first_seen_at="2026-04-30T00:00:00+08:00",
                last_seen_at="2026-04-30T00:00:00+08:00",
                canonical_title="盈趣科技：容诚会计师事务所（特殊普通合伙）关于厦门盈趣科技股份有限公司申请向特定对象发行股票的审核问询函中有关财务会计问题的专项说明（修订稿）（豁免版）",
                summary="summary",
                source="szse",
                published_at="2026-04-30T00:00:00+08:00",
                url="https://example.com/directed-offering-accounting-explanation",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-financing-inquiry-reply",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-directed-offering-inquiry-update",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-directed-offering-accounting-explanation",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "亿道信息：深圳市亿道信息股份有限公司关于深圳证券交易所" not in output
    assert "盈趣科技：关于向特定对象发行股票的审核问询函回复等文件更新的提示性公告" not in output
    assert "盈趣科技：容诚会计师事务所" not in output


def test_audit_suspicious_skips_financing_inquiry_financial_matter_explanation(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-directed-offering-financial-matter-explanation",
                first_seen_at="2026-05-09T00:00:00+08:00",
                last_seen_at="2026-05-09T00:00:00+08:00",
                canonical_title="某公司：会计师事务所关于某公司申请向特定对象发行股票的审核问询函中有关财务事项的说明",
                summary="summary",
                source="szse",
                published_at="2026-05-09T00:00:00+08:00",
                url="https://example.com/directed-offering-financial-matter-explanation",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-directed-offering-financial-matter-explanation",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "审核问询函中有关财务事项的说明" not in output


def test_audit_suspicious_skips_cninfo_restructuring_financial_matter_explanation(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-restructuring-financial-matter-explanation",
                first_seen_at="2026-05-27T00:00:00+08:00",
                last_seen_at="2026-05-27T00:00:00+08:00",
                canonical_title="天健会计师事务所（特殊普通合伙）关于永杰新材料股份有限公司重大资产重组草案的问询函中有关财务事项的说明",
                summary="summary",
                source="cninfo",
                published_at="2026-05-27T00:00:00+08:00",
                url="https://example.com/cninfo-restructuring-financial-matter-explanation",
                event_type="hard_event",
                event_subtype="acquisition_restructuring",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-restructuring-financial-matter-explanation",
                direction="bullish",
                impact_score=80.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "问询函中有关财务事项的说明" not in output


def test_audit_suspicious_skips_directed_a_share_offering_inquiry_reply_material(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-directed-a-share-offering-inquiry-reply",
                first_seen_at="2026-05-22T00:00:00+08:00",
                last_seen_at="2026-05-22T00:00:00+08:00",
                canonical_title="关于珠海冠宇电池股份有限公司2026年度向特定对象发行A股股票申请文件审核问询函的回复",
                summary="关于珠海冠宇电池股份有限公司2026年度向特定对象发行A股股票申请文件审核问询函的回复",
                source="cninfo",
                published_at="2026-05-22T00:00:00+08:00",
                url="https://example.com/directed-a-share-offering-inquiry-reply",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-directed-a-share-offering-inquiry-reply",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "关于珠海冠宇电池股份有限公司2026年度向特定对象发行A股股票申请文件审核问询函的回复" not in output


def test_audit_suspicious_skips_current_exchange_inquiry_material_noise(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stock-price-investment-inquiry",
                first_seen_at="2026-05-21T00:00:00+08:00",
                last_seen_at="2026-05-21T00:00:00+08:00",
                canonical_title="中国高科关于收到上海证券交易所《关于中国高科对外投资及股价波动事项的问询函》的公告",
                summary="summary",
                source="cninfo",
                published_at="2026-05-21T00:00:00+08:00",
                url="https://example.com/stock-price-investment-inquiry",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-financing-inquiry-financial-matter-explanation",
                first_seen_at="2026-05-21T00:00:00+08:00",
                last_seen_at="2026-05-21T00:00:00+08:00",
                canonical_title="百通能源：大华会计师事务所（特殊普通合伙）关于江西百通能源股份有限公司申请向特定对象发行股票审核问询函有关财务事项的说明",
                summary="summary",
                source="szse",
                published_at="2026-05-21T00:00:00+08:00",
                url="https://example.com/financing-inquiry-financial-matter-explanation",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-real-investigation-risk",
                first_seen_at="2026-05-21T00:00:00+08:00",
                last_seen_at="2026-05-21T00:00:00+08:00",
                canonical_title="佳通轮胎披露收到中国证监会立案告知书",
                summary="summary",
                source="cninfo",
                published_at="2026-05-21T00:00:00+08:00",
                url="https://example.com/real-investigation-risk",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stock-price-investment-inquiry",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-financing-inquiry-financial-matter-explanation",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-real-investigation-risk",
                direction="bearish",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=1" in output
    assert "股价波动事项的问询函" not in output
    assert "审核问询函有关财务事项的说明" not in output
    assert "佳通轮胎披露收到中国证监会立案告知书" in output


def test_audit_suspicious_skips_major_asset_purchase_inquiry_reply_material(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-major-asset-purchase-inquiry-reply",
                first_seen_at="2026-07-14T00:00:00+08:00",
                last_seen_at="2026-07-14T00:00:00+08:00",
                canonical_title="恒尚节能：关于上海证券交易所《关于对江苏恒尚节能科技股份有限公司重大资产购买预案信息披露的问询函》的回复公告",
                summary="恒尚节能：关于上海证券交易所《关于对江苏恒尚节能科技股份有限公司重大资产购买预案信息披露的问询函》的回复公告",
                source="cninfo",
                published_at="2026-07-14T00:00:00+08:00",
                url="https://example.com/major-asset-purchase-inquiry-reply",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-real-risk",
                first_seen_at="2026-07-14T00:00:00+08:00",
                last_seen_at="2026-07-14T00:00:00+08:00",
                canonical_title="佳通轮胎披露收到中国证监会立案告知书",
                summary="佳通轮胎披露收到中国证监会立案告知书。",
                source="cninfo",
                published_at="2026-07-14T00:00:00+08:00",
                url="https://example.com/real-risk",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-major-asset-purchase-inquiry-reply",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-real-risk",
                direction="bearish",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=1" in output
    assert "重大资产购买预案信息披露的问询函" not in output
    assert "佳通轮胎披露收到中国证监会立案告知书" in output


def test_audit_suspicious_skips_judicial_unfreeze_disclosure(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-judicial-unfreeze",
                first_seen_at="2026-04-16T00:00:00+08:00",
                last_seen_at="2026-04-16T00:00:00+08:00",
                canonical_title="居然智家：关于公司原实际控制人所持公司股份解除司法冻结的公告",
                summary="summary",
                source="szse",
                published_at="2026-04-16T00:00:00+08:00",
                url="https://example.com/judicial-unfreeze",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-judicial-unfreeze",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "解除司法冻结" not in output


def test_audit_suspicious_skips_major_litigation_disclosure(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-major-litigation",
                first_seen_at="2026-04-16T00:00:00+08:00",
                last_seen_at="2026-04-16T00:00:00+08:00",
                canonical_title="重大诉讼的公告",
                summary="summary",
                source="sse",
                published_at="2026-04-16T00:00:00+08:00",
                url="https://example.com/major-litigation",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-major-litigation",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "重大诉讼的公告" not in output


def test_audit_suspicious_skips_major_litigation_arbitration_progress_disclosure(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-major-litigation-arbitration-progress",
                first_seen_at="2026-04-16T00:00:00+08:00",
                last_seen_at="2026-04-16T00:00:00+08:00",
                canonical_title="中化岩土：关于重大诉讼、仲裁情况进展的公告",
                summary="summary",
                source="szse",
                published_at="2026-04-16T00:00:00+08:00",
                url="https://example.com/major-litigation-arbitration-progress",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-major-litigation-arbitration-progress",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "中化岩土：关于重大诉讼、仲裁情况进展的公告" not in output


def test_audit_suspicious_skips_litigation_progress_disclosure_with_company_name(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-litigation-progress-with-company-name",
                first_seen_at="2026-07-02T00:00:00+08:00",
                last_seen_at="2026-07-02T00:00:00+08:00",
                canonical_title="江苏澄星磷化工股份有限公司关于诉讼的进展公告",
                summary="江苏澄星磷化工股份有限公司关于诉讼的进展公告",
                source="sse",
                published_at="2026-07-02T00:00:00+08:00",
                url="https://example.com/sse-litigation-progress-with-company-name",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-litigation-progress-with-company-name",
                direction="neutral",
                impact_score=78.5,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "江苏澄星磷化工股份有限公司关于诉讼的进展公告" not in output


def test_audit_suspicious_skips_subsidiary_arbitration_progress_disclosure(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-subsidiary-arbitration-progress",
                first_seen_at="2026-05-07T00:00:00+08:00",
                last_seen_at="2026-05-07T00:00:00+08:00",
                canonical_title="关于全资子公司仲裁事项的进展公告",
                summary="关于全资子公司仲裁事项的进展公告",
                source="sse",
                published_at="2026-05-07T00:00:00+08:00",
                url="https://example.com/subsidiary-arbitration-progress",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-subsidiary-arbitration-progress",
                direction="neutral",
                impact_score=78.5,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "关于全资子公司仲裁事项的进展公告" not in output


def test_audit_suspicious_skips_arbitration_application_progress_disclosure(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-arbitration-application-progress",
                first_seen_at="2026-05-09T00:00:00+08:00",
                last_seen_at="2026-05-09T00:00:00+08:00",
                canonical_title="某公司：关于申请仲裁的进展公告",
                summary="关于申请仲裁的进展公告",
                source="szse",
                published_at="2026-05-09T00:00:00+08:00",
                url="https://example.com/arbitration-application-progress",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-arbitration-application-progress",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "关于申请仲裁的进展公告" not in output


def test_audit_suspicious_skips_subsidiary_arbitration_filing_disclosure(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-szse-subsidiary-arbitration-filing",
                first_seen_at="2026-05-22T00:00:00+08:00",
                last_seen_at="2026-05-22T00:00:00+08:00",
                canonical_title="ST棕榈：关于子公司提起仲裁的公告",
                summary="ST棕榈：关于子公司提起仲裁的公告",
                source="szse",
                published_at="2026-05-22T00:00:00+08:00",
                url="https://example.com/szse-subsidiary-arbitration-filing",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-szse-subsidiary-arbitration-filing",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "ST棕榈：关于子公司提起仲裁的公告" not in output


def test_audit_suspicious_skips_arbitration_progress_disclosure_without_substantive_detail(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-sse-arbitration-progress-disclosure",
                first_seen_at="2026-05-23T00:00:00+08:00",
                last_seen_at="2026-05-23T00:00:00+08:00",
                canonical_title="国电南自关于仲裁进展的公告",
                summary="国电南自关于仲裁进展的公告",
                source="sse",
                published_at="2026-05-23T00:00:00+08:00",
                url="https://example.com/sse-arbitration-progress-disclosure",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-sse-arbitration-progress-disclosure",
                direction="neutral",
                impact_score=78.5,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "国电南自关于仲裁进展的公告" not in output


def test_audit_suspicious_skips_cumulative_new_litigation_arbitration_disclosure(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cumulative-new-litigation",
                first_seen_at="2026-04-29T00:00:00+08:00",
                last_seen_at="2026-04-29T00:00:00+08:00",
                canonical_title="雅博股份：关于累计新增诉讼、仲裁情况的公告",
                summary="summary",
                source="szse",
                published_at="2026-04-29T00:00:00+08:00",
                url="https://example.com/cumulative-new-litigation",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cumulative-new-litigation",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "雅博股份：关于累计新增诉讼、仲裁情况的公告" not in output


def test_audit_suspicious_skips_equity_sale_progress_with_litigation_disclosure(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-equity-sale-litigation-progress",
                first_seen_at="2026-04-23T00:00:00+08:00",
                last_seen_at="2026-04-23T00:00:00+08:00",
                canonical_title="山东赫达：关于出售全资子公司100%股权进展暨公司涉及诉讼事项的公告",
                summary="summary",
                source="szse",
                published_at="2026-04-23T00:00:00+08:00",
                url="https://example.com/equity-sale-litigation-progress",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-equity-sale-litigation-progress",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "山东赫达：关于出售全资子公司100%股权进展暨公司涉及诉讼事项的公告" not in output


def test_audit_suspicious_skips_commodity_market_move_with_theme(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-gold-market-move",
                first_seen_at="2026-04-14T21:39:36+08:00",
                last_seen_at="2026-04-14T21:39:36+08:00",
                canonical_title="财联社4月14日电，现货黄金向上触及4800美元，日内上涨1.28%。",
                summary="财联社4月14日电，现货黄金向上触及4800美元，日内上涨1.28%。",
                source="cls",
                published_at="2026-04-14T21:39:36+08:00",
                url="https://www.cls.cn/detail/2344033",
                event_type="fast_news",
                event_subtype="market_move",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-gold-market-move",
                direction="neutral",
                impact_score=99.3,
                reasoning="rule",
                themes=["黄金"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "现货黄金向上触及4800美元" not in output


def test_audit_suspicious_skips_stcn_central_bank_gold_reserve_brief(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-central-bank-gold-reserve-brief",
                first_seen_at="2026-07-07T16:09:37+08:00",
                last_seen_at="2026-07-07T16:09:37+08:00",
                canonical_title="中国央行连续第20个月增持黄金",
                summary="人民财讯7月7日电，据央行数据，中国6月末黄金储备报7544万盎司，5月末黄金储备报7496万盎司，为连续第20个月增持黄金。6月末外汇储备报34162.6亿美元，5月末34422.38亿美元。",
                source="stcn",
                published_at="2026-07-07T16:09:37+08:00",
                url="https://example.com/stcn-central-bank-gold-reserve-brief",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-central-bank-gold-reserve-brief",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["黄金"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "中国央行连续第20个月增持黄金" not in output


def test_audit_suspicious_skips_cls_editorial_roundup_column(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cls-editorial-roundup",
                first_seen_at="2026-04-14T22:02:15+08:00",
                last_seen_at="2026-04-14T22:02:15+08:00",
                canonical_title="【公告全知道】锂电池+PCB+芯片+固态电池+储能+数据中心！公司锂电铜箔出货量持续上升",
                summary="summary",
                source="cls",
                published_at="2026-04-14T22:02:15+08:00",
                url="https://www.cls.cn/detail/2344048",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cls-editorial-roundup",
                direction="bullish",
                impact_score=99.3,
                reasoning="rule",
                themes=["算力", "PCB", "储能", "锂电池"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "【公告全知道】锂电池+PCB+芯片+固态电池+储能+数据中心！公司锂电铜箔出货量持续上升" not in output


def test_audit_suspicious_skips_cls_general_fast_news_with_theme(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cls-global-roundup",
                first_seen_at="2026-04-15T06:31:03+08:00",
                last_seen_at="2026-04-15T06:31:03+08:00",
                canonical_title="周三你需要知道的隔夜全球要闻：以黎同意将启动直接谈判；特朗普称与伊朗会谈“可能未来两天内”举行；霍尔木兹海峡恢复部分通航 美军封锁伊朗港口持续；国际原油下挫 美股纳指十连涨",
                summary="summary",
                source="cls",
                published_at="2026-04-15T06:31:03+08:00",
                url="https://www.cls.cn/detail/2344207",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cls-global-roundup",
                direction="bullish",
                impact_score=99.3,
                reasoning="rule",
                themes=["油气"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "隔夜全球要闻" not in output


def test_audit_suspicious_skips_cls_overseas_legal_response_without_hiding_company_lawsuit(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cls-openai-apple-lawsuit-response",
                first_seen_at="2026-07-15T03:35:18+08:00",
                last_seen_at="2026-07-15T03:35:18+08:00",
                canonical_title="财联社7月15日电，OpenAI回应苹果公司的诉讼案，我们严肃对待这些指控，未发现任何证据可证明该申诉具备合理依据。",
                summary="财联社7月15日电，OpenAI回应苹果公司的诉讼案，严肃对待这些指控，未发现任何证据可证明该申诉具备合理依据。",
                source="cls",
                published_at="2026-07-15T03:35:18+08:00",
                url="https://www.cls.cn/detail/2426525",
                event_type="fast_news",
                event_subtype="company_update",
            ),
            Event(
                event_id="event-stcn-company-lawsuit",
                first_seen_at="2026-04-08T19:51:57+08:00",
                last_seen_at="2026-04-08T19:51:57+08:00",
                canonical_title="佰维存储：作为被告涉及两起侵害发明专利权纠纷案件 涉案金额合计5000万元",
                summary="佰维存储涉及两起侵害发明专利权纠纷案件。",
                source="stcn",
                published_at="2026-04-08T19:51:57+08:00",
                url="https://example.com/company-lawsuit",
                event_type="fast_news",
                event_subtype="company_update",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cls-openai-apple-lawsuit-response",
                direction="neutral",
                impact_score=74.3,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-stcn-company-lawsuit",
                direction="neutral",
                impact_score=99.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=1" in output
    assert "OpenAI回应苹果公司的诉讼案" not in output
    assert "佰维存储：作为被告涉及两起侵害发明专利权纠纷案件" in output


def test_audit_suspicious_skips_irm_legal_question_only_company_update(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-irm-legal-question-only",
                first_seen_at="2026-04-30T18:30:00+08:00",
                last_seen_at="2026-04-30T18:30:00+08:00",
                canonical_title="山石网科：董秘您好，请问公司对于未决诉讼事项的信息披露标准及会计处理政策是怎样的？对于已发生的劳动争议类案件，公司是否会按照监管规则履行相应的披露义务？",
                summary="董秘您好，请问公司对于未决诉讼事项的信息披露标准及会计处理政策是怎样的？对于已发生的劳动争议类案件，公司是否会按照监管规则履行相应的披露义务？",
                source="irm_cninfo",
                published_at="2026-04-30T18:30:00+08:00",
                url="https://example.com/irm-legal-question-only",
                event_type="fast_news",
                event_subtype="company_update",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-irm-legal-question-only",
                direction="bearish",
                impact_score=74.9,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "未决诉讼事项的信息披露标准" not in output


def test_audit_suspicious_skips_irm_legal_arbitration_follow_up_question(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-irm-legal-arbitration-follow-up-question",
                first_seen_at="2026-05-24T19:21:07+08:00",
                last_seen_at="2026-05-24T19:21:07+08:00",
                canonical_title="同有科技：董秘你好，贵司同有科技“5月22日在投资者互动平台表示，公司不存在与忆恒创源原创始人相关的仲裁案件” 请问这里的公司是指上市公司主体，还是包含了上市公司以及控股的子公司。另外如果子公司存在仲裁案件，目前案件进展如何。",
                summary="董秘你好，贵司同有科技“5月22日在投资者互动平台表示，公司不存在与忆恒创源原创始人相关的仲裁案件” 请问这里的公司是指上市公司主体，还是包含了上市公司以及控股的子公司。另外如果子公司存在仲裁案件，目前案件进展如何。",
                source="irm_cninfo",
                published_at="2026-05-24T19:21:07+08:00",
                url="https://example.com/irm-legal-arbitration-follow-up-question",
                event_type="fast_news",
                event_subtype="company_update",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-irm-legal-arbitration-follow-up-question",
                direction="neutral",
                impact_score=75.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "目前案件进展如何" not in output


def test_audit_suspicious_skips_irm_legal_arbitration_follow_up_question_with_reply_denial(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-irm-legal-arbitration-follow-up-question-reply-denial",
                first_seen_at="2026-05-27T09:00:33+08:00",
                last_seen_at="2026-05-27T09:00:33+08:00",
                canonical_title="同有科技：董秘您好， 请问贵公司的全资子公司与殷雪冰的仲裁进展如何了？这关乎到贵公司的战略运营，广大投资者很关心，请回答谢谢。",
                summary="问题：董秘您好， 请问贵公司的全资子公司与殷雪冰的仲裁进展如何了？这关乎到贵公司的战略运营，广大投资者很关心，请回答谢谢。 回复：您好，感谢您的关注！公司不存在与忆恒创源原创始人殷雪冰相关的仲裁。请您以公司在指定信息披露网站公开披露的信息为准。谢谢！",
                source="irm_cninfo",
                published_at="2026-05-27T09:00:33+08:00",
                url="https://example.com/irm-legal-arbitration-follow-up-question-reply-denial",
                event_type="fast_news",
                event_subtype="company_update",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-irm-legal-arbitration-follow-up-question-reply-denial",
                direction="neutral",
                impact_score=75.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "仲裁进展如何了" not in output


def test_audit_suspicious_skips_irm_subsidiary_risk_question(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-irm-subsidiary-risk-question",
                first_seen_at="2026-05-24T20:51:33+08:00",
                last_seen_at="2026-05-24T20:51:33+08:00",
                canonical_title="国投智能：2025年全资子公司江苏税软未达预期，计提1.82亿元商誉减值，叠加应收、存货减值，拖累全年巨亏。 今日闪崩是否与子公司再爆雷、新增大额减值、业务停滞、诉讼败诉有关？公司为何不提前预警、及时披露、充分提示风险？子公司风险是否持续恶化、无法挽回？董秘是否对子公司经营失控、风险隐瞒承担责任？投资者是否有权质疑公司资产质量、持续经营能力存在重大不确定性？",
                summary="问题：2025年全资子公司江苏税软未达预期，计提1.82亿元商誉减值，叠加应收、存货减值，拖累全年巨亏。 今日闪崩是否与子公司再爆雷、新增大额减值、业务停滞、诉讼败诉有关？公司为何不提前预警、及时披露、充分提示风险？子公司风险是否持续恶化、无法挽回？董秘是否对子公司经营失控、风险隐瞒承担责任？投资者是否有权质疑公司资产质量、持续经营能力存在重大不确定性？ 回复：您好，公司股价短期波动系行业周期、市场情绪及资金偏好等多重因素综合影响，截至目前，公司不存在您提及的相关情形。公司已严格按照会计准则及监管要求，足额计提并及时披露江苏税软相关资产减值，并在定期报告中持续提示相关经营风险，不存在未预警、隐瞒风险或应披露未披露事项。公司管理层及董秘恪尽职守，依法合规履行信息披露职责，不存在对子公司经营失控、隐瞒风险的情况。公司资产质量及持续经营能力整体稳健，相关财务数据与风险提示均已充分披露，公司将持续夯实经营基本面，切实维护全体投资者利益。感谢您的关注与支持。",
                source="irm_cninfo",
                published_at="2026-05-24T20:51:33+08:00",
                url="https://example.com/irm-subsidiary-risk-question",
                event_type="fast_news",
                event_subtype="company_update",
            )
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-irm-subsidiary-risk-question",
                direction="bullish",
                impact_score=75.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            )
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "商誉减值" not in output


def test_audit_suspicious_skips_sse_einteractive_legal_disclosure_policy_reply(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-sse-legal-disclosure-policy-reply",
                first_seen_at="2026-04-20T11:37:00+08:00",
                last_seen_at="2026-04-20T11:37:00+08:00",
                canonical_title="山石网科：董秘您好，请问公司对于未决诉讼事项的信息披露标准及会计处理政策是怎样的？对于已发生的劳动争议类案件，公司是否会按照监管规则履行相应的披露义务？",
                summary="问题：董秘您好，请问公司对于未决诉讼事项的信息披露标准及会计处理政策是怎样的？对于已发生的劳动争议类案件，公司是否会按照监管规则履行相应的披露义务？ 回复：尊敬的投资者您好，感谢对公司的关注。关于诉讼、纠纷等事项，公司严格按照《上海证券交易所科创板股票上市规则》等监管制度履行信息披露义务，内部建立法律风险常态化排查、动态跟踪评估与台账管理机制，持续完善内控体系，以规范透明的治理运作维护全体股东利益。谢谢。",
                source="sse_einteractive",
                published_at="2026-04-20T11:37:00+08:00",
                url="https://example.com/sse-legal-disclosure-policy-reply",
                event_type="fast_news",
                event_subtype="company_update",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-sse-legal-disclosure-policy-reply",
                direction="bearish",
                impact_score=74.9,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "未决诉讼事项的信息披露标准" not in output


def test_audit_suspicious_skips_sse_einteractive_mna_litigation_governance_question(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-sse-mna-litigation-governance-question",
                first_seen_at="2026-05-20T08:35:00+08:00",
                last_seen_at="2026-05-20T08:35:00+08:00",
                canonical_title="三友医疗：根据公开的信息，（2025）京73民初1406号应为北京知识产权法院的诉讼，与三友关联的是水木天蓬，也就是2025年并购重组的子公司，同时，三友控股股东与董事及法人在2025年7月至2026年3月均进行减持，请问该纠纷是否与并购重组子公司主要业务存在关联，法人是否应该回避表决",
                summary="问题：根据公开的信息，（2025）京73民初1406号应为北京知识产权法院的诉讼，与三友关联的是水木天蓬，也就是2025年并购重组的子公司，同时，三友控股股东与董事及法人在2025年7月至2026年3月均进行减持，请问该纠纷是否与并购重组子公司主要业务存在关联，法人是否应该回避表决 回复：您好，公司收购水木天蓬剩余股权事宜与公司股东减持不存在任何关联关系。收购水木事宜早已在2025年2月完成资产过户及工商变更手续。目前公司经营一切正常有序开展。感谢您的关注。",
                source="sse_einteractive",
                published_at="2026-05-20T08:35:00+08:00",
                url="https://example.com/sse-mna-litigation-governance-question",
                event_type="fast_news",
                event_subtype="company_update",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-sse-mna-litigation-governance-question",
                direction="neutral",
                impact_score=74.9,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "三友医疗：根据公开的信息" not in output


def test_audit_suspicious_skips_sse_einteractive_legal_schedule_follow_up_question(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-sse-legal-schedule-follow-up-question",
                first_seen_at="2026-05-22T18:24:00+08:00",
                last_seen_at="2026-05-22T18:24:00+08:00",
                canonical_title="东方生物：董秘您好，此前公司回复已提交简易判决动议，同时提及预计 7 月宣布开庭。特此咨询两个问题： 若判决全盘驳回 FS 全部诉讼诉求，案件理应无需再开庭审理。公司此前提示 7 月或将开庭，是目前简易判决结果尚未出具，出于谨慎口径预判，还是相关判决结果已出，偏向部分驳回 / 不予支持，暂未对外披露？ 倘若简易判决结果为驳回，原定 7 月 6 日庭审日期是否保持不变，还是法院会在7月重新确定新的开庭时间？辛苦解答，谢谢！",
                summary="问题：董秘您好，此前公司回复已提交简易判决动议，同时提及预计 7 月宣布开庭。特此咨询两个问题： 若判决全盘驳回 FS 全部诉讼诉求，案件理应无需再开庭审理。公司此前提示 7 月或将开庭，是目前简易判决结果尚未出具，出于谨慎口径预判，还是相关判决结果已出，偏向部分驳回 / 不予支持，暂未对外披露？ 倘若简易判决结果为驳回，原定 7 月 6 日庭审日期是否保持不变，还是法院会在7月重新确定新的开庭时间？辛苦解答，谢谢！ 回复：尊敬的投资者您好，该诉讼事项截至2025年年度报告及2026年第一季度报告披露日，公司方主动提起简易和总结性判决的动议，要求驳回FS的诉讼请求，简易动议结果目前尚未收到，预计将在2026年7月宣布开庭时间。关于本诉讼事项的阶段性进展，请关注公司后续相关公告，谢谢！",
                source="sse_einteractive",
                published_at="2026-05-22T18:24:00+08:00",
                url="https://example.com/sse-legal-schedule-follow-up-question",
                event_type="fast_news",
                event_subtype="company_update",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-sse-legal-schedule-follow-up-question",
                direction="bullish",
                impact_score=74.9,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "东方生物：董秘您好" not in output


def test_audit_suspicious_skips_irm_cninfo_litigation_follow_up_question(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-irm-cninfo-litigation-follow-up-question",
                first_seen_at="2026-05-26T16:15:37+08:00",
                last_seen_at="2026-05-26T16:15:37+08:00",
                canonical_title="麦克奥迪：请问：公司现在与六院的诉讼进行到什么程度了？什么时候开庭？能庭外和解吗？",
                summary="请问：公司现在与六院的诉讼进行到什么程度了？什么时候开庭？能庭外和解吗？",
                source="irm_cninfo",
                published_at="2026-05-26T16:15:37+08:00",
                url="https://irm.cninfo.com.cn/ircs/question/questionDetail?questionId=2276020588407750656",
                event_type="fast_news",
                event_subtype="company_update",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-irm-cninfo-litigation-follow-up-question",
                direction="neutral",
                impact_score=75.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "麦克奥迪：请问：公司现在与六院的诉讼进行到什么程度了？什么时候开庭？能庭外和解吗？" not in output


def test_audit_suspicious_skips_private_robot_financing_general_fast_news(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-private-robot-financing",
                first_seen_at="2026-04-29T09:24:51+08:00",
                last_seen_at="2026-04-29T09:24:51+08:00",
                canonical_title="擎天租完成数亿元Pre-A轮融资 提升平台在多城市、多场景、多品类机器人应用中的交付能力",
                summary="擎天租完成数亿元Pre-A轮融资。",
                source="stcn",
                published_at="2026-04-29T09:24:51+08:00",
                url="https://example.com/private-robot-financing",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-private-robot-financing",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["机器人"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "擎天租完成数亿元Pre-A轮融资" not in output


def test_audit_suspicious_skips_stcn_robotaxi_internal_test_general_fast_news(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-robotaxi-internal-test",
                first_seen_at="2026-07-09T11:52:35+08:00",
                last_seen_at="2026-07-09T11:52:35+08:00",
                canonical_title="小鹏Robotaxi开启内测，何小鹏称Robotaxi是小鹏迈向“机器人汽车”的重要一步",
                summary="小鹏集团召开Robotaxi业务首次全员会，并宣布正式启动员工内测。小鹏未来将聚焦整车平台、自动驾驶软件及AI能力，打造服务全球合作伙伴的Robotaxi软硬件服务商。",
                source="stcn",
                published_at="2026-07-09T11:52:35+08:00",
                url="https://www.stcn.com/article/detail/4008285.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-robotaxi-internal-test",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["机器人"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "小鹏Robotaxi开启内测" not in output


def test_audit_suspicious_skips_stcn_nev_repair_safety_standard_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-nev-repair-safety-standard",
                first_seen_at="2026-07-20T14:34:45+08:00",
                last_seen_at="2026-07-20T14:34:45+08:00",
                canonical_title="《新能源汽车维修作业安全要求》国家标准8月1日起实施",
                summary="人民财讯7月20日电，据市场监管总局消息，8月1日起，《新能源汽车维修作业安全要求》（GB/T 47439—2026）国家标准正式实施。该标准主要规定了新能源汽车维修的人员与场地、作业准备、风险排查与处置、作业流程和操作安全等要求。",
                source="stcn",
                published_at="2026-07-20T14:34:45+08:00",
                url="https://www.stcn.com/article/detail/4028968.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-nev-repair-safety-standard",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["新能源车"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "新能源汽车维修作业安全要求" not in output


def test_audit_suspicious_skips_stcn_waic_touch_robot_model_showcase(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-waic-touch-robot-model-showcase",
                first_seen_at="2026-07-18T20:24:13+08:00",
                last_seen_at="2026-07-18T20:24:13+08:00",
                canonical_title="千觉机器人首个VTLA具身触觉模型亮相世界人工智能大会",
                summary="千觉机器人在世界人工智能大会带来VTLA具身触觉模型、视触觉多模态数据集、核心数采设备与触觉传感器硬件矩阵。",
                source="stcn",
                published_at="2026-07-18T20:24:13+08:00",
                url="https://www.stcn.com/article/detail/4027332.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-waic-touch-robot-model-showcase",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["机器人"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "千觉机器人首个VTLA具身触觉模型亮相世界人工智能大会" not in output


def test_audit_suspicious_skips_stcn_waic_quadruped_robot_showcase(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-waic-quadruped-robot-showcase",
                first_seen_at="2026-07-19T10:15:23+08:00",
                last_seen_at="2026-07-19T10:15:23+08:00",
                canonical_title="广和通携手璇玑动力，提升四足机器人复杂环境连续定位能力",
                summary="人民财讯7月19日电，7月17日—20日，2026世界人工智能大会在上海举行。广和通携手璇玑动力联合展示面向行业应用的四足机器人方案。通过此次合作，璇玑动力中型轮足机器人平台可在原有复杂地形运动能力基础上，进一步获得稳定的连续定位能力支撑。",
                source="stcn",
                published_at="2026-07-19T10:15:23+08:00",
                url="https://www.stcn.com/article/detail/4027469.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-waic-quadruped-robot-showcase",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["机器人"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "广和通携手璇玑动力" not in output


def test_audit_suspicious_skips_stcn_ubtech_korea_robot_validation_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-ubtech-korea-robot-validation",
                first_seen_at="2026-07-19T18:45:32+08:00",
                last_seen_at="2026-07-19T18:45:32+08:00",
                canonical_title="优必选携手韩国伙伴，推动人形机器人落地汽车零部件制造场景",
                summary="人民财讯7月19日电，近日，优必选韩国合作伙伴德山JMR（Duksan JM Robotics，DSJMR）与韩国领先汽车零部件企业AJIN Industrial正式签署合作谅解备忘录。未来，优必选、德山JMR、AJIN Industrial将三方合作，共同推动Cruzr Y1、Walker S2等工业人形机器人在韩国首个汽车零部件生产产线的验证项目，将围绕人形机器人在汽车零部件制造领域的创新应用展开合作，共同推动人形机器人从展示验证走向真实产业场景。",
                source="stcn",
                published_at="2026-07-19T18:45:32+08:00",
                url="https://www.stcn.com/article/detail/4027696.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-ubtech-korea-robot-validation",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["机器人"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "优必选携手韩国伙伴" not in output


def test_audit_suspicious_skips_stcn_waic_compute_node_showcase(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-waic-compute-node-showcase",
                first_seen_at="2026-07-20T07:10:01+08:00",
                last_seen_at="2026-07-20T07:10:01+08:00",
                canonical_title="多家国产厂商展示超节点产品 算力竞逐各显神通",
                summary="人民财讯7月20日电，2026世界人工智能大会（WAIC）现场，国产超节点成为绝对焦点。证券时报记者在现场观察到，虽然采用的芯片、架构各有所异，但每一个有超节点方案的展台前围观、交流的人群均络绎不绝，厂商们则将一排排机柜置于展台的“C位”。这场国内首次超大规模的超节点集中展示，既是一次成果检阅，也标志着国产算力行业竞逐新阶段的开启。",
                source="stcn",
                published_at="2026-07-20T07:10:01+08:00",
                url="https://www.stcn.com/article/detail/4027926.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-waic-compute-node-showcase",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "多家国产厂商展示超节点产品" not in output


def test_audit_suspicious_skips_private_biotech_c_round_financing_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-private-biotech-c-round-financing",
                first_seen_at="2026-05-19T09:24:27+08:00",
                last_seen_at="2026-05-19T09:24:27+08:00",
                canonical_title="爱科诺生物医药宣布完成5000万美元C轮融资",
                summary="爱科诺生物医药宣布完成5000万美元C轮融资。",
                source="stcn",
                published_at="2026-05-19T09:24:27+08:00",
                url="https://example.com/private-biotech-c-round-financing",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-private-biotech-c-round-financing",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["创新药"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "爱科诺生物医药宣布完成5000万美元C轮融资" not in output


def test_audit_suspicious_skips_stcn_concept_continues_strong_limit_up_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-concept-continues-strong",
                first_seen_at="2026-07-16T10:03:00+08:00",
                last_seen_at="2026-07-16T10:03:00+08:00",
                canonical_title="创新药概念持续走强 哈药股份五连板",
                summary="创新药概念持续走强，哈药股份五连板，多只成份股涨停。",
                source="stcn",
                published_at="2026-07-16T10:03:00+08:00",
                url="https://example.com/stcn-concept-continues-strong",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-concept-continues-strong",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["创新药"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "创新药概念持续走强 哈药股份五连板" not in output


def test_audit_suspicious_skips_lawsuit_related_transaction_progress_disclosure(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-dongwang-lawsuit-related-transaction-progress",
                first_seen_at="2026-07-16T00:00:00+08:00",
                last_seen_at="2026-07-16T00:00:00+08:00",
                canonical_title="浙江东望时代科技股份有限公司关于子公司提起诉讼暨关联交易的进展公告",
                summary="浙江东望时代披露子公司提起诉讼暨关联交易的进展。",
                source="sse",
                published_at="2026-07-16T00:00:00+08:00",
                url="https://example.com/dongwang-lawsuit-related-transaction-progress",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-dongwang-lawsuit-related-transaction-progress",
                direction="neutral",
                impact_score=78.5,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "子公司提起诉讼暨关联交易的进展公告" not in output


def test_audit_suspicious_skips_stcn_fund_manager_investment_opportunity_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-fund-manager-investment-opportunity",
                first_seen_at="2026-04-21T07:37:33+08:00",
                last_seen_at="2026-04-21T07:37:33+08:00",
                canonical_title="景气度“光”芒四射 基金经理把握光通信投资机会",
                summary="人民财讯4月21日电，中流击水，“光”芒四射。AI引领的科技浪潮汹涌，算力建设如火如荼，这也映射到A股市场中。从基金投资布局情况看，光通信依然是资金竞逐的方向。",
                source="stcn",
                published_at="2026-04-21T07:37:33+08:00",
                url="https://example.com/stcn-fund-manager-investment-opportunity",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-fund-manager-investment-opportunity",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "基金经理把握光通信投资机会" not in output


def test_audit_suspicious_skips_stcn_global_capital_a_share_allocation_commentary(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-global-capital-a-share-allocation",
                first_seen_at="2026-05-29T07:25:03+08:00",
                last_seen_at="2026-05-29T07:25:03+08:00",
                canonical_title="全球资本加速拥抱中国 增配A股进入黄金窗口期",
                summary="人民财讯5月29日电，在世界宏观经济面临复杂变局的当下，全球资本都在寻找更具确定性投资价值的资产。"
                "5月28日，由深交所主办的2026全球投资者大会在深圳举行。"
                "瑞银全球金融市场部中国主管房东明表示，目前全球机构投资者对中国资产处于显著低配状态，未来五年乃至更长周期将是外资增配A股的黄金窗口期。",
                source="stcn",
                published_at="2026-05-29T07:25:03+08:00",
                url="https://example.com/stcn-global-capital-a-share-allocation",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-keep-ai-build-center",
                first_seen_at="2026-05-29T11:14:22+08:00",
                last_seen_at="2026-05-29T11:14:22+08:00",
                canonical_title="联想在天津投建新一代AI算力研发制造中心",
                summary="人民财讯5月29日电，联想集团与天津签署建设新一代AI基础设施协议，将投资建设新一代AI算力产品研发制造中心。",
                source="stcn",
                published_at="2026-05-29T11:14:22+08:00",
                url="https://example.com/keep-ai-build-center",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-global-capital-a-share-allocation",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["证券"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-keep-ai-build-center",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "全球资本加速拥抱中国 增配A股进入黄金窗口期" not in output
    assert "联想在天津投建新一代AI算力研发制造中心" in output


def test_audit_suspicious_skips_stcn_stock_screen_and_industry_observation_stories(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-compute-financing-stock-screen",
                first_seen_at="2026-05-30T08:27:41+08:00",
                last_seen_at="2026-05-30T08:27:41+08:00",
                canonical_title="12只滞涨算力股获融资客重仓",
                summary="人民财讯5月30日电，受益于科技板块的走强，今年以来算力概念股整体表现强势。"
                "从融资资金来看，74只算力概念股最新融资余额合计接近2126亿元。"
                "今年以来累计涨幅低于45%，且融资余额较去年末增幅均超过30%的算力概念股有12只，按照融资余额增幅排序。",
                source="stcn",
                published_at="2026-05-30T08:27:41+08:00",
                url="https://example.com/stcn-compute-financing-stock-screen",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-stcn-storage-lithium-price-observation",
                first_seen_at="2026-05-30T08:12:34+08:00",
                last_seen_at="2026-05-30T08:12:34+08:00",
                canonical_title="海外储能需求崛起 锂价传导机制整体顺畅",
                summary="人民财讯5月30日电，记者采访获悉，下游储能需求持续火爆，为锂价提供了坚实的基本面支撑。"
                "机构预计2026年全球储能需求增速将超过50%。在锂价高企的背景下，产业链通过价格联动、下游直采等机制整体实现了顺畅传导。（上海证券报）",
                source="stcn",
                published_at="2026-05-30T08:12:34+08:00",
                url="https://example.com/stcn-storage-lithium-price-observation",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-keep-ai-build-center",
                first_seen_at="2026-05-29T11:14:22+08:00",
                last_seen_at="2026-05-29T11:14:22+08:00",
                canonical_title="联想在天津投建新一代AI算力研发制造中心",
                summary="人民财讯5月29日电，联想集团与天津签署建设新一代AI基础设施协议，将投资建设新一代AI算力产品研发制造中心。",
                source="stcn",
                published_at="2026-05-29T11:14:22+08:00",
                url="https://example.com/keep-ai-build-center",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-compute-financing-stock-screen",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-stcn-storage-lithium-price-observation",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["储能"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-keep-ai-build-center",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "12只滞涨算力股获融资客重仓" not in output
    assert "海外储能需求崛起 锂价传导机制整体顺畅" not in output
    assert "联想在天津投建新一代AI算力研发制造中心" in output


def test_audit_suspicious_skips_stcn_charging_infra_fast_news_with_theme(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-charging-infra-fast",
                first_seen_at="2026-05-03T18:13:11+08:00",
                last_seen_at="2026-05-03T18:13:11+08:00",
                canonical_title="广汽自营充电桩突破2.5万根，覆盖全国31省213市",
                summary="2026年5月，广汽集团自营充电桩网点突破2.5万根。",
                source="stcn",
                published_at="2026-05-03T18:13:11+08:00",
                url="https://example.com/stcn-charging-infra-fast",
                event_type="fast_news",
                event_subtype="general_fast_news",
            )
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-charging-infra-fast",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["充电桩"],
                triggered=True,
            )
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "广汽自营充电桩突破2.5万根，覆盖全国31省213市" not in output


def test_audit_suspicious_skips_stcn_wti_general_fast_news_with_theme(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-wti-general-fast",
                first_seen_at="2026-05-04T14:26:33+08:00",
                last_seen_at="2026-05-04T14:26:33+08:00",
                canonical_title="国际油价持续回落 WTI原油期货价格涨幅收窄至1.1%",
                summary="财联社5月4日电，国际油价持续回落，WTI原油期货价格涨幅收窄至1.1%，市场或迎来震荡。",
                source="stcn",
                published_at="2026-05-04T14:26:33+08:00",
                url="https://example.com/stcn-wti-general-fast",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-wti-general-fast",
                direction="neutral",
                impact_score=99.0,
                reasoning="rule",
                themes=["油气"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "国际油价持续回落 WTI原油期货价格涨幅收窄至1.1%" not in output


def test_audit_suspicious_skips_current_oil_low_and_glp1_access_noise(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-crude-low",
                first_seen_at="2026-07-01T21:25:47+08:00",
                last_seen_at="2026-07-01T21:25:47+08:00",
                canonical_title="纽约原油期价盘中创2月27日以来新低",
                summary="纽约商品交易所8月交货的轻质原油期货价格盘中创2月27日以来新低。",
                source="stcn",
                published_at="2026-07-01T21:25:47+08:00",
                url="https://example.com/stcn-crude-low",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-investing-glp1-access",
                first_seen_at="2026-07-01T13:55:30+00:00",
                last_seen_at="2026-07-01T13:55:30+00:00",
                canonical_title="Analysis-Older Americans left out of costly GLP-1 craze expected to flock to new program",
                summary="Analysis-Older Americans left out of costly GLP-1 craze expected to flock to new program",
                source="investing_news",
                published_at="2026-07-01T13:55:30+00:00",
                url="https://example.com/investing-glp1-access",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-crude-low",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["油气"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-investing-glp1-access",
                direction="neutral",
                impact_score=79.6,
                reasoning="rule",
                themes=["创新药"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "纽约原油期价盘中创2月27日以来新低" not in output
    assert "Analysis-Older Americans left out" not in output


def test_audit_suspicious_skips_stcn_night_session_commodity_opening_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-night-session-commodity-open",
                first_seen_at="2026-05-12T21:48:00+08:00",
                last_seen_at="2026-05-12T21:48:00+08:00",
                canonical_title="国内商品期货夜盘开盘 液化石油气涨近3%",
                summary="国内商品期货夜盘开盘，液化石油气涨近3%。",
                source="stcn",
                published_at="2026-05-12T21:48:00+08:00",
                url="https://example.com/stcn-night-session-commodity-open",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-night-session-commodity-open",
                direction="neutral",
                impact_score=99.0,
                reasoning="rule",
                themes=["油气"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "国内商品期货夜盘开盘 液化石油气涨近3%" not in output


def test_audit_suspicious_keeps_global_index_sector_move_as_market_reference(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-global-index-sector-move-reference",
                first_seen_at="2026-05-12T22:38:14+08:00",
                last_seen_at="2026-05-12T22:38:14+08:00",
                canonical_title="纳斯达克综合指数跌逾1% 芯片半导体股票集体下跌",
                summary="纳斯达克综合指数跌逾1%，芯片半导体股票集体下跌。",
                source="stcn",
                published_at="2026-05-12T22:38:14+08:00",
                url="https://example.com/global-index-sector-move-reference",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-global-index-sector-move-reference",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "纳斯达克综合指数跌逾1% 芯片半导体股票集体下跌" not in output


def test_audit_suspicious_keeps_a_share_concept_move_as_market_reference(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-a-share-concept-move-reference",
                first_seen_at="2026-05-13T10:50:16+08:00",
                last_seen_at="2026-05-13T10:50:16+08:00",
                canonical_title="PCB概念走强 大族激光等股价创新高",
                summary="人民财讯5月13日电，PCB概念走强，大族激光、生益科技均涨停，且股价再创历史新高；快克智能涨停，鹏鼎控股、国际复材等大涨。",
                source="stcn",
                published_at="2026-05-13T10:50:16+08:00",
                url="https://example.com/a-share-concept-move-reference",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-a-share-concept-move-reference",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["PCB"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "PCB概念走强 大族激光等股价创新高" not in output


def test_audit_suspicious_keeps_a_share_concept_active_limit_up_as_market_reference(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-a-share-concept-active-reference",
                first_seen_at="2026-05-14T10:24:01+08:00",
                last_seen_at="2026-05-14T10:24:01+08:00",
                canonical_title="创新药概念活跃 昂利康2连板",
                summary="人民财讯5月14日电，创新药概念活跃，昂利康2连板，南新制药涨逾7%，广生堂涨近7%，津药药业、仟源医药、联环药业等涨幅居前。",
                source="stcn",
                published_at="2026-05-14T10:24:01+08:00",
                url="https://example.com/a-share-concept-active-reference",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-a-share-concept-active-reference",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["创新药"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "创新药概念活跃 昂利康2连板" not in output


def test_audit_suspicious_skips_stcn_concept_rebound_with_theme(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-concept-rebound-reference",
                first_seen_at="2026-05-26T14:54:38+08:00",
                last_seen_at="2026-05-26T14:54:38+08:00",
                canonical_title="先进封装概念震荡回升 长电科技2连板",
                summary="人民财讯5月26日电，先进封装概念震荡回升，长电科技2连板，通富微电触及涨停，华天科技、生益科技、三佳科技此前涨停，胜科纳米、甬矽电子、联瑞新材、颀中科技涨幅居前。",
                source="stcn",
                published_at="2026-05-26T14:54:38+08:00",
                url="https://www.stcn.com/article/detail/3927581.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-concept-rebound-reference",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "先进封装概念震荡回升 长电科技2连板" not in output


def test_audit_suspicious_keeps_a_share_sector_strengthening_as_market_reference(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-a-share-sector-strengthening-reference",
                first_seen_at="2026-05-14T13:25:05+08:00",
                last_seen_at="2026-05-14T13:25:05+08:00",
                canonical_title="半导体板块震荡走强 天岳先进涨近20%",
                summary="人民财讯5月14日电，半导体板块震荡走强，天岳先进涨近20%，晶丰明源涨逾12%，燕东微涨逾10%，晶合集成、卓胜微等涨幅居前。",
                source="stcn",
                published_at="2026-05-14T13:25:05+08:00",
                url="https://example.com/a-share-sector-strengthening-reference",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-a-share-sector-strengthening-reference",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "半导体板块震荡走强 天岳先进涨近20%" not in output


def test_audit_suspicious_keeps_a_share_index_sector_active_as_market_reference(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-a-share-index-sector-active-reference",
                first_seen_at="2026-05-21T10:10:41+08:00",
                last_seen_at="2026-05-21T10:10:41+08:00",
                canonical_title="创业板指、深证成指均涨逾2% 半导体、券商等板块活跃",
                summary="人民财讯5月21日电，创业板指、深证成指均涨逾2%，半导体、券商等板块活跃。",
                source="stcn",
                published_at="2026-05-21T10:10:41+08:00",
                url="https://example.com/a-share-index-sector-active-reference",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-a-share-index-sector-active-reference",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "创业板指、深证成指均涨逾2% 半导体、券商等板块活跃" not in output


def test_audit_suspicious_keeps_hk_ai_application_move_as_market_reference(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-hk-ai-application-move-reference",
                first_seen_at="2026-05-13T14:17:12+08:00",
                last_seen_at="2026-05-13T14:17:12+08:00",
                canonical_title="港股AI应用股拉升 智谱涨逾15%",
                summary="人民财讯5月13日电，港股AI应用股拉升，智谱涨逾15%，MINIMAX-W涨逾11%。",
                source="stcn",
                published_at="2026-05-13T14:17:12+08:00",
                url="https://example.com/hk-ai-application-move-reference",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-hk-ai-application-move-reference",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["AI应用"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "港股AI应用股拉升 智谱涨逾15%" not in output


def test_audit_suspicious_skips_stcn_brent_fast_news_with_theme(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-brent-fast",
                first_seen_at="2026-05-05T08:57:22+08:00",
                last_seen_at="2026-05-05T08:57:22+08:00",
                canonical_title="国际原油短线快速拉升 布伦特原油期货涨逾5%",
                summary="财联社5月5日电，国际原油短线快速拉升，布伦特原油期货涨逾5%，市场震荡回升。",
                source="stcn",
                published_at="2026-05-05T08:57:22+08:00",
                url="https://example.com/stcn-brent-fast",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-brent-fast",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["油气"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "国际原油短线快速拉升 布伦特原油期货涨逾5%" not in output


def test_audit_suspicious_skips_stcn_precious_metal_spot_move_with_theme(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-spot-silver-fast",
                first_seen_at="2026-05-08T07:25:32+08:00",
                last_seen_at="2026-05-08T07:25:32+08:00",
                canonical_title="现货白银震荡走高，涨近1%",
                summary="人民财讯5月8日电，现货白银震荡走高，涨近1%；现货黄金涨约0.25%。",
                source="stcn",
                published_at="2026-05-08T07:25:32+08:00",
                url="https://example.com/stcn-spot-silver-fast",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-spot-silver-fast",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["黄金"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "现货白银震荡走高，涨近1%" not in output


def test_audit_suspicious_skips_stcn_phase_one_clinical_trial_start(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-phase-one-clinical-trial-start",
                first_seen_at="2026-07-04T08:38:26+08:00",
                last_seen_at="2026-07-04T08:38:26+08:00",
                canonical_title="新华制药抗肺动脉高压1类创新药LXH-1211片I期临床试验启动",
                summary=(
                    "人民财讯7月4日电，7月3日，新华制药抗肺动脉高压1类创新药LXH-1211片I期临床试验正式启动。"
                    "LXH-1211为新华制药与中南大学联合研发的1类创新药，是针对肺动脉高压的临床表现和疾病病理本质"
                    "（血管重构导致的纤维化）而设计的全新结构化合物。临床前研究显示，LXH-1211具有双重作用机制。"
                ),
                source="stcn",
                published_at="2026-07-04T08:38:26+08:00",
                url="https://www.stcn.com/article/detail/3998353.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-phase-one-clinical-trial-start",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["创新药"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "新华制药抗肺动脉高压1类创新药LXH-1211片I期临床试验启动" not in output


def test_audit_suspicious_skips_stcn_industry_prosperity_story(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-industry-prosperity",
                first_seen_at="2026-04-21T07:42:50+08:00",
                last_seen_at="2026-04-21T07:42:50+08:00",
                canonical_title="一季度锂电行业高景气延续 储能成重点布局方向",
                summary="人民财讯4月21日电，近期，锂电产业链上市公司纷纷披露一季度业绩预告或正式业绩报告。整体来看，锂电赛道维持高景气度。机构分析认为，在市场需求旺盛的背景下，锂电池产业链多个细分环节有望获益。",
                source="stcn",
                published_at="2026-04-21T07:42:50+08:00",
                url="https://example.com/stcn-industry-prosperity",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-industry-prosperity",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["储能", "锂电池"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "一季度锂电行业高景气延续 储能成重点布局方向" not in output


def test_audit_suspicious_skips_cls_market_roundup_and_limitup_digest(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cls-close-roundup",
                first_seen_at="2026-04-17T15:01:54+08:00",
                last_seen_at="2026-04-17T15:01:54+08:00",
                canonical_title="收评：创业板指涨超1%再创近11年新高 算力硬件方向持续爆发",
                summary="summary",
                source="cls",
                published_at="2026-04-17T15:01:54+08:00",
                url="https://www.cls.cn/detail/2347306",
                event_type="fast_news",
                event_subtype="market_move",
            ),
            Event(
                event_id="event-cls-limit-up-digest",
                first_seen_at="2026-04-17T15:13:25+08:00",
                last_seen_at="2026-04-17T15:13:25+08:00",
                canonical_title="4月17日涨停分析",
                summary="summary",
                source="cls",
                published_at="2026-04-17T15:13:25+08:00",
                url="https://www.cls.cn/detail/2347335",
                event_type="fast_news",
                event_subtype="market_move",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cls-close-roundup",
                direction="neutral",
                impact_score=99.3,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-cls-limit-up-digest",
                direction="neutral",
                impact_score=99.3,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "收评：创业板指涨超1%再创近11年新高 算力硬件方向持续爆发" not in output
    assert "4月17日涨停分析" not in output


def test_audit_suspicious_skips_stcn_robot_half_marathon_story(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-robot-half-marathon",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["机器人"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "“闪电”完成2026人形机器人半马" not in output


def test_audit_suspicious_skips_stcn_robot_half_marathon_supply_chain_story(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-robot-half-marathon-supply-chain",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["机器人"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "荣耀机器人半马夺冠 领益智造批量交付其全套金属结构件等产品" not in output


def test_audit_suspicious_skips_stcn_public_affairs_conference_story(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-fujian-cultural-tourism-conference",
                direction="bullish",
                impact_score=99.0,
                reasoning="rule",
                themes=["文旅"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "2026年福建省文旅经济发展大会召开" not in output


def test_audit_suspicious_skips_stcn_public_affairs_leader_visit_story(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-hainan-spaceport-public-affairs",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["商业航天"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "刘小明在海南商业航天发射场看望慰问“五一”假期在岗一线劳动者并调研重点工作进展情况" not in output


def test_audit_suspicious_skips_stcn_governor_industry_research_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-governor-ic-research",
                first_seen_at="2026-07-13T22:44:50+08:00",
                last_seen_at="2026-07-13T22:44:50+08:00",
                canonical_title="浙江省省长刘捷在宁波专题调研集成电路产业发展工作",
                summary="人民财讯7月13日电，据浙江日报，13日下午，浙江省委副书记、省长刘捷在宁波专题调研集成电路产业发展工作。刘捷在调研中强调，推动人工智能及算力、芯片、智能装备等相关产业高质量发展。",
                source="stcn",
                published_at="2026-07-13T22:44:50+08:00",
                url="https://example.com/stcn-governor-ic-research",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-keep-stcn-cooperation",
                first_seen_at="2026-07-13T21:30:57+08:00",
                last_seen_at="2026-07-13T21:30:57+08:00",
                canonical_title="江苏省政府与中科曙光签署战略合作协议",
                summary="江苏省政府与中科曙光在南京签署战略合作协议。",
                source="stcn",
                published_at="2026-07-13T21:30:57+08:00",
                url="https://example.com/stcn-cooperation",
                event_type="fast_news",
                event_subtype="cooperation_agreement",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-governor-ic-research",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-keep-stcn-cooperation",
                direction="bullish",
                impact_score=99.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "浙江省省长刘捷在宁波专题调研集成电路产业发展工作" not in output


def test_audit_suspicious_skips_stcn_ic_enterprise_exchange_story(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-wuhan-ic-enterprise-exchange",
                first_seen_at="2026-05-25T07:56:19+08:00",
                last_seen_at="2026-05-25T07:56:19+08:00",
                canonical_title="武汉市委书记盛阅春与集成电路领域企业家座谈",
                summary="人民财讯5月25日电，据长江日报，5月24日，湖北省委常委、武汉市委书记盛阅春与省内外的集成电路领域企业家座谈交流、共话合作。",
                source="stcn",
                published_at="2026-05-25T07:56:19+08:00",
                url="https://www.stcn.com/article/detail/3924630.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-wuhan-ic-enterprise-exchange",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "武汉市委书记盛阅春与集成电路领域企业家座谈" not in output


def test_audit_suspicious_skips_stcn_oil_storage_expert_guidance_service_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-oil-storage-expert-guidance-service",
                first_seen_at="2026-05-25T12:37:40+08:00",
                last_seen_at="2026-05-25T12:37:40+08:00",
                canonical_title="应急管理部启动2026年油气储存企业部级专家指导服务",
                summary="人民财讯5月25日电，为深入推进化工和危险化学品安全生产治本攻坚三年行动，应急管理部近日启动2026年油气储存企业部级专家指导服务。",
                source="stcn",
                published_at="2026-05-25T12:37:40+08:00",
                url="https://www.stcn.com/article/detail/3925214.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-oil-storage-expert-guidance-service",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["油气"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "应急管理部启动2026年油气储存企业部级专家指导服务" not in output


def test_audit_suspicious_skips_stcn_nev_safety_management_video_meeting(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-nev-safety-management-meeting",
                first_seen_at="2026-05-14T18:50:52+08:00",
                last_seen_at="2026-05-14T18:50:52+08:00",
                canonical_title="三部门召开加强新能源汽车安全管理工作视频会",
                summary="三部门召开加强新能源汽车安全管理工作视频会，部署新能源汽车安全管理相关工作。",
                source="stcn",
                published_at="2026-05-14T18:50:52+08:00",
                url="https://example.com/stcn-nev-safety-management-meeting",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-nev-safety-management-meeting",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["新能源车"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "三部门召开加强新能源汽车安全管理工作视频会" not in output


def test_audit_suspicious_skips_stcn_undersea_data_center_demonstration_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-undersea-data-center",
                first_seen_at="2026-05-14T22:43:49+08:00",
                last_seen_at="2026-05-14T22:43:49+08:00",
                canonical_title="全球首个海底数据中心落户东海",
                summary="人民财讯5月14日电，人工智能浪潮席卷全球，算力正成为至关重要的基础生产力。"
                "我国算力基建企业另辟蹊径，把算力中心建在了海里。这里是全球首个投入运行的"
                "海风直连海底数据中心，总投资16亿元，整体规划24兆瓦。",
                source="stcn",
                published_at="2026-05-14T22:43:49+08:00",
                url="https://example.com/stcn-undersea-data-center",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-undersea-data-center",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "全球首个海底数据中心落户东海" not in output


def test_audit_suspicious_skips_stcn_largest_storage_station_demonstration_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-largest-storage-station",
                first_seen_at="2026-05-23T21:59:27+08:00",
                last_seen_at="2026-05-23T21:59:27+08:00",
                canonical_title="国内单体最大智能组串式储能电站落地内蒙古",
                summary="人民财讯5月23日电，2026储能高质量发展峰会22日在内蒙古自治区包头市举办。会上披露，当地投运的400兆瓦/2400兆瓦时储能电站，为目前国内单体规模最大的智能组串式储能电站，为内蒙古加快构建新型电力系统注入强劲动能。（中国新闻网）",
                source="stcn",
                published_at="2026-05-23T21:59:27+08:00",
                url="https://example.com/stcn-largest-storage-station",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-largest-storage-station",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["储能"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "国内单体最大智能组串式储能电站落地内蒙古" not in output


def test_audit_suspicious_skips_stcn_storage_collection_station_commissioning_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-storage-collection-station-commissioning",
                first_seen_at="2026-07-04T16:48:43+08:00",
                last_seen_at="2026-07-04T16:48:43+08:00",
                canonical_title="明阳包头威俊150万千瓦独立储能电站500千伏汇集站正式投运",
                summary="人民财讯7月4日电，近期，明阳包头威俊150万千瓦独立储能电站500千伏汇集站顺利完成各项测试，"
                "正式并网投运。作为目前国内电压等级最高、配套单体储能规模最大的500千伏储能汇集站和全国储能领域的标杆性工程，"
                "该项目落地投用，将补齐蒙西地区高压储能电网配套短板，进一步完善包头市源网荷储一体化能源产业布局，"
                "为区域能源结构优化、新型电力系统建设、绿色低碳发展注入强劲持久动能。",
                source="stcn",
                published_at="2026-07-04T16:48:43+08:00",
                url="https://www.stcn.com/article/detail/3998461.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-storage-collection-station-commissioning",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["储能"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "明阳包头威俊150万千瓦独立储能电站500千伏汇集站正式投运" not in output


def test_audit_suspicious_skips_stcn_company_visit_exchange_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-company-visit-exchange",
                first_seen_at="2026-05-15T10:48:08+08:00",
                last_seen_at="2026-05-15T10:48:08+08:00",
                canonical_title="佳力图拜访之江实验室三体计算星座项目团队 交流液冷散热与太空算力温控技术",
                summary="佳力图官微消息，近日，佳力图拜访之江实验室三体计算星座项目团队。"
                "双方围绕太空计算基础设施的温控散热需求，以及佳力图地面液冷技术在航天应用场景"
                "下的转化前景进行了交流。双方将围绕太空算力温控技术路线、散热方案极端环境验证等"
                "课题持续推进交流对接。",
                source="stcn",
                published_at="2026-05-15T10:48:08+08:00",
                url="https://example.com/stcn-company-visit-exchange",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-company-visit-exchange",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "佳力图拜访之江实验室三体计算星座项目团队" not in output


def test_audit_suspicious_skips_stcn_foreign_mayor_delegation_exchange_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-foreign-mayor-delegation-exchange",
                first_seen_at="2026-05-29T08:27:56+08:00",
                last_seen_at="2026-05-29T08:27:56+08:00",
                canonical_title="德国纽伦堡市市长率团访蓉，聚焦生物医药与医疗机器人合作",
                summary="人民财讯5月29日电，据成都商报，5月28日，德国纽伦堡市市长马库斯·柯尼希率团访问成都。"
                "代表团参访成都天府国际生物城文化中心，并与成都博恩思医学机器人有限公司相关负责人进行座谈，"
                "围绕生物医药、医疗机器人及产业合作等内容展开交流。",
                source="stcn",
                published_at="2026-05-29T08:27:56+08:00",
                url="https://example.com/stcn-foreign-mayor-delegation-exchange",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-keep-ai-cooperation",
                first_seen_at="2026-05-29T08:35:33+08:00",
                last_seen_at="2026-05-29T08:35:33+08:00",
                canonical_title="博泰车联：与NVIDIA达成战略合作",
                summary="人民财讯5月29日电，博泰车联在港交所公告，公司与NVIDIA举行战略合作签约仪式。",
                source="stcn",
                published_at="2026-05-29T08:35:33+08:00",
                url="https://example.com/keep-ai-cooperation",
                event_type="fast_news",
                event_subtype="cooperation_agreement",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-foreign-mayor-delegation-exchange",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["机器人", "创新药"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-keep-ai-cooperation",
                direction="neutral",
                impact_score=99.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "德国纽伦堡市市长率团访蓉，聚焦生物医药与医疗机器人合作" not in output
    assert "博泰车联：与NVIDIA达成战略合作" not in output


def test_audit_suspicious_skips_investing_economic_colombia_runoff_story_without_hiding_other_investing_economic_news(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-investing-economic-colombia-runoff-1",
                first_seen_at="2026-06-01T17:13:03+00:00",
                last_seen_at="2026-06-01T17:13:03+00:00",
                canonical_title="Right-wing lawyer De La Espriella, leftist senator Cepeda set for heated Colombia runoff",
                summary="Right-wing lawyer De La Espriella, leftist senator Cepeda set for heated Colombia runoff",
                source="investing_economic",
                published_at="2026-06-01T17:13:03+00:00",
                url="https://www.investing.com/news/economic-indicators/rightwing-lawyer-de-la-espriella-leftist-senator-cepeda-set-for-heated-colombia-runoff-4719686",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-investing-economic-colombia-runoff-2",
                first_seen_at="2026-06-01T13:18:32+00:00",
                last_seen_at="2026-06-01T13:18:32+00:00",
                canonical_title="Colombia right-wing lawyer De La Espriella, leftist senator Cepeda set for adversarial runoff",
                summary="Colombia right-wing lawyer De La Espriella, leftist senator Cepeda set for adversarial runoff",
                source="investing_economic",
                published_at="2026-06-01T13:18:32+00:00",
                url="https://www.investing.com/news/economic-indicators/colombia-right-wing-lawyer-de-la-espriella-leftist-senator-cepeda-set-for-adversarial-runoff-4718724",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-investing-economic-control",
                first_seen_at="2026-06-01T08:00:00+00:00",
                last_seen_at="2026-06-01T08:00:00+00:00",
                canonical_title="U.S. jobless claims fall as inflation cools",
                summary="U.S. jobless claims fall as inflation cools",
                source="investing_economic",
                published_at="2026-06-01T08:00:00+00:00",
                url="https://example.com/investing-economic-control",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-investing-economic-colombia-runoff-1",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["宏观"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-investing-economic-colombia-runoff-2",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["宏观"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-investing-economic-control",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["宏观"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=1" in output
    assert "Right-wing lawyer De La Espriella, leftist senator Cepeda set for heated Colombia runoff" not in output
    assert "Colombia right-wing lawyer De La Espriella, leftist senator Cepeda set for adversarial runoff" not in output
    assert "U.S. jobless claims fall as inflation cools" in output


def test_audit_suspicious_skips_stcn_bank_insurance_chairman_meeting_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-bank-insurance-chairman-meeting",
                first_seen_at="2026-05-18T20:33:58+08:00",
                last_seen_at="2026-05-18T20:33:58+08:00",
                canonical_title="中国银行董事长葛海蛟会见友邦保险集团董事会主席杜嘉祺爵士",
                summary="据中国银行消息，5月18日，中国银行董事长葛海蛟在中国银行总行大厦会见"
                "友邦保险集团董事会主席杜嘉祺爵士，双方就国内外宏观经济形势交换意见，并围绕"
                "代理保险、托管、香港及东南亚地区合作等话题进行交流。",
                source="stcn",
                published_at="2026-05-18T20:33:58+08:00",
                url="https://example.com/stcn-bank-insurance-chairman-meeting",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-bank-insurance-chairman-meeting",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["保险"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "中国银行董事长葛海蛟会见友邦保险集团董事会主席杜嘉祺爵士" not in output


def test_audit_suspicious_skips_stcn_storage_president_appointment_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-storage-president-appointment",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["储能"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "晶澳科技任命王君生为储能公司总裁" not in output


def test_audit_suspicious_skips_stcn_space_compute_ecosystem_plan_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
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
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-space-compute-ecosystem-plan",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "优刻得加入上海太空算力产业生态伙伴计划" not in output


def test_audit_suspicious_skips_stcn_space_compute_research_institute_establishment_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-space-compute-research-institute",
                first_seen_at="2026-05-30T19:40:07+08:00",
                last_seen_at="2026-05-30T19:40:07+08:00",
                canonical_title="北京太空智算研究院在北京亦庄成立",
                summary="人民财讯5月30日电，近日，北京太空智算研究院在北京经济技术开发区（简称北京亦庄）注册成立。"
                "研究院将围绕星载算力芯片、星间激光通信、太空能源与散热、天地一体化网络及空间安全标准等方向开展关键共性技术攻关，"
                "并计划于2028年前完成首发试验星研制与发射。",
                source="stcn",
                published_at="2026-05-30T19:40:07+08:00",
                url="https://example.com/stcn-space-compute-research-institute",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-space-compute-research-institute",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "北京太空智算研究院在北京亦庄成立" not in output


def test_audit_suspicious_skips_stcn_overseas_satellite_orbit_maintenance_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-overseas-satellite-orbit-maintenance",
                first_seen_at="2026-07-04T10:22:19+08:00",
                last_seen_at="2026-07-04T10:22:19+08:00",
                canonical_title="美发射商业航天器抬升天文卫星轨道 延长工作寿命",
                summary="人民财讯7月4日电，美国航空航天局3日表示，一枚商业航天器当天从马绍尔群岛升空，"
                "部署至预定轨道，将与尼尔·格雷尔斯·斯威夫特（又称“雨燕”）天文台在轨对接，"
                "以帮助抬升该天文卫星轨道高度，延长其使用寿命。（新华社）",
                source="stcn",
                published_at="2026-07-04T10:22:19+08:00",
                url="https://www.stcn.com/article/detail/3998382.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-overseas-satellite-orbit-maintenance",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["商业航天"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "美发射商业航天器抬升天文卫星轨道 延长工作寿命" not in output


def test_audit_suspicious_skips_current_live_storage_space_compute_and_tcl_material_noise(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-storage-grid-connection",
                first_seen_at="2026-06-02T19:55:23+08:00",
                last_seen_at="2026-06-02T19:55:23+08:00",
                canonical_title="云南弥勒西100兆瓦/200兆瓦时电化学共享储能电站全容量并网",
                summary="人民财讯6月2日电，5月31日，三峡能源云南弥勒西100兆瓦/200兆瓦时电化学共享储能电站实现全容量并网。"
                "项目预计年充放电量1.16亿千瓦时，每年可消纳绿电约4000万千瓦时，相当于节约标准煤约1.2万吨、"
                "减排二氧化碳约3.3万吨，可满足1.3万个三口之家全年用电量。",
                source="stcn",
                published_at="2026-06-02T19:55:23+08:00",
                url="https://www.stcn.com/article/detail/3939966.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-stcn-space-compute-symposium",
                first_seen_at="2026-06-02T19:33:06+08:00",
                last_seen_at="2026-06-02T19:33:06+08:00",
                canonical_title="北京经开区召开太空算力企业座谈会 研究部署太空算力创新中心建设工作",
                summary="人民财讯6月2日电，6月1日，北京经济技术开发区（简称北京经开区，也称北京亦庄）工委副书记、"
                "管委会主任王磊主持召开太空算力企业座谈会，听取相关企业对北京亦庄打造太空算力产业高地的意见建议，"
                "研究部署太空算力创新中心建设工作。",
                source="stcn",
                published_at="2026-06-02T19:33:06+08:00",
                url="https://www.stcn.com/article/detail/3939939.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-szse-tcl-question-reply",
                first_seen_at="2026-06-03T00:00:00+08:00",
                last_seen_at="2026-06-03T00:00:00+08:00",
                canonical_title="TCL科技：关于发行股份及支付现金购买资产审核问询函回复的公告",
                summary="TCL科技：关于发行股份及支付现金购买资产审核问询函回复的公告",
                source="szse",
                published_at="2026-06-03T00:00:00+08:00",
                url="https://www.szse.cn/disc/disk03/finalpage/2026-06-03/dcd8bf69-0a67-4a53-820b-ec43cd0b47d2.PDF",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-storage-grid-connection",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["储能"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-stcn-space-compute-symposium",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-szse-tcl-question-reply",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "云南弥勒西100兆瓦/200兆瓦时电化学共享储能电站全容量并网" not in output
    assert "北京经开区召开太空算力企业座谈会 研究部署太空算力创新中心建设工作" not in output
    assert "TCL科技：关于发行股份及支付现金购买资产审核问询函回复的公告" not in output


def test_audit_suspicious_skips_stcn_storage_system_delivery_progress_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-storage-system-delivery-progress",
                first_seen_at="2026-06-02T20:54:12+08:00",
                last_seen_at="2026-06-02T20:54:12+08:00",
                canonical_title="晶科储能完成722MWh储能系统交付",
                summary="人民财讯6月2日电，据晶科能源消息，近日，晶科储能已向印度大型新能源基地项目完成722MWh储能系统设备交付。"
                "该项目采用144套晶科SunTera G2液冷储能系统，将为当地新能源高比例并网、清洁能源调度、电网稳定运行及峰值负荷支撑提供可靠储能能力。",
                source="stcn",
                published_at="2026-06-02T20:54:12+08:00",
                url="https://www.stcn.com/article/detail/3940044.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-storage-system-delivery-progress",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["储能"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "晶科储能完成722MWh储能系统交付" not in output


def test_audit_suspicious_skips_stcn_insurance_asset_management_regulation_reference(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-insurance-asset-management-regulation",
                first_seen_at="2026-05-20T14:42:39+08:00",
                last_seen_at="2026-05-20T14:42:39+08:00",
                canonical_title="独家丨保险资管迎来“四个支柱”监管要求",
                summary="人民财讯5月20日电，记者从多方获悉，金融监管总局资管司围绕"
                "“四个支柱、四项目标、16项核心要素”对保险资管公司提出监管要求。"
                "第一支柱是受托责任和投资者保护。第二支柱是防范系统性风险。"
                "第三支柱是市场效率和稳定性。第四支柱是金融稳定与宏观审慎。",
                source="stcn",
                published_at="2026-05-20T14:42:39+08:00",
                url="https://example.com/stcn-insurance-asset-management-regulation",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-insurance-asset-management-regulation",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["保险"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "独家丨保险资管迎来“四个支柱”监管要求" not in output


def test_audit_suspicious_skips_annual_inquiry_audit_and_legal_opinion_materials(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-annual-inquiry-audit-note",
                first_seen_at="2026-05-19T00:00:00+08:00",
                last_seen_at="2026-05-19T00:00:00+08:00",
                canonical_title="致同会计师事务所（特殊普通合伙）关于对杭州奥泰生物技术股份有限公司的2025年年报问询函审计相关事项的专项说明",
                summary="summary",
                source="sse",
                published_at="2026-05-19T00:00:00+08:00",
                url="https://example.com/annual-inquiry-audit-note",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-annual-inquiry-legal-opinion",
                first_seen_at="2026-05-19T00:00:00+08:00",
                last_seen_at="2026-05-19T00:00:00+08:00",
                canonical_title="*ST铖昌：北京君合（杭州）律师事务所关于深圳证券交易所关于浙江铖昌科技股份有限公司2025年年报的问询函相关事项的法律意见书",
                summary="summary",
                source="szse",
                published_at="2026-05-19T00:00:00+08:00",
                url="https://example.com/annual-inquiry-legal-opinion",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-annual-inquiry-audit-note",
                direction="neutral",
                impact_score=78.5,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-annual-inquiry-legal-opinion",
                direction="neutral",
                impact_score=78.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "年报问询函审计相关事项的专项说明" not in output
    assert "年报的问询函相关事项的法律意见书" not in output


def test_audit_suspicious_skips_current_low_signal_batch_20260519_night(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-annual-inquiry-valuation-reply",
                first_seen_at="2026-05-20T00:00:00+08:00",
                last_seen_at="2026-05-20T00:00:00+08:00",
                canonical_title="北京中林资产评估有限公司关于深圳证券交易所《关于对阳光新业地产股份有限公司2025年年报的问询函》涉及评估问题的回复",
                summary="summary",
                source="cninfo",
                published_at="2026-05-20T00:00:00+08:00",
                url="https://example.com/annual-inquiry-valuation-reply",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-annual-inquiry-accountant-reply",
                first_seen_at="2026-05-20T00:00:00+08:00",
                last_seen_at="2026-05-20T00:00:00+08:00",
                canonical_title="中兴华会计师事务所（特殊普通合伙）关于对阳光新业地产股份有限公司2025年年报问询函的回复",
                summary="summary",
                source="cninfo",
                published_at="2026-05-20T00:00:00+08:00",
                url="https://example.com/annual-inquiry-accountant-reply",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-annual-inquiry-receipt-notice",
                first_seen_at="2026-05-20T00:00:00+08:00",
                last_seen_at="2026-05-20T00:00:00+08:00",
                canonical_title="青海春天关于收到上海证券交易所《关于公司2025年年报有关事项的问询函》的公告",
                summary="summary",
                source="cninfo",
                published_at="2026-05-20T00:00:00+08:00",
                url="https://example.com/annual-inquiry-receipt-notice",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-annual-inquiry-generic-reply-notice",
                first_seen_at="2026-05-20T00:00:00+08:00",
                last_seen_at="2026-05-20T00:00:00+08:00",
                canonical_title="关于对深圳证券交易所2025年年报的问询函的回复公告",
                summary="关于对深圳证券交易所2025年年报的问询函的回复公告",
                source="cninfo",
                published_at="2026-05-20T00:00:00+08:00",
                url="https://example.com/annual-inquiry-generic-reply-notice",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-safe-aia-chairman-meeting",
                first_seen_at="2026-05-19T20:08:21+08:00",
                last_seen_at="2026-05-19T20:08:21+08:00",
                canonical_title="国家外汇局局长朱鹤新会见友邦保险集团主席杜嘉祺",
                summary="双方就国际经济金融形势、中国经济发展机遇、外汇政策支持保险业高质量发展等议题进行了交流。",
                source="stcn",
                published_at="2026-05-19T20:08:21+08:00",
                url="https://example.com/safe-aia-chairman-meeting",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-stcn-spot-gold-intraday-drop",
                first_seen_at="2026-05-19T21:34:31+08:00",
                last_seen_at="2026-05-19T21:34:31+08:00",
                canonical_title="现货黄金日内跌幅达2%",
                summary="人民财讯5月19日电，现货黄金日内跌幅达2%，报4470.45美元/盎司。",
                source="stcn",
                published_at="2026-05-19T21:34:31+08:00",
                url="https://example.com/stcn-spot-gold-intraday-drop",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-annual-inquiry-valuation-reply",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-annual-inquiry-accountant-reply",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-annual-inquiry-receipt-notice",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-annual-inquiry-generic-reply-notice",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-safe-aia-chairman-meeting",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["保险"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-stcn-spot-gold-intraday-drop",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["黄金"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "涉及评估问题的回复" not in output
    assert "年报问询函的回复" not in output
    assert "年报的问询函的回复公告" not in output
    assert "年报有关事项的问询函" not in output
    assert "国家外汇局局长朱鹤新会见友邦保险集团主席杜嘉祺" not in output
    assert "现货黄金日内跌幅达2%" not in output


def test_audit_suspicious_skips_current_low_signal_batch_20260518(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-arbitration-progress-generic",
                first_seen_at="2026-05-19T00:00:00+08:00",
                last_seen_at="2026-05-19T00:00:00+08:00",
                canonical_title="关于涉及仲裁的进展公告",
                summary="关于涉及仲裁的进展公告",
                source="cninfo",
                published_at="2026-05-19T00:00:00+08:00",
                url="https://example.com/arbitration-progress-generic",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-stcn-spot-silver-stands-above",
                first_seen_at="2026-05-18T21:52:16+08:00",
                last_seen_at="2026-05-18T21:52:16+08:00",
                canonical_title="现货白银站上78美元/盎司",
                summary="人民财讯5月18日电，现货白银站上78美元/盎司，日内涨2.78%。",
                source="stcn",
                published_at="2026-05-18T21:52:16+08:00",
                url="https://example.com/stcn-spot-silver-stands-above",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-stcn-taojin-interactive-computing-chain",
                first_seen_at="2026-05-18T21:42:42+08:00",
                last_seen_at="2026-05-18T21:42:42+08:00",
                canonical_title="【淘金互动易】上海将推动算力规模倍增，机构持续看好算力全产业链，这家公司正交背板材料将应用于Rubin架构的算力服务器",
                summary="上海将推动算力规模倍增，机构持续看好算力全产业链，多家公司在互动平台回复算力领域最新布局。",
                source="stcn",
                published_at="2026-05-18T21:42:42+08:00",
                url="https://example.com/stcn-taojin-interactive-computing-chain",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-stcn-amd-chairman-meeting",
                first_seen_at="2026-05-18T20:57:52+08:00",
                last_seen_at="2026-05-18T20:57:52+08:00",
                canonical_title="何立峰会见美国超威半导体公司董事会主席兼首席执行官苏姿丰",
                summary="何立峰会见美国超威半导体公司董事会主席兼首席执行官苏姿丰，欢迎跨国公司把握中国发展机遇，深化互利合作。苏姿丰表示愿继续拓展在华业务。",
                source="stcn",
                published_at="2026-05-18T20:57:52+08:00",
                url="https://example.com/stcn-amd-chairman-meeting",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-stcn-jiangsu-amd-chairman-meeting",
                first_seen_at="2026-05-19T21:25:35+08:00",
                last_seen_at="2026-05-19T21:25:35+08:00",
                canonical_title="江苏省委书记信长星会见美国超威半导体公司董事会主席兼首席执行官苏姿丰",
                summary="信长星会见美国超威半导体公司董事会主席兼首席执行官苏姿丰，希望超威半导体公司坚定在中国、在江苏发展的信心，深化产业合作，加大投资布局，携手实现更高水平的互利共赢。",
                source="stcn",
                published_at="2026-05-19T21:25:35+08:00",
                url="https://example.com/stcn-jiangsu-amd-chairman-meeting",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-irm-legal-complaint-question-only",
                first_seen_at="2026-05-18T21:09:47+08:00",
                last_seen_at="2026-05-18T21:09:47+08:00",
                canonical_title="*ST动力：请问公司在处理普益基金的问题上，有什么具体的解决方案？可否查账诉讼的同时与业务剥离同步进行，采取切实有效的措施尽快彻底解决，不要因为这个事情毁掉整个上市公司。另外公司是否考虑停牌重整，引入有实力的大股东做实控人，做好转型升级。",
                summary="请问公司在处理普益基金的问题上，有什么具体的解决方案？可否查账诉讼的同时与业务剥离同步进行，采取切实有效的措施尽快彻底解决，不要因为这个事情毁掉整个上市公司。另外公司是否考虑停牌重整，引入有实力的大股东做实控人，做好转型升级。",
                source="irm_cninfo",
                published_at="2026-05-18T21:09:47+08:00",
                url="https://example.com/irm-legal-complaint-question-only",
                event_type="fast_news",
                event_subtype="company_update",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-arbitration-progress-generic",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-stcn-spot-silver-stands-above",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["黄金"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-stcn-taojin-interactive-computing-chain",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["算力"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-stcn-amd-chairman-meeting",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-stcn-jiangsu-amd-chairman-meeting",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-irm-legal-complaint-question-only",
                direction="neutral",
                impact_score=75.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "关于涉及仲裁的进展公告" not in output
    assert "现货白银站上78美元/盎司" not in output
    assert "【淘金互动易】上海将推动算力规模倍增" not in output
    assert "何立峰会见美国超威半导体公司董事会主席兼首席执行官苏姿丰" not in output
    assert "江苏省委书记信长星会见美国超威半导体公司董事会主席兼首席执行官苏姿丰" not in output
    assert "普益基金的问题" not in output


def test_audit_suspicious_skips_overseas_pharma_antitrust_lawsuit_theme_spillover(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-overseas-pharma-antitrust-lawsuit",
                first_seen_at="2026-05-19T02:24:26+00:00",
                last_seen_at="2026-05-19T02:24:26+00:00",
                canonical_title="Japan’s Takeda engaged in antitrust scheme to delay generic constipation drug, US jury finds",
                summary="Japan’s Takeda engaged in antitrust scheme to delay generic constipation drug, US jury finds",
                source="investing_news",
                published_at="2026-05-19T02:24:26+00:00",
                url="https://example.com/overseas-pharma-antitrust-lawsuit",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-overseas-pharma-antitrust-lawsuit",
                direction="neutral",
                impact_score=79.6,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "Japan’s Takeda engaged in antitrust scheme" not in output


def test_audit_suspicious_skips_current_cninfo_inquiry_reply_variants_and_delayed_audit_reply(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-year-end-inquiry-reply-variant-1",
                first_seen_at="2026-05-27T00:00:00+08:00",
                last_seen_at="2026-05-27T00:00:00+08:00",
                canonical_title="致同会计师事务所关于深圳证券交易所《关于对珠海汇金科技股份有限公司的年报问询函》的回复",
                summary="summary",
                source="cninfo",
                published_at="2026-05-27T00:00:00+08:00",
                url="https://example.com/cninfo-year-end-inquiry-reply-variant-1",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-cninfo-year-end-inquiry-reply-variant-2",
                first_seen_at="2026-05-27T00:00:00+08:00",
                last_seen_at="2026-05-27T00:00:00+08:00",
                canonical_title="北京华亚正信资产评估有限公司对深圳证券交易所《关于对珠海汇金科技股份有限公司的年报问询函》之回复",
                summary="summary",
                source="cninfo",
                published_at="2026-05-27T00:00:00+08:00",
                url="https://example.com/cninfo-year-end-inquiry-reply-variant-2",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-cninfo-delayed-audit-inquiry-reply",
                first_seen_at="2026-05-27T00:00:00+08:00",
                last_seen_at="2026-05-27T00:00:00+08:00",
                canonical_title="阿石创：关于延期回复深圳证券交易所审核问询函的公告",
                summary="summary",
                source="cninfo",
                published_at="2026-05-27T00:00:00+08:00",
                url="https://example.com/cninfo-delayed-audit-inquiry-reply",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-year-end-inquiry-reply-variant-1",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-cninfo-year-end-inquiry-reply-variant-2",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-cninfo-delayed-audit-inquiry-reply",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "致同会计师事务所关于深圳证券交易所《关于对珠海汇金科技股份有限公司的年报问询函》的回复" not in output
    assert "北京华亚正信资产评估有限公司对深圳证券交易所《关于对珠海汇金科技股份有限公司的年报问询函》之回复" not in output
    assert "阿石创：关于延期回复深圳证券交易所审核问询函的公告" not in output


def test_audit_suspicious_keeps_solarpro_overseas_storage_project_as_market_reference(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-solarpro-overseas-storage-project",
                first_seen_at="2026-05-26T21:05:00+08:00",
                last_seen_at="2026-05-26T21:05:00+08:00",
                canonical_title="Solarpro Holding与宁德时代合作的601MWh储能项目在保加利亚并网投运",
                summary="人民财讯5月26日电，近日，东欧地区企业Solarpro Holding与宁德时代合作的601MWh大型储能项目在保加利亚成功并网投运。项目全面搭载宁德时代自主研发的天恒储能系统，这是业内首个6MWh级零衰减产品。基于此次合作，Solarpro Holding与宁德时代已达成长期合作意向，计划未来两年内进一步扩大储能项目规模。",
                source="stcn",
                published_at="2026-05-26T21:05:00+08:00",
                url="https://www.stcn.com/article/detail/3928504.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-solarpro-overseas-storage-project",
                direction="bullish",
                impact_score=79.0,
                reasoning="rule",
                themes=["储能"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "Solarpro Holding与宁德时代合作的601MWh储能项目在保加利亚并网投运" not in output


def test_audit_suspicious_skips_stcn_etf_intraday_suspension_risk_warning(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-etf-intraday-suspension-risk-warning",
                first_seen_at="2026-05-27T19:21:24+08:00",
                last_seen_at="2026-05-27T19:22:24+08:00",
                canonical_title="中韩半导体ETF华泰柏瑞将于5月28日开市起至当日10:30停牌",
                summary="人民财讯5月27日电，中韩半导体ETF华泰柏瑞(513310)将于5月28日开市起至当日10:30停牌。若基金午间收盘二级市场交易价格溢价幅度仍处于较高水平，基金有权向上交所申请5月28日下午盘中临时停牌至收盘的措施以向市场警示风险。",
                source="stcn",
                published_at="2026-05-27T19:22:24+08:00",
                url="https://www.stcn.com/article/detail/3930451.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-etf-intraday-suspension-risk-warning",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["半导体"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "中韩半导体ETF华泰柏瑞将于5月28日开市起至当日10:30停牌" not in output


def test_audit_suspicious_skips_annual_report_inquiry_mining_right_valuation_opinion(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-mining-right-inquiry-opinion",
                first_seen_at="2026-07-01T00:00:00+08:00",
                last_seen_at="2026-07-01T00:00:00+08:00",
                canonical_title="评估机构对《关于山东新华锦国际股份有限公司2025年年度报告的信息披露监管问询函》之采矿权评估发表意见",
                summary="评估机构对年报信息披露监管问询函之采矿权评估发表意见。",
                source="sse",
                published_at="2026-07-01T00:00:00+08:00",
                url="https://example.com/mining-right-inquiry-opinion",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-mining-right-inquiry-opinion",
                direction="neutral",
                impact_score=78.5,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "采矿权评估发表意见" not in output


def test_audit_suspicious_skips_stcn_overseas_storage_landing_validation_story(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-overseas-storage-landing-validation",
                first_seen_at="2026-07-02T15:26:09+08:00",
                last_seen_at="2026-07-02T15:26:09+08:00",
                canonical_title="东方日升iCon系列液冷储能已在欧洲多元场景中完成落地验证",
                summary="人民财讯7月2日电，据东方日升消息，随着欧洲电价波动加剧与REPowerEU计划的深入推进，工商业储能已从可选项变为企业的必选项。东方日升以iCon系列工商业液冷储能一体机为锚点，在波黑、比利时、立陶宛等地接连落地储能项目。近期，东方日升iCon系列液冷储能已在欧洲多元场景中完成落地验证，未来，东方日升将继续深耕欧洲市场。",
                source="stcn",
                published_at="2026-07-02T15:26:09+08:00",
                url="https://www.stcn.com/article/detail/3994666.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-overseas-storage-landing-validation",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["储能"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "东方日升iCon系列液冷储能已在欧洲多元场景中完成落地验证" not in output


def test_audit_suspicious_skips_stcn_storage_project_cooperation_and_sector_fund_flow(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-storage-project-cooperation",
                first_seen_at="2026-07-02T20:15:27+08:00",
                last_seen_at="2026-07-02T20:15:27+08:00",
                canonical_title="晶科储能与Taliva Energy达成东欧区域总计400MWh的大型储能系统项目合作",
                summary="人民财讯7月2日电，晶科能源股份有限公司子公司晶科储能近日在慕尼黑Intersolar Europe展会期间，与清洁能源开发商Taliva Energy正式完成签约，达成东欧区域总计400MWh的大型储能系统项目合作。",
                source="stcn",
                published_at="2026-07-02T20:15:27+08:00",
                url="https://www.stcn.com/article/detail/3995675.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-stcn-sector-fund-flow",
                first_seen_at="2026-07-02T19:31:59+08:00",
                last_seen_at="2026-07-02T19:31:59+08:00",
                canonical_title="今日黄金珠宝指数逆市上涨 主力资金净流入15只黄金珠宝股",
                summary="人民财讯7月2日电，7月2日，黄金珠宝指数逆市大涨，涨幅为2.89%，位于万得热门概念指数涨幅榜前列。成份股中，鹏欣资源、招金黄金和赤峰黄金涨停。据证券时报·数据宝统计，今日主力资金净流入15只黄金珠宝股。",
                source="stcn",
                published_at="2026-07-02T19:31:59+08:00",
                url="https://www.stcn.com/article/detail/3995607.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-storage-project-cooperation",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["储能"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-stcn-sector-fund-flow",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["黄金"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "晶科储能与Taliva Energy达成东欧区域总计400MWh的大型储能系统项目合作" not in output
    assert "今日黄金珠宝指数逆市上涨 主力资金净流入15只黄金珠宝股" not in output


def test_audit_suspicious_skips_stcn_domestic_commodity_night_session_close(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-domestic-commodity-night-session-close",
                first_seen_at="2026-07-02T23:06:06+08:00",
                last_seen_at="2026-07-02T23:06:06+08:00",
                canonical_title="国内商品期货夜盘收盘 液化石油气涨近3%",
                summary="人民财讯7月2日电，国内商品期货夜盘收盘涨多跌少，液化石油气（LPG）涨近3%，甲醇涨超2%，丙烯、聚丙烯、沥青、焦炭涨超1%；铁矿石跌超1%，棕榈油跌近1%。",
                source="stcn",
                published_at="2026-07-02T23:06:06+08:00",
                url="https://www.stcn.com/article/detail/3995821.html",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-domestic-commodity-night-session-close",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["油气"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "国内商品期货夜盘收盘 液化石油气涨近3%" not in output


def test_audit_suspicious_skips_cninfo_annual_report_inquiry_reply_verification_opinion(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-annual-report-inquiry-reply-verification-opinion",
                first_seen_at="2026-07-08T00:00:00+08:00",
                last_seen_at="2026-07-08T00:00:00+08:00",
                canonical_title="国金证券股份有限公司关于无锡祥生医疗科技股份有限公司2025年年度报告的信息披露监管问询函之回复的核查意见",
                summary="国金证券股份有限公司关于无锡祥生医疗科技股份有限公司2025年年度报告的信息披露监管问询函之回复的核查意见",
                source="cninfo",
                published_at="2026-07-08T00:00:00+08:00",
                url="https://example.com/cninfo-annual-report-inquiry-reply-verification-opinion",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-cninfo-accountant-special-verification-note",
                first_seen_at="2026-07-17T00:00:00+08:00",
                last_seen_at="2026-07-17T00:00:00+08:00",
                canonical_title="大华会计师事务所(特殊普通合伙)关于东易日盛家居装饰集团股份有限公司2025年年度报告的信息披露监管问询函的专项核查说明",
                summary="大华会计师事务所披露年报信息披露监管问询函专项核查说明。",
                source="cninfo",
                published_at="2026-07-17T00:00:00+08:00",
                url="https://example.com/cninfo-accountant-special-verification-note",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-cninfo-audit-committee-inquiry-verification-opinion",
                first_seen_at="2026-07-17T00:00:00+08:00",
                last_seen_at="2026-07-17T00:00:00+08:00",
                canonical_title="审计委员会关于《深圳证券交易所对摩登大道时尚集团股份有限公司2025年年报的问询函》的核查意见",
                summary="摩登大道审计委员会披露年报问询函核查意见。",
                source="cninfo",
                published_at="2026-07-17T00:00:00+08:00",
                url="https://example.com/cninfo-audit-committee-inquiry-verification-opinion",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-cninfo-lawyer-annual-report-inquiry-opinion",
                first_seen_at="2026-07-17T00:00:00+08:00",
                last_seen_at="2026-07-17T00:00:00+08:00",
                canonical_title="北京市天元律师事务所关于摩登大道时尚集团股份有限公司2025年年报问询函相关事项的法律意见书",
                summary="北京市天元律师事务所披露摩登大道年报问询函相关事项法律意见书。",
                source="cninfo",
                published_at="2026-07-17T00:00:00+08:00",
                url="https://example.com/cninfo-lawyer-annual-report-inquiry-opinion",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-annual-report-inquiry-reply-verification-opinion",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-cninfo-accountant-special-verification-note",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-cninfo-audit-committee-inquiry-verification-opinion",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-cninfo-lawyer-annual-report-inquiry-opinion",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "信息披露监管问询函之回复的核查意见" not in output


def test_audit_suspicious_skips_annual_report_inquiry_attachment_variants(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-cninfo-disclosure-inquiry-verification-note",
                first_seen_at="2026-07-17T00:00:00+08:00",
                last_seen_at="2026-07-17T00:00:00+08:00",
                canonical_title="大华会计师事务所(特殊普通合伙)关于东易日盛家居装饰集团股份有限公司2025年年度报告的信息披露监管问询函的专项核查说明",
                summary="会计师披露年度报告信息披露监管问询函的专项核查说明。",
                source="cninfo",
                published_at="2026-07-17T00:00:00+08:00",
                url="https://example.com/cninfo-disclosure-inquiry-verification-note",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-cninfo-annual-report-inquiry-audit-committee-opinion",
                first_seen_at="2026-07-17T00:00:00+08:00",
                last_seen_at="2026-07-17T00:00:00+08:00",
                canonical_title="审计委员会关于《深圳证券交易所对摩登大道时尚集团股份有限公司2025年年报的问询函》的核查意见",
                summary="审计委员会披露年报问询函核查意见。",
                source="cninfo",
                published_at="2026-07-17T00:00:00+08:00",
                url="https://example.com/cninfo-annual-report-inquiry-audit-committee-opinion",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-cninfo-annual-report-inquiry-legal-opinion",
                first_seen_at="2026-07-17T00:00:00+08:00",
                last_seen_at="2026-07-17T00:00:00+08:00",
                canonical_title="北京市天元律师事务所关于摩登大道时尚集团股份有限公司2025年年报问询函相关事项的法律意见书",
                summary="律师事务所披露年报问询函相关事项法律意见书。",
                source="cninfo",
                published_at="2026-07-17T00:00:00+08:00",
                url="https://example.com/cninfo-annual-report-inquiry-legal-opinion",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-cninfo-disclosure-inquiry-verification-note",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-cninfo-annual-report-inquiry-audit-committee-opinion",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-cninfo-annual-report-inquiry-legal-opinion",
                direction="neutral",
                impact_score=80.0,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "信息披露监管问询函的专项核查说明" not in output
    assert "年报的问询函》的核查意见" not in output
    assert "年报问询函相关事项的法律意见书" not in output


def test_audit_suspicious_skips_stcn_light_business_showcase_and_tech_breakthrough(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-robot-night-showcase",
                first_seen_at="2026-07-16T22:04:49+08:00",
                last_seen_at="2026-07-16T22:04:49+08:00",
                canonical_title="擎天租主办“机器人奇妙夜”落地贵阳",
                summary="擎天租打造RaaS文旅产品首秀，活动覆盖群舞、武术、歌曲、走秀等多元形态。",
                source="stcn",
                published_at="2026-07-16T22:04:49+08:00",
                url="https://example.com/stcn-robot-night-showcase",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-stcn-pcb-tech-breakthrough",
                first_seen_at="2026-07-16T21:46:53+08:00",
                last_seen_at="2026-07-16T21:46:53+08:00",
                canonical_title="奥士康取得超高层埋容混压PCB关键技术突破",
                summary="奥士康成功研发出N+M结构、三料混压的埋容超高层PCB，并在高可靠量产工艺上取得关键突破。",
                source="stcn",
                published_at="2026-07-16T21:46:53+08:00",
                url="https://example.com/stcn-pcb-tech-breakthrough",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-robot-night-showcase",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["机器人"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-stcn-pcb-tech-breakthrough",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["PCB"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "机器人奇妙夜" not in output
    assert "超高层埋容混压PCB关键技术突破" not in output
    assert "信息披露监管问询函的专项核查说明" not in output
    assert "2025年年报的问询函》的核查意见" not in output
    assert "年报问询函相关事项的法律意见书" not in output


def test_audit_suspicious_skips_stcn_event_and_technical_breakthrough_theme_news(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()

    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-stcn-robot-event",
                first_seen_at="2026-07-16T20:23:00+08:00",
                last_seen_at="2026-07-16T20:23:00+08:00",
                canonical_title="擎天租主办“机器人奇妙夜”落地贵阳",
                summary="擎天租主办机器人奇妙夜活动落地贵阳。",
                source="stcn",
                published_at="2026-07-16T20:23:00+08:00",
                url="https://example.com/stcn-robot-event",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
            Event(
                event_id="event-stcn-pcb-technical-breakthrough",
                first_seen_at="2026-07-16T20:33:00+08:00",
                last_seen_at="2026-07-16T20:33:00+08:00",
                canonical_title="奥士康取得超高层埋容混压PCB关键技术突破",
                summary="奥士康取得超高层埋容混压PCB关键技术突破。",
                source="stcn",
                published_at="2026-07-16T20:33:00+08:00",
                url="https://example.com/stcn-pcb-technical-breakthrough",
                event_type="fast_news",
                event_subtype="general_fast_news",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-stcn-robot-event",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["机器人"],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-stcn-pcb-technical-breakthrough",
                direction="neutral",
                impact_score=79.0,
                reasoning="rule",
                themes=["PCB"],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "机器人奇妙夜" not in output
    assert "超高层埋容混压PCB关键技术突破" not in output


def test_audit_suspicious_skips_current_inquiry_material_and_low_signal_stcn_theme_news(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()
    events = [
        Event(
            event_id="event-current-dongyi-accountant-inquiry-material",
            first_seen_at="2026-07-17T00:00:00+08:00",
            last_seen_at="2026-07-17T00:00:00+08:00",
            canonical_title="大华会计师事务所(特殊普通合伙)关于东易日盛家居装饰集团股份有限公司2025年年度报告的信息披露监管问询函的专项核查说明",
            summary="大华会计师事务所关于东易日盛2025年年度报告的信息披露监管问询函的专项核查说明。",
            source="cninfo",
            published_at="2026-07-17T00:00:00+08:00",
            url="https://example.com/dongyi-accountant-inquiry-material",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-current-modern-avenue-audit-committee-opinion",
            first_seen_at="2026-07-17T00:00:00+08:00",
            last_seen_at="2026-07-17T00:00:00+08:00",
            canonical_title="审计委员会关于《深圳证券交易所对摩登大道时尚集团股份有限公司2025年年报的问询函》的核查意见",
            summary="审计委员会关于摩登大道2025年年报问询函的核查意见。",
            source="cninfo",
            published_at="2026-07-17T00:00:00+08:00",
            url="https://example.com/modern-avenue-audit-committee-opinion",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-current-modern-avenue-legal-opinion",
            first_seen_at="2026-07-17T00:00:00+08:00",
            last_seen_at="2026-07-17T00:00:00+08:00",
            canonical_title="北京市天元律师事务所关于摩登大道时尚集团股份有限公司2025年年报问询函相关事项的法律意见书",
            summary="北京市天元律师事务所关于摩登大道2025年年报问询函相关事项的法律意见书。",
            source="cninfo",
            published_at="2026-07-17T00:00:00+08:00",
            url="https://example.com/modern-avenue-legal-opinion",
            event_type="hard_event",
            event_subtype="corporate_disclosure",
        ),
        Event(
            event_id="event-current-robot-night-raas-story",
            first_seen_at="2026-07-16T22:04:49+08:00",
            last_seen_at="2026-07-16T22:04:49+08:00",
            canonical_title="擎天租主办“机器人奇妙夜”落地贵阳",
            summary="擎天租打造的全球首个机器人奇妙夜RaaS产品首秀，拓宽RaaS+生态的商业模型。",
            source="stcn",
            published_at="2026-07-16T22:04:49+08:00",
            url="https://example.com/robot-night-raas-story",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-current-aoshikang-pcb-process-breakthrough",
            first_seen_at="2026-07-16T21:46:53+08:00",
            last_seen_at="2026-07-16T21:46:53+08:00",
            canonical_title="奥士康取得超高层埋容混压PCB关键技术突破",
            summary="奥士康研发N+M结构、三料混压的埋容超高层PCB，为高端PCB稳定制造与可靠交付提供技术支撑。",
            source="stcn",
            published_at="2026-07-16T21:46:53+08:00",
            url="https://example.com/aoshikang-pcb-process-breakthrough",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-current-meta-anthropic-compute-rental",
            first_seen_at="2026-07-18T09:12:36+08:00",
            last_seen_at="2026-07-18T09:12:36+08:00",
            canonical_title="Meta据悉洽谈向Anthropic出租AI算力，拟进军云计算市场",
            summary="人民财讯7月18日电，据报道，Meta正与人工智能初创公司Anthropic洽谈出租算力事宜，拟向其提供计算基础设施服务。",
            source="stcn",
            published_at="2026-07-18T09:12:36+08:00",
            url="https://www.stcn.com/article/detail/4027090.html",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-current-telecom-highlander-visit",
            first_seen_at="2026-07-18T08:45:19+08:00",
            last_seen_at="2026-07-18T08:45:19+08:00",
            canonical_title="中国电信广东分公司到访海兰信 共商海上风电算力合作",
            summary="双方围绕海上风电与算力基础设施融合发展展开调研，交换意见并达成多项共识。",
            source="stcn",
            published_at="2026-07-18T08:45:19+08:00",
            url="https://www.stcn.com/article/detail/4027077.html",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-current-humanoid-robot-output-standard-week",
            first_seen_at="2026-07-18T07:56:49+08:00",
            last_seen_at="2026-07-18T07:56:49+08:00",
            canonical_title="今年我国人形机器人产量有望超过10万台 产业加速进入规模化落地新阶段",
            summary="工业和信息化部人形机器人与具身智能标准化技术委员会举行标准周活动，产业从样机走向批量交付。",
            source="stcn",
            published_at="2026-07-18T07:56:49+08:00",
            url="https://www.stcn.com/article/detail/4027008.html",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
        Event(
            event_id="event-current-ai-data-center-storage-layout",
            first_seen_at="2026-07-18T08:08:02+08:00",
            last_seen_at="2026-07-18T08:08:02+08:00",
            canonical_title="人工智能数据中心储能兴起 多家上市公司积极布局",
            summary="人工智能数据中心储能产品市场需求兴起，头部企业优势凸显，多家上市公司积极布局该赛道。",
            source="stcn",
            published_at="2026-07-18T08:08:02+08:00",
            url="https://www.stcn.com/article/detail/4027039.html",
            event_type="fast_news",
            event_subtype="general_fast_news",
        ),
    ]
    JsonlStore(paths.events_path, Event).write_many(events)
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(event_id="event-current-dongyi-accountant-inquiry-material", direction="neutral", impact_score=80.0, reasoning="rule", themes=[], triggered=True),
            EventAnalysis(event_id="event-current-modern-avenue-audit-committee-opinion", direction="neutral", impact_score=80.0, reasoning="rule", themes=[], triggered=True),
            EventAnalysis(event_id="event-current-modern-avenue-legal-opinion", direction="neutral", impact_score=80.0, reasoning="rule", themes=[], triggered=True),
            EventAnalysis(event_id="event-current-robot-night-raas-story", direction="neutral", impact_score=79.0, reasoning="rule", themes=["机器人"], triggered=True),
            EventAnalysis(event_id="event-current-aoshikang-pcb-process-breakthrough", direction="neutral", impact_score=79.0, reasoning="rule", themes=["PCB"], triggered=True),
            EventAnalysis(event_id="event-current-meta-anthropic-compute-rental", direction="neutral", impact_score=79.0, reasoning="rule", themes=["算力"], triggered=True),
            EventAnalysis(event_id="event-current-telecom-highlander-visit", direction="neutral", impact_score=79.0, reasoning="rule", themes=["算力"], triggered=True),
            EventAnalysis(event_id="event-current-humanoid-robot-output-standard-week", direction="neutral", impact_score=79.0, reasoning="rule", themes=["机器人"], triggered=True),
            EventAnalysis(event_id="event-current-ai-data-center-storage-layout", direction="neutral", impact_score=79.0, reasoning="rule", themes=["算力", "储能"], triggered=True),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "信息披露监管问询函的专项核查说明" not in output
    assert "审计委员会关于《深圳证券交易所对摩登大道" not in output
    assert "年报问询函相关事项的法律意见书" not in output
    assert "机器人奇妙夜" not in output
    assert "超高层埋容混压PCB关键技术突破" not in output
    assert "Meta据悉洽谈向Anthropic出租AI算力" not in output
    assert "中国电信广东分公司到访海兰信" not in output
    assert "人形机器人产量有望超过10万台" not in output
    assert "人工智能数据中心储能兴起" not in output


def test_audit_suspicious_skips_current_inquiry_partial_reply_and_arbitration_fee_question(
    tmp_path, monkeypatch, capsys
) -> None:
    monkeypatch.chdir(tmp_path)
    paths = ProjectPaths.discover()
    JsonlStore(paths.events_path, Event).write_many(
        [
            Event(
                event_id="event-sse-annual-report-inquiry-partial-reply",
                first_seen_at="2026-07-21T00:00:00+08:00",
                last_seen_at="2026-07-21T00:00:00+08:00",
                canonical_title="关于上海证券交易所对公司2025年年度报告的信息披露监管问询函的部分回复公告",
                summary="关于上海证券交易所对公司2025年年度报告的信息披露监管问询函的部分回复公告",
                source="sse",
                published_at="2026-07-21T00:00:00+08:00",
                url="https://example.com/annual-report-inquiry-partial-reply",
                event_type="hard_event",
                event_subtype="corporate_disclosure",
            ),
            Event(
                event_id="event-irm-cninfo-arbitration-fee-question",
                first_seen_at="2026-07-20T21:02:47+08:00",
                last_seen_at="2026-07-20T21:02:47+08:00",
                canonical_title="佳沃食品：截至目前智利仲裁程序已经花了多少总费？预计接下来这个新仲裁还会再产生多少费用？",
                summary="截至目前智利仲裁程序已经花了多少总费？预计接下来这个新仲裁还会再产生多少费用？",
                source="irm_cninfo",
                published_at="2026-07-20T21:02:47+08:00",
                url="https://example.com/arbitration-fee-question",
                event_type="fast_news",
                event_subtype="company_update",
            ),
        ]
    )
    JsonlStore(paths.analyses_path, EventAnalysis).write_many(
        [
            EventAnalysis(
                event_id="event-sse-annual-report-inquiry-partial-reply",
                direction="neutral",
                impact_score=78.5,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
            EventAnalysis(
                event_id="event-irm-cninfo-arbitration-fee-question",
                direction="neutral",
                impact_score=75.2,
                reasoning="rule",
                themes=[],
                triggered=True,
            ),
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "信息披露监管问询函的部分回复公告" not in output
    assert "智利仲裁程序已经花了多少总费" not in output
