# Findings & Decisions

## Update 2026-05-26 (latest)
- 本轮核心判断：`先进封装概念震荡回升 长电科技2连板` 是新的 `market_reference` 变体，不是异常内容；`麦克奥迪` 这条是 question-only 诉讼追问，不是真正的诉讼进展公告。
- 规则决策：
  - `概念震荡回升 / 板块震荡回升` 只在同时具备 `涨停 / 连板 / 创新高 / 大涨 / 涨幅居前` 等热度上下文时，才按 `market_reference` 放过。
  - `诉讼进行到什么程度 / 什么时候开庭 / 能庭外和解` 这类 `irm_cninfo` 问询式 `company_update`，按最窄 question-only 口径过滤。
  - `audit-suspicious` 与 `text_report` 要保持同步，不要只修一侧。
- 验收结论：
  - 定向测试 `4 passed`。
  - `audit-suspicious --limit 10` -> `suspicious_count=0`
  - `latest_report.txt` 中两条目标标题均未命中。
- 下一步判断：
  - 做一次 scoped commit/push，然后只读观察后台自然轮次。

## Update 2026-05-24 (latest)
- 本轮核心判断：真正中断点不是 2026-05-21 已推送那轮，而是 2026-05-22 留在本地未提交的 live/report 收口。
- 已确认并处理的当前低信号/误分样本：
  - `国电南自关于仲裁进展的公告`
  - `ST宁科关于涉及追偿权纠纷诉讼的进展公告`
  - `东方生物...简易判决动议...预计 7 月宣布开庭...`
  - `国内单体最大智能组串式储能电站落地内蒙古`
  - `楚江新材...高纯铜靶材 / 铜基封装材料...`
  - `恒瑞医药...还是创新药龙头吗...天天跌...`
  - `扬杰科技...估值一直都比同行低很多...`
  - `诺力股份...中鼎集成5.15再次递交上市申请...`
  - `诺力股份...一季度（招股书更新）营业收入...`
  - `诺力股份：公司股价落后大盘指数50%以上了...不要光喊口号了`
  - `伊朗...武装部队在停火期间进行了重组与重整`
- 规则决策：
  - `仲裁进展 / 追偿权纠纷诉讼进展 / 简易判决动议开庭追问 / 储能电站示范稿` 继续按最窄 `audit-suspicious` 尾噪处理。
  - `伊朗...重组与重整` 的问题不是 report 过滤，而是 `event_merge` 把地缘政治语境误判成并购重组；应在 merge 层修正。
  - `楚江新材 / 恒瑞医药 / 扬杰科技 / 诺力股份` 这批是典型弱问答，继续在 `text_report` helper 里按 `title + reply` 或 `title-only` 最窄收口。
  - `ST三木：关于公司部分债务逾期和部分银行账户被冻结的公告` 当前 raw/event 只有标题，没有正文细节；按最窄 `部分债务逾期和部分银行账户被冻结` 材料口径退出 audit。
- 验收结论：
  - 初次 fresh `watchdog-once` 为 `suspicious_count=5`。
  - 连续补完后，`audit-suspicious --limit 20` 先到 `suspicious_count=1`，再回到 `suspicious_count=0`。
  - 最新 fresh `watchdog-once --source all --limit 20` 为：
    - `raw_news=611`
    - `normalized_news=611`
    - `events=476`
    - `analyses=476`
    - `failed_sources=none`
    - `watchdog_status=clean`
    - `suspicious_count=0`
- 下一步判断：
  - 当前内容侧已经收口到 `watchdog clean`；下一步优先提交当前这轮最窄增量。
  - 不要据此扩大到所有 `债务逾期` 公告；只有混合 `部分银行账户被冻结` 这类材料标题才适用。

## Update 2026-05-21 (latest)
- 本轮核心判断：`创业板指、深证成指均涨逾2% 半导体、券商等板块活跃` 不是真异常，而是 `A股指数 + 板块活跃` 这类新的 `market_reference` 模板漏网。
- 已确认样本：
  - `创业板指、深证成指均涨逾2% 半导体、券商等板块活跃`
- 判断依据：
  - 当前 `audit-suspicious` 误报理由仍是 `general_fast_news_with_theme`，不是 source 失败。
  - 同族样本 `纳指跌+半导体集体下跌`、`PCB概念走强`、`创新药概念活跃`、`半导体板块震荡走强` 已经按 `market_reference` 放过。
  - 这条样本同样具备明确题材和热度上下文，只是标题模板不同。
- 规则决策：
  - 新增 `A股指数关键词 + 板块活跃 + 涨幅热度词` 的最窄 `market_reference` 分支。
  - 只从 `audit-suspicious` 异常口径放过，不改上游评分，不删 report。
  - 不把所有指数综述、翻红、震荡、点位类快讯一并放过。
- 验收结论：
  - 红灯测试先复现 `suspicious_count=1`。
  - 定向回归 `5 passed`。
  - 即时审计 `suspicious_count=0`。
  - 后台自然循环 `2026-05-21_10:47:54` 已回 `clean`、`failed_sources=none`、`suspicious_count=0`。
- 下一步判断：
  - 后续再遇到指数类快讯，先看是否仍具备题材传导和热度词；没有就不要套本轮豁免。

## Update 2026-05-20 (latest)
- 本轮核心判断：这两条不是“真实新风险”，而是交易所问询材料文案的新变体，继续留在 `hard_event_risk_keyword` 只会让后台反复误报。
- 已确认并处理的低信号材料：
  - `中国高科关于收到上海证券交易所《关于中国高科对外投资及股价波动事项的问询函》的公告`
  - `百通能源：大华会计师事务所（特殊普通合伙）关于江西百通能源股份有限公司申请向特定对象发行股票审核问询函有关财务事项的说明`
- 规则决策：
  - `股价波动事项的问询函` 归入 `LOW_SIGNAL_HARD_EVENT_RISK_DISCLOSURE_KEYWORDS`，只退出 audit 风险审计。
  - `审核问询函有关财务事项的说明` 归入融资材料低信号口径，并同步到 `text_report` 过滤关键词。
  - 保留 `立案告知书` 作为真风险反例，证明本轮不是把所有监管/交易所风险文案一起压掉。
- 验收结论：
  - 红灯测试先复现为 `suspicious_count=3`。
  - 定向回归转绿后，全量 audit 测试 `64 passed`，合并 report 定向测试 `65 passed`。
  - 当前 `audit-suspicious --limit 20` 为 `suspicious_count=0`。
  - 手动 `watchdog-once` 为 `suspicious_count=0`。
  - 后台自然循环 `22:22:56` 已确认 `suspicious_count=0`；随后 `22:36:54` recovered，之后 clean。
- 下一步判断：
  - 当前剩余 alert 风险主要在 source，不在内容。
  - 后续再遇到 `问询函`，先分“材料文案”还是“立案/处罚/退市/重大诉讼”真风险，再决定是否进低信号口径。

## Update 2026-05-20 (latest)
- 本轮核心判断：用户平时不看 `latest_report.txt`，所以 6 小时汇总必须直接带出报告重点，而不是只保留 incident 截图里的 report head。
- 汇总展示决策：
  - `watchdog-summary` 主动读取 `data/reports/latest_report.txt`。
  - 新增 `Report Highlights`，解析前 10 条 `[关注]` / `[温度]` 报告项。
  - 每条摘要保留足够交易判断字段：类型、来源、方向、强度、题材、个股。
  - `Latest Report Head` 仍保留，但后续人工查看优先看 `Report Highlights`。
- 边界判断：
  - `Report Highlights` 是当前最新报告摘要，不是历史 6 小时内每轮报告的完整回放。
  - 6 小时汇总仍只做展示和巡检，不自动改规则、不自动提交。
- 验收结论：
  - 红灯测试先确认旧汇总没有 `Report Highlights`。
  - 相关测试 `6 passed`。
  - 手动生成的 `20260520T023731Z-summary.md` 已确认包含报告重点及字段。

## Update 2026-05-20
- 本轮核心判断：watchdog 长跑不应自动改规则，最稳妥路径是每 6 小时产出可读汇总，人工确认后再固化规则。
- 6 小时汇总决策：
  - 复用现有 `incident` JSON 和 watchdog log，不改采集/分析主链路。
  - 汇总内容包括：运行轮次、clean/alert/recovered 计数、failed_sources 排名、suspicious 标题去重、最新 report 头部摘要。
  - 默认输出到 `data/monitoring/summaries/`，不纳入 Git。
- 当前异动判断：
  - `中农发种业集团股份有限公司关于股东所持部分股份冻结的公告` 属于交易所披露材料型冻结公告。
  - 现有 audit 规则已将 `轮候冻结`、`募集资金账户被冻结` 这类材料型冻结样本降为 audit 尾噪。
  - 本轮只补 `股东所持部分股份冻结`，不扩成全量 `冻结`。
- 规则边界：
  - 公司资产查封、被司法冻结、被执行、立案调查、真实诉讼/仲裁风险仍应进入风险审计。
  - 股东持股冻结类标题只退出后台 suspicious，不代表删除 report 或改变上游评分。
- 验收结论：
  - 当前 `audit-suspicious` 已回到 `suspicious_count=0`。
  - 6 小时 summary 命令真实生成文件并能定位重复 suspicious。
  - loop 脚本测试覆盖了 run-once 汇总触发。

## Update 2026-05-19 (latest)
- 本轮核心判断：20:34-21:44 的新 `alert` 不是系统崩溃，主要是已知尾噪家族的新文本变体。
- 已确认并处理的低信号样本：
  - 年报问询函材料/回复：
    - `北京中林资产评估有限公司...涉及评估问题的回复`
    - `中兴华会计师事务所...2025年年报问询函的回复`
    - `青海春天关于收到...年报有关事项的问询函`
    - `关于对深圳证券交易所2025年年报的问询函的回复公告`
  - 会见交流类：
    - `国家外汇局局长朱鹤新会见友邦保险集团主席杜嘉祺`
    - `江苏省委书记信长星会见美国超威半导体公司董事会主席兼首席执行官苏姿丰`
  - 贵金属播报：
    - `现货黄金日内跌幅达2%`
