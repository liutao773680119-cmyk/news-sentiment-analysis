# Progress Log

## Latest Handoff Snapshot (2026-04-29)
- Task-ID:
  - `global-multisource-mainline`
- Task-Name:
  - `live report 头部弱样本收口 + audit 同步 + 提交`
- Files Changed:
  - `progress.md`
  - `task_plan.md`
  - `findings.md`
  - `task_registry.md`
  - `修改记录_会话备忘.md`
  - `避坑记录.md`
  - `src/news_sentiment/cli.py`
  - `src/news_sentiment/reporting/text_report.py`
  - `tests/test_audit_suspicious.py`
  - `tests/test_text_report_sorting.py`
- Completed This Session:
  - 按接手规则先只读复核 `task_plan.md / progress.md / findings.md / README.md` 和 worktree 状态
  - 先看 `data/reports/latest_report.txt`，确认 2026-04-29 report 头部已有新一批弱样本回流，不能直接停手
  - 按红灯测试 -> 最窄规则 -> 验证推进，收掉：
    - `cls`：美股光通信板块开盘普跌、世界银行能源价格预测、`【财联社早知道】我国最大规模科学智能集群...` 匿名拼盘稿
    - `irm_cninfo`：中工国际算电协同出海泛问答
    - `sse/szse/cninfo`：股票期权注销/授予价格调整、减持股份触及比例、董事会风险控制委员会工作细则、股权转让进展及补充协议、累计新增诉讼/仲裁材料
    - `stcn`：擎天租 Pre-A 融资机器人应用交付能力泛稿
  - `audit-suspicious` 同步补齐累计新增诉讼材料与私营机器人融资泛稿豁免，避免 report 和 audit 两套口径漂移
  - 已提交代码修复：
    - `1fe1a12 fix: filter latest live report noise`
- Current Verification:
  - `PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q` -> `232 passed`
  - `PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_audit_suspicious.py -q` -> `24 passed`
  - `PYTHONPATH=src ./.venv/bin/python -m py_compile src/news_sentiment/cli.py src/news_sentiment/reporting/text_report.py tests/test_audit_suspicious.py tests/test_text_report_sorting.py` -> 通过
  - `git diff --check` -> 通过
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` -> `raw_news=2003 normalized_news=2003 events=966 analyses=966 failed_sources=none`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment report` -> 通过
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
  - `latest_report.txt` 目标弱样本搜索 -> 无命中
- Current Report Head After Refresh:
  - 头部主要为退市风险/其他风险警示公告
  - `凯撒旅业：关于全资子公司收购福建省凯撒寰球旅游有限公司股权的进展暨关联交易公告`
  - 当前不建议继续压这些真实风险/并购样本
- Open TODO:
  - 当前适合停手交接，不继续为了更短头部补词
  - 下一轮先只读查看 `latest_report.txt`，确认是否出现新的整族弱样本
  - 如继续收口，必须同步补 `text_report` 和 `audit-suspicious` 的红灯测试
  - 若用户要推远端，再执行 `git status --short`、确认分支和远端后 push
- Risks/Blockers:
  - `urllib3 NotOpenSSLWarning` 仍会出现，但本轮命令退出码均为 0
  - live 样本会随时间滚动；不要复用本轮头部样本直接下规则
  - 继续向下压退市风险公告/真实并购进展，过拟合风险高
- Next First Command:
  - `sed -n '1,180p' data/reports/latest_report.txt`
- Known Avoidances:
  - 不要把 `audit-suspicious=0` 当成 report 头部已干净；必须直接看 report
  - 不要只改 report 过滤而忘记 audit 豁免；两套逻辑要同步
  - 不要继续压当前退市风险/真实并购样本
  - 不要扩题材库或动 `event_merge / analysis / source enable`

## Latest Handoff Snapshot (2026-04-28)
- Task-ID:
  - `global-multisource-mainline`
- Task-Name:
  - `live-smoke 后 report 头部尾噪收口 + 标准交接`
