# Findings & Decisions

## Requirements
- 目标不是普通情感分类，而是“新闻事件/内容 -> A 股炒作情绪影响 -> 相关标的 -> 交易建议”。
- 第一阶段边界定为 `B`：生成交易信号建议，不自动下单。
- 交易节奏定为 `盘中到次日` 的超短机会。
- 用户要求扩大信息源覆盖面，包括国内外实时资讯、社交媒体、名人和专家账号。
- 用户要求额外搜索 GitHub 上类似项目并分析可复用性。
- MVP 采集范围定为 `B`：硬事件 + 快讯 + 政策。
- 信号输出对象改为 `C`：同时输出题材/板块和个股。
- 题材定义方式定为 `C`：固定题材库为主，同时允许发现新题材并人工确认。
- 影响输出格式定为 `B`：方向 + 强度分数。
- 新闻处理粒度定为 `B`：先归并成事件，再统一打分。
- 个股映射方式定为 `B`：先映射题材，再从题材库/产业链映射股票。
- 交易建议触发方式定为 `A`：只要新闻事件分数达到阈值，就直接给出交易建议，不等待市场确认。
- 建议动作输出定为 `A`：第一版只输出“关注”。
- 股票池范围定为 `B`：先做主板 + 创业板，排除 ST / 退市风险股。
- 新闻影响时间窗定为 `B`：当天盘中 + 次日有效。
- 第一版交付方式定为 `A`：先做命令行 / 文本报告。
- 初始题材库来源定为 `B`：先用现成概念板块 / 行业板块做初始库，再人工修正。
- 事件评分需要增加“历史相似事件对照层”，不用绝对上限，而用历史案例分位来衡量本次冲击强度。
- 历史对照层的主评价指标定为 `C`：股价 + 涨停/连板 + 成交额 + 持续天数。

## Research Findings
- 项目初始化已完成，当前进入外部调研阶段。
- 第一批高优先级来源已经确认：
  - `巨潮资讯` 是由深交所子公司运营的法定信息披露平台，覆盖沪深京公告、互动、数据服务，适合做公告与硬事件源。
  - `证券时报` 官方站展示 `7x24` 快讯与上市公司资讯，适合作为媒体快讯层。
- 对 A 股超短情绪交易而言，法定披露和快讯媒体应视为最早一层核心来源。
- `财联社` 被多个目录与软件说明描述为 `24 小时电报/快讯` 型财经通讯社，并强调其对全球多来源监控、人工筛选和题材解读能力，适合作为高频聚合层而非唯一原始源。
- `X` 官方开发平台当前提供程序化访问帖子、用户、列表、趋势等能力，并支持近实时 filtered stream；这使其适合用来跟踪海外政策人物、企业高管、行业专家和主题账号。
- `微博` 有官方开放平台与 API 文档入口，说明国内公开社交源里至少存在可程序化接入的一条正式路径。
- 大宗商品与全球宏观方面，`EIA` 官方每周发布石油状态报告，并给出精确发布时间表；这类固定时点数据可直接纳入事件日历与盘前/盘中触发器。
- `OPEC` 官方新闻与公报页持续发布部长级会议决定、补偿方案和产量调整，是能源链条题材的重要上游事件源。
- 海外媒体源方面，`CNBC` 官方站明确提供全球市场、商业与行业栏目，以及 breaking news / app alerts 能力，可作为国际新闻辅助层。
- 中国散户情绪层里，`东方财富股吧` 是一个高相关社区入口；其官方页直接展示热门个股吧、主题吧、人气榜与问董秘入口，适合作为题材热度与讨论强度补充源。
- `微信公众平台` 官方开发文档存在，但目前拿到的官方/半官方线索主要证明其支持“公众号开发能力”，并不能直接推出“官方提供全网公众号文章实时采集接口”。
- 中国政策与产业题材方面，`国务院新闻发布会` 与 `工信部新闻发布` 是高价值官方源。它们直接驱动半导体、算力、新能源、工业软件、数据要素等板块的预期变化。
- 海外政策与宏观源方面，`White House Briefings & Statements` 与 `Federal Reserve Press Releases / FOMC` 适合作为全球风险偏好与政策冲击源，尤其影响资源、出口链、跨境支付与金融板块。
- 除法定公告外，`上证e互动` 也是重要的 A 股情绪前哨。它是上交所建立的投资者与上市公司沟通平台，适合捕捉题材问答、公司口径变化与市场关注点。
- `深交所互动易` 进一步补足了另一侧交易所互动数据。当前可直接访问 `irm.cninfo.com.cn`，页面包含最新问答、热门问答与审核状态，是盘中事件和问董秘情绪的重要补充。
- GitHub 第一轮检索显示：
  - `news sentiment trading` 方向的公开仓库大量偏向加密货币或美股。
  - `FinBERT` 相关仓库更集中在“金融文本情绪建模”，而不是“新闻到交易执行”的完整闭环。
  - 这意味着开源世界里可复用的部分主要是 `NLP 模型/特征工程` 与 `策略框架骨架`，而 A 股特有的数据源映射与情绪标签体系大概率需要自建。