- 规则决策：
  - 年报问询函继续走 `LOW_SIGNAL_HARD_EVENT_RISK_DISCLOSURE_KEYWORDS` 最窄补词。
  - 会见交流类继续要求 `会见 + 主席 + 交流/合作语义`，并排除 `签署/中标/订单/合同/采购`。
  - 贵金属播报只扩到 `现货黄金/现货白银 + 日内跌幅达` 这类点位/涨跌幅表述。
  - 不改变 `score_event`，不扩题材库，不关闭 `general_fast_news_with_theme`。
- 验收结论：
  - 红灯测试已先复现失败。
  - 定向 audit 回归 `4 passed`。
  - 当前和全源刷新后的 `audit-suspicious` 均为 `suspicious_count=0`。
  - `live-smoke --source all` 为 `failed_sources=none`。
- 下一步判断：
  - 等下一轮 watchdog 自动吃到最新本地规则；如果即时审计为 0 但日志仍是旧 alert，不要重复修。
  - 后续遇到会见类，必须先看是否有签约/订单/采购等实质落地词。
  - 后续遇到贵金属内容，点位/涨跌幅播报可降噪，产业链或政策/央行购金类不能套用。

## Update 2026-05-19 (latest)
- 本轮核心判断：后台新滚入的两条 `general_fast_news_with_theme` 不是高优先级交易信号，而是弱融资泛稿和海外法务串味。
- 已确认并处理的低信号/串味样本：
  - `爱科诺生物医药宣布完成5000万美元C轮融资`
    - 私营生物医药 C 轮融资泛稿。
    - 缺少上市公司、政策、订单、产业链兑现路径。
  - `Japan’s Takeda engaged in antitrust scheme to delay generic constipation drug, US jury finds`
    - 海外药企反垄断/诉讼新闻。
    - 当前命中 `半导体` 题材属于主题串味。
- 规则决策：
  - 私营融资只扩到 `生物医药 + 完成 + C轮融资` 的窄标题条件，沿用已有私营融资弱样本分支。
  - Takeda 只新增 `investing_news + general_fast_news + antitrust/lawsuit/jury + takeda/generic/drug/pharma` 的窄分支。
  - 不关闭 `general_fast_news_with_theme`。
  - 不改变 `score_event`，不扩题材库，不改 `text_report` 过滤。
- 验收结论：
  - 定向 audit 测试 `3 passed`。
  - `live-smoke --source all` 为 `failed_sources=none`。
  - 当前 `audit-suspicious --limit 20` 为 `suspicious_count=0`。
  - 后台从 `2026-05-19_11:47:19` 到 `2026-05-19_13:58:53` 连续多轮 `clean`。
- 下一步判断：
  - 后续遇到融资新闻，先看是否有上市公司、政策强约束、订单、产业链兑现路径；没有才按低信号处理。
  - 后续遇到海外医药法务新闻，先判断是否与 A 股主题真实相关；若只是主题串味，走 audit 窄豁免。
  - 若后台 alert 但 `suspicious_count=0`，先查采集源失败，不要继续补内容规则。

## Update 2026-05-19 (latest)
- 本轮核心判断：5/15-5/18 的历史 `alert` 主要是两类问题混在一起：
  - 内容侧 `audit-suspicious` 尾噪。
  - 采集侧短暂 `fetch_error / parse_error`。
- 已确认并处理的低信号样本：
  - 年报问询函审计相关事项专项说明。
  - 年报问询函相关事项法律意见书。
  - `关于涉及仲裁的进展公告`。
  - `现货白银站上78美元/盎司`。
  - 中行-友邦、何立峰-AMD 这类会见/交流快讯。
  - `irm_cninfo` 纯提问法律投诉。
- 已确认应保留为参考信号的样本：
  - `【淘金互动易】上海将推动算力规模倍增...Rubin架构的算力服务器`
  - 判断依据：包含算力产业链、机构观点、互动平台公司布局和具体应用路径；不应作为低信号删除，只从后台异常口径跳过。
- 规则决策：
  - 年报问询函材料继续走 `LOW_SIGNAL_HARD_EVENT_RISK_DISCLOSURE_KEYWORDS` 最窄补词。
  - 白银点位播报继续走现货贵金属点位低信号分支。
  - 会见/交流类只在无 `签署/中标/订单/合同/采购` 时降噪。
  - `淘金互动易` 产业链内容归入 `market_reference`，不进入 report 过滤。
- 验收结论：
  - 定向 audit 测试 `3 passed`。
  - 当前 `audit-suspicious --limit 20` 为 `suspicious_count=0`。
  - 5/19 后台仍可能因采集源失败显示 `alert`，但内容可疑为 0。

## Update 2026-05-15 (latest)
- 本轮核心判断：不是所有带主题的 `general_fast_news` 都要触发后台异常；公共事务会议与项目示范/科普稿可以按 audit 尾噪处理。
- 已确认低信号样本：
  - `三部门召开加强新能源汽车安全管理工作视频会`
  - `全球首个海底数据中心落户东海`
  - `佳力图拜访之江实验室三体计算星座项目团队 交流液冷散热与太空算力温控技术`
- 判断依据：
  - 新能源车样本是三部门工作视频会，缺少明确政策强约束、订单、上市公司可交易链条。
  - 海底数据中心样本是央视财经转述的示范项目/科普稿，虽带 `算力` 主题，但缺少明确上市公司、订单、政策强约束或产业链兑现路径。
  - 佳力图样本是官微信息里的拜访、交流、持续推进交流对接，缺少签署、中标、订单、合同、采购等落地信号。
- 规则决策：
  - 新能源车会议只加入 `LOW_SIGNAL_STCN_PUBLIC_AFFAIRS_TITLE_KEYWORDS` 的最窄标题关键词。
  - 海底数据中心样本新增独立 helper：只匹配 `stcn + general_fast_news + 海底数据中心 + 落户 + 东海`。
  - 公司拜访/交流样本新增独立 helper：只匹配 `stcn + general_fast_news + 拜访 + 交流 + 持续推进交流对接/进行了交流`，且排除 `签署/中标/订单/合同/采购`。
  - 不改变 `score_event`，不扩大题材库，不关闭 `general_fast_news_with_theme`。
- 验收结论：
  - 当前 `audit-suspicious --limit 10` 为 `suspicious_count=0`。
  - 后台 `news-sentiment-watch` 最近一轮为 `clean`、`failed_sources=none`、`suspicious_count=0`。
  - 本机 Git/文件读取出现卡住，定向 pytest 命令需要恢复后补跑并再提交。
- 下一步判断：
  - 如果继续出现“会议/示范/科普”类带题材快讯，仍先判断是否缺少交易链条；是尾噪才补最窄测试和规则。
  - 如果是算力订单、数据中心投资合同、上市公司明确业务进展，不能套本轮海底数据中心尾噪规则。

## Update 2026-05-14 (latest)
- 本轮核心判断：`audit-suspicious` 里的 `general_fast_news_with_theme` 不能只分成“噪音/非噪音”两类，还需要第三类 `market_reference`。
- 已确认的低信号样本：
  - `股票交易异常波动问询函` 回函
  - `年报问询函的专项说明`
  - `国内商品期货夜盘开盘 液化石油气涨近3%`
  - `*ST海源：关于新增诉讼的公告`
  - `海南海药：关于公司提起诉讼的公告`
  - `联美量子股份有限公司关于子公司募集资金账户被冻结的公告`
- 已确认应保留的参考信号：
  - `纳斯达克综合指数跌逾1% 芯片半导体股票集体下跌`
  - `PCB概念走强 大族激光等股价创新高`
  - `创新药概念活跃 昂利康2连板`
  - `半导体板块震荡走强 天岳先进涨近20%`
  - `港股AI应用股拉升 智谱涨逾15%`
- 判断依据：
  - 外盘样本有明确方向：纳指下跌、芯片半导体股票集体下跌
  - A 股样本有明确概念异动：`PCB概念走强`，并带涨停、股价创新高、大涨等上下文
  - A 股概念活跃样本有明确连板和涨幅上下文：`昂利康2连板`、`涨逾7%`、`涨幅居前`
  - A 股板块样本有明确板块异动和涨幅上下文：`半导体板块震荡走强`、`涨近20%`、`涨幅居前`
  - 港股样本有明确主题股异动：`港股AI应用股拉升`，并带 `智谱涨逾15%`
  - 这些样本都有明确题材映射：`半导体` / `PCB` / `创新药` / `AI应用`
  - 当前评分已是弱一级档位：`general_fast_news` + `impact_score=79.0`，没有被抬到公告/强催化同档
- 规则决策：
  - `market_reference` 只从 `audit-suspicious` 后台异常口径排除
  - 不进入 `LOW_SIGNAL` 词表
  - 不进入 `text_report` 过滤
  - 不改变 `score_event` 的题材识别和触发
  - 短标题诉讼材料公告只补 `audit-suspicious` 最窄关键词，不扩大到全部诉讼风险
  - `募集资金账户被冻结` 按用户判断进入 audit 尾噪关键词，不改评分与 report 过滤
- 验收结论：
  - 评分侧测试确认外盘样本继续触发 `半导体`，A 股概念样本继续触发 `PCB` / `创新药`，港股主题异动样本继续触发 `AI应用`
  - audit 侧测试确认三类样本不再导致 `suspicious_count=1`
  - audit 侧测试确认两条短标题诉讼材料不再导致 `hard_event_risk_keyword`
  - audit 侧测试确认募集资金账户冻结材料不再导致 `hard_event_risk_keyword`
  - 当前 live 数据复算 `suspicious_count=0`
  - `latest_report.txt` 仍保留该条
