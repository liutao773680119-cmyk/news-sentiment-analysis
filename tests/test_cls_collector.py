from news_sentiment.cli import main
from news_sentiment.collectors.cls import (
    collect_cls_news,
    parse_cls_telegraph_cache_payload,
    parse_cls_telegraph_html,
)
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


def test_parse_cls_telegraph_cache_payload_extracts_rows_from_api_cache() -> None:
    payload = """
    {
      "errno": 0,
      "data": {
        "roll_data": [
          {
            "id": 2384774,
            "title": "信托通道业务费率悄然上涨：头部公司主动缩量 中小机构跑步补位",
            "brief": "【信托通道业务费率悄然上涨：头部公司主动缩量 中小机构跑步补位】财联社5月29日电，头部机构主动缩量。",
            "content": "【信托通道业务费率悄然上涨：头部公司主动缩量 中小机构跑步补位】财联社5月29日电，头部机构主动缩量。",
            "ctime": 1780008503
          },
          {
            "id": 2384763,
            "title": "",
            "brief": "财联社5月29日电，阿波罗资管洽谈360亿美元债务交易，为Anthropic采购谷歌芯片提供资金。",
            "content": "财联社5月29日电，阿波罗资管洽谈360亿美元债务交易，为Anthropic采购谷歌芯片提供资金。",
            "ctime": 1780001397
          }
        ]
      }
    }
    """
    rows = parse_cls_telegraph_cache_payload(payload)
    assert len(rows) == 2
    assert rows[0].source == "cls"
    assert rows[0].source_type == "fast_news"
    assert rows[0].title == "信托通道业务费率悄然上涨：头部公司主动缩量 中小机构跑步补位"
    assert rows[0].url == "https://www.cls.cn/detail/2384774"
    assert rows[1].title == "财联社5月29日电，阿波罗资管洽谈360亿美元债务交易，为Anthropic采购谷歌芯片提供资金。"


def test_collect_cls_source_writes_raw_news(tmp_path, monkeypatch) -> None:
    payload = """
    {
      "errno": 0,
      "data": {
        "roll_data": [
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
    """

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        "news_sentiment.collectors.cls.fetch_cls_telegraph_cache_payload",
        lambda last_time=None: payload,
    )
    assert main(["collect", "--source", "cls"]) == 0
    assert (tmp_path / "data" / "raw" / "raw_news.jsonl").exists()


def test_collect_cls_news_raises_empty_result_error_on_blank_html(monkeypatch) -> None:
    monkeypatch.setattr(
        "news_sentiment.collectors.cls.fetch_cls_telegraph_cache_payload",
        lambda last_time=None: "   ",
    )
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
