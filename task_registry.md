# Task Registry

用于记录“当前有哪些并行任务正在推进、各自停在哪一步”。  
详细背景放 `task_plan.md / progress.md / findings.md`，这里只保留任务索引。

| Task-ID | Task-Name | Status | Owner | Last Update | Next First Command | Known Avoidances |
|---|---|---|---|---|---|---|
| `phase8-live-boundary` | `旧 A股单线 live 样本边界收口口径` | `done` | `main` | `2026-04-22` | `sed -n '1,220p' task_plan.md` | `不要再把它当当前主线；不要用旧 phase8 标准验收当前 --source all；后续只作为历史口径参考` |
| `phase9-source-expansion` | `第一批官方新闻源扩展` | `staged` | `main` | `2026-04-22` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment run-once --source hkex` | `hkex 仍是 staged；不要直接开进 --source all；不要把 CONNECTED/DISCLOSEABLE/MAJOR TRANSACTION 主干直接当低信号；先识别 AGM/EGM、delay、supplemental、framework、lease、results+suspension 这类材料尾巴；run-once 没 stdout 时要直接看 latest_report.txt` |
| `global-multisource-mainline` | `全球多源主线 live report 尾噪收口` | `active` | `main` | `2026-04-28` | `sed -n '1,160p' data/reports/latest_report.txt` | `不要再按旧 phase8 的 A股单线标准验收；audit=0 后仍要直接看 report 头部；当前头部已回到并购/风险/诉讼/合作样本，不要继续为了更短头部机械扩词；miit:fetch_error 单独排查；海外单股主题异动不要拉回 A股层` |
| `social-sidecar` | `社交线索层最小接线 + sidecar 展示` | `staged` | `main` | `2026-04-22` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect-social --platform fixture` | `fixture 已完成最小验收并真实写盘；只做 sidecar，不进主评分；不接 run-once/live-smoke；weibo 当前仍受 visitor gate/403 限制，不要误判成生产可用` |

## Status Convention
- `active`: 正在推进
- `blocked`: 被外部条件或未决问题阻塞
- `staged`: 已有骨架，但未进入主链
- `done`: 已完成，暂时关闭
