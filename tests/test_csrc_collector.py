from news_sentiment.cli import main
from news_sentiment.collectors.csrc import collect_csrc_news, parse_csrc_news_list
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.config_loader import load_source_definition_map


def test_parse_csrc_news_list_extracts_news_rows() -> None:
    html = """
    <meta name="others" content="页面生成时间 2026-04-10 10:42:35" />
    <li class="xwfb">
      <div class="tab-content">
        <div class="tab-list" style="display: block;">
          <ul>
            <li class="first">
              <a href="/csrc/c106311/c1234567/content.shtml" target="_blank">吴清主席会见澳门金融管理局行政管理委员会主席黄善文</a>
              <span class="time_first">2026-03-31</span>
            </li>
            <li class="li-height">
              <a href="/csrc/c106311/c1234567/content.shtml" target="_blank">吴清主席会见澳门金融管理局行政管理委员会主席黄善文</a>
              <span class="time">03-31</span>
            </li>
            <li class="li-height">
              <a href="/csrc/c100028/c7654321/content.shtml" target="_blank">中国证监会2025年法治政府建设情况</a>
              <span class="time">03-27</span>
            </li>
          </ul>
        </div>
        <div class="tab-list"></div>
      </div>
    </li>
    """
    rows = parse_csrc_news_list(html)
    assert len(rows) == 2
    assert rows[0].source == "csrc"
    assert rows[0].source_type == "policy"
    assert rows[0].title == "吴清主席会见澳门金融管理局行政管理委员会主席黄善文"
    assert rows[0].published_at == "2026-03-31T00:00:00+08:00"
    assert rows[0].url == "https://www.csrc.gov.cn/csrc/c106311/c1234567/content.shtml"
    assert rows[1].published_at == "2026-03-27T00:00:00+08:00"


def test_collect_csrc_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    html = """
    <meta name="others" content="页面生成时间 2026-04-10 10:42:35" />
    <li class="xwfb">
      <div class="tab-content">
        <div class="tab-list" style="display: block;">
          <ul>
            <li class="li-height">
              <a href="/csrc/c100028/c1234567/content.shtml" target="_blank">证监会召开资本市场改革发展座谈会</a>
              <span class="time">04-10</span>
            </li>
          </ul>
        </div>
        <div class="tab-list"></div>
      </div>
    </li>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.csrc.fetch_csrc_news_html",
        lambda url=None: html,
    )
    assert main(["collect", "--source", "csrc"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_csrc_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.csrc.fetch_csrc_news_html",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_csrc_news()
    except CollectorFetchError as exc:
        assert exc.source == "csrc"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_csrc_news_raises_parse_error_on_unmatched_html(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.csrc.fetch_csrc_news_html",
        lambda url=None: "<html><body>unexpected</body></html>",
    )

    try:
        collect_csrc_news()
    except CollectorParseError as exc:
        assert exc.source == "csrc"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_csrc_source_definition_is_registered() -> None:
    source = load_source_definition_map()["csrc"]
    assert source.source_type == "policy"
    assert source.enabled is True
