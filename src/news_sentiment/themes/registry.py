from __future__ import annotations

from news_sentiment.config_loader import load_theme_registry


def list_theme_names() -> list[str]:
    return [theme.name for theme in load_theme_registry().themes]
