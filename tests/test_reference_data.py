from news_sentiment.config_loader import load_theme_registry


def test_load_theme_registry_contains_seed_theme() -> None:
    registry = load_theme_registry()
    assert "算力" in {theme.name for theme in registry.themes}
