# Progress Log

## Session: 2026-04-01

### Phase 1: 初始化、调研、设计
- **Status:** complete
- Actions taken:
  - 初始化仓库与 Python 项目骨架
  - 完成新闻源与 GitHub 同类项目调研
  - 通过多轮头脑风暴收敛 MVP 边界
  - 写出调研文档与设计文档
- Key outputs:
  - `docs/plans/2026-04-01-news-source-and-github-survey.md`
  - `docs/plans/2026-04-01-ashare-news-sentiment-design.md`

### Phase 2: MVP 基础链路
- **Status:** complete
- Actions taken:
  - 落地 `collect -> normalize -> merge-events -> analyze-events -> report`
  - 建立 JSONL 存储与 CLI 入口
  - 跑通 fixture 驱动最小闭环
- Key files:
  - `src/news_sentiment/cli.py`
  - `src/news_sentiment/storage.py`
  - `src/news_sentiment/reporting/text_report.py`

### Phase 3: 真实源接入与 HTTP 稳定性
- **Status:** complete
- Actions taken:
  - 接入 `miit` 动态接口
  - 接入 `stcn` JSON 快讯接口
  - 接入 `cninfo` 官方公告查询接口
  - 增加 `timeout / user-agent / retry / backoff`
  - 增加 `live-smoke --source all`
- Key files:
  - `src/news_sentiment/collectors/miit.py`
  - `src/news_sentiment/collectors/stcn.py`
  - `src/news_sentiment/collectors/cninfo.py`
  - `src/news_sentiment/collectors/http.py`
  - `configs/sources.yaml`

### Phase 4: 报告收紧与事件细分
- **Status:** complete
- Actions taken:
  - 报告增加来源、发布时间、URL
  - 过滤未触发、旧闻和中性噪音项
  - 增加 `event_subtype`
  - 为 `fast_news / hard_event / policy` 增加交易化细分类
- Key files:
  - `src/news_sentiment/reporting/text_report.py`
  - `src/news_sentiment/event_merge/core.py`

### Phase 5: 题材、个股、历史样本增强
- **Status:** complete
- Actions taken:
  - 扩展题材库与别名
  - 扩展 `theme_stock_map.csv`
  - 扩展 `historical_events.jsonl`
  - 补齐 `AI应用 / 充电桩 / 数据安全 / 黄金 / 油气 / 半导体 / 户外经济 / 锂电池`
- Key files:
  - `data/reference/theme_registry.yaml`
  - `data/reference/theme_stock_map.csv`
  - `data/reference/historical_events.jsonl`
  - `src/news_sentiment/analysis/rules.py`

### Phase 6: 归并增强与公司题材映射
- **Status:** complete
- Actions taken:
  - 增加同资产 `market_move` 归并
  - 增加同股票、同催化子类的 `cninfo` 材料归并
  - 增加 `company_theme_map.csv`
  - 只对催化型 `cninfo` 子类启用公司题材映射
- Key files:
  - `src/news_sentiment/event_merge/core.py`
  - `src/news_sentiment/analysis/rules.py`
  - `src/news_sentiment/analysis/scoring.py`
  - `data/reference/company_theme_map.csv`

## Current Verification

| Check | Result |
|---|---|
| `pytest` | `69 passed` |
| `live-smoke --source all` | `raw_news=64 normalized_news=64 events=51 analyses=51 failed_sources=none` |
| Branch status | clean |

## Recent Commits

| Commit | Summary |
|---|---|
| `d854a9d` | `map cninfo catalysts to themes` |
| `cc58b91` | `add commodity themes and market-move dedupe` |
| `d0c887c` | `expand theme detection and seed mappings` |
| `296fb86` | `refine fast-news event subtype classification` |
| `ff2c8b7` | `classify event subtypes in reports` |

## Current Report Characteristics
- 真实报告已经能输出：
  - `创新药`
  - `户外经济`
  - `文旅`
  - `新能源车`
  - `锂电池`
  - `半导体`
  - `算力`
  - `黄金`
  - `机器人`
- `cninfo` 催化公告已经能带出题材和个股。
- 同资产市场异动快讯已经能收敛成一个事件。

## Open Issues
- 一部分 `cninfo` 公告虽然已收敛，但仍可能因“催化材料包”形式占据报告前列。
- `300489` 这类 `股权激励` 公告还没有稳定题材落点。
- 还没有引入市场确认层、LLM 理解层和真实回测。

## Session: 2026-04-02

