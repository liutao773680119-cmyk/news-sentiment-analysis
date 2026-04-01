# MVP Foundation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build the first runnable MVP foundation for the A-share news-driven theme radar, including file-backed pipeline commands, reference data loaders, deterministic event scoring, and a text report.

**Architecture:** Start with a file-backed local pipeline instead of a database. Use deterministic rules for collection, normalization, event merge, scoring, theme mapping, and reporting, while keeping LLM integration behind an interface so it can be added later without rewiring the pipeline.

**Tech Stack:** Python 3.9 virtualenv for local execution, pytest, stdlib `argparse`, stdlib `json`, stdlib `pathlib`, YAML via `PyYAML`.

---

### Task 1: Bootstrap Runtime Layout And CLI Entry

**Files:**
- Modify: `pyproject.toml`
- Create: `src/news_sentiment/cli.py`
- Create: `src/news_sentiment/__main__.py`
- Create: `src/news_sentiment/settings.py`
- Create: `tests/test_cli_smoke.py`

**Step 1: Write the failing test**

```python
from news_sentiment.cli import build_parser


def test_parser_exposes_expected_commands() -> None:
    parser = build_parser()
    choices = parser._subparsers._group_actions[0].choices
    assert {"collect", "normalize", "merge-events", "analyze-events", "report", "run-once"} <= set(choices)
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_cli_smoke.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing `build_parser`.

**Step 3: Write minimal implementation**

- Add optional dev dependency section for `pytest` and runtime dependency `PyYAML` in `pyproject.toml`
- Create `build_parser()` in `src/news_sentiment/cli.py`
- Add `main()` and `python -m news_sentiment` entry in `src/news_sentiment/__main__.py`
- Add a simple `ProjectPaths` helper in `src/news_sentiment/settings.py`

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_cli_smoke.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pyproject.toml src/news_sentiment/cli.py src/news_sentiment/__main__.py src/news_sentiment/settings.py tests/test_cli_smoke.py
git commit -m "feat: scaffold cli entrypoints"
```

### Task 2: Create Reference Data And Config Loaders

**Files:**
- Create: `configs/sources.yaml`
- Create: `configs/scoring.yaml`
- Create: `configs/prompts/event_summary.txt`
- Create: `configs/prompts/theme_classification.txt`
- Create: `data/reference/theme_registry.yaml`
- Create: `data/reference/theme_stock_map.csv`
- Create: `data/reference/stock_universe.csv`
- Create: `data/reference/historical_events.jsonl`
- Create: `src/news_sentiment/config_loader.py`
- Create: `tests/test_reference_data.py`

**Step 1: Write the failing test**

```python
from news_sentiment.config_loader import load_theme_registry


def test_load_theme_registry_contains_seed_theme() -> None:
    registry = load_theme_registry()
    assert "算力" in {theme.name for theme in registry.themes}
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_reference_data.py -v`
Expected: FAIL with missing loader or missing file.

**Step 3: Write minimal implementation**

- Seed `sources.yaml` with 3 enabled sources: one hard event source, one fast-news source, one policy source
- Seed `scoring.yaml` with deterministic weights and threshold
- Add initial prompts as plain text files
- Seed a small theme registry with aliases and status
- Seed a small theme-stock map and stock universe with a handful of rows
- Seed 3 to 5 historical event samples in JSONL
- Implement typed config/reference loaders in `config_loader.py`

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_reference_data.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add configs data/reference src/news_sentiment/config_loader.py tests/test_reference_data.py
git commit -m "feat: add seed configs and reference data loaders"
```

### Task 3: Build File-Backed Storage And Core Models

**Files:**
- Create: `src/news_sentiment/models.py`
- Create: `src/news_sentiment/storage.py`
- Create: `tests/test_storage.py`

**Step 1: Write the failing test**

```python
from news_sentiment.models import RawNews
from news_sentiment.storage import JsonlStore


