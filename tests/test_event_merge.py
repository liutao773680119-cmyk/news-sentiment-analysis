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


def test_merge_news_items_does_not_merge_ecb_press_releases_by_character_overlap() -> None:
    items = [
        NormalizedNews(
            news_id="ecb-1",
            source="ecb",
            source_type="policy",
            published_at="2026-04-14T11:00:00+02:00",
            captured_at="2026-04-18T12:14:51+00:00",
            title="ECB Governing Council urges Single Market boost to strengthen bank competitiveness",
            content="ECB Governing Council urges Single Market boost to strengthen bank competitiveness",
            url="https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.pr260414~ad43db8bb6.en.html",
        ),
        NormalizedNews(
            news_id="ecb-2",
            source="ecb",
            source_type="policy",
            published_at="2026-03-31T10:00:00+02:00",
            captured_at="2026-04-18T12:14:51+00:00",
            title="Eurosystem sets out comprehensive strategy for future of European payments",
            content="Eurosystem sets out comprehensive strategy for future of European payments",
            url="https://www.ecb.europa.eu/press/pr/date/2026/html/ecb.pr260331~04561d8476.en.html",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 2


def test_merge_news_items_does_not_merge_boe_news_by_character_overlap() -> None:
    items = [
        NormalizedNews(
            news_id="boe-1",
            source="boe",
            source_type="policy",
            published_at="2026-04-13T11:00:00+01:00",
            captured_at="2026-04-18T12:14:51+00:00",
            title="Bank of England enhances resolution readiness with updated operational guides",
            content="The Bank of England has today published new and updated guidance on how the Bank might implement the UK’s resolution regime in the event of a bank failure.",
            url="https://www.bankofengland.co.uk/news/2026/april/boe-enhances-resolution-readiness-with-updated-operational-guides",
        ),
        NormalizedNews(
            news_id="boe-2",
            source="boe",
            source_type="policy",
            published_at="2026-04-02T09:30:00+01:00",
            captured_at="2026-04-18T12:14:51+00:00",
            title="Changes to publication dates of the Decision Maker Panel data and Agents’ summary of business conditions",
            content="We are changing the publication dates of the Decision Maker Panel and Agents’ summary of business conditions so that they no longer fall on the same day as publication of the Monetary Policy Report.",
            url="https://www.bankofengland.co.uk/news/2026/april/changes-to-publication-dates-of-the-decision-maker-panel-data-and-agents-summary",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 2


def test_merge_news_items_does_not_merge_boc_press_releases_by_character_overlap() -> None:
    items = [
        NormalizedNews(
            news_id="boc-1",
            source="boc_press",
            source_type="policy",
            published_at="2026-03-18T09:47:23+00:00",
            captured_at="2026-04-18T12:14:51+00:00",
            title="Bank of Canada maintains policy rate at 2 1/4%",
            content="The Bank of Canada today held its target for the overnight rate at 2.25%.",
            url="https://www.bankofcanada.ca/2026/03/fad-press-release-2026-03-18/",
        ),
        NormalizedNews(
            news_id="boc-2",
            source="boc_press",
            source_type="policy",
            published_at="2026-01-28T09:47:56+00:00",
            captured_at="2026-04-18T12:14:51+00:00",
            title="Bank of Canada maintains policy rate at 2 1/4%",
            content="The Bank of Canada today held its target for the overnight rate at 2.25%.",
            url="https://www.bankofcanada.ca/2026/01/fad-press-release-2026-01-28/",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 2


def test_merge_news_items_does_not_merge_boj_policy_documents_by_character_overlap() -> None:
    items = [
        NormalizedNews(
            news_id="boj-1",
            source="boj",
            source_type="policy",
            published_at="2026-03-30T08:50:00+09:00",
            captured_at="2026-04-18T12:14:51+00:00",
            title="金融政策決定会合における主な意見（3月18、19日開催分）",
            content="金融政策決定会合における主な意見（3月18、19日開催分）",
            url="http://www.boj.or.jp/mopo/mpmsche_minu/opinion_2026/opi260319.pdf",
        ),
        NormalizedNews(
            news_id="boj-2",
            source="boj",
            source_type="policy",
            published_at="2026-03-25T08:50:00+09:00",
            captured_at="2026-04-18T12:14:51+00:00",
            title="金融政策決定会合議事要旨（1月22、23日開催分）",
            content="金融政策決定会合議事要旨（1月22、23日開催分）",
            url="http://www.boj.or.jp/mopo/mpmsche_minu/minu_2026/g260123.pdf",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 2


def test_merge_news_items_does_not_merge_fedreg_sec_documents_by_character_overlap() -> None:
    items = [
        NormalizedNews(
            news_id="fedreg-1",
            source="fedreg_sec",
            source_type="policy",
            published_at="2026-04-20T00:00:00+00:00",
            captured_at="2026-04-18T12:14:51+00:00",
            title="Concept Release on Consolidated Audit Trail and Other Audit Trails and Data Sources",
            content="Type: Proposed Rule\nAbstract: The Securities and Exchange Commission is publishing this concept release.",
            url="https://www.federalregister.gov/documents/2026/04/20/2026-07651/concept-release-on-consolidated-audit-trail-and-other-audit-trails-and-data-sources",
        ),
        NormalizedNews(
            news_id="fedreg-2",
            source="fedreg_sec",
            source_type="policy",
            published_at="2026-04-20T00:00:00+00:00",
            captured_at="2026-04-18T12:14:51+00:00",
            title="Sunshine Act Meetings",
            content="Type: Notice",
            url="https://www.federalregister.gov/documents/2026/04/20/2026-07650/sunshine-act-meetings",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 2


def test_merge_news_items_does_not_merge_bis_press_releases_by_character_overlap() -> None:
    items = [
        NormalizedNews(
            news_id="bis-1",
            source="bis",
            source_type="policy",
            published_at="2026-04-16T12:47:00+00:00",
            captured_at="2026-04-18T12:14:51+00:00",
            title="CPMI-IOSCO assesses that the United Kingdom has implemented the Principles for financial market infrastructures for two FMI types, but recommends some improvements",
            content="The UK's framework is complete and consistent with the PFMI in most aspects.",
            url="https://www.bis.org/press/p260416.htm",
        ),
        NormalizedNews(
            news_id="bis-2",
            source="bis",
            source_type="policy",
            published_at="2026-03-27T09:03:00+00:00",
            captured_at="2026-04-18T12:14:51+00:00",
            title="BIS extends term for John Williams as Chair of the Markets Committee",
            content="John C. Williams is to continue as Chair of the Markets Committee.",
            url="https://www.bis.org/press/p260327.htm",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 2


def test_merge_news_items_does_not_merge_sec_press_releases_by_character_overlap() -> None:
    items = [
        NormalizedNews(
            news_id="sec-1",
            source="sec_press",
            source_type="policy",
            published_at="2026-04-16T17:02:47+00:00",
            captured_at="2026-04-19T05:26:00+00:00",
            title="Chairman Atkins Launches 'Material Matters' Podcast",
            content="Summary: The Securities and Exchange Commission today announced the launch of Material Matters With SEC Chairman Paul Atkins.",
            url="https://www.sec.gov/newsroom/press-releases/2026-39-chairman-atkins-launches-material-matters-podcast",
        ),
        NormalizedNews(
            news_id="sec-2",
            source="sec_press",
            source_type="policy",
            published_at="2026-04-16T15:45:04+00:00",
            captured_at="2026-04-19T05:26:00+00:00",
            title="SEC Small Business Advisory Committee to Explore Ways to Encourage More IPOs",
            content="Summary: The Securities and Exchange Commission's Small Business Capital Formation Advisory Committee announced that it will hold a meeting.",
            url="https://www.sec.gov/newsroom/press-releases/2026-38-sec-small-business-advisory-committee-explore-ways-encourage-more-ipos",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 2


def test_merge_news_items_does_not_merge_cftc_press_releases_by_character_overlap() -> None:
    items = [
        NormalizedNews(
            news_id="cftc-1",
            source="cftc_press",
            source_type="policy",
            published_at="2026-04-17T14:00:02+00:00",
            captured_at="2026-04-19T05:40:00+00:00",
            title="CFTC and Kansas State University Announce Return of AgCon Conference",
            content="CFTC and Kansas State University Announce Return of AgCon Conference",
            url="https://www.cftc.gov/PressRoom/PressReleases/9215-26",
        ),
        NormalizedNews(
            news_id="cftc-2",
            source="cftc_press",
            source_type="policy",
            published_at="2026-04-15T18:42:19+00:00",
            captured_at="2026-04-19T05:40:00+00:00",
            title="CFTC Approves Order to Further Strengthen U.S. Treasury Market Liquidity",
            content="CFTC Approves Order to Further Strengthen U.S. Treasury Market Liquidity",
            url="https://www.cftc.gov/PressRoom/PressReleases/9214-26",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 2


def test_merge_news_items_does_not_merge_occ_news_releases_by_character_overlap() -> None:
    items = [
        NormalizedNews(
            news_id="occ-1",
            source="occ_news",
            source_type="policy",
            published_at="2026-04-16T11:00:00-04:00",
            captured_at="2026-04-19T05:45:00+00:00",
            title="OCC Announces Enforcement Actions for April 2026",
            content="Summary: The Office of the Comptroller of the Currency (OCC) today released enforcement actions for April 2026.",
            url="https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-28.html",
        ),
        NormalizedNews(
            news_id="occ-2",
            source="occ_news",
            source_type="policy",
            published_at="2026-04-07T17:32:46-04:00",
            captured_at="2026-04-19T05:45:00+00:00",
            title="Comptroller Statement on Final Rule Eliminating Reputation Risk from Bank Supervision",
            content="Summary: Comptroller of the Currency Jonathan V. Gould issued the following statement today.",
            url="https://www.occ.gov/news-issuances/news-releases/2026/nr-occ-2026-27.html",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 2


def test_merge_news_items_does_not_merge_investing_feeds_by_character_overlap() -> None:
    items = [
        NormalizedNews(
            news_id="investing-news-1",
            source="investing_news",
            source_type="fast_news",
            published_at="2026-04-18T21:20:03+00:00",
            captured_at="2026-04-19T03:00:00+00:00",
            title="Russia stocks lower at close of trade; MOEX Russia Index unchanged",
            content="Russia stocks lower at close of trade; MOEX Russia Index unchanged",
            url="https://www.investing.com/news/stock-market-news/russia-stocks-lower-at-close-of-trade-moex-russia-index-unchanged-4622176",
        ),
        NormalizedNews(
            news_id="investing-forex-1",
            source="investing_forex",
            source_type="fast_news",
            published_at="2026-04-17T09:07:06+00:00",
            captured_at="2026-04-19T03:00:00+00:00",
            title="Go long HUF/USD, BCA says",
            content="Go long HUF/USD, BCA says",
            url="https://www.investing.com/news/forex-news/go-long-hufusd-bca-says-93CH-4619815",
        ),
        NormalizedNews(
            news_id="investing-economic-1",
            source="investing_economic",
            source_type="fast_news",
            published_at="2026-04-17T08:07:48+00:00",
            captured_at="2026-04-19T03:00:00+00:00",
            title="Italy’s February trade surplus widens to €4.94 billion",
            content="Italy’s February trade surplus widens to €4.94 billion",
            url="https://www.investing.com/news/economic-indicators/italys-february-trade-surplus-widens-to-494-billion-93CH-4619779",
        ),
    ]

    events = merge_news_items(items)

    assert len(events) == 3


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


def test_merge_news_items_classifies_csrs_filing_notice_as_legal_dispute() -> None:
    items = [
        NormalizedNews(
            news_id="n1reg",
            source="sse",
            source_type="hard_event",
            published_at="2026-04-21T00:00:00+08:00",
            captured_at="2026-04-21T00:00:30+08:00",
            title="上海太和水科技发展股份有限公司关于收到中国证券监督管理委员会立案告知书的公告",
            content="公司收到中国证券监督管理委员会立案告知书。",
            url="https://www.sse.com.cn/disclosure/listedinfo/announcement/c/new/2026-04-21/example.pdf",
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


def test_merge_news_items_classifies_upc_patent_litigation_as_legal_dispute() -> None:
    items = [
        NormalizedNews(
            news_id="n1upc",
            source="szse",
            source_type="hard_event",
            published_at="2026-04-21T00:00:00+08:00",
            captured_at="2026-04-21T00:00:30+08:00",
            title="三诺生物：关于与雅培就EP3988471专利在UPC诉讼的公告",
            content="公司与雅培就EP3988471专利在UPC诉讼。",
            url="https://www.szse.cn/disc/disk03/finalpage/2026-04-21/0ee14919-0660-4b22-82cc-9abd1fb95e66.PDF",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "legal_dispute"


def test_merge_news_items_classifies_arbitration_award_challenge_as_legal_dispute() -> None:
    items = [
        NormalizedNews(
            news_id="n1arb",
            source="szse",
            source_type="hard_event",
            published_at="2026-04-21T00:00:00+08:00",
            captured_at="2026-04-21T00:00:30+08:00",
            title="德展健康：关于美林控股业绩承诺补偿履行情况进展暨美林控股申请撤销仲裁裁决的公告",
            content="公司披露美林控股申请撤销仲裁裁决的进展。",
            url="https://www.szse.cn/disc/disk03/finalpage/2026-04-21/example.pdf",
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


def test_merge_news_items_classifies_hkex_h_share_full_circulation_as_capital_operation() -> None:
    items = [
        NormalizedNews(
            news_id="n1hkifc",
            source="hkex",
            source_type="hard_event",
            published_at="2026-04-17T19:50:00+08:00",
            captured_at="2026-04-17T19:50:30+08:00",
            title="INSIDE INFORMATION COMPLETION OF THE H SHARE FULL CIRCULATION BY THE COMPANY",
            content="INSIDE INFORMATION COMPLETION OF THE H SHARE FULL CIRCULATION BY THE COMPANY",
            url="https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0417/2026041701393.pdf",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "capital_operation"


def test_merge_news_items_classifies_hkex_specific_mandate_share_placing_as_capital_operation() -> None:
    items = [
        NormalizedNews(
            news_id="n1hkplace",
            source="hkex",
            source_type="hard_event",
            published_at="2026-04-17T22:54:00+08:00",
            captured_at="2026-04-17T22:54:30+08:00",
            title="PLACING OF NEW SHARES UNDER SPECIFIC MANDATE AND CONNECTED TRANSACTION UNDERWRITING ARRANGEMENT BY A CONTROLLING SHAREHOLDER",
            content="PLACING OF NEW SHARES UNDER SPECIFIC MANDATE AND CONNECTED TRANSACTION UNDERWRITING ARRANGEMENT BY A CONTROLLING SHAREHOLDER",
            url="https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0417/2026041701971.pdf",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "capital_operation"


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


def test_merge_news_items_classifies_local_party_committee_industry_fund_statement_as_policy_signal() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="cls",
            source_type="fast_news",
            published_at="2026-04-20T20:24:07+08:00",
            captured_at="2026-04-20T20:24:20+08:00",
            title="广东：要用好产业引导基金 加大对集成电路、具身智能、算电协同等领域的投资",
            content="财联社4月20日电，广东省委财经委员会20日下午召开会议。会议指出，要积极布局新质生产力项目，着眼抢占发展制高点，用好产业引导基金，加大对集成电路、具身智能、算电协同等领域的投资。",
            url="https://www.cls.cn/detail/2349742",
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


def test_merge_news_items_treats_business_layout_solution_update_as_company_update() -> None:
    items = [
        NormalizedNews(
            news_id="n1layout",
            source="stcn",
            source_type="fast_news",
            published_at="2026-04-20T23:14:19+08:00",
            captured_at="2026-04-20T23:14:30+08:00",
            title="迈为股份：公司针对刻蚀、薄膜沉积及先进封装领域加速布局 推出多种产品及成套解决方案",
            content="人民财讯4月20日电，迈为股份4月20日在互动平台表示，公司坚定看好异质结钙钛矿叠层电池工艺的发展，钙钛矿/硅叠层电池依托我国成熟的晶硅光伏产业链，具备完善的产业配套，产业化落地条件完备，公司已于2025年12月签订业内首条钙钛矿/硅异质结叠层电池整线设备供应合同，标志着相关技术正式迈向产业化应用，目前项目正按计划稳步推进。在半导体领域，公司针对刻蚀、薄膜沉积及先进封装领域加速布局，推出了多种产品及成套解决方案，与头部客户建立了良好的合作关系。",
            url="https://www.stcn.com/article/detail/3768768.html",
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


def test_merge_news_items_classifies_supply_pressure_story_as_industry_data() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="cls",
            source_type="fast_news",
            published_at="2026-04-20T20:21:12+08:00",
            captured_at="2026-04-20T20:21:20+08:00",
            title="成本高企挤压生产利润 乙烯法PVC供应持续收缩",
            content="财联社4月20日电，本周国内PVC乙烯法生产企业产能利用率在63.12%，高企的原油及乙烯成本下，企业亏损压力增加，预计未来三周企业负荷延续下降趋势。",
            url="https://www.cls.cn/detail/2349741",
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


def test_merge_news_items_classifies_eia_inventory_weekly_report_as_industry_data() -> None:
    items = [
        NormalizedNews(
            news_id="eia-1",
            source="eia_wpsr",
            source_type="fast_news",
            published_at="2026-04-15T10:30:00-04:00",
            captured_at="2026-04-18T01:56:35+00:00",
            title="EIA周报 美国商业原油库存减少0.913百万桶 汽油库存减少6.328百万桶 馏分油库存减少3.123百万桶",
            content="数据截至 2026-04-10；报告日期 2026-04-15。美国商业原油库存 463.804 百万桶，较前周 -0.913；汽油库存 232.944 百万桶，较前周 -6.328；馏分油库存 111.559 百万桶，较前周 -3.123。来源：EIA Weekly Petroleum Status Report",
            url="https://www.eia.gov/petroleum/supply/weekly/index.php",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype == "industry_data"


def test_merge_news_items_classifies_eia_gasdiesel_price_update_as_industry_data() -> None:
    items = [
        NormalizedNews(
            news_id="eia-gd-1",
            source="eia_gasdiesel",
            source_type="fast_news",
            published_at="2026-04-14T14:07:55-04:00",
            captured_at="2026-04-18T02:10:00+00:00",
            title="EIA汽柴油零售价更新 美国汽油4.123美元/加仑 美国柴油5.608美元/加仑",
            content="美国汽油零售价 4.123 美元/加仑；美国柴油零售价 5.608 美元/加仑。来源：EIA Gasoline and Diesel Fuel Update",
            url="http://www.eia.gov/petroleum/gasdiesel/",
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


def test_merge_news_items_does_not_classify_share_disposal_disclaimer_as_acquisition_restructuring() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="cls",
            source_type="fast_news",
            published_at="2026-04-20T20:00:53+08:00",
            captured_at="2026-04-20T20:01:00+08:00",
            title="翔港科技：拟2.76亿元出售参股公司金泰克13.19%股权",
            content="财联社4月20日电，翔港科技公告称，公司拟将持有的深圳市金泰克半导体有限公司13.1944%股权转让给南宁市和鸣启半导体合伙企业，转让价格为2.76亿元。本次交易不构成关联交易及重大资产重组。",
            url="https://www.cls.cn/detail/2349710",
        )
    ]

    events = merge_news_items(items)

    assert len(events) == 1
    assert events[0].event_subtype != "acquisition_restructuring"


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


def test_merge_news_items_classifies_cls_us_pre_market_brief_as_general_fast_news() -> None:
    items = [
        NormalizedNews(
            news_id="n1",
            source="cls",
            source_type="fast_news",
            published_at="2026-04-20T20:46:57+08:00",
            captured_at="2026-04-20T20:47:10+08:00",
            title="美股盘前要闻一览：伊朗称暂无与美国进行第二轮谈判的计划；SK海力士量产专供英伟达下一代AI芯片的内存模组；日本央行或在4月暂缓加息",
            content="①【伊朗称暂无与美国进行第二轮谈判的计划】伊朗外交部发言人表示，伊朗与美国尚未就任何后续谈判达成一致。②【SK海力士量产专供英伟达下一代AI芯片的内存模组】存储芯片行业正在经历结构性重组。③【日本央行或在4月暂缓加息】市场等待更多通胀与工资数据。",
            url="https://www.cls.cn/detail/2349775",
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
