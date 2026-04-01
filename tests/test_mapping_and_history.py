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
