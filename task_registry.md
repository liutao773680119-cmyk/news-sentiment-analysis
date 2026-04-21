# Task Registry

用于记录“当前有哪些并行任务正在推进、各自停在哪一步”。  
详细背景放 `task_plan.md / progress.md / findings.md`，这里只保留任务索引。

| Task-ID | Task-Name | Status | Owner | Last Update | Next First Command | Known Avoidances |
|---|---|---|---|---|---|---|
| `phase8-live-boundary` | `live 样本边界收口 + irm 问答/股权激励材料/cls/stcn 栏目稿降噪` | `active` | `main` | `2026-04-21` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` | `先看当天 report 头部和 audit-suspicious；不沿用上一轮头部清单；头部如果已回到 Robotaxi/退市风险/中标类 legit 样本先停；不要把当前 legit 样本继续硬压；不要把 hkex staged 和主线混写；不要为追求全净继续过拟合 text_report` |
| `phase9-source-expansion` | `第一批官方新闻源扩展` | `staged` | `main` | `2026-04-17` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect --source hkex` | `hkex 已补最小英文 subtype 和 report 接线，但仍是 staged；不要直接开进 --source all；不要让 hkex 继续走字符重合归并；不要把 INSIDE INFORMATION 整体当成单一 subtype；先跑 hkex 单源顺序链路，再决定是否继续扩源` |

## Status Convention
- `active`: 正在推进
- `blocked`: 被外部条件或未决问题阻塞
- `staged`: 已有骨架，但未进入主链
- `done`: 已完成，暂时关闭
