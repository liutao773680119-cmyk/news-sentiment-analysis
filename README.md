# 新闻情感分析

这是一个面向 A 股新闻驱动题材雷达的 Python 项目。当前实现的是一个文件驱动的 MVP 基础链路：`collect -> normalize -> merge-events -> analyze-events -> report`。

## 当前目标

- 先跑通本地最小闭环
- 输出事件、题材、候选个股和历史参考
- 保持每一步都可追溯、可测试、可替换

## 目录结构

- `docs/plans/`: 设计文档与实现计划
- `src/news_sentiment/`: 项目源码
- `tests/`: 测试
- `data/raw/`: 原始新闻
- `data/normalized/`: 清洗后的新闻
- `data/events/`: 事件与分析结果
- `data/reference/`: 题材、股票池、历史事件参考表
- `data/reports/`: 文本报告
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
.venv/bin/python -m news_sentiment collect --source fixture
.venv/bin/python -m news_sentiment normalize
.venv/bin/python -m news_sentiment merge-events
.venv/bin/python -m news_sentiment analyze-events
.venv/bin/python -m news_sentiment report
```

一条命令执行完整链路：

```bash
.venv/bin/python -m news_sentiment run-once --source fixture
```

## 报告输出

运行 `run-once` 后，文本报告会写到：

- `data/reports/latest_report.txt`

报告内容当前至少包含：

- 事件标题
- 方向
- 强度
- 题材
- 候选个股
- 历史相似事件参考
- `关注` / `观察` 标记