- Files Changed:
  - `progress.md`
  - `task_plan.md`
  - `findings.md`
  - `task_registry.md`
  - `修改记录_会话备忘.md`
  - `避坑记录.md`
  - `src/news_sentiment/reporting/text_report.py`
  - `tests/test_text_report_sorting.py`
- Completed This Session:
  - 按交接先跑 `live-smoke --source all`，没有先扩题材库，也没有动 `event_merge / analysis / source enable`
  - 修复 `.venv` 缺 `requests` 导致 `audit-suspicious` 无法启动的问题；`pyproject.toml` 已声明该依赖，本轮只补齐本地环境
  - 修复 `text_report` 两个边界：
    - A股主题市场异动应压过 A股指数温度新闻，但海外单股主题异动仍应留在 `全球市场与商品`
    - report 时间窗应以已通过市场相关性过滤的事件计算，避免低信号新材料把旧正例全部过期
  - 基于 2026-04-28 live 样本继续按“红灯测试 -> 最窄规则 -> report/audit 验证”收掉：
    - `irm_cninfo` 弱问答：股价落后/并购计划、人形机器人液冷方案但暂未应用、毛利率抱怨和改善计划、减持原因但回复为未减持/按规披露
    - `sse/szse` 年报季材料：董事会决议、会计政策变更、计提减值、募集资金专项报告、ESG 报告、审计委员会履职、回购报告书、出售已回购股份计划、回购注销限制性股票材料
  - 保留当前头部真实/相对更强样本：
    - `中远海能` 全资子公司收购并吸收合并
    - `*ST新研` 撤销退市风险警示申请
    - `*ST西发 / ST长方` 风险警示进展
    - `ST长方` 庭外重组提示
    - `惠天热电` 重大诉讼进展
    - `诚迈科技` 签署合作协议
- Current Verification:
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment live-smoke --source all` -> `raw_news=1473 normalized_news=1473 events=760 analyses=760 failed_sources=miit:fetch_error`
  - `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q` -> `231 passed`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment report` -> 通过
  - `latest_report.txt` 已确认不再包含本轮新增处理样本关键词
  - 上述 CLI 命令仍有 `urllib3 NotOpenSSLWarning`，但退出码为 0
- Current Report Head After Refresh:
  - `中远海能关于全资子公司收购中远海运大连投资有限公司100%股权并实施吸收合并暨关联交易的公告`
  - `*ST新研：关于申请撤销公司股票退市风险警示的公告`
  - `*ST西发：关于资金占用事项被实施其他风险警示的进展公告`
  - `ST长方：关于公司股票交易被实施其他风险警示相关事项的进展公告`
  - `ST长方：关于申请庭外重组的提示性公告`
  - `惠天热电：关于子公司重大诉讼事项进展的公告`
  - `诚迈科技旗下讯天信达与武汉水务环境签署合作协议 基于开源鸿蒙重构智慧水务底座`
- Open TODO:
  - 当前 `audit-suspicious=0` 且 report 头部已回到真实并购/风险/诉讼/合作样本，优先停手，不继续压头部
  - 下一轮第一步先只读查看 `latest_report.txt`，如果没有新的整族弱样本，不补规则
  - 单独排查 `miit:fetch_error`；不要把它混成 report 规则问题
  - 若准备收尾，先跑定向验证后提交当前 8 个文件
- Risks/Blockers:
  - `miit` 当前抓取失败：`failed_sources=miit:fetch_error`
  - Python 3.9.6 的 SSL 后端是 LibreSSL，`urllib3` 会提示 `NotOpenSSLWarning`
  - 继续向下压当前头部收益低，过拟合风险高
- Next First Command:
  - `sed -n '1,160p' data/reports/latest_report.txt`