def test_jsonl_store_round_trip(tmp_path) -> None:
    store = JsonlStore(tmp_path / "raw.jsonl", RawNews)
    record = RawNews(
        news_id="n1",
        source="fixture",
        source_type="fast_news",
        published_at="2026-04-01T09:30:00+08:00",
        captured_at="2026-04-01T09:31:00+08:00",
        title="title",
        content="body",
        url="https://example.com/1",
    )
    store.write_many([record])
    loaded = store.read_all()
    assert loaded == [record]
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_storage.py -v`
Expected: FAIL with missing model or store class.

**Step 3: Write minimal implementation**

- Add dataclass-based core models for `RawNews`, `NormalizedNews`, `Event`, `EventAnalysis`, `ThemeMatch`, `ReportRow`
- Implement generic JSONL read/write store helpers
- Create directories on demand under `data/raw`, `data/normalized`, `data/events`, `data/reports`

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_storage.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/news_sentiment/models.py src/news_sentiment/storage.py tests/test_storage.py
git commit -m "feat: add file backed stores and pipeline models"
```

### Task 4: Implement Collect And Normalize Commands

**Files:**
- Create: `src/news_sentiment/collectors/__init__.py`
- Create: `src/news_sentiment/collectors/base.py`
- Create: `src/news_sentiment/collectors/fixtures.py`
- Create: `src/news_sentiment/normalize/__init__.py`
- Create: `src/news_sentiment/normalize/core.py`
- Modify: `src/news_sentiment/cli.py`
- Create: `tests/test_collect_and_normalize.py`

**Step 1: Write the failing test**

```python
from news_sentiment.cli import main


def test_collect_then_normalize_writes_output(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["collect", "--source", "fixture"]) == 0
    assert main(["normalize"]) == 0
    assert (tmp_path / "data" / "normalized" / "normalized_news.jsonl").exists()
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_collect_and_normalize.py -v`
Expected: FAIL because commands do not exist or files are not written.

**Step 3: Write minimal implementation**

- Add collector base protocol and a deterministic fixture collector
- Implement content normalization: trim whitespace, normalize timestamps, preserve source metadata
- Wire `collect` and `normalize` into CLI
- Use fixture data first for deterministic tests

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_collect_and_normalize.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/news_sentiment/collectors src/news_sentiment/normalize src/news_sentiment/cli.py tests/test_collect_and_normalize.py
git commit -m "feat: add collect and normalize commands"
```

### Task 5: Implement Event Merge

**Files:**
- Create: `src/news_sentiment/event_merge/__init__.py`
- Create: `src/news_sentiment/event_merge/core.py`
- Modify: `src/news_sentiment/cli.py`
- Create: `tests/test_event_merge.py`

**Step 1: Write the failing test**

```python
from news_sentiment.event_merge.core import merge_news_items
from news_sentiment.models import NormalizedNews


def test_merge_news_items_groups_similar_titles() -> None:
    items = [
        NormalizedNews(... title="工信部发文支持算力基础设施", ...),
        NormalizedNews(... title="工信部支持算力基础设施建设", ...),
    ]
    events = merge_news_items(items)
    assert len(events) == 1
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_event_merge.py -v`
Expected: FAIL with missing merger logic.

**Step 3: Write minimal implementation**

- Implement a deterministic title/entity/keyword overlap merger
- Preserve first-seen time, last-seen time, canonical title, and member news ids
- Wire `merge-events` command into CLI

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_event_merge.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/news_sentiment/event_merge src/news_sentiment/cli.py tests/test_event_merge.py
git commit -m "feat: add deterministic event merge"
```

### Task 6: Implement Deterministic Analysis And Scoring

**Files:**
- Create: `src/news_sentiment/analysis/__init__.py`
- Create: `src/news_sentiment/analysis/rules.py`
- Create: `src/news_sentiment/analysis/scoring.py`
- Modify: `src/news_sentiment/cli.py`
- Create: `tests/test_analysis_scoring.py`

**Step 1: Write the failing test**

```python
from news_sentiment.analysis.scoring import score_event
from news_sentiment.models import Event


def test_score_event_flags_policy_event_as_triggered() -> None:
    event = Event(... source_authority_score=0.95, canonical_title="工信部发布算力政策", ...)
    analysis = score_event(event, scoring_config=...)
    assert analysis.triggered is True
    assert analysis.direction == "bullish"
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_analysis_scoring.py -v`
Expected: FAIL with missing scoring logic.

**Step 3: Write minimal implementation**