- 下一步判断：
  - 后续遇到“外盘指数/海外板块 + A 股题材映射”、“A 股概念走强/活跃/板块震荡走强 + 涨停/连板/创新高/大涨/涨幅居前”或“港股主题股异动 + 明确 A 股题材映射”的样本，先问它有没有明确题材传导价值；有则按 `market_reference` 保留报告。
  - 后续遇到“纯开盘/收盘/点位/涨跌幅播报”的样本，仍按低信号降噪。
  - 后续遇到诉讼公告，先看是否只有标题材料口径；有金额、判决、冻结、败诉、赔偿、重大进展时不能套本轮尾噪规则。
  - 后续遇到 `募集资金账户被冻结` 同族样本，按当前用户口径优先视作 audit 尾噪。

## Update 2026-05-11 (latest)
- 本轮最有效边界仍是 cninfo 这类材料披露的“低信号材料化”最窄 title-only 收口，不扩题材库。
- 重点结论：
  - 这批 `cninfo` 噪音并非单一关键词可解释，集中在：
    - 年报问询函相关文案（含引号风格）
    - 对发行优先股类披露文本
    - `新增诉讼及进展情况` 类中性公告
  - 该类样本本身仍可触发高分，但语义偏材料披露；通过关键字白名单在 `audit-suspicious` 侧按口径收口后，`suspicious_count` 变为 0，且 `latest_report` 头部未再出现同族命中。
- 已收敛到的规则边界：
  - `LOW_SIGNAL_FINANCING_MATERIAL_CONTEXT_KEYWORDS` 新增 `发行优先股` 语义，不扩散到一般融资披露。
  - `LOW_SIGNAL_HARD_EVENT_RISK_DISCLOSURE_KEYWORDS` 新增年报问询函、监管问询函、诉讼进展类词表，仍保留原始“冻结 / 已纳入真实风险保留样本”的上下文。
  - 关键字加入在 `text_report` 不直接做 title-only 全网过滤，而是通过已有 helper 分支与 `event_subtype` 条件配合触发，避免误伤并购/退市/真实风险样本。
- 验收结论：
  - `tests/test_audit_suspicious.py`：
    - `41 passed`
  - `audit-suspicious --limit 20`：
    - `suspicious_count=0`
  - `live-smoke --source all`：
    - `raw_news=576 normalized_news=576 events=440 analyses=440 failed_sources=none`
  - `data/reports/latest_report.txt`：
    - 头部无本轮新增关键词命中
    - 已保留的样本类型为退市、订单合同、并购重组、市场异动与法务争议
- 下一步判断：
  - 当前可收口并提交推送，不建议继续在该类 `cninfo` 标题上做泛化扩词。
  - 下一轮再遇到同源同族低信号样本，先做：
    - 红灯测试（固定样本）
    - 最窄 title-only / no-reply 规则
    - 回归（含 `tests/test_audit_suspicious.py`）
    - `live-smoke --source all` 与 `audit-suspicious` 双检

## Update 2026-05-08 (latest)
- 当前最有效的动作仍是“单家族、单路径、最窄收口”：
  - `source` 问题单拆
  - `report` 尾噪单拆
  - `audit` 尾噪单拆
  - 不要混成一轮大修
- 本轮新增确认：
  - `sse_einteractive` 头部边界里，最稳的刀还是 `title + canned reply` 的最窄组合；不要先碰 subtype
  - `irm_cninfo` 当天 live 里会出现 `summary=title-only` 的 question-only 样本，旧的 `title+reply` 规则天然覆盖不到
  - `网传中标...是真的吗`、`光伏储能相关业务吗` 这类 question-only 题目，适合只在 `no-reply` 分支做 title-only 窄收口
  - 当前 analyses 真路径是 `data/events/event_analysis.jsonl`，不是 `data/analysis/analyses.jsonl`
  - live 重跑后同簇样本会重新归并，`event_id` 可能漂移；调试不要硬绑旧 `event_id`
  - `live-smoke --source all` 有时会先写完产物、后回 stdout；判断现场时要以最终 stdout 和产物时间戳一起看
- 本轮已收掉的低信号家族：
  - `sse_einteractive`：`安通控股` 两条投资者抱怨型问答
  - `sse_einteractive`：`精工钢构` 空回复抱怨问答
  - `irm_cninfo`：`中超控股` question-only 中标传闻问答
  - `irm_cninfo`：`青鸟智控` question-only 主题关联问答
- 当前明确保留：
  - 诉讼/仲裁进展公告
  - 并购/股权收购/中标主样本
  - `cls` 的 `AI应用 / CPO / 机器人 / PCB` 市场异动
  - `精工钢构：业务是否涉及数据中心及火箭发射厂...`
- 当前剩余边界：
  - 目前没有新的同族 `irm_cninfo / sse_einteractive` 弱问答停在头部
- 当前验证结论：
  - `tests/test_text_report_sorting.py` -> `242 passed`
  - `live-smoke --source all` -> `raw_news=449 normalized_news=449 events=395 analyses=395 failed_sources=none`
  - `audit-suspicious=0`
  - `latest_report.txt` 头部已确认 `安通控股 / 中超控股 / 青鸟智控` 退出
- 下一步判断：
  - 现在更适合停手提交
  - 若下一轮继续，优先只读看有没有新的 question-only live 样本再决定是否补词

## Update 2026-05-01 (latest)
- 当前最有效的动作仍是 `text_report` 层的最窄 live 样本收口，不是回头改 `event_merge / analysis`
- 本轮新增确认：
  - 后台 `news-sentiment-watch` 正常运行，但 log 最新块可能早于最新 commit；判断规则是否生效时必须等下一轮 loop
  - `audit-suspicious=0` 之后，report 头部仍可能继续滚入新的 `stcn / irm_cninfo` 尾噪，不能只看 audit
  - `report` 重写和读取必须串行；并行时很容易误读成“规则没生效”
  - `stcn public affairs` 会继续以“领导调研/看望慰问/活动进展”变体回流，即使带主题也优先按尾噪处理
  - `irm_cninfo` 还会继续出现“估值修复/专项路演/机构调研/价值宣讲”这类 title-only 问答，优先在 question-only helper 里收最窄口径
  - `stcn` 还会出现“近一周机构调研个股超X只”这类榜单型综述，优先在 report 层收，不动上游 subtype
- 本轮已收掉的低信号家族：
  - `stcn`：领导调研慰问活动、机构调研榜单、负面互动平台回复变体
  - `irm_cninfo`：`福建金森`、`东方钽业` 这类纯提问标题弱问答
- 当前明确保留：
  - A股风险公告主头部
  - `奇瑞集团4月销量超25万辆`
  - 全球分区边界暂时保留：`HF Sinclair`、`AIG`
- 当前验证结论：
  - `tests/test_text_report_sorting.py` -> `236 passed`
  - `audit-suspicious=0`
  - 串行强制刷新后的 `latest_report.txt` 中，本轮目标弱样本已全部退出
- 下一步判断：
  - 现在更适合等下一轮 loop，而不是继续补词
  - 若 `HF Sinclair / AIG` 连续多轮稳定占头部，再单独决定是否处理

## Update 2026-04-29 (latest)
- 当前最有价值动作仍是 `text_report` 层最窄尾噪收口；本轮没有动 `event_merge / analysis / source enable`
- 本轮新增确认：
  - `audit-suspicious=0` 后仍可能有 report 头部弱样本；先看 report 仍是必要步骤
  - `live-smoke --source all` 会刷新当天样本，刷新后还可能出现新的 audit 命中；不能只看第一次 report 刷新
  - report 过滤和 `audit-suspicious` 是两套逻辑；像 `累计新增诉讼`、`Pre-A 融资机器人泛稿` 必须同步处理
  - `【财联社早知道】` 仍不能一刀切；本轮只压 `机构/分析师/这家公司` 这类匿名拼盘口径
  - 退市风险/其他风险警示头部目前属于可保留样本，不建议继续为了头部更短继续压
- 本轮已收掉的低信号家族：
  - `cls`：海外板块开盘普跌、世界银行能源预测、匿名拼盘型 `财联社早知道`
  - `irm_cninfo`：算电协同出海泛问答
  - `sse/szse/cninfo`：股权激励材料、减持触及比例、治理制度、股权转让补充协议、累计新增诉讼/仲裁材料
  - `stcn`：私营平台 Pre-A 融资 + 机器人应用交付能力泛稿
- 本轮明确保留：
  - 退市风险/其他风险警示公告
  - `凯撒旅业` 全资子公司收购股权进展暨关联交易
- 当前验证结论：
  - `tests/test_text_report_sorting.py` -> `232 passed`
  - `tests/test_audit_suspicious.py` -> `24 passed`
  - `live-smoke --source all` -> `failed_sources=none`
  - `audit-suspicious=0`
  - 本轮目标关键词已从 `latest_report.txt` 退出
- 下一步判断：
  - 当前适合停手交接
  - 下一轮先只读复核 report 头部和 audit；不要沿本轮样本继续过拟合

## Update 2026-04-28 (latest)
- 当前最有价值动作仍是 `text_report` 层的最窄尾噪收口，不是改 `event_merge / analysis`
- 本轮新增确认：
  - `audit-suspicious=0` 不代表 report 头部一定干净；本轮 `audit=0` 后仍在 report 头部看到整族年报季材料和弱问答
  - report 时间窗不能用全部事件直接计算；低信号新材料也会抬高 `latest_batch_time`，导致测试里的旧正例被整体过滤
  - 带题材的 `cls/stcn market_move` 不能一刀切进 A股强催化；A股板块/概念/涨停类可回 A股层，海外单股主题异动应留 `全球市场与商品`
  - 当前 `irm_cninfo` 弱问答仍会同时出现 question-only 和带回复两类，必须分开按最窄 title/reply 组合处理
  - 年报季 `sse/szse` 材料会被题材映射抬高，例如工程机械、房地产；材料口径仍应在 report 层过滤