- Known Avoidances:
  - 不要再按旧 `phase8-live-boundary` A股单线标准验收当前 `--source all`
  - 不要因为 `audit-suspicious=0` 就默认 report 头部无噪音；report 仍要直接看
  - 不要把 `miit:fetch_error` 写成规则失败
  - 不要把所有带题材的 `cls/stcn market_move` 都拉回 A股层；海外单股主题异动仍留 `全球市场与商品`

## Latest Handoff Snapshot (2026-04-27)
- Task-ID:
  - `global-multisource-mainline`
- Task-Name:
  - `live report 头部尾噪收口 + 标准交接 + 推送前整理`
- Files Changed:
  - `progress.md`
  - `task_plan.md`
  - `findings.md`
  - `task_registry.md`
  - `src/news_sentiment/reporting/text_report.py`
  - `tests/test_text_report_sorting.py`
- Completed This Session:
  - 继续按“红灯测试 -> 最窄规则 -> report/audit 验证”只收 report 头部尾噪，不扩题材库，不动 `event_merge / analysis / source enable`
  - 连续补齐并压掉了这几批当前 live 低信号样本：
    - `亚太药业：技术开发合同补充协议暨关联交易`
    - `万润股份：续签业务合作协议暨关联交易`
    - `投资性房地产管理办法 / 房地产业务专项自查报告`
    - `股权激励归属/解除限售相关事项的核查意见`
    - `回购注销限制性股票的减资公告`
    - `购买土地使用权 + 投资合作意向书`
    - `摊薄即期回报风险提示及填补回报措施 + 相关主体承诺`
    - `关联存款风险处置预案`
    - `stcn` 的 `围绕战略合作等交流座谈`
    - `国内商品期市夜盘收盘` 变体
  - 同步补了对应的 `text_report` 回归测试，保护真实并购/收购公告不被误伤
  - 尝试在当前 Windows Python 3.10 环境安装 `pytest`，但安装被代理链路阻塞，未能补跑原样定向测试
- Current Verification:
  - `PYTHONPATH=src python -m news_sentiment report`：通过
  - `PYTHONPATH=src python -m news_sentiment audit-suspicious --limit 10`：`suspicious_count=0`
  - `latest_report.txt` 已确认不再包含本轮新增处理的上述样本
  - `华大基因：关于收购重庆新一产生命科技有限公司100%股权暨关联交易的公告` 仍保留在头部
  - `python -m pip install pytest` / `--trusted-host` / `--isolated`：均失败，错误指向坏掉的 proxy 链路
- Current Report Head After Refresh:
  - `棒杰股份：关于公司股票将被实施退市风险警示和其他风险警示暨停牌的公告`
  - `东北制药：诉讼进展公告`
  - `棕榈股份：关于公司股票被实施其他风险警示暨停复牌公告`
  - `华大基因：关于收购重庆新一产生命科技有限公司100%股权暨关联交易的公告`
  - `透景生命：关于收购控股子公司部分股权暨关联交易的公告`
- Open TODO:
  - 当前 `audit-suspicious=0` 且 report 头部已主要剩真实风险/并购样本，优先停手，不继续过拟合
  - 下一轮如要继续，先只读复核当天 `latest_report.txt`，确认是否又出现新的整族材料公告漏出
  - 若要恢复原样 `pytest` 验证，先解决当前 Windows Python 的代理/网络问题，或提供可用镜像源
- Known Avoidances:
  - 不要再把旧 `phase8-live-boundary` 当当前主线
  - 不要为了“头部更少”继续压真实风险公告或真实并购催化
  - 不要在 `pytest` 安装失败时误判为代码未验证；当前失败点在环境代理，不在代码逻辑

## Latest Handoff Snapshot (2026-04-24)
- Task-ID:
  - `phase8-live-boundary`
- Task-Name:
  - `A股强催化 live 材料公告收口 + 推送前标准交接`
- Files Changed:
  - `progress.md`
  - `task_plan.md`
  - `findings.md`
  - `src/news_sentiment/cli.py`
  - `src/news_sentiment/reporting/text_report.py`
  - `tests/test_audit_suspicious.py`
  - `tests/test_text_report_sorting.py`
  - 以及本 worktree 之前已存在的一批未提交修改
