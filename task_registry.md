# Task Registry

用于记录“当前有哪些并行任务正在推进、各自停在哪一步”。  
详细背景放 `task_plan.md / progress.md / findings.md`，这里只保留任务索引。

| Task-ID | Task-Name | Status | Owner | Last Update | Next First Command | Known Avoidances |
|---|---|---|---|---|---|---|
| `phase8-live-boundary` | `旧 A股单线 live 样本边界收口口径` | `done` | `main` | `2026-04-22` | `sed -n '1,220p' task_plan.md` | `不要再把它当当前主线；不要用旧 phase8 标准验收当前 --source all；后续只作为历史口径参考` |
| `phase9-source-expansion` | `第一批官方新闻源扩展` | `staged` | `main` | `2026-04-22` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment run-once --source hkex` | `hkex 仍是 staged；不要直接开进 --source all；不要把 CONNECTED/DISCLOSEABLE/MAJOR TRANSACTION 主干直接当低信号；先识别 AGM/EGM、delay、supplemental、framework、lease、results+suspension 这类材料尾巴；run-once 没 stdout 时要直接看 latest_report.txt` |
| `global-multisource-mainline` | `全球多源主线验收标准重定标 + 报告分层` | `active` | `main` | `2026-04-22` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment run-once --source all` | `不要再按旧 phase8 的 A股单线标准验收；当前先只读看分层后的 live 头部，不要在 audit-suspicious=0 时继续过拟合；低信号先看模板材料/栏目稿/进展包，不要把海外/宏观样本一刀切当噪音` |
| `social-sidecar` | `社交线索层最小接线 + sidecar 展示` | `staged` | `main` | `2026-04-22` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect-social --platform fixture` | `只做 sidecar，不进主评分；不接 run-once/live-smoke；weibo 当前仍受 visitor gate/403 限制，不要误判成生产可用；先完成 report 分层，再决定社交线索放在哪一层` |

## Status Convention
- `active`: 正在推进
- `blocked`: 被外部条件或未决问题阻塞
- `staged`: 已有骨架，但未进入主链
- `done`: 已完成，暂时关闭
