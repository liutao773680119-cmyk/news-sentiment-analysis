from news_sentiment.cli import main
from news_sentiment.collectors.errors import CollectorEmptyResultError
from news_sentiment.collectors.stcn import (
    collect_stcn_news,
    parse_stcn_news_list,
    parse_stcn_news_payload,
)


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


def test_parse_stcn_news_payload_extracts_flash_news_rows() -> None:
    payload = """
    {
      "state": 1,
      "msg": "操作成功",
      "data": [
        {
          "id": "3722719",
          "url": "/article/detail/3722719.html",
          "title": "智界汽车官宣郭锐为董事长兼首席执行官",
          "content": "人民财讯4月2日电，4月2日，智界汽车官宣，任命郭锐为董事长兼首席执行官。",
          "time": 1775097173000
        }
      ]
    }
    """
    rows = parse_stcn_news_payload(payload)
    assert len(rows) == 1
    assert rows[0].source == "stcn"
    assert rows[0].title == "智界汽车官宣郭锐为董事长兼首席执行官"
    assert rows[0].url == "https://www.stcn.com/article/detail/3722719.html"


def test_collect_stcn_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """
    {
      "state": 1,
      "msg": "操作成功",
      "data": [
        {
          "id": "3722719",
          "url": "/article/detail/3722719.html",
          "title": "智界汽车官宣郭锐为董事长兼首席执行官",
          "content": "人民财讯4月2日电，4月2日，智界汽车官宣，任命郭锐为董事长兼首席执行官。",
          "time": 1775097173000
        }
      ]
    }
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.stcn.fetch_stcn_news_payload",
        lambda url=None: payload,
    )
    assert main(["collect", "--source", "stcn"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_stcn_news_raises_empty_result_error_on_blank_html(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.stcn.fetch_stcn_news_payload",
        lambda url=None: "   ",
    )

    try:
        collect_stcn_news()
    except CollectorEmptyResultError as exc:
        assert exc.source == "stcn"
        assert exc.kind == "empty_result"
    else:
        raise AssertionError("Expected CollectorEmptyResultError")