- Completed This Session:
  - 按交接先只读复核项目整体和 `latest_report.txt`，没有先扩题材库
  - 处理并验证 4 条最新低信号材料/进度公告漏出：
    - `*ST美谷：关于担保事项涉及诉讼进展暨银行账户解除冻结的公告`
    - `龙大美食：关于控股股东所持公司1000万股股份被强制执行完成暨解除冻结的公告`
    - `泰达股份：天津泰达资源循环集团股份有限公司关于重大资产出售暨关联交易问询函回复的公告`
    - `东睦股份关于上海证券交易所并购重组审核委员会审核公司发行股份及支付现金购买资产并募集配套资金暨关联交易事项会议安排的公告`
  - 修法保持最窄：
    - `audit-suspicious` 增加风险材料窄豁免：`涉及诉讼进展`、`强制执行完成`
    - 并购/重组材料上下文补 `重大资产出售`
    - 问询材料只在带重组/出售/融资上下文时处理 `问询函回复`
    - report 层补 `会议安排`，用于压并购重组审核会议安排类材料
  - 没有改 `event_merge / analysis / source enable`
- Current Verification:
  - `python -m py_compile src\news_sentiment\cli.py src\news_sentiment\reporting\text_report.py tests\test_audit_suspicious.py tests\test_text_report_sorting.py`：通过
  - `PYTHONPATH=src python -m news_sentiment audit-suspicious --limit 10`：`suspicious_count=0`
  - `PYTHONPATH=src python -m news_sentiment report`：通过
  - 定向搜索 `data/reports/latest_report.txt`：上述 4 条均未出现
  - 等价 Python 断言验证 `*ST美谷` 的 audit/report 行为：通过
  - `live-smoke --source all` 本轮在 Windows 下 240 秒超时，未拿到完整 stdout；但它刷新过部分落盘数据，随后 `audit-suspicious` 已回到 0
- Current Report Head After Refresh:
  - `亚太药业：关于签署《技术开发合同补充协议》暨关联交易的公告`
  - `棒杰股份：关于公司股票将被实施退市风险警示和其他风险警示暨停牌的公告`
  - `万润股份：关于与烟台万海舟化工有限公司续签《业务合作协议》暨关联交易的公告`
  - `东北制药：诉讼进展公告`
  - `棕榈股份：关于公司股票被实施其他风险警示暨停复牌公告`
- Open TODO:
  - 当前 `audit-suspicious=0`，优先停手观察，不要为了头部更少继续过拟合
  - 下一轮如果继续主线，先只读复核当前 report 头部，再判断：
    - `亚太药业 技术开发合同补充协议暨关联交易`
    - `万润股份 续签业务合作协议暨关联交易`
    是否只是新一族低信号合同/关联交易材料
  - 若要处理，继续坚持：红灯测试 -> 最窄词面 -> report/audit 验证
- Known Avoidances:
  - 不要扩题材库
  - 不要先动 `hkex staged`
  - 不要在 `audit-suspicious=0` 时继续为了“更干净”压头部
  - 不要把 `live-smoke` 超时误读为规则失败；需要单独排查具体卡住的真实源

## Latest Handoff Snapshot (2026-04-23)
- Task-ID:
  - `phase8-live-boundary`
- Task-Name:
  - `A股强催化 live 边界收口标准交接`
- Files Changed:
  - `progress.md`
  - `task_plan.md`
  - `findings.md`
  - `src/news_sentiment/reporting/text_report.py`
  - `src/news_sentiment/event_merge/core.py`
  - `src/news_sentiment/cli.py`
  - `tests/test_text_report_sorting.py`
  - `tests/test_event_merge.py`
  - `tests/test_audit_suspicious.py`
