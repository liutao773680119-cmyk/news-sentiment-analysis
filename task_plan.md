# Task Plan: A股新闻题材雷达 MVP

## Goal
把项目推进到“真实多源输入 -> 事件归并 -> 题材/个股/历史参考输出”的可运行 MVP，并把当前接力点写清楚，保证后续会话能直接继续。

## Update 2026-04-17
- 最新已落盘并推远端的提交：
  - `443f22b` `fix: reduce registry company-update theme spillover`
  - `df2fec8` `fix: trim cls science feature story`
  - `8b6dce2` `fix: trim shareholder agreement supplement material`
- 本轮新增 staged 扩源提交：
  - `2db6b3f` `fix: tighten hkex staged source classification`
- 本轮确认的保留/过滤边界：
  - 过滤：
    - `企查查APP显示 + 经营范围包含 + 股权穿透显示` 造成的 `company_update` 题材误抬
    - `cls + general_fast_news + 全球首款/研发成功 + 科技日报 + 教授`
    - `sse/szse corporate_disclosure + 股东协议 + 补充协议`
  - 保留：
    - `华荣股份：国内首创智能化防爆高压环网柜研制成功`
    - `盈新发展：关于收购广东长兴半导体科技有限公司控制权的进展公告`
    - `恒瑞医药关于药物纳入突破性治疗品种名单的公告`
    - `云天化关于引入合作方投资建设新能源电池正极材料项目的公告`

## Update 2026-04-20
- 主线仍是 `phase8-live-boundary`，本轮没有继续做扩源，`hkex` 继续留在 staged
- 本轮按 live 头部连续收掉了一批弱信号：
  - `irm_cninfo` 弱问答、回避口径、年报导向回复
  - `sse/szse` 回购、股权激励、核查意见、风险管理、土地合同等材料公告
  - `cls` 夜盘/盘前综述、匿名拼盘栏目稿、弱财务收益股权处置稿
  - `海外单股并购快讯 + 无题材无个股`
- 同时补了几条更值钱的回正：
  - `省委财经委员会 / 产业引导基金` -> `policy_signal`
  - `乙烯法PVC供应持续收缩` -> `industry_data`
  - `UPC诉讼 / 仲裁裁决` -> `legal_dispute`
  - `美股盘前要闻一览` -> `general_fast_news`
- 当前最新验证：
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` -> `raw_news=1766 normalized_news=1766 events=468 analyses=468 failed_sources=none`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
- 当前头部已基本回到更像应保留的风险公告：
  - `*ST声迅：关于申请撤销对公司股票交易实施退市风险警示的公告`
  - `明德生物：关于公司股票交易被实施退市风险警示暨股票停复牌安排的公告`
- 结论：
  - 当前是一个适合停手的点
  - 下一轮先重跑当天 live，再决定有没有必要继续补最窄规则

## Update 2026-04-21
- 主线仍是 `phase8-live-boundary`，这轮继续只按 live 样本收口，不碰 `hkex staged`
- 本轮继续沿当天头部收掉了一批新弱样本：
  - `stcn` 的券商评论稿、`【早知道】` 摘要拼盘、基金经理配置评论、行业景气综述
  - `stcn` 的互动平台否定式回应，如 `暂未参股 / 未投资 / 未布局`
  - `irm_cninfo` 的“算力基建/后续布局”“营收/订单大概多少”“股价与业绩不对称/新项目么”这类弱问答
  - `sse_einteractive` 的题材追问变体，如 `大致有多少家`
- 本轮确认应保留：
  - `吉利将于2026北京车展发布中国首台原生Robotaxi原型车`
  - `奥特迅：关于股票交易被实施退市风险警示暨股票停牌的公告`
  - `长亮科技中标某股份制银行新网贷服务平台项目`
- 当前最新验证：
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` -> `raw_news=1781 normalized_news=1781 events=419 analyses=419 failed_sources=none`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
- 当前头部已切到更像 legit 保留样本：
  - `吉利将于2026北京车展发布中国首台原生Robotaxi原型车`
  - `奥特迅...退市风险警示`
  - `国内商品期货早盘开盘 多晶硅涨超4%`
  - `长亮科技中标某股份制银行新网贷服务平台项目`
