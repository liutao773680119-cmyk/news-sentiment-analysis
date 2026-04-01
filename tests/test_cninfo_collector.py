from news_sentiment.cli import main
from news_sentiment.collectors.cninfo import collect_cninfo_news
from news_sentiment.collectors.errors import CollectorFetchError
from news_sentiment.collectors.cninfo import parse_cninfo_news_list


def test_parse_cninfo_news_list_extracts_announcement_rows() -> None:
    html = """
    <table>
      <tr>
        <td>603019</td>
        <td>中科曙光</td>
        <td>
          <a href="/new/disclosure/detail?plate=sse&orgId=9900000001&stockCode=603019&announcementId=123456">
            中科曙光关于签署算力合作协议的公告
          </a>
        </td>
        <td>2026-04-01</td>
      </tr>
    </table>
    """
    rows = parse_cninfo_news_list(html)
    assert len(rows) == 1
    assert rows[0].source == "cninfo"
    assert rows[0].title == "中科曙光关于签署算力合作协议的公告"


def test_collect_cninfo_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    html = """
    <table>
      <tr>
        <td>603019</td>
        <td>中科曙光</td>
        <td>
          <a href="/new/disclosure/detail?plate=sse&orgId=9900000001&stockCode=603019&announcementId=123456">
            中科曙光关于签署算力合作协议的公告
          </a>
        </td>
        <td>2026-04-01</td>
      </tr>
    </table>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.cninfo.fetch_cninfo_news_html",
        lambda url=None: html,
    )
    assert main(["collect", "--source", "cninfo"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_cninfo_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.cninfo.fetch_cninfo_news_html",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_cninfo_news()
    except CollectorFetchError as exc:
        assert exc.source == "cninfo"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")
