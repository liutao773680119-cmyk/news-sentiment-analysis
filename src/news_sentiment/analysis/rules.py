from __future__ import annotations

from news_sentiment.config_loader import load_theme_registry


def detect_themes(text: str) -> list[str]:
    registry = load_theme_registry()
    matches: list[str] = []
    normalized_text = text.lower()
    for theme in registry.themes:
        tokens = [theme.name, *theme.aliases]
        if any(token.lower() in normalized_text for token in tokens):
            matches.append(theme.name)
    return list(dict.fromkeys(matches))


def detect_direction(text: str) -> str:
    bullish_tokens = ("支持", "推进", "发布", "突破", "增长")
    bearish_tokens = ("限制", "处罚", "下滑", "收缩", "风险")
    if any(token in text for token in bullish_tokens):
        return "bullish"
    if any(token in text for token in bearish_tokens):
        return "bearish"
    return "neutral"