- 结论：
  - 当前再次回到适合停手的点
  - 下一轮先重跑当天 live，不要沿用这轮头部继续过拟合

## Current Phase
Phase 8

## Phases

### Phase 1: 项目初始化与调研
- [x] 初始化 Python 项目骨架
- [x] 完成外部来源调研与 GitHub 同类项目调研
- [x] 完成第一版系统设计文档
- **Status:** complete

### Phase 2: MVP 基础链路
- [x] 落地 `collect -> normalize -> merge-events -> analyze-events -> report`
- [x] 建立 JSONL 存储与 CLI 入口
- [x] 建立最小测试基线
- **Status:** complete

### Phase 3: 真实源接入
- [x] 接入 `cninfo`
- [x] 接入 `miit`
- [x] 接入 `stcn`
- [x] 支持 `--source all` 多源混跑
- **Status:** complete

### Phase 4: 报告与过滤
- [x] 增加来源、发布时间、URL
- [x] 增加触发过滤与强度排序
- [x] 增加旧闻窗口过滤
- [x] 收紧中性 `fast_news` 和 `hard_event` 的噪音过滤
- **Status:** complete

### Phase 5: 事件细分与归并增强
- [x] 增加 `event_subtype`
- [x] 细分 `policy / hard_event / fast_news` 的交易化子类
- [x] 增加同资产 `market_move` 归并
- [x] 增加同股票、同催化子类的 `cninfo` 材料归并
- **Status:** complete

### Phase 6: 题材与映射增强
- [x] 扩展题材库与别名库
- [x] 扩展个股映射与历史样本
- [x] 增加 `黄金 / 油气 / 半导体 / AI应用 / 充电桩 / 数据安全 / 户外经济 / 锂电池`
- [x] 增加 `company_theme_map`，让 `cninfo` 催化事件能补题材
- **Status:** complete