### Phase 7: 题材误命中收紧
- **Status:** complete
- Actions taken:
  - 为 `上市申请`、`H股发行`、`分布式发电系统` 三类宽词补了负向回归测试
  - 补了 `锂电池` 正向 alias 覆盖，避免修复时把有效主题一起删掉
  - 从 `theme_registry.yaml` 中移除上述三类宽泛 alias，改为依赖更窄的主题词和上下文
  - 为 `cninfo` 无题材材料公告补了报告排序回归测试
  - 下调 `corporate_disclosure / board_resolution / equity_incentive` 这类无题材 `cninfo` 文档的报告优先级
  - 重新运行 worktree 完整测试与真实源 `live-smoke`
  - 为 `文旅` 补充最小题材 seed、个股映射和历史样本
  - 在真实 report 中接住 `2026清明档电影片单发布` -> `文旅`
  - 为 `新能源车` 补充最小题材 seed、个股映射和历史样本
  - 在真实 report 中接住 `乘联分会：3月全国乘用车厂商新能源批发预估112万辆` -> `新能源车`
  - 为 `cninfo` 的 `进展公告 / 通知债权人 / 风险评估报告 / 股权激励法律意见书` 补了过滤回归测试
  - 在 report 层过滤上述低信号 `cninfo` 材料公告
  - 为 `欧洲主要股指跌幅扩大` 这类海外指数篮子快讯补了过滤回归测试
  - 保留 `沪指` / `WTI原油期货` 这类可交易市场异动，避免一刀切误伤
  - 将 `fast_news` 的催化判断从“标题+摘要”收紧为“标题级命中”，避免业绩快讯摘要中的泛化 `订单` 误入 report
  - 用回归测试锁定 `国瑞科技：2025年亏损...` 这类摘要带 `订单` 的误入场景
  - 为 `电力资源` 补充最小题材 seed、个股映射和历史样本
  - 用回归测试锁定 `中国能建与华北电力大学签署战略合作协议` -> `电力资源`
  - 为 `cninfo` 的 `风险持续评估报告` 变体补了过滤回归测试
  - 在 report 层过滤 `风险持续评估报告`，避免同类材料公告重新漏回 report
  - 为 `美股三大指数集体低开 特斯拉跌超3%` 补了回归测试，锁定海外指数 `market_move` 摘要误带 `半导体` 的场景
  - 将 `fast_news` 的 `market_move` 题材提取收紧到标题级，避免摘要里的板块描述误带主题
  - 在 report 层过滤 `美股/海外指数类` `stcn` 快讯，即使摘要误带题材也不再占位
  - 在 report 层过滤 `港交所上市申请书` 这类 `stcn` 无题材快讯
  - 在 report 层过滤 `stcn` 的无题材股东减持快讯，如 `拟减持 / 减持不超`
  - 为 `cninfo` 的 `减持预披露 / 终止减持计划 / 回购股份用途并注销` 三类高频一般公告补了过滤回归测试
  - 在 report 层过滤上述 `cninfo` 一般公告，进一步压缩 `题材: 无` 尾项
  - 为 `功率半导体行业维持高景气` 这类样本补了回归测试，锁定 `fast_news` 标题主题优先于摘要 spillover 的行为
  - 将 `fast_news` 题材提取收紧到“标题优先、摘要兜底”，把 `功率半导体` 一类样本从 `半导体 + 算力 + 新能源车 + 机器人` 收窄为标题主题
  - 为 `董事会审计与风险管理委员会...履行监督职责情况的报告` 这类 `board_resolution` 材料文档补了过滤回归测试
  - 在 report 层过滤上述低信号 `board_resolution` 材料文档
  - 为 `国产EDA工具链和先进封装产线建设提速` 这类样本补了 `半导体` 边界回归测试
  - 将 `半导体` 扩到 `EDA / 先进封装`，并补了更贴题的代表股映射与历史关键词
  - 为 `*ST金刚：2025年净利润...` 补了回归测试，锁定业绩类 `business_guidance` 摘要误带 `算力` 的场景
  - 将业绩类 `business_guidance` 的题材提取收紧到标题级，避免年报/摘帽快讯被摘要里的赛道词误抬
  - 为 `国内期货市场夜盘收盘多数下跌 沥青跌超2%` 补了 report 过滤回归测试
  - 在 report 层过滤 `国内期货市场夜盘收盘` 这类 commodity roundup，避免无题材夜盘综述占位
  - 为 `述职报告 / 业绩说明会 / ESG报告 / 鉴证报告 / 独立性情况的专项意见` 补了显式过滤回归测试
  - 在 report 层将这批 `cninfo` / `board_resolution` 材料变体纳入低信号关键词，避免后续因方向或分数抬升重新漏回 report
  - 将优先级切到 `miit` 的高价值空题材样本，并为 `节能装备高质量发展实施方案` 补了最小 seed
  - 为 `节能装备` 补了识别、评分、映射、历史样本和 reference 数据回归测试
  - 增加了 `节能装备` 的最小个股映射与历史样本，当前 `miit` 的 `event-028` 已能带出 `节能装备`
  - 为 `信息技术创新应用` 补了 `信创` 最小 seed
  - 为 `信创` 补了识别、评分、映射、历史样本和 reference 数据回归测试
  - 增加了 `信创` 的最小个股映射与历史样本，当前 `miit` 的 `event-030` 已能带出 `信创`
  - 为 `APP（SDK）通报` 补了 `数据安全` 的窄 alias 回归测试
  - 将 `APP（SDK）通报` 挂回现有 `数据安全` 主题，没有额外新增主题或泛化 `APP / SDK` 词面
  - 当前 `miit` 的 `event-040` 已能带出 `数据安全`
  - 为 `miit` collector 补了明细页正文抓取和段落兜底解析，不再只保留标题
  - 为 `新材料` 补了最小 seed，并通过 `match_name=false` 锁定“宽题材名、窄 alias 命中”的方案
  - 当前 `miit` 的 `event-032` 已从空题材转为 `新材料`
  - 为 `policy` 事件补了“标题优先、正文兜底需 2 个 alias 命中”的题材提取约束
  - 补了 `节能装备` 正文 spillover、`部长通道` 目录式赛道罗列、`黄金期` 误命中 `黄金` 的回归测试
  - 当前 `miit` 的 `节能装备 / 信创 / 新材料` 样本已回到单主题命中，`中韩产业合作对话 / 香港创新科技局会见 / 两会精神传达 / 部长通道` 这批正文罗列型样本已清掉误命中
  - 为 `国内期货开盘涨跌不一` 这类 `stcn` 国内商品期货开盘篮子快讯补了 report 过滤回归测试
  - 在 report 层把国内商品期货开盘综述纳入低信号 `market_move` 过滤，最新 report 头部已不再被这类篮子快讯占位
  - 为 `育种芯片 / 京芯一号` 补了负向回归测试，锁定非半导体语境不应命中 `半导体`
  - 从 `半导体` 题材中移除了宽 alias `芯片`，当前 `白羽肉鸡自主育种` 已不再误打成 `半导体`
  - 为 `国家国防科技工业局于国斌：要深刻认识发展太空算力的战略意义` 补了 `event_merge` 红灯测试，锁定权威部门表态型 `stcn` 快讯不应落成 `company_update`
  - 在 `fast_news` 子类分类里新增窄规则：`带冒号标题 + 部门/官员身份 + 表态动词` 的样本归入 `policy_signal`
  - 当前 live batch 里的 `太空算力` 样本已从 `company_update` 回正为 `policy_signal`，report 头部展示为 `事件类型: 政策信号`
  - 为 `2026年全国工业和信息化科技创新和产业创新融合发展工作座谈会在苏州召开` 补了 report 红灯测试，锁定 `miit` 无题材会务综述不应继续占据 report 头部
  - 在 report 层新增窄过滤：`miit + policy + 无题材 + 会务标题 + 会务正文信号` 的样本直接视为低信号，不进入 report
  - 当前这条 `miit` 会务综述已从 `latest_report.txt` 中移除，同时带题材的 `节能装备` 政策发布会正例回归仍保持通过
  - 为 `工业和信息化部负责人会见苹果、高通、SK海力士等跨国企业和商协会负责人` 补了第二条 report 红灯测试，锁定 `miit` 无题材会见类样本也不应重新漏回 report
  - 将 `miit` 无题材会务过滤扩到 `会见 / 并座谈`，并补充 `参加会见 / 深化务实合作` 这类正文信号
  - 当前最新 `latest_report.txt` 里已经看不到 `miit` 的 `会见 / 座谈会 / 并座谈 / 工作会议 / 推进会` 一类无题材头部噪音
  - 为 `收评：三大指数集体收跌 CPO概念逆市上涨` 补了 report 红灯测试，锁定 `stcn` 指数收评篮子快讯不应因为摘要里的 `涨停` 被当成可交易 market move
  - 将 `stcn` 的 `收评 / 午评 / 早盘` 三大指数综述纳入 report 层低信号过滤
  - 为 `国内期货收盘涨跌不一 燃油涨超7%` 补了回归测试，并把这类期货收盘篮子快讯并入现有国内期货综述过滤
  - 当前最新 `latest_report.txt` 里已经看不到 `收评：三大指数...` 和 `国内期货收盘涨跌不一...` 这两类 market roundup 头部噪音
  - 为 `华瑞股份股价创下历史新高` 补了 report 红灯测试，锁定 `stcn` 无题材单股历史新高样本不应继续占据 report 头部
  - 在 report 层新增窄过滤：`stcn + market_move + 无题材 + 股价创下历史新高` 的样本直接视为低信号个股异动
  - 当前最新 `latest_report.txt` 里已经看不到 `股价创下历史新高` 这类单股异动头部噪音
  - 为 `乘联分会：1—2月中国汽车出口155万辆 同比增长61%` 补了 `event_merge` 红灯测试，锁定这类统计口径快讯应归到 `industry_data`，而不是 `company_update`
  - 将 `fast_news` 的 `industry_data` 判定扩到 `出口 / 销量 / 产量 + 同比 / 环比 / 累计` 这类统计口径组合
  - 当前真实链路里，这类 `乘联分会 / 协会 / 分会` 统计快讯已不再以 `公司动态` 形态占据 report 头部，本轮 `latest_report.txt` 回到空文件
  - 为 `华海药业：美沙拉秦肠溶片获得药品注册证书` 补了 `event_merge` 红灯测试，锁定这类 `stcn` 快讯应归到 `regulatory_approval`
  - 将 `fast_news` 的 `regulatory_approval` 判定扩到 `药品注册证书`，当前这类样本已从 `company_update` 回正到 `监管获批`
  - 为 `行政处罚事先告知书` 和 `重大资产重组实施情况之法律意见书` 补了 report 红灯测试
  - 在 report 层把 `cninfo hard_event` 收紧为“先过材料过滤，再看题材放行”，并新增 `行政处罚事先告知书 / 重大资产重组实施情况之法律意见书` 两类低信号材料过滤
  - 为 `华泰证券：3月非农超预期回升...` 和 `宏明电子：目前生产经营正常，订单情况整体稳定` 补了 report 红灯测试
  - 在 report 层新增 `stcn` 券商宏观点评过滤，以及 `生产经营正常 / 订单情况整体稳定` 这类经营近况快讯过滤
  - 当前最新 `latest_report.txt` 里，`行政处罚事先告知书`、`重组法律意见书`、`华泰证券非农点评`、`宏明电子经营近况` 都已退出，只剩 `《中国履行〈禁止化学武器公约〉报告（2024）》出版发行`
