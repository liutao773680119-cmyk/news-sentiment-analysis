from news_sentiment.event_merge.core import merge_news_items
from news_sentiment.models import NormalizedNews


def test_merge_news_items_groups_similar_titles() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="fixture",
            source_type="policy",
            published_at="2026-04-01T09:30:00+08:00",
            captured_at="2026-04-01T09:31:00+08:00",
            title="工信部发文支持算力基础设施",
            content="工信部发文支持算力基础设施建设。",
            url="https://example.com/1",
        ),
        NormalizedNews(
            news_id="n2",
            source="fixture",
            source_type="policy",
            published_at="2026-04-01T09:32:00+08:00",
            captured_at="2026-04-01T09:33:00+08:00",
            title="工信部支持算力基础设施建设",
            content="工信部表示支持算力基础设施建设。",
            url="https://example.com/2",
        ),
    ]
    events = merge_news_items(items)
    assert len(events) == 1


def test_merge_news_items_prefers_more_authoritative_source_metadata() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-01T09:29:00+08:00",
            captured_at="2026-04-01T09:29:30+08:00",
            title="证券时报：中科曙光签署算力合作协议",
            content="证券时报快讯称中科曙光签署算力合作协议。",
            url="https://www.stcn.com/article/detail/123456.html",
        ),
        NormalizedNews(
            news_id="n2",
            source="cninfo",
            source_type="hard_event",
            published_at="2026-04-01T09:31:00+08:00",
            captured_at="2026-04-01T09:31:30+08:00",
            title="中科曙光关于签署算力合作协议的公告",
            content="中科曙光关于签署算力合作协议的公告。",
            url="https://www.cninfo.com.cn/new/disclosure/detail?announcementId=123456",
        ),
    ]
    events = merge_news_items(items)
    assert len(events) == 1
    assert events[0].first_seen_at == "2026-04-01T09:29:00+08:00"
    assert events[0].source == "cninfo"
    assert events[0].canonical_title == "中科曙光关于签署算力合作协议的公告"
    assert events[0].event_subtype == "cooperation_agreement"