- 本轮已收掉的低信号家族：
  - `irm_cninfo`：股价落后/并购计划、人形机器人液冷方案但暂未应用、毛利率抱怨和改善计划、减持原因但回复为未减持
  - `sse/szse`：董事会决议、会计政策变更、计提减值、募集资金专项报告、ESG 报告、审计委员会履职、回购报告书、出售已回购股份计划、回购注销限制性股票材料
- 本轮明确保留：
  - `中远海能` 子公司收购并吸收合并
  - `*ST新研` 撤销退市风险警示申请
  - `*ST西发 / ST长方` 风险警示相关公告
  - `ST长方` 庭外重组提示
  - `惠天热电` 重大诉讼进展
  - `诚迈科技` 签署合作协议
- 当前验证结论：
  - `live-smoke --source all` 已跑完，但 `miit:fetch_error`
  - `tests/test_text_report_sorting.py` -> `231 passed`
  - `audit-suspicious=0`
  - 本轮目标关键词已从 `latest_report.txt` 退出
- 下一步判断：
  - 当前适合停手交接或提交
  - 下一轮不要沿当前头部继续下刀；先只读看是否出现新的整族弱样本
  - `miit:fetch_error` 需要单独作为 collector/source 问题排查

## Update 2026-04-27 (latest)
- 当前最有价值的动作仍是 `text_report` 层的最窄尾噪收口，而不是继续改 `event_merge / analysis`
- 本轮新确认并已收掉的低信号家族：
  - `补充协议/续签业务合作协议暨关联交易`
  - `投资性房地产管理办法 / 房地产业务专项自查报告`
  - `股权激励归属核查意见 / 回购注销限制性股票的减资公告`
  - `购买土地使用权 + 投资合作意向书`
  - `摊薄即期回报风险提示及填补回报措施`
  - `关联存款风险处置预案`
  - `围绕战略合作等交流座谈`
  - `国内商品期市夜盘收盘`
- 本轮边界判断：
  - 这些样本共同特征仍是“材料披露 / 会议交流 / 市场综述变体”，不是新的评分根因问题
  - 真实收购/并购样本如 `华大基因收购重庆新一产生命科技有限公司100%股权` 仍应保留，不能因“关联交易”裸词被误压
  - 当前 `report` 头部已主要剩真实风险和并购样本，继续下压的收益明显低于过拟合风险
- 当前验证结论：
  - `audit-suspicious=0`
  - 本轮新增处理样本均已从 `latest_report.txt` 退出
  - `pytest` 在当前 Windows Python 3.10 环境仍未装上；失败点在坏掉的 proxy 链路，而不是代码回归本身
- 下一步判断：
  - 适合停手交接
  - 下一轮优先只读复核当天新样本，不默认继续补规则
  - 若要补原样定向测试，先修代理或提供镜像源

## Update 2026-04-24 (latest)
- 本轮确认：当前最有价值的动作仍是 `text_report` 和 `audit-suspicious` 的最窄材料公告收口，而不是扩题材库或改主评分。
- 新确认的低信号材料/进度公告家族：
  - `涉及诉讼进展暨银行账户解除冻结`
  - `强制执行完成暨解除冻结`
  - `重大资产出售暨关联交易问询函回复`
  - `并购重组审核委员会...会议安排`
- 边界判断：
  - `问询函回复` 不能裸词过滤，必须绑定 `发行股份购买资产 / 关联交易 / 重大资产重组 / 重大资产出售 / 并购重组` 等上下文。
  - `会议安排` 也不能裸词扩散，只适合并购重组审核进度材料。
  - `诉讼进展公告` 如果已被 `event_merge` 归为 `legal_dispute`，可以作为真实风险事件保留；本轮压的是落在 `corporate_disclosure` 的材料/披露口径。
- 当前验证结论：
  - `audit-suspicious=0`
  - 本轮 4 条目标样本已从 `latest_report.txt` 退出
  - report 头部已经切到新样本，不建议继续机械下压
- 下一步判断：
  - 优先停手观察。
  - 如果继续，先只读复核 `亚太药业 技术开发合同补充协议暨关联交易`、`万润股份 续签业务合作协议暨关联交易` 是否属于稳定低信号合同材料族。
  - 不要因为 `live-smoke --source all` 在 Windows 下超时就回退规则；应单独定位卡住的 source。

## Update 2026-04-20
- 本轮没有继续扩源，`hkex` 继续停在 staged；主线仍是 `phase8-live-boundary`
- 这轮最有效的刀仍是 `text_report` 最窄过滤，连续收掉：
  - `irm_cninfo` 弱问答、模糊回复、年报导向口径
  - `sse/szse` 的回购、股权激励、核查意见、风险管理、土地合同等低信号材料
  - `cls` 的夜盘综述、盘前要闻、匿名拼盘栏目稿、弱财务收益股权处置稿
  - `海外单股并购快讯 + 无题材无个股`
- 本轮补了几条更值钱的回正：
  - `省委财经委员会 / 产业引导基金` -> `policy_signal`
  - `乙烯法PVC供应持续收缩` -> `industry_data`
  - `UPC诉讼 / 仲裁裁决` -> `legal_dispute`
  - `美股盘前要闻一览` -> `general_fast_news`
  - `出售/转让股权 + 不构成重大资产重组` 不该继续算 `acquisition_restructuring`
- 当前基线：
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` -> `raw_news=1766 normalized_news=1766 events=468 analyses=468 failed_sources=none`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
- 当前头部已经明显从“弱问答/弱材料/栏目稿”切回更像该保留的风险公告：
  - `*ST声迅：关于申请撤销对公司股票交易实施退市风险警示的公告`
  - `明德生物：关于公司股票交易被实施退市风险警示暨股票停复牌安排的公告`
- 当前判断：
  - 这是一个适合停手的点
  - 下一轮如果头部还是这类风险公告，不要为了更干净继续过拟合

## Update 2026-04-21
- 本轮继续沿 live 头部收口，没有继续扩源，`hkex` 仍停在 staged
- 这轮新增确认：
  - `stcn` 的券商评论稿、`【早知道】` 摘要拼盘、基金经理配置评论、行业景气综述，应该在 `report` 层按最窄口径过滤
  - `report` 和 `audit-suspicious` 需要同步白名单；只收 report 不补巡检，`suspicious_count` 还会报红
  - `stcn` 的“互动平台表示 + 暂未/未参股/未投资/未布局”更像否定式回应，不该因为标题里有 `CPO / 存储芯片` 就占头部
  - `irm_cninfo` 的“算力基建/后续布局”“营收/订单大概多少”“股价与业绩不对称/新项目么”都属于同一家族的弱问答
  - `吉利将于2026北京车展发布中国首台原生Robotaxi原型车` 有明确主体、明确时间点、明确动作和技术进展，应保留，不该继续压
- 当前基线：
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` -> `raw_news=1781 normalized_news=1781 events=419 analyses=419 failed_sources=none`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
- 当前头部已切成更像 legit 保留样本：
  - `吉利将于2026北京车展发布中国首台原生Robotaxi原型车`
  - `奥特迅...退市风险警示`
  - `国内商品期货早盘开盘 多晶硅涨超4%`
  - `长亮科技中标某股份制银行新网贷服务平台项目`
- 当前判断：
  - 再往下收的收益已经明显下降
  - 下一轮如果头部仍是这类样本，优先停手交接，不要继续过拟合

## Update 2026-04-21（latest）
- 本轮继续沿 `phase8-live-boundary` 收口，但没有再扩源；`hkex` 仍停在 staged
- 这轮新增确认：
  - `szse` 同模板退市风险公告不能再靠标题相似度归并；`hard_event` 必须先看股票代码和结构化催化
  - 修 `event_merge` 后如果不重跑 `merge-events`，`events.jsonl` 会继续保留旧错并结果
  - `analysis` 层仍有少量 live spillover，需要优先修根因而不是在 `report` 硬压：
    - `foreign relief summary` 不该误挂 `新能源车`
    - `主力资金监控` 不该误挂 `文旅`
  - `irm_cninfo` 当天 live 除了 question-only 外，还会有一整族“有回复但仍是弱问答”的样本：
    - `经营范围介绍`
    - `订单充裕 + 定期报告及相关公告`
    - `不存在应披露而未披露的事项`
    - `审慎论证`
    - `并购方向泛回复`
    - `小批量供货 + 收入占比较小 + 理性判断`
    - `减持预披露规则追问`
    - `继续回购诉求`
    - `定增正常推进`
    这类继续优先在 `text_report` helper 补最窄 title+reply 组合，不要急着改 subtype
  - `cls` 的 `股价“一”字跌停 英维克最新回应` 根因不在 `event_merge / analysis`，而在 `report` 层的有意降噪
  - `三大指数全部翻红` 这类 `cls market_move` 弱综述，真正把它漏回 report 的常见原因是正文里混入 `跌超1%` 之类 `market_move` 宽词；优先按“指数综述变体”过滤
  - `stcn` 转载互动平台口径时，`持续加大业务投入 + 在手订单充裕 + 交付有序进行` 更像弱经营更新，不该直接按真订单催化保留
  - `report` 刷新在当前环境里不总是稳定；验收不能只看命令返回，必须直接搜目标样本是否退出，必要时用 `PYTHONPATH=src` 直接调 `write_text_report()`
- 本轮明确保留：
  - `WTI原油期货跌破86美元/桶`：当前 global news 口径下应保留的大宗商品异动
  - `乌克兰国防部宣布：上半年增订2.5万台机器人...`：当前更像海外主题事件，不建议顺手压掉
  - `第二届世界人形机器人运动会将于8月在京举办`：带明确时间点和主题承接，现阶段更像 legit 保留样本