### Phase 7: 当前接力点
- [x] 收紧多题材误命中，避免泛词触发错误题材
- [x] 补 `电力资源` 最小 seed，接住 `中国能建与华北电力大学签署战略合作协议` 这类真实空题材样本
- [x] 过滤 `美股/海外指数类` `stcn` 快讯，并阻断 `market_move` 摘要误带题材
- [x] 过滤 `港交所上市申请书` 这类 `stcn` 无题材快讯
- [x] 过滤 `stcn` 无题材股东减持快讯，如 `拟减持 / 减持不超`
- [x] 过滤 `cninfo` 的 `减持预披露 / 终止减持计划 / 回购股份用途并注销` 这类高频一般公告
- [x] 收紧 `fast_news` 题材提取到“标题优先”，压缩 `功率半导体` 一类多题材过命中
- [x] 过滤 `cninfo` 的 `董事会审计与风险管理委员会...履行监督职责情况的报告` 这类 `board_resolution` 材料文档
- [x] 补 `半导体` 的集成电路边界词，接住 `EDA / 先进封装` 一类高价值空题材样本
- [x] 收紧业绩类 `business_guidance` 的摘要题材 spillover，避免 `*ST金刚` 一类年报快讯被摘要里的赛道词误抬
- [x] 过滤 `国内期货市场夜盘收盘多数下跌` 这类 `stcn` 期货综述快讯，避免无题材 commodity roundup 占位
- [x] 显式过滤 `述职报告 / 业绩说明会 / ESG报告 / 鉴证报告 / 独立性专项意见` 这批 `cninfo` 材料变体
- [x] 切到 `miit` 高价值空题材样本，并补 `节能装备` 最小 seed，接住 `节能装备高质量发展实施方案`
- [x] 补 `信创` 最小 seed，接住 `信息技术创新应用` 这类 `miit` 政策样本
- [x] 将 `APP（SDK）通报` 这类 `miit` 监管样本挂到现有 `数据安全` 主题，避免继续空题材
- [x] 为 `miit` 明细页补正文抓取，避免政策样本只剩标题、丢失窄词面
- [x] 用 `match_name=false` 的窄 alias 方案补 `新材料` 最小 seed，接住 `新材料领域中小企业圆桌会`
- [x] 收紧 `policy` 题材提取到“标题优先、正文兜底需 2 个 alias 命中”，避免 `miit` 正文目录式提及把政策新闻扩成一串题材
- [x] 过滤 `国内期货开盘涨跌不一` 这类 `stcn` 国内商品期货开盘篮子快讯，避免无题材 market roundup 占位
- [x] 移除 `半导体` 的宽 alias `芯片`，避免 `育种芯片 / 京芯一号` 这类非半导体语境误命中
- [x] 将 `权威部门表态 + 冒号标题` 的 `stcn` 快讯归到 `policy_signal`，避免 `太空算力` 一类政策口径误落成 `company_update`
- [x] 过滤 `miit` 无题材会务综述，如 `科技创新和产业创新融合发展工作座谈会在苏州召开`，避免宽口径政策动态占据 report 头部
- [x] 扩展 `miit` 无题材会务过滤到 `会见 / 并座谈`，避免 `负责人会见跨国企业` 一类样本重新漏回 report
- [x] 过滤 `stcn` 的 `收评 / 午评 / 早盘` 指数综述，以及 `国内期货收盘涨跌不一` 这类收盘篮子快讯，避免 market roundup 重新占位
- [x] 过滤 `stcn` 无题材单股异动里的 `股价创下历史新高` 这类标题，避免个股涨停摘要占据 report 头部
- [x] 将 `乘联分会：1—2月中国汽车出口...` 这类统计口径快讯从 `company_update` 归正到 `industry_data`
- [x] 将 `华海药业：...获得药品注册证书` 这类 `stcn` 快讯从 `company_update` 归正到 `regulatory_approval`
- [x] 过滤 `cninfo` 的 `行政处罚事先告知书 / 重大资产重组实施情况之法律意见书` 这类材料公告，避免即使被公司题材映射抬高也重新漏回 report
- [x] 过滤 `stcn` 的券商宏观点评和 `生产经营正常 / 订单情况整体稳定` 这类经营近况快讯，避免非催化性口径占据 report 头部
- [x] 过滤 `miit` 的 `出版发行 / 报告发布` 无题材政策动态，避免发布通稿继续占据 report 头部
- [x] 收紧 `fast_news` 子类里 `通知 / 意见 / 印发 / 合作协议 / 订单合同` 的负面商业语境边界，避免 `违约通知 / 合作破裂 / 未履行订单义务` 这类企业纠纷误落成 `policy_signal / cooperation_agreement / order_contract`
- [x] 收紧 `cninfo` 一般公告的显示优先级，避免非交易型公告占据报告头部
- [x] 过滤低信号 `cninfo` 材料公告，如进展公告、通知债权人、风险评估报告、股权激励法律意见书
- [x] 过滤 `风险持续评估报告` 这类 `cninfo` 风险评估变体，避免同类材料公告重新漏回 report
- [x] 收紧 `stcn` 的无题材一般快讯噪音，并修正泛化“突破”导致的 `market_move` 误分类
- [x] 过滤 `stcn` 海外指数篮子快讯，避免 `欧洲主要股指跌幅扩大` 这类无题材尾项进入 report
- [x] 将 `fast_news` 催化判断收紧到标题级，避免摘要里的泛化 `订单` 误把业绩快讯带进 report
- [x] 为 `算力` 补 `CPO / 光模块 / 液冷服务器 / 数据中心 / 存储` 等窄 alias，接住真实 `stcn` 头部样本
- [x] 为 `AI应用` 补 `AI营销 / 智谱AI / 人工智能应用软件开发` 等窄 alias，接住真实 `stcn` 头部样本
- [x] 新增 `工程机械 / 保险 / 航空 / 商业航天` 最小题材定义，其中 `工程机械 / 保险 / 航空` 已补个股映射和历史样本
- [x] 新增 `PCB` 最小题材定义，并补个股映射与历史样本，接住 `PCB概念震荡走强`
- [x] 新增 `房地产` 最小题材定义，并补个股映射与历史样本，接住 `房地产板块震荡走高`
- [x] 扩展 `股价创历史新高` 单股异动过滤变体，清掉 `中际旭创涨超7% 股价创历史新高`
- [x] 将 `恒生科技指数 / 恒生指数` 并入现有海外/港股指数低信号过滤，避免重新进入 report 头部
- [x] 收紧 `航空` 主题到窄 alias，避免 `航空国际货物运输代理` 这类经营范围把一般公司快讯误挂到 `航空`
- [x] 将 `材料价格涨幅 + 行业景气度` 这类快讯从 `market_move` 回正到 `industry_data`
- [x] 新增 `港口机械` 最小题材定义，并补历史样本，接住 `GENMA获海外两台装船机订单`
- [x] 将 `韩日称朝鲜再次发射不明弹道导弹 朝方暂无回应` 这类地缘/军事快讯从 `company_update` 回正到 `general_fast_news`
- [x] 将 `日韩股市 / KOSPI指数` 并入现有海外指数低信号过滤，清掉 `日韩股市集体收涨 韩国KOSPI指数涨超6%`
- [x] 将 `成立科技公司 / 投资成立新公司` 这类企业设立快讯从 `general_fast_news` 回正到 `company_update`
- [x] 将单指数 `收评 / 午评 / 早盘 / 开评` 综述并入现有指数 roundup 过滤，清掉 `收评：创业板指涨5.91% AI营销概念大涨`
- [x] 将 `国内商品期货多数收跌 / 多数收涨` 并入现有期货综述过滤，清掉 commodity roundup 新变体
- [x] 将 `瑞银：近期可采取平衡型配置...` 这类机构配置评论从 `market_move` 回正到 `general_fast_news`，并在 report 层按机构评论过滤
- [x] 将 `入股 / 新增股东 / 工商变更 + 注册资本` 这类企业资本动作快讯从 `general_fast_news` 回正到 `company_update`
- [x] 将 `授予登记完成` 并入现有 `cninfo equity_incentive` 低信号材料过滤，清掉股权激励材料新变体
- [x] 为 `申请重整 / 预重整` 新增独立 `reorganization_risk` 子类，避免 `cninfo` 重整风险事件继续落在 `corporate_disclosure`
- [x] 将 `申请重整 / 预重整` 并入方向判定的负向词，保证 `reorganization_risk` 样本自动落为 bearish
- [x] 为 `商标争议` 新增独立 `legal_dispute` 子类，并将其并入方向判定的负向词
- [x] 新增 `audit-suspicious` CLI，先离线巡检“高信号但可能误分”的样本，再决定是否补窄规则
- [x] 将 `侵害发明专利权纠纷 / 专利权纠纷` 并入 `legal_dispute`，把 `佰维存储...纠纷案件` 从 `company_update / neutral` 回正到 `legal_dispute / bearish`
- [x] 将 `归属结果暨股份上市 / 回购注销限制性股票减资暨通知债权人` 并入 `cninfo equity_incentive` 材料过滤
- [x] 将 `股东减持股份计划公告 / 增持公司股份结果公告` 并入 `cninfo corporate_disclosure` 低信号结果公告过滤
- [x] 将 `纳斯达克中国金龙指数` 并入现有海外指数低信号过滤
- [x] 将 `增持计划实施完成 / 触及1%整数倍` 并入 `cninfo corporate_disclosure` 低信号结果公告过滤
- [x] 为 `退市风险警示 / 退市风险提示公告` 新增独立 `delisting_risk` 子类
- [x] 为 `电力资源` 补 `电厂迁建EPC` 窄 alias，接住 `中国能建浙江院...EPC总承包项目`
- [x] 从 `油气` 中移除宽 alias `燃气`，清掉 `燃气轮机` 对 `油气` 的误挂
- [x] 过滤 `cninfo` 的并购重组材料文档 / 问询回复 / 报告书（修订稿）` 这类低信号材料公告，清掉 `中芯国际` 相关样本的 report 漏出
- [x] 补 `铜缆高速连接`、`苹果链`、`储能` 的最小 seed，接住 `铜缆高速连接概念拉升`、`苹果概念走强`、`隆基与华为数字能源达成战略合作`
- [x] 将 `国际航协：航油价格翻倍航空业承压...` 这类海外航空燃油后果通稿从 report 头部过滤
- [x] 将 `华海清科...先进存储...晶圆减薄装备首台出机` 的 `算力, 半导体` 多题材误挂收敛为 `半导体`
- [x] 将 `信维通信：公司商业航天业务进展顺利` 从 `order_contract` 回正到 `company_update`
- [ ] 评估是否引入更细的“市场确认”或“催化强度分层”
- **Status:** in_progress

### Phase 8: 指数类异动展示策略
- [x] 明确 `沪指 / 深证成指 / 创业板指` 这类 A 股核心指数异动继续保留在 report 中
- [x] 将 A 股核心指数异动单独降权并标记为 `温度`，避免和题材催化混排
- [ ] 如果不保留，补对应 report 过滤测试和窄规则
- **Status:** in_progress

## Current State
- 工作分支：`mvp-foundation`
- 当前分支状态：dirty
- 当前最新推远端提交：`27886b0 fix: tighten live report boundary filters`
- 当前已启用真实源：`cninfo`、`miit`、`stcn`、`csrc`、`sse`、`szse`、`cls`
- 当前 staged 真实源：`hkex`
- 当前 CLI：
  - `collect`
  - `normalize`
  - `merge-events`
  - `analyze-events`
  - `audit-suspicious`
  - `report`
  - `run-once`
  - `live-smoke`

## Verification Baseline
- `./.venv/bin/python -m pytest tests/test_event_merge.py -q`
  - `51 passed`
- `./.venv/bin/python -m pytest tests/test_analysis_scoring.py -k "hkex_profit_warning or hkex_positive_profit_alert or delisting_risk or legal_dispute or reorganization_risk" -q`
  - `7 passed`
- `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -k "hkex_" -q`
  - `2 passed`
- `./.venv/bin/python -m pytest tests/test_hkex_collector.py -q`
  - `5 passed`
- `./.venv/bin/python -m pytest tests/test_analysis_scoring.py -k "company_setup_registry_scope_as_theme or advanced_storage_equipment_as_compute_infra" -q`
  - `2 passed`
- `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -k "cls_science_feature_story_without_hiding_company_product_progress" -q`
  - `1 passed`
- `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -k "exchange_shareholder_agreement_supplement_material_without_hiding_control_change_progress" -q`
  - `1 passed`
- `PYTHONPATH=src ./.venv/bin/python -m news_sentiment report`
  - `latest_report.txt` 已刷新
- `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
  - `suspicious_count=0`

