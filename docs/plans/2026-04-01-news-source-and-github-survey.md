# 新闻源与 GitHub 相似项目调研

日期：2026-04-01

## 调研目标

为“A 股盘中到次日超短情绪交易”任务建立来源地图，识别哪些实时新闻、公告、社交与政策源值得优先接入，同时评估 GitHub 上哪些开源项目可以复用。

## 结论摘要

1. 最值得优先接入的不是“更大而全”的新闻站，而是能最早触发题材炒作的几层源：
   - 法定披露：巨潮资讯、交易所公告
   - 交易所互动：上证 e 服务 / e 互动、深交所互动易
   - 快讯媒体：财联社、证券时报
   - 散户情绪面板：东方财富股吧
   - 政策事件源：国务院、工信部、Fed、White House、EIA、OPEC
   - 海外社交/专家账号：X
2. “海外资讯很重要”，但它更像题材触发器与预期放大器，而不是直接给出 A 股标的的现成答案。
3. GitHub 上没有接近完整的“A 股新闻 -> 情绪 -> 题材 -> 标的 -> 交易建议”成品。可复用的是：
   - NLP / 金融模型层：FinGPT、FinBERT 类
   - 全球新闻流层：GDELT 类
   - 下游研究框架层：FinRL 类
4. 你真正要自建的核心壁垒有三块：
   - A 股题材知识图谱
   - 新闻到题材/标的映射规则与模型
   - 超短情绪标签与回测框架

## 来源分层

### 1. 硬事件源

- 巨潮资讯
- 上交所 / 深交所公告
- 上证 e 服务 / e 互动
- 深交所互动易

用途：
- 抓公告、问答、公司确认口径、监管变化
- 对盘中异动最有解释力

### 2. 快讯媒体源

- 财联社
- 证券时报

用途：
- 抓突发新闻、产业链传导、题材整理
- 适合作为高频聚合层

注意：
- 这类源通常是二次编辑与聚合，重要新闻仍应回溯到原始出处做交叉验证

### 3. 政策与宏观源

- 国务院新闻发布会
- 工信部新闻发布
- White House Briefings & Statements
- Federal Reserve Press Releases / FOMC
- EIA Weekly Petroleum Status Report
- OPEC Press Releases

用途：
- 识别政策驱动、行业催化和全球风险偏好变化
- 适合构建事件日历

### 4. 社交与情绪源

- X
- 微博
- 东方财富股吧
- 微信公众号白名单

用途：
- 监控名人、政策人物、专家、分析师、行业 KOL
- 观察散户情绪扩散速度

注意：
- 微信公众平台官方文档能证明公众号开发能力存在，但当前没有足够证据表明官方提供全网公众号文章实时采集接口

## GitHub 项目结论

### 可以借的

- `AI4Finance-Foundation/FinGPT`
  - 适合借金融领域 LLM / NLP 能力
- `xraptorgg/FinBERT-LSTM`
  - 适合借金融情绪模型思路
- `chaitanyaphalak/GDELTDataScripts`
  - 适合借全球新闻流抓取思路
- `zchris07/FinRL-Ensemble-Stock-Trading`
  - 适合借下游研究/策略框架

### 借不了的

- A 股新闻驱动超短交易的完整工程闭环
- A 股题材知识图谱
- 新闻到概念板块再到个股的映射系统
- 超短情绪标签体系与触发条件

## 对系统设计的直接启发

第一阶段不应该做成“单一模型判断新闻好坏”，而应该做成多层流水线：

1. 多源采集
2. 去重与事件归并
3. 事件分类
4. 情绪/预期影响分析
5. A 股题材映射
6. 个股候选生成
7. 交易建议打分

## 参考链接

- 巨潮资讯: https://www.cninfo.com.cn/
- 证券时报: https://stcn.com/
- 财联社: https://www.cls.cn/
- 上证 e 服务: https://www.sseinfo.com/services/service/szefw/
- 深交所互动易: https://irm.cninfo.com.cn/newircs/
- 东方财富股吧: https://guba.eastmoney.com/
- X API: https://docs.x.com/x-api
- 微博开放平台入口: https://www.weibo.com/openapi
- 微信公众号开发文档: https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html
- 国务院新闻发布会示例: https://www.gov.cn/lianbo/fabu/202501/content_6998669.htm?slb=true
- 工信部新闻发布: https://www.miit.gov.cn/xwfb/gxdt/index.html
- White House Briefings & Statements: https://www.whitehouse.gov/briefings-statements/
- Federal Reserve Press Releases: https://www.federalreserve.gov/newsevents/pressreleases.htm
- EIA Weekly Petroleum Status Report: https://www.eia.gov/petroleum/supply/weekly/
- OPEC Press Releases: https://www.opec.org/press-releases.html
- FinGPT: https://github.com/AI4Finance-Foundation/FinGPT
- GDELTDataScripts: https://github.com/chaitanyaphalak/GDELTDataScripts
- FinRL-Ensemble-Stock-Trading: https://github.com/zchris07/FinRL-Ensemble-Stock-Trading