- 当前基线：
  - `./.venv/bin/python -m pytest tests/test_event_merge.py tests/test_analysis_rules.py tests/test_text_report_sorting.py -q` -> `318 passed`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
- 当前头部已经回到更像该保留的样本：
  - `乌克兰机器人扩单`
  - `WTI跌破86`
  - `世界人形机器人运动会`
  - `奥特迅 / *ST声迅 / 明德生物 / ST赛为` 退市风险公告
- 当前判断：
  - 这轮主线已经到适合停手和提交的点
  - 下一轮如果头部主要仍是这几类样本，不继续为了更干净过拟合

## Update 2026-04-17（hkex staged）
- 本轮新增确认：
  - `hkex` collector 已经能抓官方 JSON，不是采集没通；当前问题在于英文标题的 subtype 和降噪还不够。
  - `hkex` 英文标题不能沿用通用字符重合归并；`LIST OF DIRECTORS ...` 和 `PROFIT WARNING` 这种完全不相干的标题会被错并。
  - `hkex` 只补 `report` 过滤不够；至少还需要最小英文 subtype，才能把真催化从 `corporate_disclosure` 里分出来。
  - `report` 的 `hkex` 英文材料过滤必须大小写无关；真实标题会同时出现全大写和普通大小写变体。
- 本轮已落地：
  - `PROFIT WARNING / PROFIT ALERT` -> `business_guidance`
  - `CHANGE OF DIRECTORS / RE-DESIGNATION ...` -> `executive_change`
  - `CONNECTED / MAJOR / VERY SUBSTANTIAL / DISCLOSEABLE TRANSACTION` -> `acquisition_restructuring`
  - `INSIDE INFORMATION - UPDATE ON WINDING UP PETITION` -> `reorganization_risk`
  - `INSIDE INFORMATION ... ARBITRATION PROCEEDINGS` -> `legal_dispute`
  - `PROFIT WARNING` -> `bearish`
  - `POSITIVE PROFIT ALERT` -> `bullish`
- 当前单源验收结论：
  - `collect --source hkex` 实际写出 `1087` 条 raw
  - 修复前 `1087` 条会错并成 `10` 个 event；修复后恢复到 `1087` 个 event
  - `audit-suspicious --limit 10` 已回到 `0`
  - `latest_report.txt` 已能保留 `MAJOR / CONNECTED TRANSACTION`、`PROFIT WARNING` 一类真实催化标题
- 当前仍未完成：
  - `corporate_disclosure` 仍有 `1036` 条，说明 `hkex` 还不能直接开进 `--source all`
  - `INSIDE INFORMATION` 仍过宽，后续需要更细上下文分流
  - `hkex` 还没有 stock code / company mapping，当前个股仍为空

## Update 2026-04-22（hkex staged）
- 本轮新增确认：
  - `hkex` 这一轮最有效的刀仍然是 `text_report` 最窄词面过滤，不需要继续碰 `event_merge / analysis`
  - 真正值得过滤的并不是 `CONNECTED / DISCLOSEABLE / MAJOR TRANSACTION` 主干，而是：
    - `AGM/EGM`
    - `delay in despatch / extension of completion date`
    - `supplemental announcement / revision of annual caps`
    - `service/framework/maintenance/lease agreement`
    - `management accounts/results + continued suspension of trading`
    - `voluntary announcement acquisition of assets`
  - 当 `hkex` 头部收口到 `CONNECTED TRANSACTION - ACQUISITION OF SOFTWARE ASSETS`、`CAPITAL INCREASE AGREEMENT`、`FURTHER INVESTMENT IN PRECIOUS METALS` 这类标题时，继续下刀的误伤风险已经明显高于收益
  - `run-once --source hkex` 当前经常没有可读 stdout，不能拿“终端安静”当失败；要直接看 `latest_report.txt`
- 当前判断：
  - `hkex staged` 仍不该直接开进 `--source all`
  - 但当前也已经不适合继续为“更干净头部”去砍剩余交易主标题
  - 下一轮只有在 `run-once --source hkex` 再冒出一整族明显材料公告时，才值得继续补窄规则

## Update 2026-04-22（global multisource mainline）
- 本轮新增确认：
  - 当前 `--source all` 已经不是旧 `phase8-live-boundary` 的 A 股单线输入，而是混合了 A 股、国内政策、全球政策和全球市场源
  - 因此当前头部出现全球政策/港交所/商品/海外监管样本，本身不再等于“主线失真”
  - 当前最大的失配不在 `event_merge / analysis`，而在“旧的验收标准 + 单榜混排展示”仍在套新主线
  - 继续补 `text_report` 过滤的收益已低于“先做分层展示”的收益
- 当前判断：
  - 接受全球多源主线后，最合理的方向是 `分层总榜`
  - `audit-suspicious = 0` 继续作为硬线
  - 只有在分层之后，某一层内部仍明显被模板材料或栏目稿占位，才值得继续补最窄规则

## Update 2026-04-22（social sidecar）
- 本轮新增确认：
  - 社交源更适合先作为 sidecar 线索层，不适合直接并入主评分
  - 当前最小闭环已经够用：
    - `collect-social --platform fixture|weibo`
    - `data/social/social_signals.jsonl`
    - report 底部 `社交热度观察`
  - `fixture` 已能证明 sidecar 写盘和展示链路成立
  - `weibo` 当前真实抓取仍受访客门/403 限制，现阶段只能保留最小接线和清晰失败提示
  - 当前更稳的失败处理不是抛异常打断，而是输出：
    - `warning: social_platform_failed=weibo:fetch_error:...`
- 当前判断：
  - 这一步的价值是把“社交线索层”边界先钉住，而不是追求微博已生产可用
  - 下一轮如果继续社交扩源，优先找稳定公开入口或官方/半官方可读源
  - 在分层报告还没完成前，不建议让社交热度参与主榜排序

## Update 2026-04-22（report layering）
- 本轮新增确认：
  - 当前最值得先改的确实是展示层，不是评分层
  - `text_report` 改成 4 层骨架后，能把“全球多源主线”意图直接体现在报告结构里
  - `社交热度观察` 留在主层之后，能避免 sidecar 抢主榜位置
- 当前判断：
  - 下一轮更应该看“层内排序是否合理”，而不是退回单榜继续压头部
  - 只有某一层内部仍明显被模板材料占位，才值得继续补最窄规则

## Update 2026-04-22（layer ordering + risk subtype）
- 本轮新增确认：
  - 分层骨架落地后，最值钱的一刀不是新增过滤，而是层内排序微调
  - `重大诉讼进展 / 立案通知书` 这类只有标题词面的风险公告，当前需要直接在 subtype 和方向层回正，不能继续留在 `corporate_disclosure / neutral`
- 当前判断：
  - 当前 `audit-suspicious` 已回到 `0`
  - 下一轮若新的 live 头部没有再冒出整族弱样本，优先停手观察，不继续过拟合

