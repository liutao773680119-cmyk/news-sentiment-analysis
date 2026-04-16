from news_sentiment.cli import main
from news_sentiment.collectors.cls import collect_cls_news, parse_cls_telegraph_html
from news_sentiment.collectors.errors import CollectorEmptyResultError


def test_parse_cls_telegraph_html_extracts_rows_from_next_data() -> None:
    html = """
    <html>
      <body>
        <script id="__NEXT_DATA__" type="application/json">
          {
            "props": {
              "pageProps": {
                "initialState": {
                  "telegraph": {
                    "telegraphList": [
                      {
                        "id": 2343974,
                        "title": "ST中青宝：撤销其他风险警示 证券简称变更为“中青宝”",
                        "brief": "【ST中青宝：撤销其他风险警示 证券简称变更为“中青宝”】财联社4月14日电，公司股票将于4月16日复牌并撤销其他风险警示。",
                        "content": "【ST中青宝：撤销其他风险警示 证券简称变更为“中青宝”】财联社4月14日电，公司股票将于4月16日复牌并撤销其他风险警示。",
                        "ctime": 1776170960
                      },
                      {
                        "id": 2343971,
                        "title": "",
                        "brief": "财联社4月14日电，据报道，沃什的美联储主席确认听证会将于4月21日举行。",
                        "content": "财联社4月14日电，据报道，沃什的美联储主席确认听证会将于4月21日举行。",
                        "ctime": 1776170740
                      }
                    ]
                  }
                }
              }
            }
          }
        </script>
      </body>
    </html>
    """
    rows = parse_cls_telegraph_html(html)
    assert len(rows) == 2
    assert rows[0].source == "cls"
    assert rows[0].source_type == "fast_news"
    assert rows[0].title == "ST中青宝：撤销其他风险警示 证券简称变更为“中青宝”"
    assert rows[0].url == "https://www.cls.cn/detail/2343974"
    assert rows[1].title == "财联社4月14日电，据报道，沃什的美联储主席确认听证会将于4月21日举行。"


def test_collect_cls_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    html = """
    <html>
      <body>
        <script id="__NEXT_DATA__" type="application/json">
          {
            "props": {
              "pageProps": {
                "initialState": {
                  "telegraph": {
                    "telegraphList": [
                      {
                        "id": 2344008,
                        "title": "杭可科技：拟1.79亿元增资杭可仪器获51%股权",
                        "brief": "【杭可科技：拟1.79亿元增资杭可仪器获51%股权】财联社4月14日电，公司拟增资杭可仪器。",
                        "content": "【杭可科技：拟1.79亿元增资杭可仪器获51%股权】财联社4月14日电，公司拟增资杭可仪器。",
                        "ctime": 1776172462
                      }
                    ]
                  }
                }
              }
            }
          }
        </script>
      </body>
    </html>
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.cls.fetch_cls_telegraph_html",
        lambda url=None: html,
    )
    assert main(["collect", "--source", "cls"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_cls_news_raises_empty_result_error_on_blank_html(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.cls.fetch_cls_telegraph_html",
        lambda url=None: "   ",
    )

    try:
        collect_cls_news()
    except CollectorEmptyResultError as exc:
        assert exc.source == "cls"
        assert exc.kind == "empty_result"
    else:
        raise AssertionError("Expected CollectorEmptyResultError")