- Key files:
  - `tests/test_analysis_rules.py`
  - `tests/test_analysis_scoring.py`
  - `tests/test_mapping_and_history.py`
  - `tests/test_reference_data.py`
  - `tests/test_miit_collector.py`
  - `tests/test_text_report_sorting.py`
  - `tests/test_event_merge.py`
  - `src/news_sentiment/collectors/miit.py`
  - `src/news_sentiment/config_loader.py`
  - `src/news_sentiment/reporting/text_report.py`
  - `src/news_sentiment/event_merge/core.py`
  - `data/reference/theme_registry.yaml`
  - `data/reference/theme_stock_map.csv`
  - `data/reference/historical_events.jsonl`
  - `task_plan.md`
  - `findings.md`
  - `progress.md`

## Updated Verification

| Check | Result |
|---|---|
| `./.venv/bin/python -m pytest tests -q` | `167 passed` |
| `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` | `raw_news=64 normalized_news=64 events=52 analyses=52 failed_sources=none` |

## Updated Observations
- `stcn` 的宽词多题材误命中已先收掉一轮，至少不再把泛化的 `上市申请 / H股发行 / 分布式发电系统` 直接映射到 `创新药 / 锂电池 / 油气`。
- live report 头部已经优先回到 `stcn` 实时事件，`cninfo` 无题材材料公告被压到了后面。
- `文旅` 已经从空题材转为可识别题材，当前真实样本 `清明档电影片单发布` 已能带出题材、个股和历史参考。
- `新能源车` 也已经从空题材转为可识别题材，当前真实样本 `乘联分会：3月全国乘用车厂商新能源批发预估112万辆` 已能带出题材、个股和历史参考。
- `电力资源` 已补上最小 seed，后续再遇到 `中国能建与华北电力大学签署战略合作协议` 一类样本时，已能通过 `新型能源体系 / 新型电力系统` 触发题材识别。
- 当前 live report 里已基本看不到 `cninfo` 的 `题材: 无` 尾噪，说明窄过滤已生效。
- `欧洲主要股指跌幅扩大` 这类海外指数篮子快讯已从 report 里移除，不再以 `跌幅扩大` 这类宽词直接占位。
- `国瑞科技：2025年亏损...` 这类年报快讯也不再因为摘要中出现泛化 `订单` 而误入 report。
- `风险持续评估报告` 这类 `cninfo` 材料公告也已经被纳入过滤，不再作为变体漏回 report。
- `美股/海外指数类`、`港股上市申请类`、`stcn` 股东减持快讯，以及 `cninfo` 的 `减持预披露 / 终止减持计划 / 回购股份用途并注销` 一般公告都已经从 report 里移除。
- `功率半导体行业维持高景气` 这类文章的题材范围也已经收紧，后续会优先保留标题主题，不再让摘要中的次级需求场景把题材扩成一串。
- `董事会审计与风险管理委员会...履行监督职责情况的报告` 这类 `board_resolution` 材料文档也已被纳入过滤。
- `半导体` 的集成电路边界样本已经补上，`EDA / 先进封装` 一类高价值窄词现在能直接带出题材、个股和历史参考。
- `*ST金刚` 这类业绩/摘帽快讯已不再因为摘要里的 `算力 / 智算中心` 被误打成题材，最新 live report 头部已清掉这类误命中。
- `国内期货市场夜盘收盘多数下跌 沥青跌超2%` 这类夜盘综述也已从 report 中移除，`latest_report.txt` 再次回到空文件。
- `晋西车轴独立董事2025年度述职报告`、`关于召开2025年年度业绩说明会的公告`、`ESG报告`、`鉴证报告`、`独立性情况的专项意见` 这批材料变体现在也被显式锁进过滤关键词里了。
- `miit` 的 `event-028` 已从空题材转为 `节能装备`，`event-030` 已转为 `信创`，`event-040` 也已稳定挂到 `数据安全`；三条都在当前 batch 外的 report 时间窗之外，所以 `latest_report.txt` 仍保持为空。
- `miit` 现在不再只采标题，`event-032` 的正文已经能进入 `raw -> normalized -> events` 链路，并带出 `policy_support` 子类和 `新材料` 主题。
- `新材料` 采用了 `match_name=false` 的窄 alias 方案，只靠 `先进基础材料 / 关键战略材料 / 前沿新材料 / 人工智能+材料` 触发，避免把泛化 `新材料` 标题直接当题材。
- `policy` 事件在正文补齐后暴露出新的 spillover 问题：正文里目录式提到 `半导体 / 锂电池 / 机器人 / 新能源汽车 / 黄金期` 时，会把会务类政策新闻误打成多题材；这一层现在已经收紧为“标题优先、正文兜底需 2 个 alias 命中”。
- 当前 live batch 里，`节能装备高质量发展实施方案 -> 节能装备`、`信息技术创新应用 -> 信创`、`新材料领域中小企业圆桌会 -> 新材料` 仍能稳定命中；`第五次中韩产业合作部长级对话`、`香港创新科技及工业局局长孙东`、`部长通道谈现代化产业体系` 这类样本已经回到 `themes=[]`。
- `国内期货开盘涨跌不一 燃油涨超4%` 这类开盘篮子快讯也已经从 report 头部移除，当前头部重新回到更像题材催化的 `stcn` 事件。
- `白羽肉鸡自主育种` 这类新闻此前因 `育种芯片 / 京芯一号` 被误打成 `半导体`，现在已经被清掉，说明 `半导体` 的宽 alias `芯片` 确实是误命中根因。
- `太空算力` 这条样本已经确认不是题材误命中，问题出在 `fast_news` 子类过宽地把“权威部门表态”归进了 `company_update`；现在已回正为 `policy_signal`。
- `2026年全国工业和信息化科技创新和产业创新融合发展工作座谈会在苏州召开` 这条样本已经确认不值得补题材；正文只有总纲式方向盘点，没有稳定窄词，当前应按 `miit` 会务综述直接过滤出 report。
- `工业和信息化部负责人会见苹果、高通、SK海力士等跨国企业和商协会负责人` 这类样本也已经确认不值得补题材；虽然正文带行业名，但本质仍是对外会见通稿，当前应与会务综述按同层级过滤。
- `收评：三大指数集体收跌 CPO概念逆市上涨` 这类样本也已经确认不值得保留；问题不在标题本身，而在摘要里的 `涨停 / 涨幅居前` 会把整条指数综述误抬成 `market_move`。
- `国内期货收盘涨跌不一 燃油涨超7%` 与此前的开盘/夜盘综述属于同一类 commodity roundup，当前应继续与 `国内期货开盘涨跌不一 / 国内期货市场夜盘收盘` 按同层级过滤。
- `华瑞股份股价创下历史新高` 这类样本也已经确认不值得保留；本质仍是单股涨停/新高快照，没有题材承接，当前应和其他无题材个股异动按同层级压掉。
- `乘联分会：1—2月中国汽车出口155万辆 同比增长61%` 这类样本则属于另一类问题：它不该被过滤，而是应从 `company_update` 回正为 `industry_data`。
- `华海药业：...获得药品注册证书` 这类 `stcn` 快讯也证明，部分药监核准样本不是 report 噪音，而是 `event_subtype` 归档偏宽；当前应优先回正到 `regulatory_approval`，而不是继续沿用 `company_update`。
- `行政处罚事先告知书` 和 `重大资产重组实施情况之法律意见书` 则说明，`cninfo` 的材料型文档即使被公司题材映射抬出主题，也不应直接回到 report。
- `华泰证券：3月非农超预期回升...` 和 `宏明电子：目前生产经营正常，订单情况整体稳定` 则说明，`stcn` 里还会出现一类“有标题、有行业词，但没有交易催化”的券商点评和经营近况快讯。
- `《中国履行〈禁止化学武器公约〉报告（2024）》出版发行` 则说明，`miit` 里还有一类 `出版发行 / 报告发布` 的无题材政策动态，不适合作为 report 头部项保留。
- 当前这类 `miit` 发布通稿已经被 report 层过滤，最新 `latest_report.txt` 头部回到了 `千问3.6Plus大模型登顶全球模型调用排行榜首，日调用量破万亿 -> AI应用` 这类更贴近题材催化的样本。
- `千问3.6Plus` 这条样本进一步确认，当前 `AI应用` 命中不是靠宽词误伤，而是因为正文里明确出现了 `Qwen3.6-Plus` 这类具体产品名。
- 相对地，只有 `模型API平台 / 模型调用排行榜` 这类泛化表述、没有具体产品名或应用场景时，当前不会单独抬成 `AI应用`；这一层已经用评分回归测试锁住。
- 事件层此前还没有把 `千问3.6Plus...日调用量破万亿` 归到 `industry_data`，会落成 `company_update`；当前已补上 `模型调用排行榜 / 调用量 / Token` 这类窄统计口径，事件层与评分层现在一致。
- `中东局势致燃料紧缺 日本多地温泉被迫停业` 则说明，`stcn` 里还会出现一类“带原油/重油词面、但本质是海外民生后果”的油气通稿。这类样本不适合保留在 report 头部。
- 当前这类海外民生油气通稿已按 `stcn + general_fast_news + 日本 + 温泉 + 被迫停业` 的窄组合从 report 中移除，`latest_report.txt` 头部重新回到 `千问3.6Plus... -> AI应用`。
- `小鹏回应澳大利亚独家经销商合作破裂` 暴露出另一层 `fast_news` 子类误判：正文里的 `违约通知 / 合作协议约定 / 未履行订单义务` 会把企业商业纠纷误抬成 `policy_signal / cooperation_agreement / order_contract`。当前已把 `行动方案 / 规划` 与 `通知 / 意见 / 印发` 拆开处理，并给 `合作协议 / 订单合同` 增加负向约束；这类样本现在回到 `company_update`。
- 这轮又补到一层真实漏口：`fast_news` 分支里还残留了一个裸的 `中标 / 订单 / 合同 -> order_contract`，会把 `订单义务` 这种纠纷语境重新抬回去。当前已用完整 live 正文补红灯测试，并统一改成走 `_is_order_contract_fast_news()` 的负向语境过滤；直接复算 `小鹏回应澳大利亚独家经销商合作破裂` 现已返回 `company_update`。
- `data/events/events.jsonl` 里该样本仍可能显示旧的 `order_contract`，说明这个文件在当前会话里是旧快照；这轮验收以当前代码直接复算、`pytest` 和 `live-smoke` 为准，不以旧快照为准。
- 继续沿着这条线扩了一格后，又补到另一类相邻边界：标题已经是 `回应`，正文却带 `合作协议 / 订单` 强词的“传闻澄清”样本，当前也会被误抬成 `order_contract`。现已增加一个窄前置判断：标题含 `回应 / 澄清 / 否认 / 辟谣 / 说明`，且正文同时出现 `传闻 / 回应记者 / 框架协议 / 不涉及 / 不存在 / 未披露` 这类澄清语境时，优先回到 `company_update`。
- 这轮又把 `stcn` 的一类公共事务/社会民生通稿锁进了 report 过滤：`韩国鼓励非高峰使用公共交通`、`南非延长签证宽限期`、`清明假期跨区域人员流动量预计...`、`深圳市暴雨黄色预警信号扩展至全市`。这些样本当前即使被未来题材词面误抬高，也不应回到 report 头部。
- 顺着同一类模式再往前看，`农业成本因伊朗战事上升 土耳其取消部分化肥关税` 和 `迪拜甲骨文大楼外立面遭防空系统拦截碎片击中 无人员伤亡` 也属于海外公共事务通稿，而不是可交易催化。当前已并入同一组 `stcn public affairs` 标题过滤，避免未来 `农业/化肥` 或 `甲骨文/云计算` 词面把它们抬回 report。
- 当前最新 `latest_report.txt` 已重新回到空文件，说明本轮 batch 没有通过 report 门槛的高信号事件；这与当前策略一致，不为了“有输出”把低信号通稿重新放回头部。