## Immediate Next Steps
1. 先重跑当天主链，不沿用上一轮头部判断：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all`
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
2. 下一步第一条命令固定为：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all`
3. 如果 `live-smoke --source all` 通过，再继续：
   - 先看当天 report 头部是否仍主要是 legit 保留样本：
     - `吉利将于2026北京车展发布中国首台原生Robotaxi原型车`
     - `奥特迅...退市风险警示`
     - `长亮科技中标某股份制银行新网贷服务平台项目`
   - 再判断是否真的还有新的 `irm_cninfo / stcn / cls` 弱样本值得继续收
4. 如果头部仍主要是 legit 保留样本：
   - 先停，不继续压头部
   - 不要为了“更干净”继续过拟合 `text_report`
5. 如果出现新的弱样本：
   - 先补红灯测试
   - 再补最窄 `text_report` 过滤或必要的 `event_merge` 回正
   - 不做大范围题材扩张，也不碰 `hkex staged`
6. 如果主线切回扩源：
   - `hkex` 仍保持 staged
   - 先 `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect --source hkex`
   - 再顺序跑：
     - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment normalize`
     - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment merge-events`
     - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment analyze-events`
     - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment report`
     - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
7. `hkex` 下一步不要直接扩过滤面，优先补：
   - `INSIDE INFORMATION` 的更细 subtype/方向边界
   - stock code / company mapping
   - 再决定是否能进入 `--source all`

