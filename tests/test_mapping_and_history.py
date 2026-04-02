from news_sentiment.history.matcher import match_historical_events
from news_sentiment.mapping.stock_mapper import map_themes_to_stocks


def test_map_themes_to_stocks_returns_weighted_candidates() -> None:
    rows = map_themes_to_stocks(["算力"])
    assert rows[0].stock_code
    assert rows[0].weight > 0


def test_match_historical_events_returns_theme_related_samples() -> None:
    matches = match_historical_events(["算力"])
    assert matches
    assert "算力" in matches[0]["themes"]


def test_map_themes_to_stocks_supports_extended_seed_themes() -> None:
    rows = map_themes_to_stocks(["AI应用", "充电桩", "数据安全"])
    assert {row.theme_name for row in rows} >= {"AI应用", "充电桩", "数据安全"}


def test_match_historical_events_supports_extended_seed_themes() -> None:
    matches = match_historical_events(["AI应用", "充电桩", "数据安全"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"AI应用", "充电桩", "数据安全"} <= matched_themes


def test_map_themes_to_stocks_supports_commodity_seed_themes() -> None:
    rows = map_themes_to_stocks(["黄金", "油气"])
    assert {row.theme_name for row in rows} >= {"黄金", "油气"}


def test_match_historical_events_supports_commodity_seed_themes() -> None:
    matches = match_historical_events(["黄金", "油气"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"黄金", "油气"} <= matched_themes


def test_map_themes_to_stocks_supports_company_theme_seed_themes() -> None:
    rows = map_themes_to_stocks(["户外经济", "锂电池"])
    assert {row.theme_name for row in rows} >= {"户外经济", "锂电池"}


def test_match_historical_events_supports_company_theme_seed_themes() -> None:
    matches = match_historical_events(["户外经济", "锂电池"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"户外经济", "锂电池"} <= matched_themes


def test_map_themes_to_stocks_supports_semiconductor_theme() -> None:
    rows = map_themes_to_stocks(["半导体"])
    assert {row.theme_name for row in rows} >= {"半导体"}


def test_match_historical_events_supports_semiconductor_theme() -> None:
    matches = match_historical_events(["半导体"])
    matched_themes = {theme for row in matches for theme in row["themes"]}
    assert {"半导体"} <= matched_themes