## Suggested Next Moves
1. 下一步执行顺序明确为：先盯 `stcn` 头部样本，再看 `miit` 无题材会务/发布变体，最后再看 `cninfo` 新的材料公告变体。
2. `stcn` 的“权威部门表态”快讯现在已单独归到 `policy_signal`，后续保持这条窄规则，不扩大到普通企业发言。
3. `stcn` 的三大指数 `收评 / 午评 / 早盘`、国内期货 `开盘 / 收盘 / 夜盘` 篮子快讯，以及 `股价创下历史新高` 这类无题材单股异动，都继续按 report 层低信号样本处理。
4. 后续若出现 `协会 / 分会 / 乘联分会` 一类统计口径快讯，优先检查是否应归到 `industry_data`，不要再落成 `company_update`。
5. `Qwen / 千问` 这类模型产品样本维持当前 `AI应用` 判定；如果后续只出现泛化 `模型API平台排行` 口径，再单独观察是否需要收紧 alias。
6. `日本温泉被迫停业` 这类海外民生油气通稿维持 report 层窄过滤；若后续出现相邻标题模式，只补更窄的民生后果关键词，不回退 `油气` 题材识别本身。
7. 后续若再出现 `回应 / 终止合作 / 发出违约通知 / 未履行订单义务` 这类企业纠纷快讯，优先检查 `event_subtype` 是否被正文文种词误抬高，不要直接把它们当政策或订单催化。
8. 若 `events.jsonl` 与当前规则结果不一致，先判断是否只是落盘快照未刷新，避免把旧快照误当成规则仍然失效。
9. 后续若再出现“回应合作协议传闻 / 澄清订单传闻 / 否认签约消息”这类样本，优先看它们是不是传闻澄清，不要因为正文带 `合作协议 / 订单 / 合同` 就直接归成真实催化。
10. 后续若再出现 `公共交通 / 签证宽限期 / 跨区域人员流动量 / 暴雨预警 / 化肥关税 / 外立面碎片击中` 一类 `stcn` 通稿，即使被题材映射抬高，也继续按 report 层低信号公共事务样本处理。
11. `miit` 继续只补窄过滤，不扩宽泛政策词；`cninfo` 继续只收材料公告变体；只有新 live 样本在 report 里反复出现且具备稳定窄词面时，才补最小 seed 题材。