- Implement deterministic theme detection from title/content aliases
- Implement direction and impact scoring from source priority, event type, freshness, and explicit trigger words
- Reserve an analyzer interface for future LLM integration
- Wire `analyze-events` command into CLI

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_analysis_scoring.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/news_sentiment/analysis src/news_sentiment/cli.py tests/test_analysis_scoring.py
git commit -m "feat: add event analysis and scoring"
```

### Task 7: Implement Theme-To-Stock Mapping And Historical Matching

**Files:**
- Create: `src/news_sentiment/themes/__init__.py`
- Create: `src/news_sentiment/themes/registry.py`
- Create: `src/news_sentiment/mapping/__init__.py`
- Create: `src/news_sentiment/mapping/stock_mapper.py`
- Create: `src/news_sentiment/history/__init__.py`
- Create: `src/news_sentiment/history/matcher.py`
- Create: `tests/test_mapping_and_history.py`

**Step 1: Write the failing test**

```python
from news_sentiment.history.matcher import match_historical_events
from news_sentiment.mapping.stock_mapper import map_themes_to_stocks


def test_map_themes_to_stocks_returns_weighted_candidates() -> None:
    rows = map_themes_to_stocks(["算力"])
    assert rows[0].stock_code
    assert rows[0].weight > 0
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_mapping_and_history.py -v`
Expected: FAIL with missing mapping or matcher.

**Step 3: Write minimal implementation**

- Load theme registry and stock mapping from reference data
- Rank stock candidates by relation type and weight
- Match historical events by shared themes and keywords
- Return top comparable samples with basic summary fields

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_mapping_and_history.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/news_sentiment/themes src/news_sentiment/mapping src/news_sentiment/history tests/test_mapping_and_history.py
git commit -m "feat: add stock mapping and historical matching"
```

### Task 8: Implement Text Reporting And `run-once`

**Files:**
- Create: `src/news_sentiment/reporting/__init__.py`
- Create: `src/news_sentiment/reporting/text_report.py`
- Modify: `src/news_sentiment/cli.py`
- Create: `tests/test_report_pipeline.py`

**Step 1: Write the failing test**

```python
from news_sentiment.cli import main


def test_run_once_generates_text_report(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["run-once", "--source", "fixture"]) == 0
    report_path = tmp_path / "data" / "reports" / "latest_report.txt"
    assert report_path.exists()
    assert "关注" in report_path.read_text(encoding="utf-8")
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_report_pipeline.py -v`
Expected: FAIL because `run-once` or report generation is missing.

**Step 3: Write minimal implementation**

- Implement report rendering with event summary, direction, impact score, themes, stocks, and historical comparables
- Add `report` command for already-generated analysis
- Add `run-once` orchestration command

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_report_pipeline.py -v`
Expected: PASS

**Step 5: Run full test suite**

Run: `.venv/bin/python -m pytest`
Expected: all tests PASS

**Step 6: Commit**

```bash
git add src/news_sentiment/reporting src/news_sentiment/cli.py tests/test_report_pipeline.py
git commit -m "feat: add text report and run-once pipeline"
```

### Task 9: Document Local Developer Workflow

**Files:**
- Modify: `README.md`
- Create: `tests/test_readme_commands.py`

**Step 1: Write the failing test**

```python
from pathlib import Path


def test_readme_mentions_venv_and_run_once() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    assert ".venv/bin/python -m pytest" in readme
    assert "run-once" in readme
```

**Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/test_readme_commands.py -v`
Expected: FAIL because README does not document the workflow yet.

**Step 3: Write minimal implementation**

- Add local environment setup instructions using `.venv`
- Add command examples for each CLI stage
- Add one example of the expected text report shape

**Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/test_readme_commands.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add README.md tests/test_readme_commands.py
git commit -m "docs: add local workflow instructions"
```

## Notes

- Keep the first implementation deterministic. Do not add live network collectors until the pipeline and tests are stable.
- Add future LLM integration behind an interface in `analysis/`, but do not require external APIs in the first green build.
- Prefer fixture-driven tests over real HTTP in the initial milestone.
- Keep intermediate artifacts on disk so the report is fully traceable.

Plan complete and saved to `docs/plans/2026-04-01-mvp-foundation-implementation.md`. Two execution options:

**1. Subagent-Driven (this session)** - I dispatch fresh subagent per task, review between tasks, fast iteration

**2. Parallel Session (separate)** - Open new session with executing-plans, batch execution with checkpoints

Which approach?