## Known Risks
- 当前题材识别仍是规则驱动，后续仍可能出现新的宽词误伤。
- `company_theme_map` 目前是种子表，不是完整股票库。
- `cninfo` 部分公告仍然会以“材料型文档”进入高分区，需要继续压缩。
- 当前还没有市场确认层，也没有真实交易回测。
- `cls` 已并入主链后，report 头部会自然出现全球快讯；不要把这类样本默认当成噪音。
- `cls` 的研报/解读稿仍可能吃到 `order_contract` 或强催化路径，需要继续收 subtype 边界。
- `report` 过滤和 `audit-suspicious` 是两套逻辑；不能只看其中一边。
- 当前已经进入收益递减区；如果头部只剩 legit 风险公告，优先停止继续压头部。
- `hkex` 当前虽然已经能留下部分真催化，但 `corporate_disclosure` 仍有 `1036` 条；现在启用到主链会明显拉低信噪比。
- `hkex` 英文标题如果继续走通用字符重合归并，会再次出现大面积错并。

## Update 2026-04-15

### Current Phase
- `Phase 9`
- 含义：`cls` 已完成 staged -> mainline 并入，当前主任务从“修明显漏口”切到“看头部保留项是否需要进一步分层”。

### Verification Baseline Override
- `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -k "miit_standardization_group_meeting_without_theme or deprioritizes_cls_global_information_below_direct_catalysts" -q`
  - `2 passed`
