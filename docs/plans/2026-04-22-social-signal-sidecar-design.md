# 社交源线索层最小设计

## 目标
在不污染当前“全球多源主线”主评分链路的前提下，引入社交平台热度信号，作为事件的辅助线索层。

本设计只解决 3 件事：
- 哪些社交源值得先接
- 社交数据如何落盘
- 社交热度如何展示但不进入主评分

本设计不做：
- 社交帖子内容理解
- 社交源直接参与 `impact_score`
- 社交源直接改写 `triggered`
- 社交源和公告/快讯的自动强绑定排序

## 边界

### 放在哪一层
- 放在线索层，不放在主信号层。
- 线索层职责：
  - 发现某事件是否在社交平台快速升温
  - 辅助判断题材是否正在被共同讨论
  - 给人工阅读提供“热度确认”
- 主信号层职责不变：
  - 仍以交易所公告、监管源、政策源、新闻快讯为主
  - `impact_score / triggered / direction` 继续只由现有主链决定

### 为什么不能直接进主信号层
- 社交平台噪音高，真假混杂。
- 热度和交易价值不是同一个量。
- 讨论量上升，可能只是争议、谣言、情绪宣泄，不等于有效催化。
- 当前系统还没有谣言过滤、账号分层、可信度建模，直接并入主评分风险太大。

## 平台优先级

### 第一优先
- `微博`
  - 国内政策、题材热词、行业事件、板块讨论扩散最快
  - 对当前主线贴合度最高

### 第二优先
- `X / Twitter`
  - 海外政策、商品、科技链、地缘事件扩散快
  - 对“全球多源主线”有天然补强

### 暂缓
- `Reddit`
  - 适合海外科技/散户情绪，但与当前主线贴合度低于微博和 X
- `知乎`
  - 长文讨论多，盘中时效弱
- `小红书 / Telegram / Discord / YouTube`
  - 内容噪音、结构化程度、风控难度都不适合当前阶段

## 最小数据结构

不修改现有 `Event / EventAnalysis` 主模型，先单独落一份 sidecar 数据。

建议新增：
- 文件：
  - `data/social/social_signals.jsonl`
- 记录结构：

```python
@dataclass(frozen=True)
class SocialSignal:
    event_id: str
    platform: str
    captured_at: str
    heat_score: float
    heat_delta: float
    co_mentioned_themes: list[str]
    sample_posts: list[str]
```

字段解释：
- `event_id`
  - 已有事件 ID。社交层只挂靠到现有事件，不自建主事件流。
- `platform`
  - 如 `weibo`、`x`
- `captured_at`
  - 当前抓取时间
- `heat_score`
  - 当前热度分
- `heat_delta`
  - 相比上一轮的升温幅度
- `co_mentioned_themes`
  - 和该事件一同被讨论的题材词
- `sample_posts`
  - 少量样本文本或标题，供人工核对

## 采集接口

建议新增一个 sidecar collector 接口，不复用当前主 collector 输出。

```python
def collect_social_signals() -> list[SocialSignal]:
    ...
```

### 设计要求
- 不返回 `RawNews`
- 不参与 `normalize -> merge-events -> analyze-events` 主链
- 允许失败，不阻断主链运行
- 允许单平台缺失

## 事件挂接方式

第一版不做复杂 embedding 或全文相似度匹配，先用最保守方式：

1. 只对已经进入主报告的事件做社交查询
2. 用 `canonical_title`、核心实体词、主题词做检索
3. 只生成 sidecar 热度，不反向创建新事件

这样做的好处：
- 不会引入第二套事件归并
- 不会把社交噪音反推回主事件流
- 易于失败隔离

## 报告展示

不改主榜排序，先在报告底部或单独章节加一个新块：

### 社交热度观察
- 只展示当前主报告中的事件里，哪些在社交平台升温
- 每条展示：
  - 标题
  - 平台
  - 热度分
  - 升温幅度
  - 共现题材

建议形态：

```text
[社交热度观察]
- 吉利将于2026北京车展发布中国首台原生Robotaxi原型车
  平台: 微博, X
  热度: 82
  增速: +18
  共现题材: Robotaxi, 智能驾驶
```

### 为什么不直接插回主榜
- 会把“热”误当成“强催化”
- 会把不同性质的信号混成一个排序
- 当前更需要的是辅助确认，而不是主排序重写

## 最小实现顺序

1. 新增 `SocialSignal` sidecar 数据模型
2. 新增 `data/social/social_signals.jsonl` 路径
3. 新增独立 social collector 接口
4. 先接 `微博`
5. 再接 `X`
6. 在 `text_report` 里加 `社交热度观察` 区块
7. 等 sidecar 稳定后，再评估是否允许对排序做很小的加权

## 验收标准

第一版验收不看“能不能改变主排名”，只看这 4 条：
- 主链输出不被社交源污染
- 社交源失败不阻断主链
- `social_signals.jsonl` 能稳定生成
- `latest_report.txt` 能稳定展示 `社交热度观察`

## 当前结论
- 社交源值得接，但只应该先进线索层。
- 第一优先是 `微博`，第二优先是 `X`。
- 当前最稳的路径不是“把社交源并进主评分”，而是先做一个 sidecar 热度层。