- Completed This Session:
  - 继续沿 live report 头部做最窄 `text_report` 收口，没有扩题材库，也没有继续改 `source enable`
  - 已收掉：
    - `cninfo` 并购重组材料：`报告书（修订稿）`、`审核问询函回复`
    - 融资授权/简易程序定增材料
    - `sse_einteractive / irm_cninfo` 模板化弱回复、审批占位回复、资产注入/重组模板回复、股价抱怨型问答
    - 交易所治理/制度/附件材料家族
    - `股权激励计划相关事项的核查意见`
    - `cls` 的 `今日投资舆情热点`
  - 同步补了 `audit-suspicious` 的窄豁免，当前这批样本不再误报
  - 明确保留未继续压：
    - `乐普 DBS`
    - `长光华芯：硅光集成产线预计2026年底通线 光通信订单起量`
    - `乐普 MWM109`
    - `东华软件 DeepSeek/国产芯片适配`
- Current Verification:
  - 当前 Windows 会话未直接复用 worktree `.venv`
  - 改用本机 Python 3.10 做等价验证
  - `py_compile`：通过
  - 直连 Python 断言：通过
  - `PYTHONPATH=src python -m news_sentiment report`：通过
  - `PYTHONPATH=src python -m news_sentiment audit-suspicious --limit 10`：`suspicious_count=0`
  - 已确认 `latest_report.txt` 不再包含：
    - `中芯国际...报告书（修订稿）`
    - `中芯国际...审核问询函回复`
    - `天府文旅...简易程序向特定对象发行股票`
    - `中文在线...股权激励计划相关事项的核查意见`
    - `今日投资舆情热点`
- Open TODO:
  - 下一步先只读复核，不直接补规则
  - 第一优先样本：
    - `艾迪药业关于公司收购控股子公司少数股东股权进展的公告`
  - 只有它被判断为新的一族“低信号并购进展/材料公告”时，才进入：
    - 红灯测试
    - 最窄规则
    - `report/audit` 验证
  - `乐普 DBS` 当前先留，不建议先动
- Risks/Blockers:
  - 继续向下压的主要风险已经变成对当天 live 样本过拟合
  - `pytest` 在当前 Windows 会话下未原样执行，不要把这点误读成“没验证”
  - `cftc_press:fetch_error` 仍是独立采集问题，不要混到本主线
- Next First Command:
  - `Get-Content data/reports/latest_report.txt -TotalCount 40`
- Known Avoidances:
  - 不要先动 `乐普 DBS`
  - 不要一上来扩题材库
  - 不要只因为想让头部更干净就继续压 `report`

## Latest Handoff Snapshot
- Task-ID:
  - `social-sidecar`
- Task-Name:
  - `社交线索层 fixture 最小验收 + 不提交版标准交接`
- Files Changed:
  - `progress.md`
  - `task_plan.md`
  - `findings.md`
  - `task_registry.md`
  - `修改记录_会话备忘.md`
  - `避坑记录.md`
- Completed This Session:
  - 已切到 `social-sidecar` 只读复核当前边界，没有改代码
  - 已完成最小验收：
    - `tests/test_social_collectors.py` -> `3 passed`
    - `tests/test_report_pipeline.py -k report_reads_social_signals_sidecar_when_present` -> `1 passed`
    - `collect-social --platform fixture` 已真实写盘
  - 已确认当前 sidecar 边界仍成立：
    - `fixture` 可用于写盘与展示验收
    - `社交热度观察` 仍显示在主报告层之后
    - 不进入主评分，不接 `run-once / live-smoke`
    - `weibo` 仍只保留最小接线和失败可见性，不能当生产可用
