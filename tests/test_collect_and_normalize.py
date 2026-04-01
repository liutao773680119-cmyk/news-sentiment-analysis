from news_sentiment.cli import main


def test_collect_then_normalize_writes_output(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["collect", "--source", "fixture"]) == 0
    assert main(["normalize"]) == 0
    assert (tmp_path / "data" / "normalized" / "normalized_news.jsonl").exists()
