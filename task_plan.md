# Task Plan: 新闻源与开源项目调研

## Goal
梳理适用于 A 股超短情绪交易的实时新闻与社交信号来源，并调研 GitHub 上可复用的相似开源项目，为后续系统设计提供输入。

## Current Phase
Phase 5

## Phases

### Phase 1: Requirements & Discovery
- [x] Understand user intent
- [x] Identify constraints and requirements
- [x] Document findings in findings.md
- **Status:** complete

### Phase 2: Source Research
- [x] Research official/news/social/disclosure data sources
- [x] Classify sources by timeliness, market relevance, and accessibility
- [x] Document source coverage and gaps
- **Status:** complete

### Phase 3: GitHub Survey
- [x] Search similar open-source projects
- [x] Group projects by capability and maturity
- [x] Document reuse opportunities and limitations
- **Status:** complete

### Phase 4: Synthesis
- [x] Propose a practical source stack for phase 1
- [x] Translate research into architecture implications
- [x] Prepare next brainstorming question
- **Status:** complete

### Phase 5: Delivery
- [x] Review output files
- [x] Summarize research for user
- [x] Deliver links, analysis, and recommendations
- **Status:** complete

## Key Questions
1. 哪些实时来源最适合捕捉 A 股盘中到次日的题材炒作？
2. 哪些来源有公开入口，哪些需要爬虫、订阅或第三方数据接口？
3. 开源项目能复用到哪一层，是“抓新闻”，还是“事件到交易信号”？

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 先做外部调研，再继续头脑风暴细化系统 | 用户明确要求先搜索并总结来源和同类项目 |
| 调研范围覆盖国内外新闻、官方披露、社交媒体与专家账号 | 用户希望范围广，且超短情绪交易依赖多源异步触发 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| `python` command not found | 1 | Switched to `python3` |
| `python3 -m pytest` failed because `pytest` is missing | 1 | Logged as environment gap; no install performed yet |
| GitHub search connector rejected `topn` as string | 1 | Retry with integer parameter |
| GitHub file fetch timed out / transport failed | 1 | Fall back to repository search results and public metadata |

## Notes
- Update findings after every two search/browse actions.
- Favor official product pages, docs, or maintainer repositories when verifying current availability.