- 当前最新验证：
  - `./.venv/bin/python -m pytest tests/test_social_collectors.py -q` -> `3 passed`
  - `./.venv/bin/python -m pytest tests/test_report_pipeline.py -q -k 'report_reads_social_signals_sidecar_when_present'` -> `1 passed`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect-social --platform fixture` -> 已真实写出 `data/social/social_signals.jsonl`
  - 手动 `write_text_report()` 后，`latest_report.txt` 已确认包含：
    - `[社交热度观察]`
    - `平台: fixture`
- Open TODO:
  - 如果下一轮继续 `social-sidecar`，先明确是走：
    - 只补 README/交接说明
    - 还是继续验证 `weibo` 失败可见性
  - 在没有稳定公开入口前，不建议直接做 `weibo` 生产化
- Risks/Blockers:
  - 当前 `data/social/social_signals.jsonl` 仍是未提交新文件
  - `weibo` 仍受 visitor gate / 403 限制；当前只能证明失败可见，不证明可用
- Next First Command:
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment collect-social --platform fixture`
- Known Avoidances:
  - 不要把 `fixture` 验收通过误写成“社交源生产可用”
  - 不要把 sidecar 顺手并进主评分或主报告排序
- Task-ID:
  - `global-multisource-mainline`
- Task-Name:
  - `全球多源主线 A股强催化 live 小补收口 + 不提交版停手交接`
- Files Changed:
  - `progress.md`
  - `task_plan.md`
  - `findings.md`
  - `task_registry.md`
  - `修改记录_会话备忘.md`
  - `避坑记录.md`
  - `src/news_sentiment/reporting/text_report.py`
  - `tests/test_text_report_sorting.py`
- Completed This Session:
  - 本轮继续只按 `A股强催化` live 头部做最窄 `text_report` 收口，没有改 `event_merge / analysis / source enable`
  - 已连续补掉 3 批弱样本：
    - `irm_cninfo / sse_einteractive` 的追问型弱问答、题材催问、股价异动追问、互动口号式留言
    - `sse / szse / cninfo` 的会议资料、提示性公告、监管工作函评估回复、授信担保、框架协议、自愿披露、增持计划、股权激励预留权益失效
    - `stcn` 的 `拟...回购股份` 快讯
  - 用户本轮进一步确认的新口径：
    - `回购方案 / 回购预案` 也不保留
    - `贵州茅台关于以集中竞价交易方式回购股份方案的公告` 已并入低信号材料过滤
  - 当前手动重写 report 后，`A股强催化` 头部只剩：
    - `*ST和科：关于申请撤销对公司股票交易实施退市风险警示的公告`
    - `天孚通信：1.6T光引擎处于量产状态...协调供应商争取更多交付`
    - `永鼎股份：100G EML及硅光高功率芯片具备批量生产能力 启动扩产计划`
  - 当前判断：
    - 已回到适合停手的点
    - 本轮按用户要求不提交，只做标准交接
- 当前最新验证：
  - `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q -k 'filters_live_weak_investor_qa_variants_without_hiding_substantive_catalyst or filters_live_exchange_material_variants_without_hiding_substantive_events or filters_investor_qa_and_exchange_material_within_ashare_section'` -> `3 passed`
  - `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q -k 'filters_second_batch_live_investor_qa_variants_without_hiding_substantive_cls_updates or filters_second_batch_live_exchange_material_variants_without_hiding_real_risk'` -> `2 passed`
  - `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q -k 'filters_exchange_buyback_result_purpose_and_plan_materials or filters_weak_acquisition_followup_and_low_signal_increase_plan_and_stcn_buyback_flash'` -> `2 passed`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
  - 手动 `write_text_report()` 后，`latest_report.txt` 已确认不再包含：
    - `乖宝宠物：拟1亿元—2亿元回购股份`
    - `贵州茅台关于以集中竞价交易方式回购股份方案的公告`
- Open TODO:
  - 下一轮若继续主线，先只做轻验收，不先改规则：
    - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
    - `PYTHONPATH=src python3 - <<'PY' ... write_text_report(...) ... PY`
    - `sed -n '1,220p' data/reports/latest_report.txt`
  - 只有出现新的整族弱样本重新占位，才继续补最窄 `text_report`