- `./.venv/bin/python -m pytest tests/test_report_pipeline.py -q`
  - `3 passed`
- `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all`
  - `raw_news=1250`
  - `normalized_news=1250`
  - `events=285`
  - `analyses=285`
  - `failed_sources=none`
- `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
  - `suspicious_count=0`

### Immediate Next Steps Override
1. 先重跑当天 `live-smoke --source all` 和 `audit-suspicious --limit 10`。
2. 如果结果仍稳定，优先检查 `cls` 的 `【风口研报·公司】...` 是否要与真实 `order_contract` 分开，而不是继续堆 `report` 过滤。
3. 如果切回扩源，下一条支线命令才是：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect --source hkex`

## Update 2026-04-11

### Current Phase
- `Phase 9`
- 含义：`szse` 已完成主链接入，当前主任务转为 `hkex` staged 收口后再决定是否并入 `--source all``。

### Current State Override
- 工作分支：`mvp-foundation`
- 当前分支状态：有未提交修改
- 当前已启用真实源：
  - `cninfo`
  - `stcn`
  - `miit`
  - `csrc`
  - `sse`
  - `szse`
- 当前 staged 真实源：
  - `hkex`
- 当前 CLI 除既有命令外，已实际用于巡检和扩源验收的关键入口：
  - `live-smoke`
  - `audit-suspicious`
  - `collect --source hkex`

### Verification Baseline Override
- `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all`
  - `raw_news=785`
  - `normalized_news=785`
  - `events=210`
  - `analyses=210`
  - `failed_sources=none`
- `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 20`
  - `suspicious_count=0`
- `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect --source hkex`
  - 真实网络验收通过
  - `data/raw/raw_news.jsonl` 当前写出 `392` 条 `hkex` 官方样本
- `./.venv/bin/python -m pytest tests/test_szse_collector.py tests/test_cli_smoke.py tests/test_live_smoke.py tests/test_report_pipeline.py -q`
  - `12 passed`
- `./.venv/bin/python -m pytest tests/test_hkex_collector.py -q`
  - `5 passed`

### Immediate Next Steps Override
1. 先不要继续把精力放在 `szse / sse / csrc` 的“是否能接入”上；这一步已经过了，当前优先级切到 `hkex` 启用前的最小过滤。
2. 下一步第一条命令固定为：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect --source hkex`
3. 然后做只读扫描：
   - 先看 `hkex` 最新 50 条标题，按标题族归并高噪音样本
   - 优先锁定 `Next Day Disclosure Return / Chinese section placeholder / AGM / Proxy / Annual / ESG / Monthly Return / Board Meeting`
