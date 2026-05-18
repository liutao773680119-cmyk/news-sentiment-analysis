# Task Registry

用于记录“当前有哪些并行任务正在推进、各自停在哪一步”。  
详细背景放 `task_plan.md / progress.md / findings.md`，这里只保留任务索引。

| Task-ID | Task-Name | Status | Owner | Last Update | Next First Command | Known Avoidances |
|---|---|---|---|---|---|---|
| `phase8-live-boundary` | `旧 A股单线 live 样本边界收口口径` | `done` | `main` | `2026-04-22` | `sed -n '1,220p' task_plan.md` | `不要再把它当当前主线；不要用旧 phase8 标准验收当前 --source all；后续只作为历史口径参考` |
| `phase9-source-expansion` | `第一批官方新闻源扩展` | `staged` | `main` | `2026-04-22` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment run-once --source hkex` | `hkex 仍是 staged；不要直接开进 --source all；不要把 CONNECTED/DISCLOSEABLE/MAJOR TRANSACTION 主干直接当低信号；先识别 AGM/EGM、delay、supplemental、framework、lease、results+suspension 这类材料尾巴；run-once 没 stdout 时要直接看 latest_report.txt` |
| `global-multisource-mainline` | `全球多源主线 live report 尾噪收口` | `active` | `main` | `2026-05-19` | `rg -n '^=====|watchdog_status=|failed_sources=|suspicious_count=' /tmp/news-sentiment-watch.log | tail -n 40` | `不要再按旧 phase8 的 A股单线标准验收；audit=0 后仍要直接看 report 头部；report 过滤和 audit-suspicious 要同步；report 重写和读取不要并行；不要查错 analyses 路径，当前是 data/events/event_analysis.jsonl；不要硬绑旧 event_id 排 live 问题；cninfo 年报问询函和发行优先股/诉讼材料先走最窄 title-only 口径，不扩题材；外盘指数+题材板块联动若有 A股映射，按 market_reference 保留 report，仅从 audit 异常口径排除；A股概念走强/活跃或板块震荡走强且带涨停/连板/创新高/大涨/涨幅居前上下文时也按 market_reference 处理，不当噪音删除；港股主题股异动且有明确A股题材映射时也按 market_reference 处理；短标题诉讼/仲裁材料只按 audit 尾噪处理；募集资金账户被冻结按用户口径视作 audit 尾噪；会见/交流类只有在无签署/中标/订单/合同/采购时才按尾噪；淘金互动易算力产业链按 market_reference 保留报告；suspicious_count=0 但 watchdog alert 时优先排查 failed_sources` |
| `social-sidecar` | `社交线索层最小接线 + sidecar 展示` | `staged` | `main` | `2026-04-22` | `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect-social --platform fixture` | `fixture 已完成最小验收并真实写盘；只做 sidecar，不进主评分；不接 run-once/live-smoke；weibo 当前仍受 visitor gate/403 限制，不要误判成生产可用` |

## Status Convention
- `active`: 正在推进
- `blocked`: 被外部条件或未决问题阻塞
- `staged`: 已有骨架，但未进入主链
- `done`: 已完成，暂时关闭
