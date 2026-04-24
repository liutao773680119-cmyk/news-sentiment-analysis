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
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "*ST仁东：关于对深圳证券交易所2025年年报问询函回复的公告" not in output
    assert "*ST仁东：评估机构关于仁东控股年报问询函有关问题的专项说明" not in output


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
        ]
    )

    assert main(["audit-suspicious", "--limit", "10"]) == 0

    output = capsys.readouterr().out
    assert "suspicious_count=0" in output
    assert "亿道信息：深圳市亿道信息股份有限公司关于深圳证券交易所" not in output


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
