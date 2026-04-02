from news_sentiment.config_loader import load_source_definitions, load_theme_registry


def test_load_theme_registry_contains_seed_theme() -> None:
    registry = load_theme_registry()
    assert "算力" in {theme.name for theme in registry.themes}


def test_load_source_definitions_include_http_runtime_settings() -> None:
    sources = {item.source_id: item for item in load_source_definitions()}
    assert sources["cninfo"].timeout_seconds == 10
    assert sources["cninfo"].user_agent
