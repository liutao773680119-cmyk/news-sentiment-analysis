from pathlib import Path


def test_readme_mentions_venv_and_run_once() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    assert ".venv/bin/python -m pytest" in readme
    assert "run-once" in readme
