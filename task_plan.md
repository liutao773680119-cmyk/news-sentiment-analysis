# Task Plan: A股新闻题材雷达 MVP

## Update 2026-05-24 (latest handoff)
- 当前真实主线仍是 `global-multisource-mainline`
- 本轮补完了 2026-05-22 中断的本地未提交收口：
  - `audit-suspicious`：
    - `国电南自关于仲裁进展的公告`
    - `ST宁科关于涉及追偿权纠纷诉讼的进展公告`
    - `东方生物...简易判决动议...预计 7 月宣布开庭...`
    - `国内单体最大智能组串式储能电站落地内蒙古`
  - `event_merge`：
    - `WTI原油期货日内涨3%` 保持 `market_move`
    - `伊朗...武装部队在停火期间进行了重组与重整` 不再误归并购重组
  - `text_report`：
    - `楚江新材 / 恒瑞医药 / 扬杰科技 / 诺力股份` 新一批弱问答已退出头部
    - 新补 `诺力股份：公司股价落后大盘指数50%以上了...不要光喊口号了`
- 当前验证：
  - `tests/test_audit_suspicious.py` 定向组 -> `6 passed`
  - `tests/test_event_merge.py` 定向组 -> `2 passed`
  - `tests/test_text_report_sorting.py` 定向组 -> `4 passed`
  - `audit-suspicious --limit 20` -> `suspicious_count=1`
  - `watchdog-once --source all --limit 20` -> `20260523T232729Z-watchdog.json`，`failed_sources=none`，`suspicious_count=1`
- 当前唯一残留：
  - `ST三木：关于公司部分债务逾期和部分银行账户被冻结的公告`
- 当前判断：
  - 这条先视为真风险，不继续按噪声压。

## Immediate Next Steps (2026-05-24 latest)
1. 先复核当前未提交 diff，确认只包含本轮 6 个代码/测试文件和交接文件：
   - `git diff -- src/news_sentiment/cli.py src/news_sentiment/event_merge/core.py src/news_sentiment/reporting/text_report.py tests/test_audit_suspicious.py tests/test_event_merge.py tests/test_text_report_sorting.py progress.md task_plan.md findings.md task_registry.md 修改记录_会话备忘.md 避坑记录.md`
2. 再做 scoped commit / push。
3. push 后只读观察后台：
   - `rg -n '^=====|watchdog_status=|failed_sources=|suspicious_count=' /tmp/news-sentiment-watch.log | tail -n 40`
4. 如果 fresh live 继续只剩 `ST三木`，先停手，不再为“更干净头部”继续压规则。

## Update 2026-05-21 (latest handoff)
- 当前真实主线仍是 `global-multisource-mainline`
- 本轮已处理后台新滚入的 `general_fast_news_with_theme` 误报：
  - `创业板指、深证成指均涨逾2% 半导体、券商等板块活跃`
- 本轮规则决策：
  - 该样本归入 `market_reference`，不是新的内容风险。
  - 新增最窄条件：
    - `stcn`
    - `general_fast_news`
    - 标题含 `创业板指 / 深证成指 / 沪指`
    - 同时含 `板块活跃`
    - 同时含 `涨逾 / 涨近 / 大涨`
  - 不改评分，不动 report 过滤，不把所有指数快讯一起放行。
- 当前验证：
  - 红灯：
    - `tests/test_audit_suspicious.py -k 'a_share_index_sector_active_as_market_reference' -q` -> 先失败，`suspicious_count=1`
  - 绿灯：
    - `tests/test_audit_suspicious.py -k 'a_share_index_sector_active_as_market_reference or global_index_sector_move_as_market_reference or a_share_concept_move_as_market_reference or a_share_concept_active_limit_up_as_market_reference or a_share_sector_strengthening_as_market_reference' -q` -> `5 passed`
    - `audit-suspicious --limit 20` -> `suspicious_count=0`
    - 后台自动循环：
      - `10:15:11 / 10:26:15 / 10:37:04` -> `alert`
      - `10:47:54` -> `clean`

## Immediate Next Steps (2026-05-21 latest)
1. 提交并推送本轮变更。
2. 推送后继续只读观察后台：
   - `rg -n '^=====|watchdog_status=|failed_sources=|suspicious_count=' /tmp/news-sentiment-watch.log | tail -n 40`
3. 如果再出现指数类快讯误报，先分：
   - `A股指数 + 板块活跃 + 涨幅热度词`
   - 纯指数综述 / 点位播报
4. 只有前者才考虑继续按 `market_reference` 扩窄口径；不要把所有指数快讯一刀切放过。

## Update 2026-05-20 (latest handoff)
- 当前真实主线仍是 `global-multisource-mainline`
- 本轮已处理当前两条交易所问询材料噪声：
  - `中国高科关于收到上海证券交易所《关于中国高科对外投资及股价波动事项的问询函》的公告`
  - `百通能源：大华会计师事务所（特殊普通合伙）关于江西百通能源股份有限公司申请向特定对象发行股票审核问询函有关财务事项的说明`
- 本轮规则决策：
  - `audit-suspicious` 侧新增最窄关键词：
    - `股价波动事项的问询函`
    - `审核问询函有关财务事项的说明`
  - `text_report` 同步补 `审核问询函有关财务事项的说明`
  - 不改评分，不扩题材库，不把全部 `问询函` 当噪声。
- 当前验证：
  - `tests/test_audit_suspicious.py -q` -> `64 passed`
  - `tests/test_text_report_sorting.py::test_write_text_report_filters_financing_inquiry_reply_and_judicial_unfreeze_without_hiding_catalyst -q` -> `1 passed`
  - 合并验证 -> `65 passed`
  - `audit-suspicious --limit 20` -> `suspicious_count=0`
  - `watchdog-once --source all --limit 20` -> `suspicious_count=0`
  - 后台自动循环 -> `22:36 recovered`，之后 `clean`

## Immediate Next Steps (2026-05-20 latest)
1. 先只读观察后台下一轮：
   - `rg -n '^=====|watchdog_status=|failed_sources=|suspicious_count=' /tmp/news-sentiment-watch.log | tail -n 40`