## Session: 2026-04-08

### Phase 8: 真实头部样本补题材与变体过滤
- **Status:** in_progress
- Actions taken:
  - 为 `逆回购操作` 增加 `stcn` 宏观流动性低信号过滤，清掉例行公开市场操作通稿。
  - 将 `开评：三大指数...` 这类开盘指数综述回正为 `market_move`，并在 report 层与 `收评 / 午评 / 早盘` 一并过滤。
  - 为 `算力` 补充 `CPO / 光模块 / 液冷服务器 / 数据中心 / 存储` 等窄 alias，接住 `CPO概念`、`液冷服务器概念`、`数据中心存储更替项目`。
  - 为 `AI应用` 补充 `AI营销 / 智谱AI / 人工智能应用软件开发` 等窄 alias，接住 `AI营销概念`、`智谱AI概念` 和相关企业新设业务样本。
  - 新增 `工程机械 / 保险 / 航空 / 商业航天` 的最小主题定义；其中 `工程机械 / 保险 / 航空` 同步补了个股映射和历史样本。
  - 将 A 股核心指数异动保留为单独的 `温度` 展示，并下调排序，避免和题材催化混排。
  - 新增 `PCB` 最小主题定义，并补个股映射与历史样本，接住 `PCB概念震荡走强 合力泰等涨停`。
  - 新增 `房地产` 最小主题定义，并补个股映射与历史样本，接住 `房地产板块震荡走高 中天服务涨停`。
  - 将 `恒生科技指数 / 恒生指数` 并入现有海外/港股指数低信号过滤，避免港股指数快讯重新进入 report 头部。
  - 将 `北京推出32条创新医药高质量发展措施` 这类 `措施` 口径快讯从 `公司动态` 回正到 `政策信号`。
  - 将 `航空` 主题收紧到窄 alias，避免 `航空国际货物运输代理` 这类经营范围把一般公司快讯误挂到 `航空`。
  - 将 `芯片“基石”价格大涨 半导体材料景气度值得期待` 这类材料价格/景气度快讯从 `市场异动` 回正到 `行业数据`。
  - 新增 `港口机械` 最小题材定义，并补 1 条历史样本，接住 `润邦股份：GENMA获海外两台装船机订单`。
  - 扩展 `股价创历史新高` 变体过滤，清掉 `中际旭创涨超7% 股价创历史新高`。
  - 将 `韩日称朝鲜再次发射不明弹道导弹 朝方暂无回应` 这类地缘/军事快讯从 `company_update` 回正到 `general_fast_news`，避免“回应”宽词把非公司新闻误挂成公司动态。
  - 将 `日韩股市 / KOSPI指数` 并入现有海外指数低信号过滤，清掉 `日韩股市集体收涨 韩国KOSPI指数涨超6%` 这类外盘指数快讯。
  - 将 `成立科技公司 / 投资成立新公司` 这类企业设立快讯从 `general_fast_news` 回正到 `company_update`，避免真实公司动作继续落在兜底一般快讯。
  - 将 `收评：创业板指涨5.91% AI营销概念大涨` 这类单指数收评综述并入现有指数 roundup 过滤，避免 `AI营销` 题材词把收评综述重新抬回头部。
  - 将 `国内商品期货多数收跌 / 多数收涨` 并入现有期货综述过滤，清掉 `液化气跌停` 这类 commodity roundup 变体。
  - 将 `瑞银：近期可采取平衡型配置 避免大幅调仓` 这类机构配置评论从 `market_move` 回正到 `general_fast_news`，并在 report 层按机构评论过滤，避免摘要里的 `WTI / 油价` 误挂 `油气` 后重新占位。
  - 将 `蔚来资本、国君创投等入股灵猴机器人` 这类股权投资/新增股东快讯从 `general_fast_news` 回正到 `company_update`，避免真实资本动作继续挂在兜底一般快讯。
  - 将 `股票期权激励计划授予登记完成` 并入现有 `cninfo equity_incentive` 低信号材料过滤，清掉 `授予登记完成` 这类股权激励材料变体。
  - 为 `申请重整 / 预重整` 新增独立 `reorganization_risk` 子类，避免 `cninfo` 里的重整风险事件继续落在 `corporate_disclosure`。
  - 将 `申请重整 / 预重整` 并入方向判定的负向词，保证 `reorganization_risk` 样本自动落为 bearish，而不是继续停在 neutral。
  - 为 `商标争议` 新增独立 `legal_dispute` 子类，并将其并入方向判定的负向词，避免这类法律争议继续落在 `corporate_disclosure` 且停在 neutral。
  - 新增 `audit-suspicious` CLI，用现有 `events.jsonl + event_analysis.jsonl` 离线巡检“高信号但可能误分”的事件，优先覆盖 `hard_event corporate_disclosure + 风险词`、`general_fast_news + 已挂题材`、`market_move + 开评/收评/午评/早盘` 三类可疑样本。
  - 为 `audit-suspicious` 补 CLI 和集成回归测试，确认输出只做巡检、不改主链路。
  - 将 `佰维存储：作为被告涉及两起侵害发明专利权纠纷案件...` 从 `company_update / neutral` 回正到 `legal_dispute / bearish`，并把 `侵害发明专利权纠纷 / 专利权纠纷` 纳入法律争议边界。
  - 将 `关于2022、2023、2024年限制性股票激励计划归属结果暨股份上市的公告` 并入现有 `cninfo equity_incentive` 低信号材料过滤。
  - 将 `股东减持股份计划公告` 并入现有 `cninfo corporate_disclosure` 低信号材料过滤。
  - 将 `关于回购注销限制性股票减资暨通知债权人的公告` 并入现有 `cninfo equity_incentive` 低信号材料过滤。
  - 将 `控股股东增持公司股份结果公告` 并入现有 `cninfo corporate_disclosure` 低信号材料过滤。
  - 将 `纳斯达克中国金龙指数涨超4%` 并入现有海外指数低信号过滤，避免新一轮外盘指数样本重新进入 report。
  - 将 `增持计划实施完成 / 触及1%整数倍` 并入 `cninfo corporate_disclosure` 低信号结果公告过滤。
  - 为 `退市风险警示 / 退市风险提示公告` 新增独立 `delisting_risk` 子类，并在 report 中显示为 `退市风险`。
  - 为 `电力资源` 补充窄 alias `电厂迁建EPC`，接住 `中国能建浙江院...电厂迁建EPC总承包项目`。
  - 从 `油气` 中移除宽 alias `燃气`，清掉 `燃气轮机` 对 `油气` 的误挂。