- Risks/Blockers:
  - 当前继续追求“只剩更少标题”的收益已经很低，过拟合风险高
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment report` 在当前环境里不总是稳定反映最新源码；验收时优先手动调用 `write_text_report()`
  - 当前 worktree 仍有未提交代码修改：
    - `src/news_sentiment/reporting/text_report.py`
    - `tests/test_text_report_sorting.py`
- Next First Command:
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10`
- Known Avoidances:
  - 不要再把 `回购方案 / 回购预案 / stcn 拟回购股份快讯` 当应保留样本
  - 不要只跑 `report` 就断言产物已刷新；先搜目标标题或手动调用 `write_text_report()`
  - 不要在当前只剩 `*ST和科 / 天孚通信 / 永鼎股份` 这类样本时继续为了更干净头部过拟合

## Latest Handoff Snapshot
- Task-ID:
  - `global-multisource-mainline`
- Task-Name:
  - `全球多源主线分层后层内排序微调 + 风险公告 subtype 回正`
- Files Changed:
  - `progress.md`
  - `task_plan.md`
  - `findings.md`
  - `task_registry.md`
  - `README.md`
  - `src/news_sentiment/analysis/rules.py`
  - `src/news_sentiment/event_merge/core.py`
  - `src/news_sentiment/reporting/text_report.py`
  - `tests/test_analysis_scoring.py`
  - `tests/test_event_merge.py`
  - `tests/test_text_report_sorting.py`
- Completed This Session:
  - 已确认当前 `--source all` 实际已不是旧的 `phase8-live-boundary` 输入集合，而是“全球多源主线”
  - 已确认当前 enabled source 可分为 4 层：
    - `A股硬事件`：`cninfo / sse / szse`
    - `A股快讯`：`stcn / cls / irm_cninfo / sse_einteractive`
    - `国内政策监管`：`miit / csrc`
    - `全球政策/市场`：`bis / boj / boc_press / boe / ecb / fed / fedreg_sec / fedreg_ofac / sec_press / cftc_press / investing_* / eia_*`
  - 已将主线验收标准从“头部主要是 A 股单票催化”重定标为：
    - `audit-suspicious = 0`
    - 头部允许全球政策/市场样本出现
    - 低信号判断改为识别“模板材料/栏目稿/进展包”，而不是“海外样本一律压掉”
    - 当剩余样本已是各层里的 legit 主标题时停手
  - 已给出推荐方案：`分层总榜`
    - `A股强催化`
    - `国内政策与监管`
    - `全球政策与监管`
    - `全球市场与商品`
  - 已把 report 从单榜混排改成 4 层骨架输出：
    - `A股强催化`
    - `国内政策与监管`
    - `全球政策与监管`
    - `全球市场与商品`
  - 已把 `A股强催化` 层内排序再收一刀：
    - 真催化/风险事件优先于 `irm_cninfo / sse_einteractive` 问答
    - 交易所一般材料继续后排，不再靠高分题材词顶在最前
  - 已将这轮新冒出的 `ST岭南` 两条风险公告回正：
    - `关于重大诉讼的进展公告` -> `legal_dispute / bearish`
    - `关于收到万安县住房和城乡建设局立案通知书的公告` -> `legal_dispute / bearish`
  - 已新增社交 sidecar 最小链路：
    - `SocialSignal` 数据结构
    - `data/social/social_signals.jsonl` 写盘路径
    - `collect-social --platform fixture|weibo`
    - report 底部 `社交热度观察` 区块
  - 已确认当前社交 sidecar 边界：
    - 只做线索层，不进入主评分
    - 不接入 `run-once` / `live-smoke`
    - `weibo` 当前若被访客门/403 挡住，只打清晰 warning，不打断主线脚本
