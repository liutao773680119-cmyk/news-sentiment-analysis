from news_sentiment.cli import main
from news_sentiment.collectors.stcn import parse_stcn_news_list


def test_parse_stcn_news_list_extracts_flash_news_rows() -> None:
    html = """
    <div class="item">
      <a href="/article/detail/123456.html">绿色电力概念震荡回升 豫能控股、宁波能源涨停</a>
      <span>14:37</span>
    </div>
    """
    rows = parse_stcn_news_list(html, date_str="2026-04-01")
    assert len(rows) == 1
    assert rows[0].source == "stcn"
    assert rows[0].title == "绿色电力概念震荡回升 豫能控股、宁波能源涨停"


def test_collect_stcn_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    html = """
    <div class="item">
      <a href="/article/detail/123456.html">绿色电力概念震荡回升 豫能控股、宁波能源涨停</a>
      <span>14:37</span>
    </div>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.stcn.fetch_stcn_news_html",
        lambda url=None: html,
    )
    monkeypatch.setattr(
        "news_sentiment.collectors.stcn.current_china_date",
        lambda: "2026-04-01",
    )
    assert main(["collect", "--source", "stcn"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()
