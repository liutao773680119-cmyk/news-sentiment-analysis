from news_sentiment.cli import main


def test_run_once_generates_text_report(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["run-once", "--source", "fixture"]) == 0
    report_path = tmp_path / "data" / "reports" / "latest_report.txt"
    assert report_path.exists()
    assert "关注" in report_path.read_text(encoding="utf-8")
