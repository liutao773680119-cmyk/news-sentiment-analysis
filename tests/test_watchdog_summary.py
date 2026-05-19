import json
from pathlib import Path

from news_sentiment.cli import main


def _write_incident(path: Path, *, failed_sources: list[str], suspicious_titles: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "final": {
                    "failed_sources": failed_sources,
                    "suspicious_count": len(suspicious_titles),
                    "suspicious_titles": suspicious_titles,
                },
                "report_head": [
                    "[A股强催化]",
                    "[关注] 算力企业签署合作协议",
                    "事件类型: 合作协议",
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_watchdog_summary_writes_six_hour_markdown(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    log_path = tmp_path / "watch.log"
    log_path.write_text(
        "\n".join(
            [
                "===== 2026-05-20_00:00:00 =====",
                "watchdog_status=clean",
                "suspicious_count=0",
                "===== 2026-05-20_01:00:00 =====",
                "watchdog_status=alert",
                "failed_sources=szse:fetch_error",
                "suspicious_count=1",
                "===== 2026-05-20_06:30:00 =====",
                "watchdog_status=clean",
                "suspicious_count=0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    incident_dir = tmp_path / "data" / "monitoring" / "incidents"
    _write_incident(
        incident_dir / "20260520T010000Z-watchdog.json",
        failed_sources=["szse:fetch_error"],
        suspicious_titles=["中农发种业集团股份有限公司关于股东所持部分股份冻结的公告"],
    )
    _write_incident(
        incident_dir / "20260519T210000Z-watchdog.json",
        failed_sources=[],
        suspicious_titles=["窗口外旧标题"],
    )

    assert (
        main(
            [
                "watchdog-summary",
                "--hours",
                "6",
                "--now",
                "2026-05-20T06:00:00Z",
                "--log-path",
                str(log_path),
                "--log-timezone",
                "utc",
            ]
        )
        == 0
    )

    output = capsys.readouterr().out
    assert "summary_path=" in output
    summary_path = Path(output.strip().split("summary_path=", 1)[1])
    content = summary_path.read_text(encoding="utf-8")

    assert "# Watchdog Summary" in content
    assert "Window: 2026-05-20T00:00:00Z -> 2026-05-20T06:00:00Z" in content
    assert "- Iterations: 2" in content
    assert "- clean: 1" in content
    assert "- alert: 1" in content
    assert "- `szse:fetch_error`: 1" in content
    assert "中农发种业集团股份有限公司关于股东所持部分股份冻结的公告" in content
    assert "算力企业签署合作协议" in content
    assert "窗口外旧标题" not in content
