---
description: Phase 1.5: 专家评审流程
---

你将执行 Axiom v4.2 的 Phase 1.5 评审工作流。

**目标**: 通过 5 位专家角色并行评审 Draft PRD，并由 Review Aggregator 汇总为 Rough PRD。

**步骤**:
1) 读取工作流定义: `.agent/workflows/2-reviewing.md`。
2) 并行运行 5 个 Expert Role (`ux_director`, `product_director`, `domain_expert`, `tech_lead`, `critic`)。
3) 运行 `review-aggregator` 技能生成 Rough PRD。
4) 同步到飞书文档 (如有集成)。
5) 请求用户确认以进入 Phase 2。

**注意**:
- 评审意见必须基于 facts 和 logic。
- 汇总时必须遵循优先级：Safety > Tech > Strategy > Logic > UX。
