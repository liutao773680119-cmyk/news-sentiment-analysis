from news_sentiment.cli import build_parser


def test_parser_exposes_expected_commands() -> None:
    parser = build_parser()
    choices = parser._subparsers._group_actions[0].choices
    assert {
        "collect",
        "normalize",
        "merge-events",
        "analyze-events",
        "report",
        "run-once",
    } <= set(choices)