- GitHub 第二轮定向到 `A股/新闻/量化` 后，公开结果依然很少，进一步说明 A 股新闻驱动超短交易系统的公开工程沉淀不多。
- GitHub 第三轮更清晰地暴露出可复用层次：
  - `AI4Finance-Foundation/FinGPT` 代表金融领域 LLM/NLP 工具层。
  - `GDELT` 相关仓库代表全球新闻流抓取/检索层。
  - 但两者都不能直接解决 `新闻 -> A股题材映射 -> 超短交易建议` 这一最关键的中国市场特有问题。
- `FinRL` 类仓库更多提供策略训练或强化学习框架，对“新闻驱动超短交易”来说只能作为下游研究骨架，无法替代上游新闻理解系统。

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| 先做“来源地图”和“开源地图”，再做架构设计 | 避免先入为主，先确认可得数据与可复用模块 |

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| 本地未安装 `pytest` | 记录为后续环境初始化事项，不阻塞当前调研 |

## Resources
- `README.md`
- `task_plan.md`
- 巨潮资讯: https://www.cninfo.com.cn/
- 证券时报: https://stcn.com/
- 财联社: https://www.cls.cn/
- X Developer Platform: https://docs.x.com/
- X API Overview: https://docs.x.com/x-api
- 微博开放平台官方微博入口: https://www.weibo.com/openapi
- EIA Weekly Petroleum Status Report: https://www.eia.gov/petroleum/supply/weekly/
- EIA Weekly Release Schedule: https://www.eia.gov/petroleum/supply/weekly/schedule.php
- OPEC Press Releases: https://www.opec.org/press-releases.html
- CNBC Markets & Business: https://www.cnbc.com/
- 微信公众号开发文档入口: https://developers.weixin.qq.com/doc/offiaccount/Getting_Started/Overview.html
- 东方财富股吧: https://guba.eastmoney.com/
- 国务院新闻发布会示例: https://www.gov.cn/lianbo/fabu/202501/content_6998669.htm?slb=true
- 工信部新闻发布: https://www.miit.gov.cn/xwfb/gxdt/index.html
- White House Briefings & Statements: https://www.whitehouse.gov/briefings-statements/
- Federal Reserve Press Releases: https://www.federalreserve.gov/newsevents/pressreleases.htm
- Federal Reserve FOMC Releases: https://www.federalreserve.gov/newsevents/pressreleases/2026-press-fomc.htm
- 上证e互动上线说明: https://www.sse.com.cn/aboutus/mediacenter/hotandd/c/c_20150912_3988691.shtml
- 上证e服务: https://www.sseinfo.com/services/service/szefw/
- 深交所互动易: https://irm.cninfo.com.cn/newircs/
- GitHub repo: https://github.com/jasonyip184/StockSentimentTrading
- GitHub repo: https://github.com/xraptorgg/FinBERT-LSTM
- GitHub repo: https://github.com/KevinKuo41/Sentiment_Analysis_On_Financial_News_Headlines_With_BERT_And_FinBERT
- GitHub repo: https://github.com/paulwxq/fin_analysis
- GitHub repo: https://github.com/AI4Finance-Foundation/FinGPT
- GitHub repo: https://github.com/chaitanyaphalak/GDELTDataScripts
- GitHub repo: https://github.com/zchris07/FinRL-Ensemble-Stock-Trading