## Update 2026-04-22（A股强催化 live 小补停手点）
- 本轮新增确认：
  - 当前最有效的刀仍是 `text_report` 最窄标题/回复过滤，不需要再动 `event_merge / analysis`
  - `回购方案 / 回购预案 / stcn 拟回购股份快讯` 这一簇，当前用户口径是不保留
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment report` 在当前环境里不总是可靠刷新产物；验收更稳的是直接 `write_text_report()`
- 本轮新增收口：
  - `irm_cninfo / sse_einteractive` 的追问型弱问答、谣言核实追问、口号式互动留言
  - `会议资料 / 提示性公告 / 监管工作函评估回复 / 授信担保 / 框架协议 / 增持计划 / 预留权益失效`
  - `stcn` 的 `拟...回购股份` 快讯
  - 交易所 `回购股份方案 / 回购公司股份方案 / 回购公司股份的预案`
- 当前判断：
  - 当前 `A股强催化` 头部只剩 `*ST和科 / 天孚通信 / 永鼎股份`
  - 这 3 条更像 legit 保留样本，继续下刀的误伤风险已经高于收益

## Update 2026-04-22（social sidecar fixture 验收）
- 本轮新增确认：
  - `fixture` 已足够证明 sidecar 的写盘与报告展示链路成立
  - `社交热度观察` 当前仍稳定显示在主报告层之后，没有抢主榜位置
  - 当前更稳的结论仍是：
    - sidecar 只做线索层
    - `weibo` 只保留最小接线和失败可见
    - 不把这次验收写成“社交源生产可用”

## Update 2026-04-17
- 本轮新增确认：
  - `company_update` 的题材误抬，不一定该在 `report` 层收；像 `中国电建成立绿能科技服务公司` 这类 `企查查APP显示 + 经营范围包含 + 股权穿透显示`，更稳的修法是 `analysis/rules.py` 的 summary spillover 抑制。
  - `cls + general_fast_news` 里存在一类科技特稿，不是纯市场快讯，也不是公司催化。`全球首款/研发成功 + 科技日报 + 教授` 这类样本更适合在 `report` 层按特稿处理。
  - `sse/szse corporate_disclosure` 里还会出现 `股东协议 + 补充协议` 这类材料变体；它和已处理的 `股份购买协议` 一样，更像协议材料而不是结果公告。
- 本轮明确保留：
  - `华荣股份：国内首创智能化防爆高压环网柜研制成功`
  - `盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告`
  - `恒瑞医药关于药物纳入突破性治疗品种名单的公告`
  - `云天化关于引入合作方投资建设新能源电池正极材料项目的公告`
- 当前更稳的判断：
  - `恒瑞医药...突破性治疗品种名单` 先保留，它更像真实药品催化
  - `云天化...引入合作方投资建设...` 目前也先保留；虽然是 `corporate_disclosure + themes=[]`，但标题本身带 `引入合作方 + 投资建设 + 项目`，继续压有过拟合风险

## Current Product Definition
- 目标不是普通新闻情感分类，而是 `新闻/事件 -> A 股题材炒作情绪 -> 题材/个股 -> 关注信号`。
- 第一版不自动下单，只输出 `关注`。
- 时间窗是 `盘中到次日`。
- 当前优先输入层是：
  - `硬事件`：`cninfo`
  - `快讯`：`stcn`
  - `政策`：`miit`

## Current Architecture
- 当前链路：
  - `collect`
  - `normalize`
  - `merge-events`
  - `analyze-events`
  - `report`
- 数据存储仍以 JSONL 为主，适合快速迭代。
- `event_type` 保留粗分类，`event_subtype` 承担交易化细分。
- 评分仍是规则驱动，但已经具备：
  - 来源权威性
  - 时间新鲜度
  - 政策加权
  - 市场事件加权
  - 题材加权

## Implemented Capabilities
- 已打通真实源：
  - `cninfo`
  - `miit`
  - `stcn`
- 已支持：
  - `--source all`
  - `live-smoke --source all`
  - 来源级 `timeout / retry / backoff`
  - `failed_sources` 类型化错误输出
- 已实现报告增强：
  - 来源
  - 发布时间
  - URL
  - 方向
  - 强度
  - 题材
  - 个股
  - 历史参考
  - 事件类型

## Event Processing Findings
- 标题相似度归并不够，必须补结构化归并。
- 当前已经额外实现：
  - 同资产 `market_move` 归并
  - 同股票、同催化子类的 `cninfo` 材料归并
- 这两层归并已经把真实 `events` 数从更高水平压到 `51` 左右，明显减少报告冗余。

## Theme Layer Findings
- 仅靠文本直接命中题材不够，`cninfo` 公告尤其容易落成 `题材: 无`。
- 目前题材层是三段组合：
  - 文本主题命中
  - 题材别名库
  - `company_theme_map` 补充公司到题材
- `company_theme_map` 只对更像催化的 `cninfo` 子类生效，避免普通公告误抬高。
- 宽词 alias 会直接制造多题材误命中，已经确认至少以下三类需要移除或收紧：
  - `上市申请` 不应直接映射到 `创新药`
  - `H股发行` 不应直接映射到 `锂电池`
  - `分布式发电系统` 不应直接映射到 `油气`
- 当前更稳的做法是保留窄主题词和行业上下文，而不是继续把宽词塞进 alias 库。
- 针对真实 report 里的空题材样本，`文旅` 已经补齐最小 seed：
  - 触发词先只保留 `清明档 / 电影片单 / 院线 / 旅游演艺`
  - 配套补了最小个股映射和历史样本
  - 当前真实样本 `2026清明档电影片单发布` 已能命中 `文旅`
- 针对真实 report 里的空题材样本，`新能源车` 也已补齐最小 seed：
  - 触发词先只保留 `新能源批发 / 新能源乘用车 / 新能源汽车`
  - 配套补了最小个股映射和历史样本
  - 当前真实样本 `乘联分会：3月全国乘用车厂商新能源批发预估112万辆` 已能命中 `新能源车`
- 针对真实 report 里的空题材样本，`电力资源` 也已补齐最小 seed：
  - 触发词先只保留 `新型能源体系 / 新型电力系统`
  - 配套补了最小个股映射和历史样本
  - 当前真实样本 `中国能建与华北电力大学签署战略合作协议` 已有对应回归测试锁定
- 针对 `半导体` 的集成电路边界样本，也已补上窄词：
  - 触发词先只保留 `EDA / 先进封装`
  - 配套补了更贴题的代表股映射和历史关键词
  - 当前 `国产EDA工具链和先进封装产线建设提速` 一类样本已能命中 `半导体`
- 针对 `miit` 的政策空题材样本，`节能装备` 也已补齐最小 seed：
  - 当前只保留窄主题 `节能装备 / 高效节能设备 / 节能设备`
  - 配套补了最小个股映射和历史样本
  - 当前 `工业和信息化部举行《节能装备高质量发展实施方案（2026—2028年）》新闻发布会` 已能命中 `节能装备`
- 针对 `miit` 的政策空题材样本，`信创` 也已补齐最小 seed：
  - 当前只保留窄主题 `信息技术创新应用 / 信息技术应用创新`
  - 配套补了最小个股映射和历史样本
  - 当前 `李乐成调研信息技术创新应用和未来产业发展研究工作` 已能命中 `信创`
- `miit` 的 `APP（SDK）通报` 样本没有单独开新主题，而是挂回现有 `数据安全`：
  - 当前只补了窄 alias `侵害用户权益行为的APP（SDK）通报`
  - 没有把泛化 `APP / SDK` 塞进词库
  - 当前 `关于侵害用户权益行为的APP（SDK）通报` 已能命中 `数据安全`
- `miit` 政策样本只采标题会直接损失正文里的行业窄词，已经确认会漏掉 `先进基础材料 / 关键战略材料 / 前沿新材料 / 人工智能+材料` 这类高价值词面。
- 当前 `miit` collector 已补上明细页正文抓取和段落兜底解析，`event-032` 的正文已能进入后续归并和题材识别链路。
- 对于题材名本身过宽、但正文窄词足够稳的样本，可以用 `match_name=false` 锁住“只靠 alias 命中”的方案：
  - 当前 `新材料` 只保留 `先进基础材料 / 关键战略材料 / 前沿新材料 / 人工智能+材料`
  - 不让泛化 `新材料` 标题本身直接触发
  - 当前 `工业和信息化部召开新材料领域中小企业圆桌会` 已能通过正文命中 `新材料`
- `miit` 正文补齐后，也暴露了新的题材 spillover 风险：
  - `节能装备高质量发展实施方案` 会因为正文顺手提到 `算力 / 新型电力系统` 被扩成多主题
  - `部长通道谈现代化产业体系、人工智能产业` 会因为正文盘点 `新能源汽车 / 人形机器人` 被误打成赛道主题
  - `香港对接国家战略的黄金期` 会因为 `黄金期` 这种普通表述误命中 `黄金`
- 当前更稳的做法是：
  - `policy` 事件先只看标题命中的主题
  - 只有标题没有主题时，才允许正文兜底
  - 正文兜底只统计 alias，不吃题材名本身，而且至少要有 `2` 个窄 alias 命中

## Report Layer Findings
- 真实 report 的另一个问题不是“误命中”，而是排序：无题材但高分的 `cninfo` 文档会因为分数高，压过更值得先看的 `stcn` 实时快讯。
- 已先把以下 `cninfo` 无题材子类降到后排：
  - `corporate_disclosure`
  - `board_resolution`
  - `equity_incentive`
- 在此基础上，又额外过滤了更低信号的 `cninfo` 材料公告：
  - `进展公告`
  - `通知债权人`
  - `述职报告`
  - `业绩说明会`
  - `风险评估报告`
  - `风险持续评估报告`
  - `环境、社会与公司治理（ESG）报告`
  - `鉴证报告`
  - `减持股份的预披露公告`
  - `终止股份减持计划`
  - `回购股份用途并注销`
  - `股权激励法律意见书`
- `stcn` 的海外指数篮子快讯也是一类 report 尾噪，例如 `欧洲主要股指跌幅扩大`，这类信息只有宽泛市场描述，没有题材或个股承接，已经在 report 层做了窄过滤。
- `stcn` 的商品期货综述快讯也是同类尾噪，例如 `国内期货市场夜盘收盘多数下跌 沥青跌超2%`，这类夜盘收盘汇总没有明确 A 股题材承接，也已经在 report 层做了窄过滤。
- `stcn` 的国内商品期货开盘篮子快讯也是同类尾噪，例如 `国内期货开盘涨跌不一 燃油涨超4%`，这类开盘综述同样没有明确 A 股题材承接，也应该和夜盘综述按同一层级做窄过滤。
- `美股/海外指数类` `market_move` 还有一个隐性问题：摘要里经常会顺带提到某个海外板块，比如 `存储芯片板块大跌`，如果直接拿整段文本做题材提取，会把 `美股三大指数集体低开` 误打成 `半导体`。
- `功率半导体行业维持高景气` 这类文章也有类似问题：标题已经明确主行业，但摘要会再列出 `AI算力 / 新能源汽车 / 人形机器人` 等下游场景，如果直接把整段文本平铺命中，会把题材扩成一串。
- `fast_news` 的催化判断不能直接扫“标题+摘要”全文；年报或电话会议快讯的摘要里经常会出现泛化 `订单 / 合同`，会把本质上无题材的业绩新闻误带进 report。
- 当前更稳的做法是：`fast_news` 催化优先看标题，题材提取也优先看标题；只有标题没有题材时，才回退到摘要做兜底。
- 但 `business_guidance` 里还有一类特殊尾噪：年报/业绩标题本身没有题材，摘要却会顺带提到新业务赛道，例如 `*ST金刚` 的年报摘要里带了 `算力 / 智算中心`。这类情况也已收紧为标题优先，不再让摘要里的赛道词直接抬题材。
- `港交所上市申请书` 这类 `stcn` 快讯虽然形式上像“监管获批/上市申请”，但对当前 A 股题材雷达的盘中可看性很弱，已经在 report 层做窄过滤。
- `stcn` 的无题材股东减持快讯，例如 `拟减持 / 减持不超`，也已经在 report 层做窄过滤。
- 当前 `cninfo` 的 `题材: 无` 尾噪已经明显下降，`减持预披露 / 终止减持计划 / 回购股份用途并注销` 这批高频一般公告也已收掉。
- `cninfo` 的 `board_resolution` 子类里，`董事会审计与风险管理委员会...履行监督职责情况的报告` 这类材料文档也已经纳入过滤。
- `cninfo` 的 `board_resolution` 子类里，`独立董事独立性情况的专项意见` 这类材料文档也已纳入过滤。
- 在这轮新增 `国内期货市场夜盘收盘` 过滤后，当前 live report 已回到允许为空的状态，没有再被期货综述类尾噪占位。

## Active Seed Themes
- `算力`
- `AI应用`
- `机器人`
- `充电桩`
- `数据安全`
- `黄金`
- `油气`
- `户外经济`
- `文旅`
- `新能源车`
- `电力资源`
- `锂电池`
- `半导体`
- `创新药`

## Real Report Effects Observed
- 当前真实报告已能稳定命中：
  - `广州：建设多元融合的城市一张算力网...` -> `算力`
  - `现货黄金跌破4600美元/盎司` -> `黄金`
  - `长安汽车等成立天枢智能机器人公司` -> `机器人`
  - `广州：加快粤芯、增芯等重大项目建设...` -> `半导体`
  - `Sora退出 可灵AI周度活跃用户环比增长` -> `AI应用`
  - `2026清明档电影片单发布` -> `文旅`
  - `乘联分会：3月全国乘用车厂商新能源批发预估112万辆` -> `新能源车`
  - `300005` 的 `cninfo` 定增受理材料 -> `户外经济`
  - `603026` 的公告 -> `锂电池`
  - `300009` 的高管变动公告 -> `创新药`

## Current Weak Points
- 一些宽泛政策新闻还会误打到不该命中的主题。
- `miit` 当前还有一批 `72.0` 分的空题材政策样本，其中最像可交易窄主题的是 `节能装备高质量发展实施方案`，但还没完成最小 seed 评估。
- `miit` 的 `节能装备高质量发展实施方案`、`信息技术创新应用`、`APP（SDK）通报` 和 `新材料领域中小企业圆桌会` 已接住；更宽的政策会务类样本仍不适合直接扩题材。
- `miit` 的会务综述、部长通道、外事会见、中韩产业对话这类正文目录式样本，在收紧 `policy` 题材提取后已经回到 `themes=[]`，不再因为正文顺手罗列行业词而误抬题材。
- 当前新的主问题已经从 `miit` 空题材，转到真实 report 里新冒出来的误命中样本，例如 `白羽肉鸡自主育种` 被误打成 `半导体`。
- `半导体` 的 alias 里，`芯片` 这类词面过宽，已经证实会把 `育种芯片 / 京芯一号` 这类农业育种语境误打成 `半导体`。
- 当前更稳的做法是保留 `集成电路 / 晶圆 / EDA / 先进封装 / 粤芯 / 增芯` 这批更贴行业的窄词，移除单独的 `芯片`。
- `太空算力` 这条样本进一步证明，report 头部的新问题不一定是题材误命中，也可能是 `event_subtype` 归档过宽。
- 对 `stcn` 来说，`带冒号标题 + 权威部门/官员身份 + 表态动词` 的快讯更像 `policy_signal`，不该因为标题里有 `：` 就直接落成 `company_update`。
- `miit` 的会务综述样本也不适合为了“补题材”去硬扩词库。像 `科技创新和产业创新融合发展工作座谈会在苏州召开` 这种正文，只是在总纲层面罗列 `人形机器人 / 量子信息` 等方向，没有稳定、可复用的窄词。
- 这类 `miit` 样本更稳的做法不是补新主题，而是在 report 层按 `无题材 + 会务标题 + 会务正文信号` 做窄过滤。
- 同类地，`工业和信息化部负责人会见苹果、高通、SK海力士等跨国企业和商协会负责人` 这类对外会见通稿，也不适合因为正文出现公司名或行业名就补题材。
- 当前更稳的做法是把 `会见 / 并座谈` 一并纳入 `miit` 无题材会务过滤，和 `座谈会 / 工作会议 / 推进会` 按同层级处理。
- `stcn` 的指数综述类 market roundup 也有类似问题。像 `收评：三大指数集体收跌 CPO概念逆市上涨` 这种样本，真正把它送进 report 的不是标题，而是摘要里附带的 `涨停 / 涨幅居前`。
- 对这类样本，更稳的做法不是提高 market move 权重，而是在 report 层把 `收评 / 午评 / 早盘` 的三大指数综述直接视为低信号 market roundup。
- `国内期货收盘涨跌不一 燃油涨超7%` 也证明，国内期货综述不能只过滤开盘和夜盘，收盘篮子快讯也要按同层级处理。
- `华瑞股份股价创下历史新高` 则说明，`stcn` 里还有一类单股 market move 噪音。标题本身不带题材，摘要只是单股涨停/新高快照，也不适合继续占据 report 头部。
- 当前更稳的做法是把 `股价创下历史新高` 这类无题材单股异动，也按 report 层低信号样本处理。
- 但 `乘联分会：1—2月中国汽车出口155万辆 同比增长61%` 这类样本不是 report 噪音，而是 `event_subtype` 归档过宽。它属于统计口径快讯，更贴近 `industry_data`，不该因为标题带 `：` 就直接落成 `company_update`。
- 当前更稳的做法是把 `出口 / 销量 / 产量 + 同比 / 环比 / 累计` 这类统计组合也纳入 `industry_data` 判定。
- `华海药业：...获得药品注册证书` 这类 `stcn` 快讯也属于子类归档问题，不该继续落成 `company_update`；更稳的做法是直接回正到 `regulatory_approval`。
- `行政处罚事先告知书` 和 `重大资产重组实施情况之法律意见书` 这类 `cninfo` 材料文档，即使被公司题材映射抬高，也不适合重新进入 report。
- `华泰证券：3月非农超预期回升...` 这类券商宏观点评，以及 `目前生产经营正常，订单情况整体稳定` 这类经营近况快讯，也不适合作为交易雷达头部项保留。
- `《中国履行〈禁止化学武器公约〉报告（2024）》出版发行` 这类 `miit` `出版发行 / 报告发布` 政策动态，也不适合作为无题材头部项保留。
- `千问3.6Plus大模型登顶全球模型调用排行榜首，日调用量破万亿` 这条样本目前是合理正例。它不是靠泛化 `大模型` 误命中，而是正文里明确出现了 `Qwen3.6-Plus` 这类具体产品名。
- `cninfo` 一般公告的主流低信号样本已基本压下去，但后续仍可能出现新的材料型变体，需要继续按样本做窄过滤。
- `股权激励`、`控制权变更` 等子类还缺更稳定的题材映射。
- `business_guidance` 的业绩类标题已经收紧，但后续仍可能冒出新的标题变体，需要继续按真实样本补回归。
- 还没有市场确认层，也没有 LLM rerank。

## Decisions Locked In

| Decision | Why |
|---|---|
| 先用规则层做稳 MVP，不急着上 LLM | 先把真实数据链、归并和题材映射做扎实 |
| 题材库只围绕真实高价值样本扩展 | 避免词库失控、误命中飙升 |
| `company_theme_map` 只服务催化子类 | 防止普通公告被公司题材整体抬高 |
| 报告优先服务“盘中可看性” | 先让头部结果像交易雷达，而不是新闻归档 |
| 宽词 alias 直接删除，不靠模糊兜底 | 比继续扩 alias 更稳，也更可解释 |
| 对无题材 `cninfo` 材料公告先降序，再决定是否过滤 | 先保留信息，再逐步提高 report 信噪比 |
| 对明显低信号的 `cninfo` 材料公告直接过滤出 report | 比长期保留尾噪更符合交易雷达目标 |
| 当一个 batch 没有高信号事件时，允许 `latest_report.txt` 为空 | 不为了凑结果把低信号噪音重新放回 report |

## Recommended Next Step
- 当前优先级已经从“继续补 live 规则”切到“两条线并行”：
  - 主线继续收 live 样本边界
  - 支线把第一批官方源做成可安全并入 `--source all`
- `csrc` 这条官方政策源已经确认不该抓 `c100028/common_xq_list.shtml`：
  - 该页面今天返回空列表
  - 更稳的做法是抓证监会首页 `新闻发布 -> 证监会要闻` 模块
  - 当前 `csrc` collector 已按这个入口改完，并完成真实单源网络验收
- `csrc` 当前实现锁定了三个关键判断：
  - 首页首条和普通条目虽然结构不同，但都应落成同一组 `policy` 原始新闻
  - 首页首条会在列表里重复出现，collector 需要按 URL 去重
  - 首页普通条目只有 `MM-DD`，应以页面生成时间补成年份
- `csrc` 当前真实验收结果是：
  - `collect --source csrc` 已成功
  - `data/raw/raw_news.jsonl` 当前写出 `5` 条官方样本
  - 但还没有完成 `live-smoke --source all` 全链路验收，因为上一条命令被用户手动中断
- `sse` 当前仍是 staged：
  - 官方页面和字段已经摸清
  - `queryCompanyBulletinNew.do` 的真实查询参数还没完全对准
  - 在参数验通前继续保持 `configs/sources.yaml` 里的 `enabled: false`
- 下一步最优先的不是继续扩题材库，也不是继续改 `rules.py`，而是先把扩源验收到可控状态：
  - 先跑 `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all`
  - 再跑 `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
  - 确认 `csrc` 打开后不会把 report 头部拖成低信号政策通稿
