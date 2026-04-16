# Task Registry

用于记录“当前有哪些并行任务正在推进、各自停在哪一步”。  
详细背景放 `task_plan.md / progress.md / findings.md`，这里只保留任务索引。

| Task-ID | Task-Name | Status | Owner | Last Update | Next First Command | Known Avoidances |
|---|---|---|---|---|---|---|
| `phase8-live-boundary` | `live 样本边界收口 + 低信号披露/cls 栏目稿降噪` | `active` | `main` | `2026-04-17` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` | `先看当天 report 头部和 audit-suspicious；不沿用上一轮头部清单；不要继续压 cls 全球内容；不要把【公告全知道】直接当编辑稿压掉；不要把华测导航的业务合作+对外担保自动并入授信/担保额度材料；不要把申请撤销对公司股票交易实施退市风险警示重新打回 bearish` |
| `phase9-source-expansion` | `第一批官方新闻源扩展` | `staged` | `main` | `2026-04-15` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect --source hkex` | `cls 已完成并入；hkex 仍是 staged；不要直接开进 --source all；先做最小验收，不要把全球快讯目标重新收回 A 股单线目标` |

## Status Convention
- `active`: 正在推进
- `blocked`: 被外部条件或未决问题阻塞
- `staged`: 已有骨架，但未进入主链
- `done`: 已完成，暂时关闭
