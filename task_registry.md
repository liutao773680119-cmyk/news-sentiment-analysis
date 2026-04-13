# Task Registry

用于记录“当前有哪些并行任务正在推进、各自停在哪一步”。  
详细背景放 `task_plan.md / progress.md / findings.md`，这里只保留任务索引。

| Task-ID | Task-Name | Status | Owner | Last Update | Next First Command | Known Avoidances |
|---|---|---|---|---|---|---|
| `phase8-live-boundary` | `live 样本边界收口` | `active` | `main` | `2026-04-13` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` | `先看当天 report 头部和 audit-suspicious；不沿用上一轮头部清单；冻结/解除冻结先判断是否为实质风险，不自动压低` |
| `phase9-source-expansion` | `第一批官方新闻源扩展` | `active` | `main` | `2026-04-11` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect --source hkex` | `hkex 已验通但噪音重；启用前先补最小过滤；不要直接开进 --source all` |

## Status Convention
- `active`: 正在推进
- `blocked`: 被外部条件或未决问题阻塞
- `staged`: 已有骨架，但未进入主链
- `done`: 已完成，暂时关闭
