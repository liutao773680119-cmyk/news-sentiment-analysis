from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorParseError
from news_sentiment.collectors.miit import collect_miit_news, parse_miit_news_list


def test_parse_miit_news_list_extracts_news_rows() -> None:
    html = """
    <ul>
      <li>
        <a href="/xwfb/gxdt/art/2026/art_123.html" title="工信部召开新闻发布会部署算力基础设施">
          工信部召开新闻发布会部署算力基础设施
        </a>
        <span>2026-04-01</span>
      </li>
    </ul>
    """
    rows = parse_miit_news_list(html)
    assert len(rows) == 1
    assert rows[0].source == "miit"
    assert rows[0].title == "工信部召开新闻发布会部署算力基础设施"


def test_collect_miit_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    html = """
    <ul>
      <li>
        <a href="/xwfb/gxdt/art/2026/art_123.html" title="工信部召开新闻发布会部署算力基础设施">
          工信部召开新闻发布会部署算力基础设施
        </a>
        <span>2026-04-01</span>
      </li>
    </ul>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.miit.fetch_miit_news_html",
        lambda url=None: html,
    )
    assert main(["collect", "--source", "miit"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_miit_news_raises_parse_error_on_unmatched_html(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.miit.fetch_miit_news_html",
        lambda url=None: "<html><body>unexpected</body></html>",
    )

    try:
        collect_miit_news()
    except CollectorParseError as exc:
        assert exc.source == "miit"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")