- 如果 `csrc` 在 `--source all` 下表现不稳，当前推荐动作不是回退代码，而是先临时 staged：
  - 只把 `configs/sources.yaml` 里的 `csrc.enabled` 改回 `false`
  - 保留 collector、测试和注册表改造
- 之后继续扩源时，优先级保持不变：
  - `P0`: 官方公告/监管、官方政策
  - `P1`: 财经媒体、行业协会/数据机构
  - `P2`: 海外官方/媒体
  - `P3`: 社交/自媒体，只能先做线索层，不能直接进主信号层
- `data/events/events.jsonl` 仍然不能作为最新规则效果依据；扩源后的真实基线，必须以现跑的 `collect / live-smoke / audit-suspicious` 为准。

## Update 2026-04-11

### Source Layer Findings
- 当前输入层已不再是最早的 `cninfo / miit / stcn` 三源形态。
- 当前已启用真实源：
  - `cninfo`
  - `stcn`
  - `miit`
  - `csrc`
  - `sse`
  - `szse`
- 当前 staged 真实源：
  - `hkex`
- `szse` 已完成接入和主链验证；后续不要再把它当成“待验通骨架”处理。

### HKEX Findings
- `hkex` 官方页面的 `lci.html` 更像外壳，直接抓表格 HTML 会拿到空壳或不稳定结构。
- 当前更稳的官方路径是读取官方脚本 `https://www1.hkexnews.hk/ncms/js/lci.js` 后定位 JSON 分页源。
- 已确认可用的分页模式为：
  - `/ncms/json/eds/lcisehk1relsde_{page}.json`