- Key files:
  - `src/news_sentiment/reporting/text_report.py`
  - `src/news_sentiment/event_merge/core.py`
  - `src/news_sentiment/cli.py`
  - `src/news_sentiment/analysis/rules.py`
  - `data/reference/theme_registry.yaml`
  - `data/reference/theme_stock_map.csv`
  - `data/reference/historical_events.jsonl`
  - `tests/test_audit_suspicious.py`
  - `tests/test_cli_smoke.py`
  - `tests/test_text_report_sorting.py`
  - `tests/test_event_merge.py`
  - `tests/test_analysis_scoring.py`
  - `tests/test_mapping_and_history.py`

## Latest Verification

| Check | Result |
|---|---|
| `./.venv/bin/python -m pytest tests -q` | `231 passed` |
| `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` | `raw_news=64 normalized_news=64 events=45 analyses=45 failed_sources=none` |
| `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10` | `suspicious_count=0` |

## Latest Handoff Snapshot
- Task-ID: `phase8-live-boundary`
- Task-Name: `live 样本边界收口`
- Files Changed:
  - `src/news_sentiment/reporting/text_report.py`
  - `src/news_sentiment/event_merge/core.py`
  - `src/news_sentiment/cli.py`
  - `tests/test_text_report_sorting.py`
  - `tests/test_event_merge.py`
  - `tests/test_audit_suspicious.py`
