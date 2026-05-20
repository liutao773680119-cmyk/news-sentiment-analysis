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