- `hkex` 单源真实网络验收已经通过：
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect --source hkex`
  - 当前写出 `392` 条样本
- 但 `hkex` 的主要问题已经不是“能不能抓”，而是“抓到后噪音非常重”。

### HKEX High-Noise Families
- `Next Day Disclosure Return`
- `published by the issuer in the Chinese section`
- `Notice of AGM / EGM`
- `Proxy Form`
- `Annual Report / ESG Report`
- `General mandates / re-election / AGM circular`
- `Monthly Return`
- `Date of Board Meeting`

### Verification Findings
- 最新全链路基线已经不是早期的 `64 / 45`。
- 当前最新基线为：
  - `live-smoke --source all` -> `raw_news=785 normalized_news=785 events=210 analyses=210 failed_sources=none`
  - `audit-suspicious --limit 20` -> `suspicious_count=0`
- 这说明当前主问题已从“已有源是否稳定”转为“新源启用前如何控制噪音”。

### Recommended Next Step Override
- 下一步不建议继续扩题材库，也不建议继续在 `szse` 上追加修边。
- 当前最优先动作是：
  - 先对 `hkex` 最新标题做一轮只读归类
  - 再补最窄的 report 过滤
  - 最后才决定是否把 `hkex` 并入 `--source all`
- 一个重要注意点是：
  - `report` 过滤和 `audit-suspicious` 是分离逻辑
  - 因此启用 `hkex` 前，必须同时盯 report 头部和 `audit-suspicious` 结果，不能只看其一

## Update 2026-04-16

### Current Phase
- `Phase 9`
- 含义：`cls` 并入后的主线已从“全球快讯降层”转到“低信号披露/栏目稿尾噪收尾 + 保留边界锁定”。

### What Changed
- `report` 层继续清掉一批低信号披露与编辑尾噪：
  - `审核问询函回复 / 并购重组材料文档 / 报告书（修订稿）`
  - `解除司法冻结 / 重大诉讼的公告 / 重大诉讼、仲裁情况进展`
  - `增持公司股份计划 / 股份减持完成 / 变更股份回购用途`
  - `停牌核查 + 股票交易风险/风险提示`
  - `【风口研报·洞察】 / 【金牌纪要库】 / 《新闻联播》要闻 / 【电报解读】`
  - `现货白银... / 美股光通信股走势分化 / 再次向港交所提交上市申请书 / 盘后A股上市公司重点业绩公告精选`
- `analysis/scoring` 新增最窄上游抑制：
  - `cninfo + hard_event + corporate_disclosure` 中，`ESG报告 / 业绩网上说明会 / 责任保险` 不再默认触发
- 正样本边界已明确锁住：
  - `中远海能...投资建造两艘巴拿马型原油轮暨关联交易`
  - `关于延期披露2025年年度报告及退市风险提示性公告`
  - `【公告全知道】...245亿元投建算电协同项目`
  - `华测导航...开展供应链融资业务合作暨对外担保`
  - `GQY视讯...可能被实施退市风险警示的风险提示公告`

### Verification Baseline Override
- `./.venv/bin/python -m pytest tests/test_analysis_scoring.py -q`
  - `45 passed`
- `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -k "gold_memo_column" -q`
  - `1 passed`
- `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -k "cls_global_market_brief_without_hiding_domestic_order_catalyst" -q`
  - `1 passed`
- `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -k "after_hours_earnings_digest or repeat_hk_listing_application_fast_news" -q`
  - `2 passed`
- `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all`
  - `raw_news=1235`
  - `normalized_news=1235`
  - `events=280`
  - `analyses=280`
  - `failed_sources=none`
- `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
  - `suspicious_count=0`

### Current Report Head
- `中远海能...投资建造两艘巴拿马型原油轮暨关联交易`
- `印度石油部...80万吨液化石油气进口订单`
- `【公告全知道】...245亿元投建算电协同项目`
- `上交所就晶科科技...245亿元建设算力中心相关项目发布监管工作函`
- `*ST荣控...申请撤销对公司股票交易实施退市风险警示`
- `华测导航...开展供应链融资业务合作暨对外担保`
- `GQY视讯...可能被实施退市风险警示的风险提示公告`

### Current Decisions
- `【公告全知道】` 当前先保留；它是“栏目包装 + 真催化摘要”的混合体，不按纯编辑稿压。
- `华测导航...开展供应链融资业务合作暨对外担保` 当前先保留；它不等同于纯授信/担保额度材料。
- `GQY视讯...可能被实施退市风险警示的风险提示公告` 当前按首次风险提示保留。
- 如果后续重审 `华测导航`，先补 3 条测试：`scoring triggered`、`report 一保一压`、`event_merge subtype`。

### Known Risks Override
- `【公告全知道】` 继续下刀前必须先确认是否误伤真催化摘要。
- `业务合作 + 对外担保` 这类标题只是弱簇，不是纯材料簇；直接压整簇风险大。
- `report` 过滤和 `audit-suspicious` 仍是两套逻辑；继续验收时必须成对看。

## Update 2026-04-17

### What Changed
- `国内期货夜盘收盘多数上涨 甲醇等涨超2%` 已确认是已知 `market_move roundup` 同簇新变体：
  - 问题在 `text_report` 低信号词表缺少 `夜盘收盘多数上涨`
  - 已用最小方案修复：补 1 条回归 + 补 1 个词表项
- `*ST荣控...申请撤销对公司股票交易实施退市风险警示的公告` 已确认不是事件分类问题：
  - 问题在 `analysis/rules.py` 的 bullish 风险撤销白名单缺少该措辞
  - 已用最小方案修复：补 1 条白名单短语 + 补 1 条分析回归

### Verification Baseline Override
- `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -k "domestic_futures_night_session_up_roundup" -q`
  - `1 passed`
- `./.venv/bin/python -m pytest tests/test_analysis_scoring.py -k "delisting_risk_revocation_application" -q`
  - `2 passed`
- `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all`
  - `raw_news=1259`
  - `normalized_news=1259`
  - `events=270`
  - `analyses=270`
  - `failed_sources=none`
- `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
  - `suspicious_count=0`

### Current Report Head
- `中远海能...投资建造两艘巴拿马型原油轮暨关联交易`
- `*ST中基...申请撤销退市风险警示`
- `*ST荣控...申请撤销对公司股票交易实施退市风险警示`
- `华测导航...开展供应链融资业务合作暨对外担保`
- `GQY视讯...可能被实施退市风险警示的风险提示公告`

### Current Decisions
- `*ST荣控` 当前已回正到 `bullish`，后续不要再按通用 `风险` 词打回 `bearish`。
- `华测导航...开展供应链融资业务合作暨对外担保` 仍是弱簇边界样本，先保留。
- `GQY视讯...可能被实施退市风险警示的风险提示公告` 当天没有新的重复提示变体，继续保留。
## Update 2026-04-23 (latest)
- 这轮最有效的刀法仍然是 `text_report` 的最窄 live 样本收口，而不是继续动 `event_merge / analysis` 或扩题材库
- 本轮确认的新低信号家族：
  - `cninfo` 并购重组材料文档：`报告书（修订稿）`、`审核问询函回复`
  - 融资授权材料：`提请股东会授权董事会办理以简易程序向特定对象发行股票`
  - `irm_cninfo / sse_einteractive` 模板化弱回复：
    - 审评审批占位回复
    - `暂无项目涉及 / 以公开披露为准`
    - 资产注入/重组模板回复
    - 股价抱怨型问答
  - 交易所治理/制度/附件材料：
    - `ESG报告`
    - `内控自评`
    - `专项审核报告`
    - `持续督导保荐总结报告书`
    - `章程/议事规则`
    - `财务公司年度风险评估报告`
    - `支持创新创业管理办法`
    - `期货和衍生品交易业务内部控制制度`
    - `独立董事独立性专项意见/自查报告`
  - `equity_incentive` 材料变体：`股权激励计划相关事项的核查意见`
  - `cls` 栏目汇总：`今日投资舆情热点`
- 本轮同时确认应保留而未继续压的样本：
  - `乐普 DBS`
  - `长光华芯：硅光集成产线预计2026年底通线 光通信订单起量`
  - `乐普 MWM109`
  - `东华软件 DeepSeek/国产芯片适配`
- 当前最重要的新判断：
  - 现在的主风险已经从“明显漏出”切到了“继续沿当天 live 往下收会过拟合”
  - 因此下一步不该默认继续补规则，而该先做只读复核
- 下一步任务锁定：
  1. 先复核 `艾迪药业关于公司收购控股子公司少数股东股权进展的公告`
  2. 只有它被判断为新的一族低信号进展/材料公告时，才进入“红灯测试 -> 最窄规则 -> report/audit 验证”
  3. `乐普 DBS` 目前先不动
- 环境注意点：
  - 当前 Windows 会话无法直接复用 worktree `.venv`；本轮验证依赖本机 Python 3.10
  - `pytest` 未原样执行，但已用 `py_compile + 直接断言 + report/audit 实跑` 做等价验证
  - `cftc_press:fetch_error` 仍是独立采集问题，不属于本轮 handoff 的下一步主任务