def test_merge_news_items_does_not_merge_fed_monetary_updates_by_character_overlap() -> None:
    items = [
        NormalizedNews(
            news_id="fed-1",
            source="fed",
            source_type="policy",
            published_at="2026-04-14T18:00:00+00:00",
            captured_at="2026-04-18T01:48:33+00:00",
            title="Minutes of the Board’s discount rate meetings on February 9 and March 18, 2026",
            content="Category: Monetary Policy\nSummary: Minutes of the Board’s discount rate meetings on February 9 and March 18, 2026",
            url="https://www.federalreserve.gov/newsevents/pressreleases/monetary20260414a.htm",
        ),
        NormalizedNews(
            news_id="fed-2",
            source="fed",
            source_type="policy",
            published_at="2026-04-08T18:00:00+00:00",
            captured_at="2026-04-18T01:48:33+00:00",
            title="Minutes of the Federal Open Market Committee, March 17–18, 2026",
            content="Category: Monetary Policy\nSummary: Minutes of the Federal Open Market Committee, March 17–18, 2026",
            url="https://www.federalreserve.gov/newsevents/pressreleases/monetary20260408a.htm",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 2


def test_merge_news_items_classifies_license_agreement_hard_event_as_cooperation_agreement() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="szse",
            source_type="hard_event",
            published_at="2026-04-13T00:00:00+08:00",
            captured_at="2026-04-13T00:00:30+08:00",
            title="海思科：关于与AbbVie签署Nav1.8抑制剂授权许可协议的公告",
            content="公司与AbbVie签署Nav1.8抑制剂授权许可协议。",
            url="https://www.szse.cn/disc/disk03/finalpage/2026-04-13/ad636da8-97bd-46df-a62f-e40774181e59.PDF",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "cooperation_agreement"


def test_merge_news_items_classifies_control_change_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="cninfo",
            source_type="hard_event",
            published_at="2026-04-01T20:00:00+08:00",
            captured_at="2026-04-01T20:00:30+08:00",
            title="关于控股股东签署《股份转让协议》暨控制权拟发生变更的提示性公告",
            content="公司控股股东签署股份转让协议，控制权拟发生变更。",
            url="https://www.cninfo.com.cn/new/disclosure/detail?announcementId=123457",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "control_change"


def test_merge_news_items_classifies_reorganization_risk_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="cninfo",
            source_type="hard_event",
            published_at="2026-04-09T00:00:00+08:00",
            captured_at="2026-04-09T00:00:30+08:00",
            title="美克家居关于控股股东被申请重整的提示性公告",
            content="公司控股股东被申请重整，相关事项存在不确定性。",
            url="https://www.cninfo.com.cn/new/disclosure/detail?stockCode=600337&announcementId=1225085557",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "reorganization_risk"


def test_merge_news_items_classifies_legal_dispute_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="cninfo",
            source_type="hard_event",
            published_at="2026-04-09T00:00:00+08:00",
            captured_at="2026-04-09T00:00:30+08:00",
            title="天奈科技关于商标争议事项进展的公告",
            content="公司披露商标争议事项的最新进展。",
            url="https://www.cninfo.com.cn/new/disclosure/detail?stockCode=688116&announcementId=1225085617",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "legal_dispute"


def test_merge_news_items_classifies_patent_infringement_dispute_as_legal_dispute() -> None:
    items = [
        NormalizedNews(
            news_id="n1p",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-08T19:51:57+08:00",
            captured_at="2026-04-08T19:52:10+08:00",
            title="佰维存储：作为被告涉及两起侵害发明专利权纠纷案件 涉案金额合计5000万元",
            content="公司作为被告涉及两起侵害发明专利权纠纷案件，涉案金额合计5000万元。",
            url="https://www.stcn.com/article/detail/3733099.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "legal_dispute"


def test_merge_news_items_classifies_delisting_risk_notice_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1d",
            source="cninfo",
            source_type="hard_event",
            published_at="2026-04-09T00:00:00+08:00",
            captured_at="2026-04-09T00:00:30+08:00",
            title="关于公司股票交易可能被实施退市风险警示的提示性公告",
            content="公司股票交易可能被实施退市风险警示。",
            url="https://www.cninfo.com.cn/new/disclosure/detail?stockCode=002542&announcementId=1225086578",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "delisting_risk"


def test_merge_news_items_classifies_other_risk_warning_notice_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1dr",
            source="sse",
            source_type="hard_event",
            published_at="2026-04-11T00:00:00+08:00",
            captured_at="2026-04-11T00:00:30+08:00",
            title="天津海泰科技发展股份有限公司关于实施其他风险警示暨停牌的公告",
            content="公司股票将被实施其他风险警示并停牌。",
            url="https://static.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-04-11/600082_20260411_5ZMP.pdf",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "delisting_risk"


def test_merge_news_items_classifies_out_of_court_reorganization_as_reorganization_risk() -> None:
    items = [
        NormalizedNews(
            news_id="n1or",
            source="szse",
            source_type="hard_event",
            published_at="2026-04-11T00:00:00+08:00",
            captured_at="2026-04-11T00:00:30+08:00",
            title="美丽生态：关于对子公司同步开展庭外重组工作的公告",
            content="公司拟对子公司同步开展庭外重组工作，相关事项存在不确定性。",
            url="https://www.szse.cn/disc/disk03/finalpage/2026-04-11/14db6489-2bd4-463e-a8e1-3c6e9ed69a63.PDF",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "reorganization_risk"


def test_merge_news_items_classifies_bankruptcy_liquidation_application_as_reorganization_risk() -> None:
    items = [
        NormalizedNews(
            news_id="n1bl",
            source="sse",
            source_type="hard_event",
            published_at="2026-04-13T00:00:00+08:00",
            captured_at="2026-04-13T00:00:30+08:00",
            title="关于公司下属公司申请破产清算的公告",
            content="公司下属公司申请破产清算，相关事项存在不确定性。",
            url="https://static.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-04-13/600981_20260413_UTEJ.pdf",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "reorganization_risk"


def test_merge_news_items_classifies_executive_departure_disclosure_as_executive_change() -> None:
    items = [
        NormalizedNews(
            news_id="n1e",
            source="cninfo",
            source_type="hard_event",
            published_at="2026-04-10T00:00:00+08:00",
            captured_at="2026-04-10T00:00:30+08:00",
            title="苏州锴威特半导体股份有限公司关于公司高级管理人员离任的公告",
            content="公司高级管理人员因个人原因离任。",
            url="https://www.cninfo.com.cn/new/disclosure/detail?stockCode=688693&announcementId=1225090949",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "executive_change"


def test_merge_news_items_classifies_hkex_profit_warning_as_business_guidance() -> None:
    items = [
        NormalizedNews(
            news_id="n1hkpw",
            source="hkex",
            source_type="hard_event",
            published_at="2026-04-17T21:00:00+08:00",
            captured_at="2026-04-17T21:00:30+08:00",
            title="PROFIT WARNING",
            content="PROFIT WARNING",
            url="https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0417/example-profit-warning.pdf",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "business_guidance"


def test_merge_news_items_classifies_hkex_change_of_directors_as_executive_change() -> None:
    items = [
        NormalizedNews(
            news_id="n1hked",
            source="hkex",
            source_type="hard_event",
            published_at="2026-04-17T21:24:00+08:00",
            captured_at="2026-04-17T21:24:30+08:00",
            title="CHANGE OF DIRECTORS RE-DESIGNATION OF DIRECTOR AND CHANGE IN COMPOSITION OF BOARD COMMITTEES",
            content="CHANGE OF DIRECTORS RE-DESIGNATION OF DIRECTOR AND CHANGE IN COMPOSITION OF BOARD COMMITTEES",
            url="https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0417/example-director-change.pdf",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "executive_change"


def test_merge_news_items_classifies_hkex_very_substantial_connected_transaction_as_acquisition_restructuring() -> None:
    items = [
        NormalizedNews(
            news_id="n1hktx",
            source="hkex",
            source_type="hard_event",
            published_at="2026-04-10T22:55:00+08:00",
            captured_at="2026-04-10T22:55:30+08:00",
            title="(1) Very Substantial Disposal and Connected Transaction - Disposal of a Subsidiary",
            content="(1) Very Substantial Disposal and Connected Transaction - Disposal of a Subsidiary",
            url="https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0410/example-transaction.pdf",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "acquisition_restructuring"


def test_merge_news_items_does_not_merge_unrelated_hkex_english_disclosures_by_character_overlap() -> None:
    items = [
        NormalizedNews(
            news_id="n1hkmd",
            source="hkex",
            source_type="hard_event",
            published_at="2026-04-17T21:26:00+08:00",
            captured_at="2026-04-17T21:26:30+08:00",
            title="LIST OF DIRECTORS AND THEIR ROLES AND FUNCTIONS",
            content="LIST OF DIRECTORS AND THEIR ROLES AND FUNCTIONS",
            url="https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0417/example-directors.pdf",
        ),
        NormalizedNews(
            news_id="n1hkpw",
            source="hkex",
            source_type="hard_event",
            published_at="2026-04-17T21:00:00+08:00",
            captured_at="2026-04-17T21:00:30+08:00",
            title="PROFIT WARNING",
            content="PROFIT WARNING",
            url="https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0417/example-profit-warning.pdf",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 2


def test_merge_news_items_classifies_hkex_inside_information_winding_up_petition_as_reorganization_risk() -> None:
    items = [
        NormalizedNews(
            news_id="n1hkiw",
            source="hkex",
            source_type="hard_event",
            published_at="2026-04-17T18:42:00+08:00",
            captured_at="2026-04-17T18:42:30+08:00",
            title="INSIDE INFORMATION - UPDATE ON WINDING UP PETITION",
            content="INSIDE INFORMATION - UPDATE ON WINDING UP PETITION",
            url="https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0417/example-winding-up.pdf",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "reorganization_risk"


def test_merge_news_items_classifies_hkex_inside_information_arbitration_as_legal_dispute() -> None:
    items = [
        NormalizedNews(
            news_id="n1hkia",
            source="hkex",
            source_type="hard_event",
            published_at="2026-04-16T17:29:00+08:00",
            captured_at="2026-04-16T17:29:30+08:00",
            title="INSIDE INFORMATION IN RELATION TO ARBITRATION PROCEEDINGS",
            content="INSIDE INFORMATION IN RELATION TO ARBITRATION PROCEEDINGS",
            url="https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0416/example-arbitration.pdf",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "legal_dispute"


def test_merge_news_items_classifies_market_move_fast_news_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-01T14:10:00+08:00",
            captured_at="2026-04-01T14:10:10+08:00",
            title="创业板指跌超2%",
            content="创业板指跌超2%，机器人概念股回调。",
            url="https://www.stcn.com/article/detail/999999.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "market_move"


def test_merge_news_items_classifies_opening_market_commentary_as_market_move() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-08T09:27:29+08:00",
            captured_at="2026-04-08T09:27:40+08:00",
            title="开评：三大指数集体高开 创业板指涨3.07%",
            content="人民财讯4月8日电，4月8日，三大指数集体高开，沪指涨1.03%，深证成指涨2.36%，创业板指涨3.07%。盘面上，有色、半导体、通信设备、元器件等板块涨幅居前；石油、煤炭、多元金融、供气供热等板块跌幅居前。",
            url="https://www.stcn.com/article/detail/3731324.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "market_move"


def test_merge_news_items_does_not_classify_generic_business_breakthrough_as_market_move() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T19:05:06+08:00",
            captured_at="2026-04-02T19:05:10+08:00",
            title="招商公路：2025年净利润同比下降13.38% 拟10派3.73元",
            content="报告期内，招商公路交通科技板块新签合同额突破41亿元、逆势增长10.67%。",
            url="https://www.stcn.com/article/detail/3723970.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype != "market_move"


def test_merge_news_items_classifies_policy_signal_fast_news_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T13:02:32+08:00",
            captured_at="2026-04-02T13:02:40+08:00",
            title="四川：到2027年底在全省范围内建成205万个充电设施",
            content="四川省发展和改革委员会等部门印发《四川省电动汽车充电设施服务能力倍增行动方案》。",
            url="https://www.stcn.com/article/detail/3722999.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "policy_signal"


def test_merge_news_items_classifies_authority_statement_fast_news_as_policy_signal() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-03T14:34:22+08:00",
            captured_at="2026-04-03T14:34:30+08:00",
            title="国家国防科技工业局于国斌：要深刻认识发展太空算力的战略意义",
            content="人民财讯4月3日电，国家国防科技工业局商业航天司副司长于国斌4月3日在2026太空算力产业大会上表示，要深刻认识发展太空算力的战略意义。",
            url="https://www.stcn.com/article/detail/3726229.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "policy_signal"


def test_merge_news_items_classifies_industry_project_release_fast_news_as_policy_signal() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-03T15:23:58+08:00",
            captured_at="2026-04-03T15:24:10+08:00",
            title="2026太空算力产业大会发布十大重点攻关项目",
            content="4月3日，在2026太空算力产业大会上，算力产业发展方阵“太空算力专业委员会”成立。大会当天发布十大重点攻关项目，将联合产业界开展攻关合作。",
            url="https://www.stcn.com/article/detail/3726318.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "policy_signal"


def test_merge_news_items_classifies_policy_measure_fast_news_as_policy_signal() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-08T10:16:17+08:00",
            captured_at="2026-04-08T10:16:30+08:00",
            title="北京推出32条创新医药高质量发展措施",
            content="人民财讯4月8日电，北京市有关部门推出32条创新医药高质量发展措施，加快创新药和高端医疗器械产业发展。",
            url="https://www.stcn.com/article/detail/3731685.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "policy_signal"


def test_merge_news_items_does_not_treat_breach_notice_as_policy_signal() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-04T11:16:21+08:00",
            captured_at="2026-04-04T11:16:30+08:00",
            title="小鹏回应澳大利亚独家经销商合作破裂",
            content="人民财讯4月4日电，小鹏依据合作协议约定，正式向TrueEV发出违约通知，终止其独家代理资格。",
            url="https://www.stcn.com/article/detail/3727875.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "company_update"


def test_merge_news_items_does_not_treat_order_obligation_dispute_as_order_contract() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-04T11:16:21+08:00",
            captured_at="2026-04-04T11:16:30+08:00",
            title="小鹏回应澳大利亚独家经销商合作破裂",
            content="人民财讯4月4日电，近日，小鹏澳洲独家代理TrueEV进入托管（破产管理）程序，引起关注。小鹏方面回应记者，在过去两年合作期间，小鹏通过多方渠道了解到，TrueEV已发生资金链断裂并被融资方接管，且持续超过一年未进行车辆采购，同时未能履行包括454台汽车在内的订单义务。TrueEV还与当地经销商发生公开商业冲突，导致双方信任基础严重受损。因此，小鹏依据合作协议约定，正式向TrueEV发出违约通知，终止其独家代理资格，但保留代理身份。但TrueEV否认存在上述运营问题，转而通过法律程序向小鹏提出诉求。澳大利亚当地法院已于4月1日驳回了其相关禁令申请。",
            url="https://www.stcn.com/article/detail/3727875.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "company_update"


def test_merge_news_items_treats_response_to_cooperation_rumor_as_company_update() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-04T11:30:00+08:00",
            captured_at="2026-04-04T11:30:10+08:00",
            title="公司回应签署算力合作协议传闻",
            content="人民财讯4月4日电，公司回应记者称，与相关方签署的是框架合作协议，仅用于技术交流，不涉及具体订单，不存在应披露而未披露事项。",
            url="https://www.stcn.com/article/detail/3727999.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "company_update"


def test_merge_news_items_treats_business_progress_with_undisclosed_order_data_as_company_update() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-09T12:24:38+08:00",
            captured_at="2026-04-09T12:24:48+08:00",
            title="信维通信：公司商业航天业务进展顺利",
            content="人民财讯4月9日电，信维通信4月9日在互动平台表示，公司商业航天业务进展顺利，具体订单数据因涉及商业保密协议不便公开披露。",
            url="https://www.stcn.com/article/detail/3734470.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "company_update"


def test_merge_news_items_keeps_real_order_contract_fast_news_as_order_contract() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T20:40:00+08:00",
            captured_at="2026-04-02T20:40:10+08:00",
            title="中科曙光：签订10亿元算力订单",
            content="人民财讯4月2日电，公司与客户签订10亿元算力订单，将分阶段完成交付。",
            url="https://example.com/fast-contract",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "order_contract"


def test_merge_news_items_does_not_treat_geopolitical_response_as_company_update() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-08T13:49:45+08:00",
            captured_at="2026-04-08T13:49:55+08:00",
            title="韩日称朝鲜再次发射不明弹道导弹 朝方暂无回应",
            content="人民财讯4月8日电，据韩联社、日本共同社报道，韩国军方和日本防卫省称朝鲜再次发射不明弹道导弹，朝方暂未作出回应。",
            url="https://www.stcn.com/article/detail/3732161.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "general_fast_news"


def test_merge_news_items_classifies_company_setup_fast_news_as_company_update() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-08T14:39:37+08:00",
            captured_at="2026-04-08T14:39:47+08:00",
            title="琏升科技成立数字科技公司 含AI及卫星相关业务",
            content="人民财讯4月8日电，企查查APP显示，近日，成都琏升数字科技有限公司成立，经营范围包含人工智能应用软件开发、卫星技术综合应用系统集成等。",
            url="https://www.stcn.com/article/detail/3732239.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "company_update"


def test_merge_news_items_does_not_treat_broker_allocation_commentary_as_market_move() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-08T15:10:24+08:00",
            captured_at="2026-04-08T15:10:34+08:00",
            title="瑞银：近期可采取平衡型配置 避免大幅调仓",
            content="人民财讯4月8日电，美伊达成临时停火协议的消息公布后，国际油价大幅跳水，WTI原油期货价格大跌超10%。瑞银财富管理投资总监办公室指出，投资者可以考虑采取平衡型配置，而非押注地缘政治事件的走向，并避免仓促大幅调整战略资产配置。",
            url="https://www.stcn.com/article/detail/3732323.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "general_fast_news"


def test_merge_news_items_classifies_equity_investment_fast_news_as_company_update() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-08T15:09:32+08:00",
            captured_at="2026-04-08T15:09:42+08:00",
            title="蔚来资本、国君创投等入股灵猴机器人",
            content="人民财讯4月8日电，企查查APP显示，近日，苏州灵猴机器人有限公司发生工商变更，新增蔚来资本、国君创投等为股东，同时注册资本由1.26亿元增至约1.41亿元。",
            url="https://www.stcn.com/article/detail/3732313.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "company_update"


def test_merge_news_items_classifies_tech_breakthrough_fast_news_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T13:18:30+08:00",
            captured_at="2026-04-02T13:18:35+08:00",
            title="科学家实现DNA安全加密实景测试",
            content="研究人员开发出一种基于DNA的安全加密方案并完成真实场景测试。",
            url="https://www.stcn.com/article/detail/3723007.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "tech_breakthrough"


def test_merge_news_items_classifies_industry_data_fast_news_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T13:27:31+08:00",
            captured_at="2026-04-02T13:27:40+08:00",
            title="Sora退出 可灵AI周度活跃用户环比增长",
            content="数据显示，可灵AI周活跃用户环比增长4%，月活跃用户达780万。",
            url="https://www.stcn.com/article/detail/3723013.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "industry_data"


def test_merge_news_items_classifies_colon_prefixed_industry_data_fast_news_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-03T16:45:32+08:00",
            captured_at="2026-04-03T16:45:40+08:00",
            title="乘联分会：1—2月中国汽车出口155万辆 同比增长61%",
            content="乘联分会：2026年1-2月中国汽车实现出口155万辆，同比2025年同期增速61%。2026年2月中国新能源汽车出口32万辆，同比增长120%。",
            url="https://www.stcn.com/article/detail/3726758.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "industry_data"


def test_merge_news_items_classifies_regional_industrial_output_growth_as_industry_data() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-13T22:11:54+08:00",
            captured_at="2026-04-13T22:12:00+08:00",
            title="上海：今年前两个月三大先导产业制造业产值增长13.8%",
            content="人民财讯4月13日电，记者从13日在上海举行的国新办中外记者见面会上了解到，上海新产业、新业态、新动能加快成长，新质生产力培育壮大，今年前两个月，人工智能、集成电路、生物医药三大先导产业制造业产值增长13.8%。",
            url="https://www.stcn.com/article/detail/3745834.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "industry_data"


def test_merge_news_items_classifies_forecast_production_growth_fast_news_as_industry_data() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-09T14:00:30+08:00",
            captured_at="2026-04-09T14:00:40+08:00",
            title="集邦咨询：预估2026年中国人形机器人市场产量将年增94%",
            content="根据TrendForce集邦咨询最新研究报告，预估2026年中国人形机器人市场产量将年增94%，商业化进程提速。",
            url="https://www.stcn.com/article/detail/3734553.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "industry_data"


def test_merge_news_items_classifies_material_price_story_as_industry_data() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-08T13:08:38+08:00",
            captured_at="2026-04-08T13:08:50+08:00",
            title="芯片“基石”价格大涨 半导体材料景气度值得期待",
            content="人民财讯4月8日电，2026年第一季度，电子靶材企业已普遍启动提价，其中常规靶材价格涨幅达20%，特殊小金属类靶材涨幅更是达到60%—70%。半导体材料行业的景气度也值得期待。",
            url="https://www.stcn.com/article/detail/3732041.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "industry_data"


def test_merge_news_items_classifies_model_usage_rank_fast_news_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-04T10:44:37+08:00",
            captured_at="2026-04-04T10:44:45+08:00",
            title="千问3.6Plus大模型登顶全球模型调用排行榜首，日调用量破万亿",
            content="发布仅1天的千问新模型Qwen3.6-Plus，冲上全球知名大模型API调用平台OpenRouter的日榜榜首，日调用量突破1.4万亿Token。",
            url="https://www.stcn.com/article/detail/3727870.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "industry_data"


def test_merge_news_items_classifies_business_guidance_fast_news_subtype() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T12:57:03+08:00",
            captured_at="2026-04-02T12:57:10+08:00",
            title="安科生物：2026年曲妥珠单抗销售目标仍是收入及利润大幅增长",
            content="公司在电话会议上表示，2026年销售目标仍是收入、利润双双大幅增长。此前产品已获批上市。",
            url="https://www.stcn.com/article/detail/3722993.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "business_guidance"


def test_merge_news_items_classifies_share_acquisition_resume_trading_fast_news_as_acquisition_restructuring() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-09T20:03:48+08:00",
            captured_at="2026-04-09T20:03:58+08:00",
            title="睿能科技：拟收购博泰智能75%股权 股票明起复牌",
            content="人民财讯4月9日电，睿能科技公告称，拟以发行股份及支付现金的方式收购博泰智能75%股权，公司股票将于明日起复牌。",
            url="https://www.stcn.com/article/detail/3735652.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "acquisition_restructuring"


def test_merge_news_items_classifies_profit_preview_with_downstream_industry_context_as_business_guidance() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-09T19:43:54+08:00",
            captured_at="2026-04-09T19:44:00+08:00",
            title="中钨高新：一季度净利润同比预增256%—276%",
            content="人民财讯4月9日电，中钨高新(000657)4月9日公告，预计2026年第一季度净利润为9亿元—9.5亿元，比上年同期增长256%—276%（重述后）。报告期内，受钨原料市场整体供给偏紧、下游需求旺盛等因素影响，钨原料价格大幅上涨，销量同步增长；同时，公司依托全产业链优势，有效实现价格传导，叠加工程机械、高端制造下游行业需求上升，硬质合金产品订单稳步增长，实现量价齐升，显著提升整体盈利水平。",
            url="https://www.stcn.com/article/detail/3735545.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "business_guidance"


def test_merge_news_items_classifies_drug_registration_fast_news_as_regulatory_approval() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-03T16:59:02+08:00",
            captured_at="2026-04-03T16:59:10+08:00",
            title="华海药业：美沙拉秦肠溶片获得药品注册证书",
            content="公司于近日收到国家药品监督管理局核准签发的美沙拉秦肠溶片的《药品注册证书》。",
            url="https://www.stcn.com/article/detail/3726793.html",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "regulatory_approval"


def test_merge_news_items_groups_market_move_updates_for_same_asset() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T13:49:59+08:00",
            captured_at="2026-04-02T13:50:05+08:00",
            title="现货黄金日内跌幅扩大至3%",
            content="现货黄金日内跌幅扩大至3%，现货白银日内跌幅扩大至6%。",
            url="https://www.stcn.com/article/detail/3723028.html",
        ),
        NormalizedNews(
            news_id="n2",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T13:53:04+08:00",
            captured_at="2026-04-02T13:53:10+08:00",
            title="现货黄金跌破4600美元/盎司",
            content="现货黄金跌破4600美元/盎司，日内跌3.33%。",
            url="https://www.stcn.com/article/detail/3723032.html",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].first_seen_at == "2026-04-02T13:49:59+08:00"
    assert set(events[0].member_news_ids) == {"n1", "n2"}
    assert events[0].event_subtype == "market_move"


def test_merge_news_items_does_not_group_market_move_updates_for_different_assets() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T13:49:59+08:00",
            captured_at="2026-04-02T13:50:05+08:00",
            title="现货黄金日内跌幅扩大至3%",
            content="现货黄金日内跌幅扩大至3%。",
            url="https://www.stcn.com/article/detail/3723028.html",
        ),
        NormalizedNews(
            news_id="n2",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-02T13:56:55+08:00",
            captured_at="2026-04-02T13:57:02+08:00",
            title="沪指跌幅扩大至1%",
            content="沪指跌幅扩大至1%，深证成指跌1.87%。",
            url="https://www.stcn.com/article/detail/3723042.html",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 2


def test_merge_news_items_classifies_gold_touch_price_fast_news_as_market_move() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="cls",
            source_type="fast_news",
            published_at="2026-04-14T21:39:36+08:00",
            captured_at="2026-04-14T21:39:40+08:00",
            title="财联社4月14日电，现货黄金向上触及4800美元，日内上涨1.28%。",
            content="财联社4月14日电，现货黄金向上触及4800美元，日内上涨1.28%。",
            url="https://www.cls.cn/detail/2344033",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "market_move"


def test_merge_news_items_classifies_cls_overnight_roundup_as_general_fast_news() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="cls",
            source_type="fast_news",
            published_at="2026-04-15T06:31:03+08:00",
            captured_at="2026-04-15T06:31:10+08:00",
            title="周三你需要知道的隔夜全球要闻：以黎同意将启动直接谈判；特朗普称与伊朗会谈“可能未来两天内”举行；霍尔木兹海峡恢复部分通航 美军封锁伊朗港口持续；国际原油下挫 美股纳指十连涨",
            content="国际原油期货收盘下挫，WTI原油期货结算价收跌7.87%，美股三大指数集体收涨，道指涨0.66%，纳指涨1.96%。",
            url="https://www.cls.cn/detail/2344207",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "general_fast_news"


def test_merge_news_items_does_not_classify_optical_communication_feature_story_as_market_move() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="cls",
            source_type="fast_news",
            published_at="2026-04-15T06:20:13+08:00",
            captured_at="2026-04-15T06:20:20+08:00",
            title="光通信进入可持续景气周期 产业链多环节成长空间打开",
            content="近日，美国光通信龙头Lumentum表示，美国巨型AI数据中心对其光通信组件的需求正在加速增长。这家获得英伟达投资的公司，其股价过去一年上涨超过1500%。",
            url="https://www.cls.cn/detail/2344212",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype != "market_move"


def test_merge_news_items_groups_structured_cninfo_catalyst_documents() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="cninfo",
            source_type="hard_event",
            published_at="2026-04-02T11:44:27+08:00",
            captured_at="2026-04-02T11:44:30+08:00",
            title="北京市天元律师事务所关于探路者控股集团股份有限公司向特定对象发行A股股票的法律意见",
            content="北京市天元律师事务所关于探路者控股集团股份有限公司向特定对象发行A股股票的法律意见",
            url="https://www.cninfo.com.cn/new/disclosure/detail?stockCode=300005&announcementId=1225073842",
        ),
        NormalizedNews(
            news_id="n2",
            source="cninfo",
            source_type="hard_event",
            published_at="2026-04-02T11:44:27+08:00",
            captured_at="2026-04-02T11:44:31+08:00",
            title="关于2025年度向特定对象发行A股股票申请获得深圳证券交易所受理的公告",
            content="关于2025年度向特定对象发行A股股票申请获得深圳证券交易所受理的公告",
            url="https://www.cninfo.com.cn/new/disclosure/detail?stockCode=300005&announcementId=1225073837",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert set(events[0].member_news_ids) == {"n1", "n2"}
    assert events[0].event_subtype == "financing_acceptance"