- 当前最新验证：
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 10` -> `suspicious_count=0`
  - 当前 `latest_report.txt` 头部已能稳定出现全球多源样本，不再适合按旧 `phase8` 标准验收
  - `./.venv/bin/python -m pytest tests/test_event_merge.py -q -k 'major_litigation_progress_as_legal_dispute or case_filing_notice_as_legal_dispute'` -> `2 passed`
  - `./.venv/bin/python -m pytest tests/test_analysis_scoring.py -q -k 'major_litigation_progress_as_bearish or case_filing_notice_as_bearish'` -> `2 passed`
  - `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q -k 'demotes_investor_qa_and_exchange_material_within_ashare_section or groups_entries_into_global_multisource_sections or keeps_social_section_after_mainline_sections'` -> `3 passed`
- Open TODO:
  - 下一轮先只读看新的 live 头部，不急着继续改规则：
    - 先跑 `run-once --source all`
    - 再看有没有新的弱问答/材料重新冒头
    - 如果头部仍主要是当前这些样本，优先停手
  - 社交 sidecar 下一步更适合做：
    - 明确平台接入顺序和数据源可用性
    - 继续停留在线索层，不要提前并到主评分
  - 暂不建议先动：
    - `event_merge / analysis`
    - `configs/sources.yaml` 的 enabled 集合
  - 实现前先补最小设计/计划落盘，避免下一轮又按旧 `phase8` 继续压头部
- Risks/Blockers:
  - 如果继续沿旧 `phase8-live-boundary` 口径验收，会把全球多源主线误判成“头部失真”
  - 当前再继续下刀的主要风险已经从“单榜失配”变成“对当天 live 过拟合”
  - `weibo` 当前真实抓取仍受访客门/403 限制，现阶段不能把“能写 fixture sidecar”误判成“微博生产可用”
- Next First Command:
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment run-once --source all`
- Known Avoidances:
  - 不要再把当前主线按旧 `phase8-live-boundary` 的 A 股单线标准验收
  - 不要先改 source 开关来“修头部”；当前接受的是全球多源主线
  - 不要在当前 `audit-suspicious=0` 的状态下继续为了更干净头部过拟合

## Update 2026-04-22（hkex staged）
- 主线仍是 `phase9-source-expansion` 的 `hkex staged` 收口，`hkex` 仍未启用到 `--source all`
- 本轮继续沿 `run-once --source hkex` 的头部做最窄过滤，累计补了 13 条 `hkex` 回归测试
- 本轮新增收口：
  - `results / management accounts + continued suspension of trading`
  - `voluntary announcement acquisition of assets`
  - `connected transaction + continuing connected transaction + lease agreement`
- 经过多轮重刷后，当前 `latest_report.txt` 头部里更像应保留的剩余项主要是：
  - `CONNECTED TRANSACTION - ACQUISITION OF SOFTWARE ASSETS`
  - `CONNECTED TRANSACTION ENTERING INTO THE CAPITAL INCREASE AGREEMENT`
  - `DISCLOSEABLE TRANSACTION: FURTHER INVESTMENT IN PRECIOUS METALS`
- 当前验证：
  - `./.venv/bin/python -m pytest tests/test_text_report_sorting.py -q -k 'hkex_'` -> `13 passed`
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment run-once --source hkex` -> 已重刷
  - `PYTHONPATH=src ./.venv/bin/python -m news_sentiment audit-suspicious --limit 20` -> `suspicious_count=0`
- 结论：
  - 当前再次回到适合停手的点
  - 下一轮如果头部仍主要是上述 3 类交易主标题，不继续为了更干净过拟合

## Update 2026-04-22（global multisource mainline）
- 当前主线判断已从旧的 `phase8-live-boundary` 切换为“全球多源主线”
- 当前 enabled source 已经不是 A 股单线集合，而是 4 层混合输入：
  - `A股硬事件`
  - `A股快讯`
  - `国内政策监管`
  - `全球政策/市场`
- 当前更稳的结论：
  - 主线问题已经从“继续过滤弱样本”切到“报告展示与验收标准重定标”
  - 现在最该做的是报告分层，而不是继续压头部
- 推荐目标：
  - 保留一个总报告
  - 改成分层总榜，而不是单榜混排
  - 先做展示分层，再决定是否需要继续补规则

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
