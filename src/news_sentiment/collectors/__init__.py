from news_sentiment.collectors.boe import collect_boe_news, parse_boe_news_feed
from news_sentiment.collectors.cls import collect_cls_news, parse_cls_telegraph_html
from news_sentiment.collectors.cninfo import collect_cninfo_news, parse_cninfo_news_list
from news_sentiment.collectors.csrc import collect_csrc_news, parse_csrc_news_list
from news_sentiment.collectors.ecb import collect_ecb_news, parse_ecb_press_feed
from news_sentiment.collectors.eia_gasdiesel import collect_eia_gasdiesel_news, parse_eia_gasdiesel_feed
from news_sentiment.collectors.eia_wpsr import collect_eia_wpsr_news, parse_eia_wpsr_release
from news_sentiment.collectors.errors import (
    CollectFailure,
    CollectorEmptyResultError,
    CollectorError,
    CollectorFetchError,
    CollectorParseError,
)
from news_sentiment.collectors.fed import collect_fed_news, parse_fed_press_feed
from news_sentiment.collectors.fixtures import collect_fixture_news
from news_sentiment.collectors.hkex import collect_hkex_news, parse_hkex_news_payload
from news_sentiment.collectors.irm_cninfo import collect_irm_cninfo_news, parse_irm_cninfo_homepage
from news_sentiment.collectors.miit import collect_miit_news, parse_miit_news_list
from news_sentiment.collectors.sse import collect_sse_news, parse_sse_news_payload
from news_sentiment.collectors.sse_einteractive import collect_sse_einteractive_news, parse_sse_einteractive_feed
from news_sentiment.collectors.stcn import collect_stcn_news, parse_stcn_news_list
from news_sentiment.collectors.szse import collect_szse_news, parse_szse_news_payload

REGISTERED_COLLECTORS = {
    "fixture": collect_fixture_news,
    "boe": collect_boe_news,
    "cls": collect_cls_news,
    "csrc": collect_csrc_news,
    "cninfo": collect_cninfo_news,
    "ecb": collect_ecb_news,
    "eia_gasdiesel": collect_eia_gasdiesel_news,
    "eia_wpsr": collect_eia_wpsr_news,
    "fed": collect_fed_news,
    "hkex": collect_hkex_news,
    "irm_cninfo": collect_irm_cninfo_news,
    "miit": collect_miit_news,
    "sse": collect_sse_news,
    "sse_einteractive": collect_sse_einteractive_news,
    "stcn": collect_stcn_news,
    "szse": collect_szse_news,
}


def get_registered_collectors():
    return dict(REGISTERED_COLLECTORS)


__all__ = [
    "CollectFailure",
    "collect_cls_news",
    "collect_boe_news",
    "collect_cninfo_news",
    "collect_csrc_news",
    "collect_ecb_news",
    "collect_eia_gasdiesel_news",
    "collect_eia_wpsr_news",
    "collect_fed_news",
    "collect_fixture_news",
    "collect_hkex_news",
    "collect_irm_cninfo_news",
    "collect_miit_news",
    "collect_sse_news",
    "collect_sse_einteractive_news",
    "collect_stcn_news",
    "collect_szse_news",
    "get_registered_collectors",
    "CollectorEmptyResultError",
    "CollectorError",
    "CollectorFetchError",
    "CollectorParseError",
    "parse_boe_news_feed",
    "parse_cls_telegraph_html",
    "parse_cninfo_news_list",
    "parse_csrc_news_list",
    "parse_ecb_press_feed",
    "parse_eia_gasdiesel_feed",
    "parse_eia_wpsr_release",
    "parse_fed_press_feed",
    "parse_hkex_news_payload",
    "parse_irm_cninfo_homepage",
    "parse_miit_news_list",
    "parse_sse_news_payload",
    "parse_sse_einteractive_feed",
    "parse_stcn_news_list",
    "parse_szse_news_payload",
]