- Completed This Session:
  - 延续 `report` 层最窄收口，已清掉多批 live 低信号样本：
    - `hkex` 治理/材料标题族
    - `销售情况简报 / 获得房地产项目 / 回购贷款承诺函 / 谅解备忘录`
    - `回购实施结果 / 回购股份用途并注销 / 互动易制度 / IPO 投资风险特别公告`
    - `股权激励草案摘要 / 处罚决定书 / 监管措施或处罚及整改情况`
    - `可转债信用评级报告 / 询价转让股份的核查报告`
    - 多个减持披露变体
  - 在 `event_merge/core.py` 完成 subtype 修正：
    - `其他风险警示` -> `delisting_risk`
    - `庭外重组` -> `reorganization_risk`
    - `授权许可协议` -> `cooperation_agreement`
  - 在 `audit-suspicious` 清掉材料型误报：
    - `可转债审核问询函之回复（修订稿）`
  - 最近一次验收结果：
    - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` -> `raw_news=624 normalized_news=624 events=186 analyses=186 failed_sources=none`
    - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 20` -> `suspicious_count=2`
    - 随后切到新批次样本时：
      - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` -> `raw_news=429 normalized_news=429 events=160 analyses=160 failed_sources=none`
      - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 20` -> `suspicious_count=0`