4. 真正动规则时，只做最窄 report 过滤：
   - 先把明显材料型、会务型、治理型文档压掉
   - 不要顺手扩题材库
   - 不要直接把 `hkex` 打开到 `--source all`
5. 完成最小过滤后再验收：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all`
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 20`
6. 判断标准固定为：
   - `hkex` 不再把明显低信号披露材料顶到 report 头部
   - `audit-suspicious` 不因为 `hkex` 新开而回升
   - 仍不误伤真正高信号交易催化公告

### Known Risks Override
- `hkex` 虽然单源验通，但披露型文档比例高，直接并入 `--source all` 很可能拉低 report 信噪比。
- `report` 过滤和 `audit-suspicious` 属于两套逻辑；只压 report 头部，不代表巡检计数一定同步下降。
- 当前 worktree 里源码和交接文档都有未提交修改；下个会话接手前必须先看 `git -C .worktrees/mvp-foundation status --short`。

## Update 2026-04-16

### Immediate Next Steps Override
1. 先重跑当天基线：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all`
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
2. 只读检查当天 report 头部是否仍保留这 3 类边界：
   - `【公告全知道】...`
   - `华测导航...开展供应链融资业务合作暨对外担保`
   - `GQY视讯...可能被实施退市风险警示的风险提示公告`
3. 如果要重审 `华测导航`，先补 3 条测试再动规则：
   - `tests/test_analysis_scoring.py`：`华测导航...` 保持 `triggered=True`
   - `tests/test_text_report_sorting.py`：`华测导航...` 保留，对照 `申请综合授信额度` 过滤
   - `tests/test_event_merge.py`：`华测导航...` subtype 仍是 `corporate_disclosure`
4. 当前不要继续压：
   - `cls` 全球内容
   - `【公告全知道】` 栏目包装稿
   - `业务合作 + 对外担保` 整簇
5. 如果主线暂时停在这里，优先做标准交接和远端同步，不再追加新规则。

### Known Risks Override
- `【公告全知道】` 是“栏目包装 + 真催化摘要”的混合体，不适合按纯编辑尾噪处理。
- `业务合作 + 对外担保` 不是纯低信号材料簇；直接压整簇会误伤真实业务动作。
- `repeat hk listing application` 不只来自 `stcn`，`cls` 也会出现同类标题；规则不要只绑单一 source。

## Update 2026-04-17

### Immediate Next Steps Override
1. 先重跑当天基线：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all`
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
2. 只读检查当天 report 头部是否仍保留这 4 类边界：
   - `中远海能...关联交易`
   - `*ST中基 / *ST荣控` 风险撤销申请
   - `华测导航...开展供应链融资业务合作暨对外担保`
   - `GQY视讯...可能被实施退市风险警示的风险提示公告`
3. 当前不要继续压：
   - `【公告全知道】` 栏目包装稿
   - `业务合作 + 对外担保` 整簇
   - 风险撤销申请的 bullish 变体
4. 如果后续重审 `华测导航`，仍先补 3 条测试再动规则：
   - `analysis/scoring.py` 保持 `triggered=True`
   - `text_report` 一保一压
   - `event_merge` subtype 保持 `corporate_disclosure`

### Known Risks Override
- `国内期货夜盘收盘多数上涨` 这类 round-up 变体优先按 `text_report` 标题词表收，不要误扩到上游。
- `申请撤销对公司股票交易实施退市风险警示` 这类措辞虽带 `风险`，但语义是风险撤销申请；不要被通用 bearish 词覆盖。
