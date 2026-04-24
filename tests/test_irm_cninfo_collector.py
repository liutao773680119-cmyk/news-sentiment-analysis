from datetime import datetime, timedelta, timezone

from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError
from news_sentiment.collectors.irm_cninfo import (
    IRM_CNINFO_DETAIL_TIMEOUT_SECONDS,
    IRM_CNINFO_HOME_TIMEOUT_SECONDS,
    collect_irm_cninfo_news,
    fetch_irm_cninfo_homepage,
    fetch_irm_cninfo_question_detail,
    parse_irm_cninfo_homepage,
    parse_irm_cninfo_question_detail_payload,
)
from news_sentiment.config_loader import load_source_definition_map


CHINA_TZ = timezone(timedelta(hours=8))


def test_parse_irm_cninfo_homepage_extracts_question_cards() -> None:
    html = """
    <div class="left-content table-list" style="position: relative;">
      <div class="table-head pd-20">
        <span class="compnay-name">军信股份&nbsp;<span class="company-code hidden-sm-and-up">(301109)</span></span>
        <span class="company-code hidden-xs-only">[301109]</span>
        <span class="question-time hidden-sm-and-up">1小时前</span>
      </div>
      <div class="table-content translate-box pd-20" style="overflow: inherit;">
        <a>
          <div class="question-content" style="font-weight: normal;">
            <img src="//ircsstatic.cninfo.com.cn/ircs//assets/images/question-icon.png" alt="" class="question-icon">
            董秘您好，请问公司垃圾焚烧项目何时公布中标消息？
          </div>
        </a>
      </div>
      <div class="table-footer pd-10-20">
        <span class="question-platform hidden-xs-only">来源 &nbsp;网站</span>
        <span @click="clickEventPraise($event,'301109','S','2247768240096677888','Q')"
              data-status="0"
              class="like-content el-col-xs-8 ">
        </span>
        <a href="//irm.cninfo.com.cn/ircs/question/questionDetail?questionId=2247768240096677888" target="_blank"></a>
      </div>
      <div class="el-loading-mask cover"><div class="el-loading-spinner"></div></div>
    </div>
    """

    now = datetime(2026, 4, 18, 12, 0, tzinfo=CHINA_TZ)
    rows = parse_irm_cninfo_homepage(html, now=now)
    assert len(rows) == 1
    assert rows[0].news_id == "irm_cninfo-2247768240096677888"
    assert rows[0].source == "irm_cninfo"
    assert rows[0].source_type == "fast_news"
    assert rows[0].published_at == "2026-04-18T11:00:00+08:00"
    assert rows[0].title == "军信股份：董秘您好，请问公司垃圾焚烧项目何时公布中标消息？"
    assert rows[0].content == "董秘您好，请问公司垃圾焚烧项目何时公布中标消息？"
    assert rows[0].url == "https://irm.cninfo.com.cn/ircs/question/questionDetail?questionId=2247768240096677888"


