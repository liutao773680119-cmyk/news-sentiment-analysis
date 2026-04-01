# A 股新闻情绪与题材雷达设计

日期：2026-04-01

## 目标

构建一个面向 `A 股盘中到次日` 的新闻驱动情绪雷达系统。系统持续采集高价值新闻与政策事件，归并为结构化事件，分析其对 A 股题材炒作情绪的潜在影响，同时输出对应题材与候选个股，并给出 `关注` 级提示。

第一版目标不是自动交易，而是验证 `新闻/事件 -> 题材 -> 个股 -> 关注信号` 这条链路是否稳定、够快、可解释、可回测。

## 第一版边界

- 输入范围：`硬事件 + 快讯 + 政策`
- 节奏范围：`盘中到次日`
- 输出对象：`题材/板块 + 个股`
- 交易动作：只输出 `关注`
- 股票池：`主板 + 创业板`，排除 `ST / 退市风险股`
- 题材体系：`固定题材库 + 新题材人工确认`
- 处理粒度：先 `事件归并`，再统一分析与打分

## 主要来源

### 1. 硬事件源

- 巨潮资讯
- 上证 e 服务 / e 互动
- 深交所互动易

### 2. 快讯媒体源

- 财联社
- 证券时报

### 3. 政策与宏观源

- 国务院新闻发布会
- 工信部新闻发布
- White House Briefings & Statements
- Federal Reserve Press Releases / FOMC
- EIA Weekly Petroleum Status Report
- OPEC Press Releases

## 总体链路

系统按单向流水线运行：

1. 采集新闻与公告
2. 清洗与标准化
3. 事件归并
4. LLM 结构化分析
5. 规则/因子评分
6. 题材识别
7. 个股映射
8. 历史相似事件对照
9. CLI / 文本报告输出

每一步都保留中间结果，保证可追溯、可调试、可回测。

## LLM 与多维度因子协同

本项目不采用“纯大模型直接给交易建议”的方式，而采用 `LLM + 结构化因子 + 历史对照` 的混合框架。

### LLM 负责

- 事件摘要
- 实体抽取
- 事件类型识别
- 题材识别
- 影响方向判断
- 影响理由生成

### 结构化因子负责

- 来源权威性
- 是否首次出现
- 是否属于公告/政策/高优先级快讯
- 是否明确点名产业、公司或商品
- 是否具备题材扩散潜力
- 是否匹配 `盘中到次日` 的交易时间窗

### 历史对照层负责

- 检索历史相似事件
- 校准当前事件处于历史冲击分布的什么位置
- 输出更接近交易语言的参考说明

## 事件归并与评分

### 事件归并

系统不直接按单条新闻出结论，而是先归并成 `event`。归并参考以下因素：

- 发布时间接近
- 标题与正文相似
- 核心实体一致
- 关键词与主题重叠
- 来源间的转载/扩散关系

事件归并后保留：

- 最早来源
- 最权威来源
- 所有成员新闻
- 首次出现时间
- 最后更新时间

### 事件评分

第一版输出：

- `direction`: 利多 / 利空 / 中性
- `impact_score`: 强度分数

当 `impact_score` 超过阈值时，系统输出 `关注` 结果。

## 题材库与个股映射

### 题材库三层结构

1. `标准题材标签`
2. `别名与触发词库`
3. `新题材候选区`

初始题材库来源采用 `现成概念板块 / 行业板块 + 人工修正`。

### 个股映射原则

系统不让模型直接猜股票，而是采用：

`事件 -> 题材 -> 股票`

每个题材维护股票映射关系，并为股票标注关联类型与权重，例如：

- 龙头
- 核心受益
- 次级受益
- 概念关联

最终按题材分与映射权重生成候选个股列表。

## 历史相似事件对照层

评分不使用固定“上限新闻模板”，而使用 `历史相似事件库` 进行校准。

### 历史主评价指标

- 股价表现
- 涨停家数
- 连板高度
- 成交额放大
- 持续天数

### 输出目的

让系统不仅回答“这次强不强”，还回答：

- 它像不像历史上的强催化事件
- 历史上同类事件引发了什么市场现象
- 当前事件大致处于历史冲击的什么分位

## 数据模型

第一版至少包含以下核心数据表：

### `raw_news`

- `news_id`
- `source`
- `source_type`
- `published_at`
- `captured_at`
- `title`
- `content`
- `url`

### `events`

- `event_id`
- `first_seen_at`
- `last_seen_at`
- `canonical_title`
- `summary`
- `member_news_ids`
- `event_type`
- `primary_entities`

### `event_analysis`

- `event_id`
- `direction`
- `impact_score`
- `reasoning`
- `themes`
- `new_theme_candidates`
- `time_window`
- `triggered`

### `theme_stock_map`

- `theme_id`
- `theme_name`
- `stock_code`
- `stock_name`
- `relation_type`
- `weight`

### `historical_events`

- `historical_event_id`
- `event_type`
- `themes`
- `keywords`
- `representative_stocks`
- `max_move`
- `limit_up_count`
- `board_height`
- `turnover_expansion`
- `duration_days`

## 建议目录结构

```text
src/news_sentiment/
  collectors/
  normalize/
  event_merge/
  analysis/
  themes/
  mapping/
  history/
  reporting/
  cli.py

configs/
  sources.yaml
  scoring.yaml
  prompts/

data/
  raw/
  normalized/
  events/
  processed/
  reference/
  reports/
```

## 第一版 CLI 工作流

建议提供以下命令：

- `collect`
- `normalize`
- `merge-events`
- `analyze-events`
- `report`
- `run-once`

其中 `run-once` 顺序执行整条链路，输出一份文本报告。

## 实现优先级

### Phase 1

- 接入少量高价值来源
- 跑通采集与清洗

### Phase 2

- 建立事件归并
- 建立初始题材库与题材到个股映射

### Phase 3

- 接入 LLM 结构化分析
- 建立规则评分器
- 输出第一版报告

### Phase 4

- 补充历史相似事件库
- 加入历史校准层

## GitHub 项目的借鉴边界

### 可以借

- `FinGPT / FinNLP`
  - 金融 NLP 任务拆解
  - 新闻下载器与数据接入思路
- `GDELT` 相关项目
  - 全球新闻事件化处理思路
- `FinRL`
  - 训练/测试/交易式流水线组织方式

### 不能直接借

- A 股题材知识图谱
- 题材到个股映射关系
- A 股超短情绪标签体系
- 历史相似事件对照库

以上四部分是本项目真正需要自建的核心壁垒。

## 下一步

完成设计确认后，进入实现准备阶段：

1. 固化目录与配置样板
2. 建立初始题材库与股票池参考表
3. 实现首批采集器
4. 跑通 `run-once` 最小闭环
