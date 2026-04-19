from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorFetchError
from news_sentiment.collectors.sse_einteractive import collect_sse_einteractive_news, parse_sse_einteractive_feed
from news_sentiment.config_loader import load_source_definition_map


def test_parse_sse_einteractive_feed_extracts_latest_reply_rows() -> None:
    html = """
    <div class="m_feed_item" id="item-1688091">
      <div class="m_feed_detail m_qa_detail">
        <div class="m_feed_cnt ">
          <div class="m_feed_txt" id="m_feed_txt-1688091">
            <a href='user.do?uid=139138' >:有友食品(603697)</a>请问有友食品在鸡爪原料处理环节，具体采用何种方式进行清洗、去腥、去色处理？
          </div>
          <div class="m_feed_func">
            <div class="m_feed_from">
              <span>2026年03月17日 08:35</span>
              <em>来自</em>
              <a href="javascript:;">网站</a>
            </div>
          </div>
        </div>
      </div>
      <div class="m_feed_detail m_qa">
        <div class="m_feed_face">
          <a class="ansface" rel="tag" uid="139138" href="user.do?uid=139138" title="有友食品"></a>
          <p>有友食品</p>
        </div>
        <div class="m_feed_cnt">
          <div class="m_feed_txt" id="m_feed_txt-1688091">
            尊敬的投资者您好！公司全品类产品生产全过程严格遵守食品安全法律法规及行业监管要求，感谢您的关注。
          </div>
        </div>
        <div class="m_feed_func top10" style="margin-left: 70px;">
          <div class="m_feed_from" style="padding-left: 35px;">
            <span>2026年03月18日 18:22</span>
            <em>来自</em>
            <a href="javascript:;">网站</a>
          </div>
        </div>
      </div>
    </div>
    """

    rows = parse_sse_einteractive_feed(html)
    assert len(rows) == 1
    assert rows[0].news_id == "sse_einteractive-1688091"
    assert rows[0].source == "sse_einteractive"
    assert rows[0].source_type == "fast_news"
    assert rows[0].published_at == "2026-03-18T18:22:00+08:00"
    assert rows[0].title == "有友食品：请问有友食品在鸡爪原料处理环节，具体采用何种方式进行清洗、去腥、去色处理？"
    assert rows[0].content == (
        "问题：请问有友食品在鸡爪原料处理环节，具体采用何种方式进行清洗、去腥、去色处理？\n"
        "回复：尊敬的投资者您好！公司全品类产品生产全过程严格遵守食品安全法律法规及行业监管要求，感谢您的关注。"
    )
    assert rows[0].url == "https://sns.sseinfo.com/qadetail.do?weiboId=1688091"


def test_collect_sse_einteractive_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    html = """
    <div class="m_feed_item" id="item-1703412">
      <div class="m_feed_detail m_qa_detail">
        <div class="m_feed_cnt ">
          <div class="m_feed_txt" id="m_feed_txt-1703412">
            <a href='user.do?uid=243284' >:有友食品(603697)</a>请问泡椒凤爪新品渠道反馈如何？
          </div>
          <div class="m_feed_func"><div class="m_feed_from"><span>2026年04月17日 09:15</span><em>来自</em><a href=\"javascript:;\">网站</a></div></div>
        </div>
      </div>
      <div class="m_feed_detail m_qa">
        <div class="m_feed_face"><p>有友食品</p></div>
        <div class="m_feed_cnt"><div class="m_feed_txt" id="m_feed_txt-1703412">新品目前处于推广阶段，渠道反馈总体稳定。</div></div>
        <div class="m_feed_func top10" style="margin-left: 70px;"><div class="m_feed_from" style="padding-left: 35px;"><span>2026年04月18日 10:20</span><em>来自</em><a href=\"javascript:;\">网站</a></div></div>
      </div>
    </div>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.sse_einteractive.fetch_sse_einteractive_feed",
        lambda: html,
    )
    assert main(["collect", "--source", "sse_einteractive"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_sse_einteractive_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.sse_einteractive.fetch_sse_einteractive_feed",
        lambda: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_sse_einteractive_news()
    except CollectorFetchError as exc:
        assert exc.source == "sse_einteractive"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_sse_einteractive_source_definition_is_registered() -> None:
    source = load_source_definition_map()["sse_einteractive"]
    assert source.source_type == "fast_news"
    assert source.enabled is True