## Visual/Browser Findings
- 巨潮资讯首页明确写明其为“深圳证券交易所法定信息披露平台”，并提供公告、资讯、数据、互动等入口。
- 证券时报首页明确展示“7x24小时提供标准化快讯”，且强调上市公司资讯与非公告机会解读。
- 财联社相关公开介绍反复强调“24 小时电报”“全球多来源监控”“人工筛选”，说明其更像面向交易的高频二次加工流。
- X 官方文档明确写到支持 posts search、filtered stream、trends 与 pay-per-usage；对“监控特定账号 + 关键词”的海外事件捕捉很关键。
- 微博开放平台官方微博页面直接给出 `open.weibo.com` 与 API 文档入口，证明其仍保有官方开发者通道。
- EIA 官方页面给出周报的当前发布日期与下次发布日期，调度页还给出标准发布时间为每周三美东 `10:30 a.m.`，说明其非常适合做结构化事件驱动源。
- OPEC 官方页能直接看到按日期发布的 `OPEC+` 会议信息、部长级会议声明与产量调整决定；这类事件天然适合映射到原油、化工、航运与资源类 A 股情绪。
- CNBC 官方页面明确展示 `Markets`、`Latest Market News`、breaking news 与 app alerts，说明其适合作为国际市场辅助资讯流。
- 东方财富股吧页面直接展示 `热门个股吧`、`热门主题吧`、`人气榜` 与 `问董秘`，说明它不仅是讨论区，也是观察散户关注迁移和题材扩散的情绪面板。
- 微信开发文档入口能够验证“公众号/服务号开发能力”存在，但当前没有证据表明官方提供面向研究者的全量公众号文章流接口；这部分更可能要依赖订阅、人工白名单或第三方采集。
- 国务院新闻办页面会明确给出发布会时间、出席部门与问答实录；工信部新闻发布页则按“工信动态”“新闻发布会”“部领导活动”等栏目组织内容，说明这两类站点适合做政策事件源和时间线回放。
- White House 官方页面持续按日期发布 `Briefings & Statements`；Fed 官方页面则按年份和 FOMC 维度维护 press releases，说明两者都适合做结构化海外政策事件源。
- 上交所官方稿件明确写明 `上证e互动` 由上交所建立并于 2013 年 7 月 5 日上线试运行；上证信息站点则显示它已并入 `上证e服务` 投资者关系栏目。
- 深交所互动易当前页面可直接看到 `最新`、`热门`、`待审核` 等问答视图，证明它是一个实时可观察的互动事件流，而不只是静态资料页。
- GitHub 搜索结果表明，相似项目通常只覆盖单层能力：要么是情绪模型，要么是交易 demo，很少有适用于 A 股超短题材交易的完整生产级链路。
- 针对 `A股` 与 `akshare sentiment news` 的 GitHub 检索结果稀少甚至为空，说明不能指望直接拼装现成仓库完成你的目标。
- `FinGPT` 与 `GDELT` 的出现说明开源可借的是底层数据与模型积木，而不是适配你场景的现成交易系统。
- `FinRL` 搜索结果进一步确认：交易框架可以借，但 alpha 生成逻辑仍需围绕新闻与情绪重建。
