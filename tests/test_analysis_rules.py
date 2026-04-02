from news_sentiment.analysis.rules import detect_themes


def test_detect_themes_matches_ai_application_aliases() -> None:
    text = "Sora退出后，可灵AI周度活跃用户环比增长，Qwen新版本继续发布。"
    assert "AI应用" in detect_themes(text)


def test_detect_themes_matches_charging_infra_aliases() -> None:
    text = "四川提出到2027年底建成205万个充电设施，提升公共充电容量。"
    assert "充电桩" in detect_themes(text)


def test_detect_themes_matches_data_security_aliases() -> None:
    text = "科学家实现DNA安全加密实景测试，为敏感领域通信加密开辟新途径。"
    assert "数据安全" in detect_themes(text)


def test_detect_themes_matches_innovative_drug_aliases() -> None:
    text = "礼来口服GLP-1减肥药获批上市，曲妥珠单抗销售目标仍保持增长。"
    themes = detect_themes(text)
    assert "创新药" in themes
