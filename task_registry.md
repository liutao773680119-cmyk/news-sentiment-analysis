# Task Registry

用于记录“当前有哪些并行任务正在推进、各自停在哪一步”。  
详细背景放 `task_plan.md / progress.md / findings.md`，这里只保留任务索引。

| Task-ID | Task-Name | Status | Owner | Last Update | Next First Command | Known Avoidances |
|---|---|---|---|---|---|---|
| `phase8-live-boundary` | `live 样本边界收口 + 交易所同模板错并修复 + irm/equity_incentive/cls/stcn 新漏样收口` | `active` | `main` | `2026-04-21` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` | `先看当天 report 头部和 audit-suspicious；不要只看 report 要同步看 events.jsonl；不沿用上一轮头部清单；没有新弱样本就先停；不要把 hkex staged 和主线混写；不要为追求全净继续过拟合 text_report；cls 单票跌停回应只压无题材解释稿；report 刷新后要核对目标样本是否真退出` |
| `phase9-source-expansion` | `第一批官方新闻源扩展` | `staged` | `main` | `2026-04-22` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment run-once --source hkex` | `hkex 仍是 staged；不要直接开进 --source all；不要把 CONNECTED/DISCLOSEABLE/MAJOR TRANSACTION 主干直接当低信号；先识别 AGM/EGM、delay、supplemental、framework、lease、results+suspension 这类材料尾巴；run-once 没 stdout 时要直接看 latest_report.txt` |

## Status Convention
- `active`: 正在推进
- `blocked`: 被外部条件或未决问题阻塞
- `staged`: 已有骨架，但未进入主链
- `done`: 已完成，暂时关闭
