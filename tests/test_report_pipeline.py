from news_sentiment.cli import main


def test_run_once_generates_text_report(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["run-once", "--source", "fixture"]) == 0
    report_path = tmp_path / "data" / "reports" / "latest_report.txt"
    assert report_path.exists()
    content = report_path.read_text(encoding="utf-8")
    assert "关注" in content
    assert "来源:" in content
    assert "发布时间:" in content
    assert "URL:" in content