def test_collect_irm_cninfo_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    html = """
    <div class="left-content table-list" style="position: relative;">
      <div class="table-head pd-20">
        <span class="compnay-name">TCL中环&nbsp;<span class="company-code hidden-sm-and-up">(002129)</span></span>
        <span class="company-code hidden-xs-only">[002129]</span>
        <span class="question-time hidden-sm-and-up">11小时前</span>
      </div>
      <div class="table-content translate-box pd-20" style="overflow: inherit;">
        <a>
          <div class="question-content" style="font-weight: normal;">请问公司硅片价格策略是否有调整？</div>
        </a>
      </div>
      <div class="table-footer pd-10-20">
        <span @click="clickEventPraise($event,'002129','S','2246254753773940736','Q')"></span>
        <a href="//irm.cninfo.com.cn/ircs/question/questionDetail?questionId=2246254753773940736" target="_blank"></a>
      </div>
      <div class="el-loading-mask cover"><div class="el-loading-spinner"></div></div>
    </div>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.irm_cninfo.fetch_irm_cninfo_homepage",
        lambda: html,
    )
    monkeypatch.setattr(
        "news_sentiment.collectors.irm_cninfo.fetch_irm_cninfo_question_detail",
        lambda question_id: """
        {
          "statusCode": 200,
          "data": {
            "shortName": "TCL中环",
            "stockCode": "002129",
            "questionContent": "请问公司硅片价格策略是否有调整？",
            "questionDate": 1776182400000,
            "replyContent": "尊敬的投资者，您好。公司经营情况请以公告为准。",
            "replyDate": 1776268800000
          }
        }
        """,
    )
    assert main(["collect", "--source", "irm_cninfo"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_parse_irm_cninfo_question_detail_payload_prefers_reply_date() -> None:
    payload = """
    {
      "statusCode": 200,
      "data": {
        "shortName": "军信股份",
        "stockCode": "301109",
        "questionContent": "请问公司垃圾焚烧项目何时公布中标消息？",
        "questionDate": 1776410664000,
        "replyContent": "公司已收到中标通知书，并已披露公告。",
        "replyDate": 1776470253000
      }
    }
    """

    detail = parse_irm_cninfo_question_detail_payload(payload)
    assert detail["company_name"] == "军信股份"
    assert detail["stock_code"] == "301109"
    assert detail["question_content"] == "请问公司垃圾焚烧项目何时公布中标消息？"
    assert detail["reply_content"] == "公司已收到中标通知书，并已披露公告。"
    assert detail["published_at"] == "2026-04-18T07:57:33+08:00"


def test_collect_irm_cninfo_news_prefers_detail_payload_and_skips_unanswered(monkeypatch) -> None:
    html = """
    <div class="left-content table-list" style="position: relative;">
      <div class="table-head pd-20">
        <span class="compnay-name">军信股份&nbsp;<span class="company-code hidden-sm-and-up">(301109)</span></span>
        <span class="company-code hidden-xs-only">[301109]</span>
        <span class="question-time hidden-sm-and-up">1小时前</span>
      </div>
      <div class="table-content translate-box pd-20" style="overflow: inherit;">
        <a><div class="question-content">请问公司垃圾焚烧项目何时公布中标消息？</div></a>
      </div>
      <div class="table-footer pd-10-20">
        <span @click="clickEventPraise($event,'301109','S','2247768240096677888','Q')"></span>
      </div>
      <div class="el-loading-mask cover"><div class="el-loading-spinner"></div></div>
    </div>
    <div class="left-content table-list" style="position: relative;">
      <div class="table-head pd-20">
        <span class="compnay-name">TCL中环&nbsp;<span class="company-code hidden-sm-and-up">(002129)</span></span>
        <span class="company-code hidden-xs-only">[002129]</span>
        <span class="question-time hidden-sm-and-up">11小时前</span>
      </div>
      <div class="table-content translate-box pd-20" style="overflow: inherit;">
        <a><div class="question-content">请问截止4月10日股东人数是多少？</div></a>
      </div>
      <div class="table-footer pd-10-20">
        <span @click="clickEventPraise($event,'002129','S','2246254753773940736','Q')"></span>
      </div>
      <div class="el-loading-mask cover"><div class="el-loading-spinner"></div></div>
    </div>
    """

    def fake_detail(question_id: str) -> str:
        if question_id == "2247768240096677888":
            return """
            {
              "statusCode": 200,
              "data": {
                "shortName": "军信股份",
                "stockCode": "301109",
                "questionContent": "请问公司垃圾焚烧项目何时公布中标消息？",
                "questionDate": 1776410664000,
                "replyContent": "公司已收到中标通知书，并已披露公告。",
                "replyDate": 1776470253000
              }
            }
            """
        return """
        {
          "statusCode": 200,
          "data": {
            "shortName": "TCL中环",
            "stockCode": "002129",
            "questionContent": "请问截止4月10日股东人数是多少？",
            "questionDate": 1776420000000,
            "replyContent": "",
            "replyDate": null
          }
        }
        """

    monkeypatch.setattr(
        "news_sentiment.collectors.irm_cninfo.fetch_irm_cninfo_homepage",
        lambda: html,
    )
    monkeypatch.setattr(
        "news_sentiment.collectors.irm_cninfo.fetch_irm_cninfo_question_detail",
        fake_detail,
    )
    rows = collect_irm_cninfo_news()
    assert len(rows) == 1
    assert rows[0].news_id == "irm_cninfo-2247768240096677888"
    assert rows[0].published_at == "2026-04-18T07:57:33+08:00"
    assert rows[0].content == "问题：请问公司垃圾焚烧项目何时公布中标消息？\n回复：公司已收到中标通知书，并已披露公告。"


def test_collect_irm_cninfo_news_caps_detail_enrichment_and_keeps_homepage_rows(monkeypatch) -> None:
    html = """
    <div class="left-content table-list" style="position: relative;">
      <div class="table-head pd-20">
        <span class="compnay-name">军信股份&nbsp;<span class="company-code hidden-sm-and-up">(301109)</span></span>
        <span class="company-code hidden-xs-only">[301109]</span>
        <span class="question-time hidden-sm-and-up">1小时前</span>
      </div>
      <div class="table-content translate-box pd-20" style="overflow: inherit;">
        <a><div class="question-content">请问公司垃圾焚烧项目何时公布中标消息？</div></a>
      </div>
      <div class="table-footer pd-10-20">
        <span @click="clickEventPraise($event,'301109','S','2247768240096677888','Q')"></span>
      </div>
      <div class="el-loading-mask cover"><div class="el-loading-spinner"></div></div>
    </div>
    <div class="left-content table-list" style="position: relative;">
      <div class="table-head pd-20">
        <span class="compnay-name">TCL中环&nbsp;<span class="company-code hidden-sm-and-up">(002129)</span></span>
        <span class="company-code hidden-xs-only">[002129]</span>
        <span class="question-time hidden-sm-and-up">2小时前</span>
      </div>
      <div class="table-content translate-box pd-20" style="overflow: inherit;">
        <a><div class="question-content">请问公司硅片价格策略是否有调整？</div></a>
      </div>
      <div class="table-footer pd-10-20">
        <span @click="clickEventPraise($event,'002129','S','2246254753773940736','Q')"></span>
      </div>
      <div class="el-loading-mask cover"><div class="el-loading-spinner"></div></div>
    </div>
    """
    fetched_question_ids: list[str] = []

    def fake_detail(question_id: str) -> str:
        fetched_question_ids.append(question_id)
        return """
        {
          "statusCode": 200,
          "data": {
            "shortName": "军信股份",
            "stockCode": "301109",
            "questionContent": "请问公司垃圾焚烧项目何时公布中标消息？",
            "questionDate": 1776410664000,
            "replyContent": "公司已收到中标通知书，并已披露公告。",
            "replyDate": 1776470253000
          }
        }
        """

    monkeypatch.setattr(
        "news_sentiment.collectors.irm_cninfo.fetch_irm_cninfo_homepage",
        lambda: html,
    )
    monkeypatch.setattr(
        "news_sentiment.collectors.irm_cninfo.fetch_irm_cninfo_question_detail",
        fake_detail,
    )
    monkeypatch.setattr("news_sentiment.collectors.irm_cninfo.IRM_CNINFO_MAX_DETAIL_ENRICHMENT", 1)

    rows = collect_irm_cninfo_news()

    assert fetched_question_ids == ["2247768240096677888"]
    assert len(rows) == 2
    assert rows[0].content == "问题：请问公司垃圾焚烧项目何时公布中标消息？\n回复：公司已收到中标通知书，并已披露公告。"
    assert rows[1].news_id == "irm_cninfo-2246254753773940736"
    assert rows[1].content == "请问公司硅片价格策略是否有调整？"


def test_irm_cninfo_live_fetches_use_short_no_retry_timeouts(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    class FakeResponse:
        encoding = "utf-8"
        text = "{}"

        def raise_for_status(self) -> None:
            return None

    def fake_get(url: str, **kwargs: object) -> FakeResponse:
        calls.append({"url": url, **kwargs})
        return FakeResponse()

    monkeypatch.setattr("news_sentiment.collectors.irm_cninfo.requests.get", fake_get)

    fetch_irm_cninfo_homepage()
    fetch_irm_cninfo_question_detail("2247768240096677888")

    assert calls[0]["timeout"] == (IRM_CNINFO_HOME_TIMEOUT_SECONDS, IRM_CNINFO_HOME_TIMEOUT_SECONDS)
    assert calls[1]["timeout"] == (IRM_CNINFO_DETAIL_TIMEOUT_SECONDS, IRM_CNINFO_DETAIL_TIMEOUT_SECONDS)


def test_collect_irm_cninfo_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.irm_cninfo.fetch_irm_cninfo_homepage",
        lambda: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_irm_cninfo_news()
    except CollectorFetchError as exc:
        assert exc.source == "irm_cninfo"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_irm_cninfo_source_definition_is_registered() -> None:
    source = load_source_definition_map()["irm_cninfo"]
    assert source.source_type == "fast_news"
    assert source.enabled is True
