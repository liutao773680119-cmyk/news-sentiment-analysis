from news_sentiment.cli import main
from news_sentiment.collectors.eia_wpsr import (
    collect_eia_wpsr_news,
    parse_eia_wpsr_release,
)
from news_sentiment.collectors.errors import CollectorFetchError, CollectorParseError
from news_sentiment.config_loader import load_source_definition_map


def test_parse_eia_wpsr_release_extracts_weekly_petroleum_row() -> None:
    page_html = """
    <html>
      <body>
        <div>
          <span>Data for week ending Apr. 10, 2026</span>
          <span class="responsive-container"><span class="label">Release Date:</span> <span class="date">Apr. 15, 2026</span></span>
          <span class="responsive-container"><span class="label">Next Release Date:</span> <span class="date">Apr. 22, 2026</span></span>
        </div>
      </body>
    </html>
    """
    table1_csv = '''"STUB_1","4/10/26","4/3/26","Difference","Percent Change"
"Commercial (Excluding SPR)","463.804","464.717","-0.913","-0.200"
"Total Motor Gasoline","232.944","239.272","-6.328","-2.600"
"Distillate Fuel Oil","111.559","114.681","-3.123","-2.700"
'''

    rows = parse_eia_wpsr_release(page_html, table1_csv)
    assert len(rows) == 1
    assert rows[0].news_id == "eia_wpsr-20260415"
    assert rows[0].source == "eia_wpsr"
    assert rows[0].source_type == "fast_news"
    assert rows[0].published_at == "2026-04-15T10:30:00-04:00"
    assert rows[0].title == "EIA周报 美国商业原油库存减少0.913百万桶 汽油库存减少6.328百万桶 馏分油库存减少3.123百万桶"
    assert (
        "数据截至 2026-04-10；报告日期 2026-04-15。美国商业原油库存 463.804 百万桶，较前周 -0.913；"
        in rows[0].content
    )
    assert rows[0].url == "https://www.eia.gov/petroleum/supply/weekly/index.php"


def test_collect_eia_wpsr_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    page_html = """
    <html><body>
      <span>Data for week ending Apr. 10, 2026</span>
      <span class="responsive-container"><span class="label">Release Date:</span> <span class="date">Apr. 15, 2026</span></span>
    </body></html>
    """
    table1_csv = '''"STUB_1","4/10/26","4/3/26","Difference","Percent Change"
"Commercial (Excluding SPR)","463.804","464.717","-0.913","-0.200"
"Total Motor Gasoline","232.944","239.272","-6.328","-2.600"
"Distillate Fuel Oil","111.559","114.681","-3.123","-2.700"
'''

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.eia_wpsr.fetch_eia_wpsr_page",
        lambda url=None: page_html,
    )
    monkeypatch.setattr(
        "news_sentiment.collectors.eia_wpsr.fetch_eia_wpsr_table1_csv",
        lambda url=None: table1_csv,
    )
    assert main(["collect", "--source", "eia_wpsr"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_eia_wpsr_news_raises_fetch_error_on_network_failure(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.eia_wpsr.fetch_eia_wpsr_page",
        lambda url=None: (_ for _ in ()).throw(TimeoutError("timed out")),
    )

    try:
        collect_eia_wpsr_news()
    except CollectorFetchError as exc:
        assert exc.source == "eia_wpsr"
        assert exc.kind == "fetch_error"
    else:
        raise AssertionError("Expected CollectorFetchError")


def test_collect_eia_wpsr_news_raises_parse_error_on_unmatched_payload(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.eia_wpsr.fetch_eia_wpsr_page",
        lambda url=None: "<html><body>empty</body></html>",
    )
    monkeypatch.setattr(
        "news_sentiment.collectors.eia_wpsr.fetch_eia_wpsr_table1_csv",
        lambda url=None: '"STUB_1","4/10/26"\n',
    )

    try:
        collect_eia_wpsr_news()
    except CollectorParseError as exc:
        assert exc.source == "eia_wpsr"
        assert exc.kind == "parse_error"
    else:
        raise AssertionError("Expected CollectorParseError")


def test_eia_wpsr_source_definition_is_registered() -> None:
    source = load_source_definition_map()["eia_wpsr"]
    assert source.source_type == "fast_news"
    assert source.enabled is False
