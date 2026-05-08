from pathlib import Path


def test_readme_mentions_venv_and_run_once() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    assert ".venv/bin/python -m pytest" in readme
    assert "run-once" in readme
    assert "live-smoke" in readme
    assert "watchdog-once" in readme
    assert "--source all" in readme
    assert "PYTHONPATH=src .venv/bin/python -m news_sentiment" in readme
