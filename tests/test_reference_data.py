from news_sentiment.config_loader import load_source_definitions, load_theme_registry


def test_load_theme_registry_contains_seed_theme() -> None:
    registry = load_theme_registry()
    assert "算力" in {theme.name for theme in registry.themes}
    assert {"AI应用", "充电桩", "数据安全", "创新药", "黄金", "油气", "户外经济", "文旅", "锂电池", "半导体", "新能源车", "电力资源", "节能装备", "信创", "新材料", "铜缆高速连接", "苹果链", "储能", "稀土永磁"} <= {
        theme.name for theme in registry.themes
    }


def test_load_source_definitions_include_http_runtime_settings() -> None:
    sources = {item.source_id: item for item in load_source_definitions()}
    assert sources["cninfo"].timeout_seconds == 10
    assert sources["cninfo"].user_agent
    assert sources["cninfo"].retry_count == 2
    assert sources["cninfo"].backoff_seconds == 1.0
