# Findings & Decisions

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
