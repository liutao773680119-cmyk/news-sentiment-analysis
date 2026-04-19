from news_sentiment.cli import build_parser
from news_sentiment.collectors import get_registered_collectors


def test_parser_exposes_expected_commands() -> None:
    parser = build_parser()
    choices = parser._subparsers._group_actions[0].choices
    assert {
        "collect",
        "normalize",
        "merge-events",
        "analyze-events",
        "audit-suspicious",
        "live-smoke",
        "report",
        "run-once",
    } <= set(choices)


def test_registered_collectors_expose_expected_sources() -> None:
    assert {
        "fixture",
        "boe",
        "boc_press",
        "boj",
        "bis",
        "cls",
        "cftc_press",
        "cninfo",
        "csrc",
        "ecb",
        "eia_gasdiesel",
        "eia_wpsr",
        "fed",
        "fedreg_ofac",
        "fedreg_sec",
        "hkex",
        "irm_cninfo",
        "investing_economic",
        "investing_news",
        "investing_forex",
        "miit",
        "occ_news",
        "sec_press",
        "sse",
        "sse_einteractive",
        "stcn",
        "szse",
    } <= set(get_registered_collectors())