2. 再跑当前即时审计：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 20`
3. 如果 `alert` 回来但 `suspicious_count=0`，先按 source 问题查 `failed_sources`，不要继续补内容规则。
4. 如果又出现新 `问询函` 变体，先补红灯测试，再判断是否属于：
   - 年报问询材料
   - 融资审核财务说明
   - 股价波动问询材料
   - 真风险公告

## Update 2026-05-20 (latest handoff)
- 当前真实主线仍是 `global-multisource-mainline`
- 本轮增强后台 6 小时汇总：
  - 命令：`watchdog-summary --hours 6`
  - 输出：`data/monitoring/summaries/*-summary.md`
  - 后台 loop 默认每 6 小时自动生成一次
  - 新增 `Report Highlights` 区块，直接摘要当前 `data/reports/latest_report.txt`
  - 每条摘要包含：标题、类型、来源、方向、强度、题材、个股
  - 目的：用户平时不用单独打开 `latest_report.txt`，只看 6 小时汇总也能看到报告重点
- 当前验证：
  - `tests/test_watchdog_summary.py tests/test_readme_commands.py tests/test_watchdog_loop_script.py -q` -> `6 passed`
  - `py_compile src/news_sentiment/watchdog_summary.py tests/test_watchdog_summary.py` -> passed
  - `watchdog-summary --hours 6` -> 已生成 `data/monitoring/summaries/20260520T023731Z-summary.md`
  - `Report Highlights` 已确认包含类型、来源、方向、强度、题材、个股

## Immediate Next Steps (2026-05-20 latest)
1. 提交并推送本轮变更。
2. 推送后只读确认当前最新汇总：
   - `sed -n '/## Report Highlights/,+80p' data/monitoring/summaries/$(ls -1 data/monitoring/summaries/*-summary.md | tail -1)`
3. 等下一轮后台自动 6 小时汇总自然生成后，再确认其也包含 `Report Highlights`。
4. 后续继续观察新 `suspicious`，但不自动改规则。

## Update 2026-05-19 (latest handoff)
- 当前真实主线仍是 `global-multisource-mainline`
- 本轮处理 20:34-21:44 夜间 watchdog alert：
  - 年报问询函材料/回复类：
    - 评估问题回复
    - 会计师事务所年报问询函回复
    - 收到年报有关事项问询函公告
    - 年报的问询函的回复公告
  - 会见交流类：
    - 外汇局会见友邦保险主席
    - 江苏省委书记会见 AMD 董事会主席兼 CEO
  - 贵金属点位播报：
    - 现货黄金日内跌幅达 2%
- 当前验证：
  - `tests/test_audit_suspicious.py -k 'current_low_signal_batch_20260519_night or current_low_signal_batch_20260518 or precious_metal_spot_move or chairman_meeting' -q` -> `4 passed`
  - `audit-suspicious --limit 20` -> `suspicious_count=0`
  - `live-smoke --source all` -> `raw_news=568 normalized_news=568 events=457 analyses=457 failed_sources=none`
  - 刷新后 `audit-suspicious --limit 20` -> `suspicious_count=0`

## Immediate Next Steps (2026-05-19 latest)
1. 先只读观察 watchdog 是否吃到本地最新规则：
   - `rg -n '^=====|watchdog_status=|failed_sources=|suspicious_count=' /tmp/news-sentiment-watch.log | tail -n 40`
2. 再跑当前审计：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 20`
3. 若后台自动日志仍显示旧 `21:44 alert=2`，但即时审计为 0，先等下一轮自动 loop，不要重复补规则。
4. 若用户要求收口，下一步是标准提交并推送：
   - `git add src/news_sentiment/cli.py tests/test_audit_suspicious.py progress.md task_plan.md findings.md task_registry.md 修改记录_会话备忘.md 避坑记录.md`
   - `git commit -m "fix: suppress latest night audit noise"`
   - `git push origin HEAD:mvp-foundation`

## Update 2026-05-19 (latest handoff)
- 当前真实主线仍是 `global-multisource-mainline`
- 本轮继续处理 5/19 后台新滚入的 `audit-suspicious` 尾噪：
  - `爱科诺生物医药宣布完成5000万美元C轮融资`
    - 私营生物医药 C 轮融资泛稿。
    - 只退出 audit 异常，不扩题材库。
  - `Japan’s Takeda engaged in antitrust scheme to delay generic constipation drug, US jury finds`
    - 海外药企反垄断/诉讼新闻。
    - 本轮 `半导体` 主题属于串味，只按 `investing_news + pharma antitrust/lawsuit` 最窄口径跳过。
- 当前验证：
  - `tests/test_audit_suspicious.py -k 'overseas_pharma_antitrust_lawsuit_theme_spillover or private_biotech_c_round_financing_story or private_robot_financing_general_fast_news' -q` -> `3 passed`
  - `live-smoke --source all` -> `raw_news=614 normalized_news=614 events=463 analyses=463 failed_sources=none`
  - `audit-suspicious --limit 20` -> `suspicious_count=0`
  - 后台 `2026-05-19_11:47:19` 到 `2026-05-19_13:58:53` 连续 clean。

## Immediate Next Steps (2026-05-19 latest)
1. 推送后只读观察后台：
   - `rg -n '^=====|watchdog_status=|failed_sources=|suspicious_count=' /tmp/news-sentiment-watch.log | tail -n 40`
2. 再跑当前审计：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 20`
3. 如果 `suspicious_count=0` 但 `watchdog_status=alert`，先看 `failed_sources`，不要继续补内容降噪。
4. 如果继续出现新内容异常：
   - 先判断是 `low_signal`、`market_reference`、主题串味还是真实风险。
   - 再补红灯测试和最窄规则。
   - 最后跑定向测试、`live-smoke --source all`、`audit-suspicious`。

## Update 2026-05-19 (latest handoff)
- 当前真实主线仍是 `global-multisource-mainline`
- 本轮回溯 `2026-05-15` 到 `2026-05-19`：
  - 5/15-5/18 确有多轮 `watchdog_status=alert`
  - 5/19 内容可疑已回到 `suspicious_count=0`
  - 仍存在采集源短暂失败：`szse / csrc / sse_einteractive` 等
- 本轮已处理的内容异常：
  - 年报问询函审计专项说明 / 法律意见书材料
  - 仲裁进展材料
  - 会见/交流类快讯
  - 现货白银点位播报
  - `irm_cninfo` 纯提问法律投诉
  - `【淘金互动易】` 算力产业链内容按 `market_reference` 保留报告，只退出 audit 异常
- 当前验证：
  - `tests/test_audit_suspicious.py -k 'current_low_signal_batch_20260518 or bank_insurance_chairman_meeting_story or annual_inquiry_audit_and_legal_opinion_materials' -q` -> `3 passed`
  - `audit-suspicious --limit 20` -> `suspicious_count=0`

## Immediate Next Steps (2026-05-19 latest)
1. 推送后只读观察后台：
   - `rg -n '^=====|watchdog_status=|failed_sources=|suspicious_count=' /tmp/news-sentiment-watch.log | tail -n 40`
2. 再跑当前审计：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 20`
3. 如果 `suspicious_count=0` 但 `watchdog_status=alert`，优先看 `failed_sources`，不要继续补内容降噪。
4. 如果出现新内容异常，继续按：
   - 先判断是否 `low_signal`、`market_reference` 或真实风险
   - 红灯测试
   - 最窄规则
   - 定向测试 + 当前审计

## Update 2026-05-15 (latest handoff)
- 当前真实主线仍是 `global-multisource-mainline`
- 本轮继续围绕后台 `audit-suspicious` 误报做最窄降噪：
  - `三部门召开加强新能源汽车安全管理工作视频会`
    - 归入 `stcn` 公共事务/会议类低信号
    - 不扩新能源车题材库
  - `全球首个海底数据中心落户东海`
    - 归入 `stcn` 项目示范/科普型低信号
    - 不影响真实算力订单、产业链催化、上市公司明确业务进展
  - `佳力图拜访之江实验室三体计算星座项目团队 交流液冷散热与太空算力温控技术`
    - 归入 `stcn` 公司拜访/交流对接类低信号
    - 不影响签署、中标、订单、合同、采购类真实合作进展
- 当前验证：
  - `audit-suspicious --limit 10` -> `suspicious_count=0`
  - `news-sentiment-watch` 最近一轮 `2026-05-15_09:10:48` -> `watchdog_status=clean`、`failed_sources=none`、`suspicious_count=0`
  - 定向 pytest 和 `git diff --check` 本轮曾出现本机文件读取阻塞，未拿到最终输出；需在 Git/文件读取恢复后补跑。
- 当前阻塞：
  - 本机出现 `git status` / `git diff` / 部分文件头部读取卡住现象。
  - 交接文件已更新；commit/push 需等 Git 可用后执行。

## Immediate Next Steps (2026-05-15 latest)
1. 先清理/确认卡住的只读进程：
   - `ps -axo pid,stat,etime,command | rg 'git status|git diff|pytest tests/test_audit_suspicious|sed -n' | rg -v rg`
2. Git 恢复后补跑：
   - `./.venv/bin/pytest tests/test_audit_suspicious.py -k 'undersea_data_center_demonstration_story or nev_safety_management_video_meeting or public_affairs' -q`
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
3. 然后提交推送：
   - `git add src/news_sentiment/cli.py tests/test_audit_suspicious.py progress.md task_plan.md findings.md task_registry.md 修改记录_会话备忘.md 避坑记录.md`
   - `git commit -m "fix: suppress latest public affairs audit noise"`
   - `git push origin HEAD:mvp-foundation`
4. 暂不建议：
   - 继续泛化 `stcn` 公共事务词表
   - 关闭全部 `general_fast_news_with_theme`
   - 把项目示范类规则扩到所有数据中心/算力新闻

## Update 2026-05-14 (latest handoff)
- 当前真实主线仍是 `global-multisource-mainline`
- 本轮围绕后台 `audit-suspicious` 连续 alert 做口径分层：
  - 材料/流程型低信号继续走最窄降噪：
    - `股票交易异常波动问询函` 回函
    - `年报问询函的专项说明`
    - `国内商品期货夜盘开盘 + 涨跌幅播报`
    - `新增诉讼的公告`
    - `提起诉讼的公告`
    - `募集资金账户被冻结`
  - 外盘题材联动信号不再当噪音：
    - `纳斯达克综合指数跌逾1% 芯片半导体股票集体下跌`
    - 保留在 report
    - 保留 `半导体` 题材与 A 股候选映射
    - 仅从 `audit-suspicious` 异常口径中按 `market_reference` 跳过
  - A 股概念异动信号不再当噪音：
    - `PCB概念走强 大族激光等股价创新高`
    - 保留 `PCB` 题材映射和 `impact_score=79.0`
    - 仅从 `audit-suspicious` 异常口径中按 `market_reference` 跳过
    - `创新药概念活跃 昂利康2连板`
    - 保留 `创新药` 题材映射和 `impact_score=79.0`
    - 仅从 `audit-suspicious` 异常口径中按 `market_reference` 跳过
    - `半导体板块震荡走强 天岳先进涨近20%`
    - 保留 `半导体` 题材映射和 `impact_score=79.0`
    - 仅从 `audit-suspicious` 异常口径中按 `market_reference` 跳过
  - 港股主题异动信号不再当噪音：
    - `港股AI应用股拉升 智谱涨逾15%`
    - 保留 `AI应用` 题材映射和 `impact_score=79.0`
    - 仅从 `audit-suspicious` 异常口径中按 `market_reference` 跳过
- 当前验证：
  - `tests/test_analysis_scoring.py -k 'a_share_sector_strengthening_as_theme_reference or a_share_concept_active_limit_up_as_theme_reference or a_share_concept_move_as_theme_reference or global_index_sector_move_as_theme_reference' -q` -> `4 passed`
  - `tests/test_audit_suspicious.py -k 'a_share_sector_strengthening_as_market_reference or a_share_concept_active_limit_up_as_market_reference or a_share_concept_move_as_market_reference or global_index_sector_move_as_market_reference' -q` -> `4 passed`
  - `tests/test_audit_suspicious.py -k 'short_litigation_material_notices or major_litigation_and_filing_progress_notices or cumulative_new_litigation_arbitration_disclosure or major_litigation_disclosure' -q` -> `4 passed`
  - `tests/test_audit_suspicious.py -k 'fundraising_account_freeze_material_notice or waiting_freeze_notice or short_litigation_material_notices or major_litigation_disclosure' -q` -> `4 passed`
  - 当前数据复算：`suspicious_count=0`
  - `latest_report.txt` 仍保留 `纳斯达克综合指数跌逾1% 芯片半导体股票集体下跌`
- 当前判断：
  - 外盘半导体联动、A 股概念走强/概念活跃/板块震荡走强、港股主题股拉升都属于 `market_reference`，不是 `LOW_SIGNAL`。
  - 后台 alert 需要减少误报，但不能牺牲报告里的参考信号。

## Immediate Next Steps (2026-05-14 latest)
1. 推送后继续观察下一轮后台：
   - `rg -n '^=====|watchdog_status=|suspicious_count=|failed_sources=' /tmp/news-sentiment-watch.log | tail -n 20`
2. 再跑一次当前口径：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
3. 如果后台仍是同一条 `纳斯达克综合指数...半导体...`、`PCB概念走强...`、`创新药概念活跃...`、`半导体板块震荡走强...` 或 `港股AI应用股拉升...`，先确认 loop 是否吃到最新 commit；不要再加 report 过滤。
4. 如果出现新的题材联动，按 `market_reference` 判断：
   - 有明确指数/板块/概念/主题股方向 + 明确 A 股题材映射：保留 report，仅跳过 audit 异常
   - 纯指数点位或商品开盘播报：按低信号处理
5. 如果出现新的短标题诉讼材料公告，先看 report 位置和是否有实质风险细节；无金额/判决/重大进展时才按 audit 尾噪处理。
6. 如果再次出现 `募集资金账户被冻结` 同族样本，按当前用户口径优先当 audit 尾噪，不要反向恢复成强风险正例。
7. 暂不建议：
   - 把 `general_fast_news_with_theme` 整体关掉
   - 把 `market_reference` 加入 `text_report` 过滤
   - 为了追求 `watchdog_status=clean` 删除有参考价值的题材联动新闻
   - 把所有诉讼公告一刀切为噪声

## Update 2026-05-11 (latest handoff)
- 当前真实主线仍是 `global-multisource-mainline`
- 目前已完成 `cninfo` 年报问询函与发行优先股/诉讼材料的同步降噪：
  - `src/news_sentiment/cli.py` 添加关键字收敛
  - `tests/test_audit_suspicious.py` 补 8 条新异常固定回归
- 近期验证：
  - `PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit_suspicious.py -q` -> `41 passed`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 20` -> `suspicious_count=0`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` -> `raw_news=576 normalized_news=576 events=440 analyses=440 failed_sources=none`
  - `latest_report.txt` 无关键异常标题命中
- 当前风险：
  - `audit-suspicious=0` 不等于 report 头部 0 风险，仍每轮要看 `latest_report.txt`
- 当前首选下一步：
  1. `sed -n '1,160p' data/reports/latest_report.txt`
  2. `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
  3. `git add src/news_sentiment/cli.py tests/test_audit_suspicious.py progress.md findings.md task_plan.md task_registry.md 修改记录_会话备忘.md 避坑记录.md`
  4. `git commit`
  5. `git push origin HEAD:mvp-foundation`

## Update 2026-05-08 (latest handoff)
- 当前真实主线仍是 `global-multisource-mainline`
- 本轮从 `sse_einteractive / irm_cninfo` 头部尾噪继续：
  - `news-sentiment-watch` 口径仍稳定
  - `failed_sources=none`
  - `suspicious_count=0`
  - `latest_report.txt` 里本轮目标尾噪已退出
- 本轮已处理：
  - `text_report`：
    - `安通控股` 两条投资者抱怨型 `sse_einteractive` 问答
    - `精工钢构` 空回复抱怨问答
    - `中超控股` question-only `网传中标...是真的吗`
    - `青鸟智控` question-only `光伏储能相关业务吗`
- 当前验证：
  - `tests/test_text_report_sorting.py -q` -> `242 passed`
  - `live-smoke --source all` -> `raw_news=449 normalized_news=449 events=395 analyses=395 failed_sources=none`
  - `audit-suspicious --limit 10` -> `suspicious_count=0`
- 当前结论：
  - 本轮目标尾噪已经清掉
  - 当前只剩 `精工钢构` 的实质算力问答保留在头部，这条按现口径应保留
  - 现在更适合收尾推送，不适合继续泛化
- 当前风险：
  - `audit=0` 不等于 report 头部完全没有边界样本
  - live 重跑后同簇 `event_id` 可能变化，排障要按当前标题/正文对齐
  - `data/events/event_analysis.jsonl` 才是当前 analyses 路径
  - `irm_cninfo` 当前会有 `summary=title-only` 的 question-only live 样本，旧 reply 规则不覆盖

## Immediate Next Steps (2026-05-08 latest)
1. 直接收尾：
   - `git status --short`
   - `git add ...`
   - `git commit`
   - `git push`
2. 下一轮如果继续，只先只读查看：
   - `sed -n '1,180p' data/reports/latest_report.txt`
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
3. 如果再出现新的 `irm_cninfo` question-only 弱问答，继续按：
   - 红灯测试
   - 最窄 title-only 规则
   - 定向测试
   - `live-smoke --source all`
4. 暂不建议：
   - 为了更短头部继续压当前 `cls/stcn` 真样本
   - 重开已处理家族
   - 混修 source 问题和 report/audit 尾噪

## Update 2026-05-01 (latest handoff)
- 当前真实主线仍是 `global-multisource-mainline`
- 本轮从后台 loop 巡检继续：
  - `news-sentiment-watch` 正常运行
  - `failed_sources=none`
  - `audit-suspicious=0`
  - 但 `latest_report.txt` 头部持续滚入新一批 `stcn / irm_cninfo` 尾噪，所以继续按最窄规则收口
- 本轮已处理：
  - `stcn public affairs`：
    - `刘小明在海南商业航天发射场看望慰问...`
  - `irm_cninfo` question-only 弱问答：
    - `福建金森`
    - `东方钽业`
  - `stcn` 榜单/综述：
    - `近一周机构调研个股超700只`
  - `stcn negative platform reply`：
    - `安宁股份：目前公司未单独提取钒产品`
- 当前验证：
  - `tests/test_text_report_sorting.py -q` -> `236 passed`
  - `audit-suspicious --limit 10` -> `suspicious_count=0`
  - 串行重写后的 `latest_report.txt` 已确认本轮目标样本退出
- 当前提交：
  - `881c5d6 fix: trim latest public affairs and irm complaint noise`
  - `772fa56 fix: trim latest survey roundup and platform qa noise`
- 当前结论：
  - A股头部已基本回到风险/订单合同样本
  - 当前更值得观察的是全球分区边界，不是继续压 A 股问答尾噪
- 当前风险：
  - loop 最新自动落盘块仍是 `2026-05-01_20:52:50`，早于最后一批规则提交
  - `HF Sinclair` 和 `AIG` 目前属于边界样本，继续下刀的过拟合风险开始升高

## Immediate Next Steps (2026-05-01 latest)
1. 先只读查看：
   - `tail -n 120 /tmp/news-sentiment-watch.log`
   - `sed -n '1,170p' data/reports/latest_report.txt`
2. 确认下一轮 loop 已经吃到 `772fa56`。
3. 只盯两个全球分区边界：
   - `HF Sinclair` 二季度原油加工量指引
   - `AIG` 软件风险敞口
4. 只有它们连续多轮稳定占头部，才按：
   - 红灯测试
   - 最窄规则
   - `tests/test_text_report_sorting.py`
   - `report` + `audit-suspicious`
5. 暂不建议：
   - 扩题材库
   - 动 `event_merge / analysis / source enable`
   - 为了更短头部继续压当前真实风险公告

## Update 2026-04-29 (latest handoff)
- 当前真实主线仍是 `global-multisource-mainline`
- 本轮从 2026-04-28 交接继续，只读复核后发现：
  - `audit-suspicious=0`
  - 但 `latest_report.txt` 头部又出现新一批弱样本，不能直接停手
- 本轮已处理：
  - `cls` 海外/栏目弱样本：
    - 美股光通信板块开盘普跌
    - 世界银行能源价格预测
    - `【财联社早知道】我国最大规模科学智能集群...` 匿名拼盘稿
  - `irm_cninfo` 弱问答：
    - 中工国际算电协同出海泛问答
  - 交易所/巨潮材料：
    - 股票期权注销/授予价格调整
    - 减持股份触及比例
    - 董事会风险控制委员会工作细则
    - 股权转让交易进展及签署补充协议
    - 累计新增诉讼/仲裁材料
  - `stcn` 泛稿：
    - 擎天租 Pre-A 融资机器人应用交付能力
  - 同步补了 `text_report` 与 `audit-suspicious` 测试，避免两套口径漂移
- 当前验证：
  - `tests/test_text_report_sorting.py -q` -> `232 passed`
  - `tests/test_audit_suspicious.py -q` -> `24 passed`
  - `py_compile` -> 通过
  - `git diff --check` -> 通过
  - `live-smoke --source all` -> `raw_news=2003 normalized_news=2003 events=966 analyses=966 failed_sources=none`
  - `report` -> 通过
  - `audit-suspicious --limit 10` -> `suspicious_count=0`
  - `latest_report.txt` 目标弱样本搜索 -> 无命中
- 当前提交：
  - `1fe1a12 fix: filter latest live report noise`
- 当前结论：
  - report 头部已回到退市风险/其他风险警示及少量真实并购进展
  - 当前适合停手交接，不建议继续为了“更短头部”补词
- 当前风险：
  - `urllib3 NotOpenSSLWarning` 仍会出现，但命令退出码为 0
  - live 样本滚动很快，下一轮不能复用本轮头部直接补规则

## Immediate Next Steps (2026-04-29 latest)
1. 先只读查看：
   - `sed -n '1,180p' data/reports/latest_report.txt`
2. 再跑：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
3. 如果 report 头部仍是退市风险/真实并购进展，优先停手，不继续压头部。
4. 如果出现新弱样本，必须按：
   - 红灯测试
   - 最窄规则
   - `tests/test_text_report_sorting.py`
   - 如涉及巡检，同步 `tests/test_audit_suspicious.py`
   - `report` + `audit-suspicious`
   - 必要时 `live-smoke --source all`
5. 暂不建议：
   - 扩题材库
   - 动 `event_merge / analysis / source enable`
   - 继续压真实风险公告、真实并购、真实诉讼/风险警示进展

## Update 2026-04-28 (latest handoff)
- 当前真实主线仍是 `global-multisource-mainline`
- 本轮从交接指定验收继续推进：
  - 补齐本地 `.venv` 缺失的 `requests`
  - 跑 `live-smoke --source all`
  - 按当前 live report 头部做最窄 `text_report` 收口
- 本轮已处理：
  - report 时间窗按已通过市场相关性过滤的事件计算，避免低信号新材料把旧正例整体挤掉
  - A股主题市场异动回 `A股强催化`，海外单股主题异动留 `全球市场与商品`
  - `irm_cninfo` 弱问答变体：
    - 股价落后 + 并购计划
    - 人形机器人液冷方案但暂未应用
    - 毛利率抱怨 + 改善计划
    - 减持原因但回复为未减持/按规披露
  - `sse/szse` 年报季材料：
    - 董事会决议
    - 会计政策变更
    - 计提减值准备
    - 募集资金存放/管理/使用专项报告
    - ESG 报告
    - 审计委员会履职报告
    - 回购报告书/出售已回购股份计划/回购注销限制性股票材料
- 当前验证：
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` -> `raw_news=1473 normalized_news=1473 events=760 analyses=760 failed_sources=miit:fetch_error`
  - `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q` -> `231 passed`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment report` -> 通过
  - `latest_report.txt` 已确认本轮新增处理关键词不再出现
- 当前结论：
  - report 头部已回到并购、退市/风险、诉讼、合作协议等应先保留样本
  - 当前适合停手交接，不建议继续为了“更短头部”补词
- 当前风险：
  - `miit:fetch_error` 是采集源问题，需单独排查
  - `urllib3 NotOpenSSLWarning` 仍会出现，但当前命令退出码为 0

## Immediate Next Steps (2026-04-28 latest)
1. 先只读查看：
   - `sed -n '1,160p' data/reports/latest_report.txt`
2. 如果头部仍是本轮记录的并购/退市风险/诉讼/合作协议样本，优先停手或提交。
3. 如果要继续规则收口，必须先确认新样本属于“整族弱样本”，再按：
   - 红灯测试
   - 最窄规则
   - `tests/test_text_report_sorting.py`
   - `audit-suspicious --limit 10`
   - `report` + 目标关键词搜索
4. `miit:fetch_error` 单独排查，不和 report 收口混线。
5. 暂不建议：
   - 扩题材库
   - 动 `event_merge / analysis / source enable`
   - 继续压真实风险公告、真实并购、真实诉讼进展
   - 把 `hkex staged` 开进 `--source all`

## Update 2026-04-27 (latest handoff before push)
- 当前真实主线仍是 `global-multisource-mainline`，重点是 `--source all` 下 report 尾噪收口，不扩题材库，不动 `event_merge / analysis`
- 本轮已继续压掉：
  - `补充协议/续签业务合作协议暨关联交易`
  - `投资性房地产管理办法 / 房地产业务专项自查报告`
  - `股权激励归属核查意见 / 回购注销限制性股票的减资公告`
  - `购买土地使用权 + 投资合作意向书`
  - `摊薄即期回报风险提示及填补回报措施`
  - `关联存款风险处置预案`
  - `stcn` 的 `围绕战略合作等交流座谈`
  - `国内商品期市夜盘收盘` 变体
- 当前验证：
  - `PYTHONPATH=src python -m news_sentiment report` -> 通过
  - `PYTHONPATH=src python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
  - `latest_report.txt` 已确认不再包含本轮新增处理样本
  - `华大基因：关于收购重庆新一产生命科技有限公司100%股权暨关联交易的公告` 仍保留
- 环境注意：
  - 当前 Windows Python 3.10 仍未装上 `pytest`
  - 已尝试 `pip install pytest`、`--trusted-host`、`--isolated`，均被坏掉的 proxy 链路阻塞
  - 后续若要补原样测试，先处理代理/镜像问题

## Update 2026-04-24 (latest handoff before push)
- 主线仍按 `phase8-live-boundary` 的节奏做 live 头部最窄收口，不扩题材库，不动 `source enable`
- 本轮已处理：
  - `*ST美谷` 的 `涉及诉讼进展暨银行账户解除冻结`
  - `龙大美食` 的 `强制执行完成暨解除冻结`
  - `泰达股份` 的 `重大资产出售暨关联交易问询函回复`
  - `东睦股份` 的 `并购重组审核委员会...会议安排`
- 本轮规则边界：
  - `涉及诉讼进展`、`强制执行完成` 只作为风险披露/材料公告收口
  - `问询函回复` 只在并购重组/重大资产出售/融资材料上下文里收口，不做裸词泛化
  - `会议安排` 只在并购重组材料上下文里用于 report 过滤
- 当前验证：
  - `py_compile` 通过
  - `PYTHONPATH=src python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
  - `PYTHONPATH=src python -m news_sentiment report` -> 通过
  - `latest_report.txt` 已确认不再包含本轮 4 条目标样本
  - `live-smoke --source all` 在 Windows 下 240 秒超时；不要把它直接当成规则失败

## Immediate Next Steps (2026-04-24 latest)
1. 当前第一优先级是停手观察，而不是继续补规则。
2. 下一轮第一条命令建议：
   - `PYTHONPATH=src python -m news_sentiment audit-suspicious --limit 10`
3. 然后只读查看：
   - `Get-Content data/reports/latest_report.txt -TotalCount 80`
4. 如果 `audit-suspicious` 仍为 0，优先不动规则。
5. 如果继续处理 report 头部，先复核：
   - `亚太药业：关于签署《技术开发合同补充协议》暨关联交易的公告`
   - `万润股份：关于与烟台万海舟化工有限公司续签《业务合作协议》暨关联交易的公告`
6. 只有确认它们是稳定低信号合同/关联交易材料族，才按“红灯测试 -> 最窄规则 -> report/audit 验证”推进。
7. 暂不建议：
  - 扩题材库
  - 动 `event_merge / analysis`
  - 打开或推进 `hkex staged`
  - 继续为了“头部更干净”压合法风险事件或真实催化

## Immediate Next Steps (2026-04-27 latest)
1. 当前优先级仍是停手观察，不继续沿当天样本向下过拟合。
2. 下一轮固定第一条命令：
   - `PYTHONPATH=src python -m news_sentiment audit-suspicious --limit 10`
3. 然后只读查看：
   - `Get-Content data/reports/latest_report.txt -TotalCount 120`
4. 如果 `audit-suspicious` 仍为 0，且头部主要剩真实风险/并购样本，优先不动规则。
5. 如果后续要恢复原样 `pytest` 验证，先处理当前 Windows Python 的代理/镜像问题，再补跑定向测试。
6. 暂不建议：
   - 再压当前头部里的真实风险公告
   - 继续机械扩充 `LOW_SIGNAL_*` 词表
   - 提前把 `hkex staged` 开进 `--source all`

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

## Update 2026-04-21（latest）
- 主线仍是 `phase8-live-boundary`，这轮把当天剩余的 `irm/stcn/cls` 弱样本继续收口，并完成标准交接
- 本轮新增收口：
  - 修掉 `szse` 同模板退市风险公告错并：
    - `hard_event` 归并先看结构化催化和股票代码
    - 股票代码提取补了 `news_id` fallback
    - `奥特迅 / *ST声迅 / 明德生物 / ST赛为` 已拆回四条独立 event
  - `analysis` 补了两条 live spillover 回正：
    - `荷兰出台纾困计划应对能源价格高企` 不再误挂 `新能源车`
    - `主力资金监控：立讯精密净卖出超12亿` 不再误挂 `文旅`
  - `text_report` 连续补了最窄过滤，继续收掉：
    - `irm_cninfo` 的 question-only 弱问答
    - `irm_cninfo` 的经营范围介绍、订单充裕、未披露事项否认、审慎论证、并购方向泛回复、小批量供货但收入占比较小、减持预披露规则追问、继续回购诉求、定增正常推进
    - `szse equity_incentive` 的 `限制性股票激励计划有关事项的核查意见`
    - `cls` 的 `股价“一”字跌停 英维克最新回应`
    - `cls` 的 `三大指数全部翻红`
    - `stcn` 的 `协创数据：2026年将持续加大算力业务投入 目前在手订单充裕`
    - `荣耀夺冠机器人“空间神经末梢”由深圳纽瑞芯提供`
- 本轮明确保留：
  - `乌克兰国防部宣布：上半年增订2.5万台机器人 计划将后勤完全自动化`
  - `WTI原油期货跌破86美元/桶`
  - `第二届世界人形机器人运动会将于8月在京举办`
- 当前最新验证：
  - `./.venv/bin/python -m pytest tests/test_event_merge.py tests/test_analysis_rules.py tests/test_text_report_sorting.py -q` -> `318 passed`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
  - `latest_report.txt` 当前头部已回到更像 legit 保留样本：
    - `乌克兰机器人扩单`
    - `WTI跌破86`
    - `世界人形机器人运动会`
    - `奥特迅 / *ST声迅 / 明德生物 / ST赛为` 退市风险公告
- 结论：
  - 这轮 `phase8-live-boundary` 已到适合停手和提交的点
  - 下一轮如果仍要继续主线，先重跑当天 live；若头部主要仍是上述样本，不再继续压 `report`

## Update 2026-04-22（hkex staged）
- 当前关注点切到 `phase9-source-expansion` 的 `hkex staged`
- 本轮没有继续扩源，只沿 `hkex` 单源报告头部连续补最窄过滤
- 已连续补掉：
  - `performance undertaking / results update + convertible bonds accounting treatment / resumption guidance`
  - `AGM/EGM + transaction`
  - `delay in despatch of circular / extension of proposed completion date`
  - `director share acquisition / supplemental announcement / annual caps`
  - `maintenance work contracts / service framework agreement / leasing and licensing framework agreement`
  - `purchase agreements + sales agreements`
  - `results/management accounts + continued suspension of trading`
  - `voluntary announcement acquisition of assets`
  - `connected transaction + continuing connected transaction + lease agreement`
- 当前最新验证：
  - `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q -k 'hkex_'` -> `13 passed`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment run-once --source hkex` -> 已重刷
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 20` -> `suspicious_count=0`
- 当前头部剩余更像 legit 保留样本：
  - `CONNECTED TRANSACTION - ACQUISITION OF SOFTWARE ASSETS`
  - `CONNECTED TRANSACTION ENTERING INTO THE CAPITAL INCREASE AGREEMENT`
  - `DISCLOSEABLE TRANSACTION: FURTHER INVESTMENT IN PRECIOUS METALS`
- 结论：
  - 当前是 `hkex staged` 一个适合停手的点
  - 下一轮若仍想继续，只在出现新的明显材料族时补最窄规则；不要直接砍剩余交易主标题

## Update 2026-04-22（global multisource mainline）
- 当前主线口径已切换为“全球多源主线”，不再沿用旧的 `phase8-live-boundary` A 股单线验收标准
- 当前 enabled source 可分为 4 层：
  - `A股硬事件`：`cninfo / sse / szse`
  - `A股快讯`：`stcn / cls / irm_cninfo / sse_einteractive`
  - `国内政策监管`：`miit / csrc`
  - `全球政策/市场`：`bis / boj / boc_press / boe / ecb / fed / fedreg_sec / fedreg_ofac / sec_press / cftc_press / investing_* / eia_*`
- 新的主线验收标准：
  - `audit-suspicious = 0` 继续保留
  - 报告头部允许出现全球政策/市场样本
  - 低信号判断重点从“海外/宏观是否出现”改成“是不是模板材料 / 栏目稿 / 进展包”
  - 当剩余样本已是各层里的 legit 主标题时停手
- 推荐方案：
  - 采用 `分层总榜`
  - 层次顺序：
    - `A股强催化`
    - `国内政策与监管`
    - `全球政策与监管`
    - `全球市场与商品`
- 下一步实施顺序：
  1. 先实现 `report` 分层骨架
  2. 再调每层内部排序
  3. 最后才决定是否需要继续补 `text_report` 过滤
- 暂不建议：
  - 先改 `event_merge / analysis`
  - 先改 `configs/sources.yaml` 的 enabled 集合
  - 继续用旧 `phase8` 标准盯着头部继续下刀

## Update 2026-04-22（global multisource mainline report layering）
- 本轮已落地：
  - `text_report` 从单榜混排切到 4 层骨架：
    - `A股强催化`
    - `国内政策与监管`
    - `全球政策与监管`
    - `全球市场与商品`
  - `社交热度观察` 仍保留在主报告所有层之后
- 本轮明确没动：
  - `analysis/scoring`
  - `event_merge`
  - `source enable` 集合
- 当前验证：
  - `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q -k 'groups_entries_into_global_multisource_sections or keeps_social_section_after_mainline_sections'` -> `2 passed`
  - `./.venv/bin/python -m pytest tests/test_report_pipeline.py -q` -> `4 passed`
  - `./.venv/bin/python -m pytest tests/test_cli_smoke.py -q` -> `2 passed`
- 下一步更稳的顺序：
  1. 先看每层内部排序是否需要微调
  2. 再决定是否补层说明或层摘要
  3. 只有层内仍被模板材料占位，才继续补最窄过滤

## Update 2026-04-22（layer ordering + risk subtype fix）
- 本轮已落地：
  - `A股强催化` 层内排序已再微调一轮：
    - 真催化/风险事件优先
    - `irm_cninfo / sse_einteractive` 问答后排
    - 交易所一般材料后排
  - `ST岭南` 两条样本已回正为：
    - `重大诉讼进展` -> `legal_dispute / bearish`
    - `立案通知书` -> `legal_dispute / bearish`
- 当前验证：
  - `./.venv/bin/python -m pytest tests/test_event_merge.py -q -k 'major_litigation_progress_as_legal_dispute or case_filing_notice_as_legal_dispute'` -> `2 passed`
  - `./.venv/bin/python -m pytest tests/test_analysis_scoring.py -q -k 'major_litigation_progress_as_bearish or case_filing_notice_as_bearish'` -> `2 passed`
  - `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q -k 'demotes_investor_qa_and_exchange_material_within_ashare_section or groups_entries_into_global_multisource_sections or keeps_social_section_after_mainline_sections'` -> `3 passed`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
- 下一步更稳的顺序：
  1. 先只读看下一批 live 头部
  2. 若没有新的明显弱样本，优先停手
  3. 只有新样本重新破坏层内观感，才继续补最窄规则

## Update 2026-04-22（social sidecar）
- 本轮新增了最小社交 sidecar 骨架，但明确不改主评分主链路
- 已落地：
  - `SocialSignal` 数据结构
  - `data/social/social_signals.jsonl` 存储
  - `collect-social --platform fixture|weibo`
  - report 底部 `社交热度观察` 区块
- 当前边界：
  - sidecar 只做线索层
  - 不接入 `run-once` / `live-smoke`
  - `fixture` 只用于验证写盘与展示链路
  - `weibo` 当前只保留最小接线；若被访客门/403 挡住，CLI 输出 warning 但不打断主线
- 当前验证：
  - `./.venv/bin/python -m pytest tests/test_social_collectors.py -q` -> `3 passed`
  - `./.venv/bin/python -m pytest tests/test_report_pipeline.py -q` -> `4 passed`
  - `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q -k social_signal_section_without_affecting_main_entries` -> `1 passed`
- 下一步更稳的顺序：
  1. 先完成主报告分层
  2. 再决定社交 sidecar 放在哪一层最合适
  3. 最后才评估是否让社交信号参与排序或权重
- 暂不建议：
  - 把社交热度直接并入 `analysis/scoring`
  - 因 `weibo` 当前 visitor gate 问题就误改主链路
  - 在没有稳定官方/公开入口前声称微博已生产可用

## Update 2026-04-22（A股强催化 live 小补收口）
- 本轮继续沿最新 `A股强催化` 头部做最窄 `text_report` 收口，不改 `event_merge / analysis`
- 本轮新增收口：
  - `irm_cninfo / sse_einteractive` 弱问答：
    - `为什么一直不正式公告披露`
    - `招聘网站上招聘光模块技术人员`
    - `样品送这么久了`
    - `股价异动 + 收购追问`
    - `订单被抢` 谣言核实追问
    - `生态逻辑` 口号式互动留言
  - 交易所/公告材料：
    - `年度股东会会议资料`
    - `监管工作函...评估相关问题的回复`
    - `持续关连交易：养护工程合同`
    - `房屋租赁合同暨关联交易`
    - `续签日常关联交易合同`
    - `申请综合授信 + 订单融资 + 提供担保`
    - `框架协议 + 自愿性披露公告`
    - `增持股份计划`
    - `股权激励预留权益失效`
  - 新确认用户口径：
    - `stcn` 的 `拟...回购股份` 快讯不保留
    - 交易所 `回购股份方案 / 回购公司股份方案 / 回购公司股份的预案` 也不保留
- 当前最新验证：
  - `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q -k 'filters_live_weak_investor_qa_variants_without_hiding_substantive_catalyst or filters_live_exchange_material_variants_without_hiding_substantive_events or filters_investor_qa_and_exchange_material_within_ashare_section'` -> `3 passed`
  - `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q -k 'filters_second_batch_live_investor_qa_variants_without_hiding_substantive_cls_updates or filters_second_batch_live_exchange_material_variants_without_hiding_real_risk'` -> `2 passed`
  - `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q -k 'filters_exchange_buyback_result_purpose_and_plan_materials or filters_weak_acquisition_followup_and_low_signal_increase_plan_and_stcn_buyback_flash'` -> `2 passed`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
  - 手动 `write_text_report()` 后，当前 `A股强催化` 头部只剩：
    - `*ST和科：关于申请撤销对公司股票交易实施退市风险警示的公告`
    - `天孚通信：1.6T光引擎...协调供应商争取更多交付`
    - `永鼎股份：100G EML及硅光高功率芯片具备批量生产能力 启动扩产计划`
- 当前判断：
  - 已重新回到适合停手的点
  - 下一轮先轻验收，不再继续压头部

## Update 2026-04-22（social sidecar fixture 最小验收）
- 本轮没有改 `social-sidecar` 代码，只做最小验收
- 当前最新验证：
  - `./.venv/bin/python -m pytest tests/test_social_collectors.py -q` -> `3 passed`
  - `./.venv/bin/python -m pytest tests/test_report_pipeline.py -q -k 'report_reads_social_signals_sidecar_when_present'` -> `1 passed`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect-social --platform fixture` -> 已真实写盘
  - 手动 `write_text_report()` 后，`latest_report.txt` 已确认包含：
    - `[社交热度观察]`
    - `平台: fixture`
- 当前判断：
  - `fixture` 路径已经够证明 sidecar 写盘和展示链路成立
  - `weibo` 仍只保留最小接线和失败可见，不应当成生产可用
  - 下一轮如果继续 sidecar，更适合补说明或验证失败可见性，不适合直接并入主评分

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
1. 先不要继续改规则，先做轻验收：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
   - `PYTHONPATH=src python3 - <<'PY' ... write_text_report(...) ... PY`
   - `sed -n '1,220p' data/reports/latest_report.txt`
2. 如果 `A股强催化` 仍主要是：
   - `*ST和科`
   - `天孚通信`
   - `永鼎股份`
   则优先停手，不继续补规则
3. 只有新的整族弱样本重新冒头，才继续补最窄 `text_report`
4. 其余旧步骤只作为历史参考
5. 如果下一轮继续主线，先重跑当天主链，不沿用本轮头部判断：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all`
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
6. 下一步第一条命令固定为：
   - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all`
7. 如果当天头部仍主要是：
   - `乌克兰机器人扩单`
   - `WTI跌破86`
   - `世界人形机器人运动会`
   - `退市风险公告`
   则优先停手，不继续过拟合 `text_report`
     - `奥特迅...退市风险警示`
     - `长亮科技中标某股份制银行新网贷服务平台项目`
   - 再判断是否真的还有新的 `irm_cninfo / stcn / cls` 弱样本值得继续收
8. 如果头部仍主要是 legit 保留样本：
   - 先停，不继续压头部
   - 不要为了“更干净”继续过拟合 `text_report`
9. 如果出现新的弱样本：
   - 先补红灯测试
   - 再补最窄 `text_report` 过滤或必要的 `event_merge` 回正
   - 不做大范围题材扩张，也不碰 `hkex staged`
10. 如果主线切回扩源：
   - `hkex` 仍保持 staged
   - 先 `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect --source hkex`
   - 再顺序跑：
     - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment normalize`
     - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment merge-events`
     - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment analyze-events`
     - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment report`
     - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
11. `hkex` 下一步不要直接扩过滤面，优先补：
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
## Update 2026-04-23 (latest)
- 主线仍是 `phase8-live-boundary`，这轮继续只按 live report 头部做最窄收口，不扩题材库，不改 `source enable`
- 本轮已完成：
  - `cninfo` 并购重组材料：`报告书（修订稿）`、`审核问询函回复`
  - 融资授权/简易程序定增材料收口，并回正相关误分类
  - `sse_einteractive / irm_cninfo` 弱回复、审批占位回复、资产注入/重组模板回复、股价抱怨型问答收口
  - 交易所治理/制度/附件材料扩充过滤
  - `股权激励计划相关事项的核查意见`
  - `cls` 的 `今日投资舆情热点`
- 本轮验证口径：
  - 当前 Windows 会话里未直接复用 worktree `.venv`
  - 改用 `py_compile + 直接 Python 断言 + report/audit 实跑`
  - 最新 `audit-suspicious --limit 10` 仍为 `0`
- 当前停点判断：
  - 这一批最明显的材料/栏目型漏出基本已经收干净
  - 继续向下压的收益明显下降，过拟合风险上升
- Immediate Next Steps:
  1. 先只读复核当前 `latest_report.txt` 头部，不先改规则
  2. 第一优先检查：`艾迪药业关于公司收购控股子公司少数股东股权进展的公告`
  3. 判断标准：
     - 如果它只是新的一族“低信号并购进展/材料型公告”，先补红灯测试，再补最窄规则
     - 如果它更像应保留催化，就停手，不继续为了头部更干净过拟合
  4. `乐普 DBS` 当前先留；只有复核后确认回复完全落回模板口径，才考虑下一轮
  5. `cftc_press:fetch_error` 仍单独挂起，不与主线 report 过滤混做