- Open TODO:
  - 下一轮优先处理 `冻结 / 解除冻结` 主线：
    - `龙元建设关于公司及控股子（孙）公司部分银行账户被冻结的公告`
    - `甘咨询...募集资金专户部分资金被冻结的公告`
    - `深圳市龙图光罩股份有限公司关于全资子公司部分自有资金及募集资金解除冻结的公告`
  - report 头部残余候选：
    - `立方退 / ST中迪` 的风险提示公告是否继续保留为风险事件
    - `关于实际控制人减持计划期限届满暨实施情况的公告`
    - `ST英飞拓：股票交易异常波动暨风险提示`
  - 保持“先补红灯测试，再补最窄规则，再做 live 验收”的节奏，不切回题材库扩展
- Risks/Blockers:
  - live 样本滚动很快，头部清单会随日期切换；不能拿上一轮 report 头部直接推断当前最优先噪音簇
  - `冻结 / 解除冻结` 既可能是程序披露，也可能是真风险；下一轮不能一把全压
  - 当前 worktree 有大量未提交修改；继续接手时不要回退无关文件
- Next First Command:
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all`
- Known Avoidances:
  - 不要因为 `report` 头部干净就默认 `audit-suspicious` 也同步归零；两边必须一起验
  - 不要把 `冻结 / 解除冻结` 自动当成低信号材料处理；先判断是否是实质风险
  - 不要沿用上一轮 report 头部清单继续下规则；先重跑 live，再按当天样本收口

## Session: 2026-04-11（szse 已启用，hkex staged）

### Phase 8-9: szse 启用收口 + hkex staged 接入
- **Status:** in_progress
- Actions taken:
  - 已将 `szse` 接入主链并纳入 `--source all`，同时补齐对应 collector 测试和主链回归。
  - 已基于真实样本收紧 `szse` / `cninfo` / `stcn` 的低信号公告和 report 过滤，避免 `audit-suspicious` 被低质量材料公告反复命中。
  - 已新增 `hkex` collector，并完成官方路径摸底与单源真实网络验收，但当前仍保持 staged，未并入 `--source all`。
  - 已确认 `hkex` 官方数据不是静态表格 HTML，而是由官方脚本 `lci.js` 指向的 `/ncms/json/eds/` JSON 分页。
- Key files:
  - `src/news_sentiment/collectors/szse.py`
  - `src/news_sentiment/collectors/hkex.py`
  - `src/news_sentiment/collectors/__init__.py`
  - `configs/sources.yaml`
  - `tests/test_szse_collector.py`
  - `tests/test_hkex_collector.py`
  - `tests/test_cli_smoke.py`
  - `tests/test_live_smoke.py`
  - `tests/test_report_pipeline.py`
  - `task_plan.md`
  - `findings.md`

## Current Verification

| Check | Result |
|---|---|
| `./.venv/bin/python -m pytest tests/test_szse_collector.py tests/test_cli_smoke.py tests/test_live_smoke.py tests/test_report_pipeline.py -q` | `12 passed` |
| `./.venv/bin/python -m pytest tests/test_hkex_collector.py -q` | `5 passed` |
| `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` | `raw_news=785 normalized_news=785 events=210 analyses=210 failed_sources=none` |
| `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 20` | `suspicious_count=0` |
| `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect --source hkex` | 成功写出 `392` 条 `hkex` 样本 |

## Updated Observations
- 当前已启用真实源：
  - `cninfo`
  - `stcn`
  - `miit`
  - `csrc`
  - `sse`
  - `szse`
- 当前 staged 真实源：
  - `hkex`
- `szse` 已不再是 staged；下一轮不要再把它当成“待验通源”重复判断。
- `hkex` 已验通单源抓取，但噪音明显重于现有源；启用前要先做最小过滤，不要直接开进 `--source all`。
- 当前已识别的 `hkex` 高噪音标题族：
  - `Next Day Disclosure Return`
  - `published by the issuer in the Chinese section`
  - `Notice of AGM / EGM`
  - `Proxy Form`
  - `Annual Report / ESG Report`
  - `General mandates / re-election / AGM circular`
  - `Monthly Return`
  - `Date of Board Meeting`
- `report` 过滤和 `audit-suspicious` 是两套逻辑；不要误以为只压了 report 头部，巡检计数就一定同步下降。
- 当前 worktree 仍有大量未提交修改；下个会话接手前先看 `git -C .worktrees/mvp-foundation status --short`，不要覆盖现有工作面。
