# 新闻情感分析

这是一个面向 A 股新闻驱动题材雷达的 Python 项目。当前实现的是一个文件驱动的 MVP 基础链路：`collect -> normalize -> merge-events -> analyze-events -> report`，并已支持多源混跑。

## 当前目标

- 先跑通本地最小闭环
- 输出事件、题材、候选个股和历史参考
- 保持每一步都可追溯、可测试、可替换
- 社交源当前只作为 sidecar 线索层，不进入主评分

## 目录结构

- `docs/plans/`: 设计文档与实现计划
- `src/news_sentiment/`: 项目源码
- `tests/`: 测试
- `data/raw/`: 原始新闻
- `data/normalized/`: 清洗后的新闻
- `data/events/`: 事件与分析结果
- `data/reference/`: 题材、股票池、历史事件参考表
- `data/reports/`: 文本报告
- `data/social/`: 社交 sidecar 线索
- `configs/`: 来源、评分、提示词配置

## 本地开发

先创建虚拟环境并安装最小依赖：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install pytest PyYAML
```

运行测试：

```bash
.venv/bin/python -m pytest
```

## CLI 命令

逐步执行：

```bash
PYTHONPATH=src .venv/bin/python -m news_sentiment collect --source cninfo
PYTHONPATH=src .venv/bin/python -m news_sentiment normalize
PYTHONPATH=src .venv/bin/python -m news_sentiment merge-events
PYTHONPATH=src .venv/bin/python -m news_sentiment analyze-events
PYTHONPATH=src .venv/bin/python -m news_sentiment report
```

一条命令执行完整链路：

```bash
PYTHONPATH=src .venv/bin/python -m news_sentiment run-once --source fixture
```

多源混跑：

```bash
PYTHONPATH=src .venv/bin/python -m news_sentiment collect --source all
PYTHONPATH=src .venv/bin/python -m news_sentiment run-once --source all
PYTHONPATH=src .venv/bin/python -m news_sentiment live-smoke --source all
PYTHONPATH=src .venv/bin/python -m news_sentiment watchdog-once --source all --limit 10
```

`live-smoke` 会直接跑完整链路，并输出 `raw_news`、`events`、`analyses`、`failed_sources` 和报告路径。`failed_sources` 会附带错误类型，如 `fetch_error`、`parse_error`、`empty_result`，适合快速检查真实源当前是否可用。

`watchdog-once` 会在 `live-smoke` 之后自动跑一轮 `audit-suspicious` 口径检查；如果发现 `failed_sources`，会额外做单源探测、落盘 incident 快照到 `data/monitoring/incidents/`，并在“单源探测已恢复且 `suspicious_count=0`”时自动再跑一轮全源主链路，用来吸收瞬时抖动。

生成最近 6 小时后台汇总：

```bash
PYTHONPATH=src .venv/bin/python -m news_sentiment watchdog-summary --hours 6
```

汇总会读取 `data/monitoring/incidents/` 与 watchdog 日志，输出到 `data/monitoring/summaries/`。watchdog 日志按本机时区解析，后台 loop 默认每 6 小时自动生成一次汇总。

如需把后台 loop 切到自动处理版，直接运行仓库脚本：

```bash
scripts/run_news_sentiment_watchdog_loop.sh
```

可选环境变量：

- `NEWS_SENTIMENT_WATCH_LOG`: 日志路径，默认 `/tmp/news-sentiment-watch.log`
- `NEWS_SENTIMENT_WATCH_INTERVAL_SECONDS`: 轮询间隔，默认 `600`
- `NEWS_SENTIMENT_WATCH_LIMIT`: 巡检输出上限，默认 `10`
- `NEWS_SENTIMENT_WATCH_LOCK_DIR`: loop 锁目录，默认 `data/monitoring/news-sentiment-watch.lock`
- `NEWS_SENTIMENT_WATCH_HEARTBEAT_PATH`: heartbeat 状态文件，默认 `data/monitoring/watchdog_heartbeat.json`
- `NEWS_SENTIMENT_WATCH_INCIDENT_RETENTION`: incident 保留数量，默认 `200`
- `NEWS_SENTIMENT_SUMMARY_ENABLED`: 是否启用 6 小时汇总，默认 `1`
- `NEWS_SENTIMENT_SUMMARY_INTERVAL_SECONDS`: 汇总间隔，默认 `21600`
- `NEWS_SENTIMENT_SUMMARY_HOURS`: 每次汇总覆盖小时数，默认 `6`

社交 sidecar：

```bash
PYTHONPATH=src .venv/bin/python -m news_sentiment collect-social --platform fixture
PYTHONPATH=src .venv/bin/python -m news_sentiment collect-social --platform weibo
```

`collect-social` 当前只写 `data/social/social_signals.jsonl`，不会进入 `run-once` / `live-smoke` 主链路打分。`fixture` 用于验证写盘链路；`weibo` 目前先保留最小接线，若遇到访客门或 403，会输出 `warning: social_platform_failed=weibo:fetch_error:...`。
如需复用本机微博登录态，可在运行前临时设置 `WEIBO_COOKIE='...'`；collector 会额外带上 `Cookie` 和 `Referer` 请求头。不要把真实 cookie 写进仓库。

当前已接入的真实源：

- `cninfo`: 巨潮资讯公告
- `miit`: 工信部新闻发布
- `stcn`: 证券时报快讯
- `fixture`: 本地测试夹具源

真实源抓取当前支持来源级 `timeout`、`user-agent`、`retry_count` 和线性 `backoff_seconds` 配置。

## 报告输出

运行 `run-once` 后，文本报告会写到：

- `data/reports/latest_report.txt`

报告内容当前至少包含：

- 事件标题
- 来源
- 发布时间
- URL
- 方向
- 强度
- 题材
- 候选个股
- 历史相似事件参考
- `关注` 标记
- `社交热度观察` sidecar 区块（如果存在 `social_signals.jsonl`）

当前报告行为：

- 只展示 `triggered=True` 的事件
- 按强度从高到低排序
- 多源归并后优先展示更权威来源的事件元数据
