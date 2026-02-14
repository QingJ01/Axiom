---
description: Phase 3: 实施交付流程
---

你将执行 Axiom v4.2 的 Phase 3 实施工作流。

**目标**: 基于 Manifest 并行执行开发任务，通过编译门禁，并生成交付报告。

**步骤**:
1) 读取工作流定义: `.agent/workflows/4-implementing.md`。
2) 执行 **DAG Analysis & Dispatch** (并行最多 3 任务)。
3) 微循环开发 (Design -> Code -> Test -> Review)。
4) 执行 **Compilation Gate** (构建检查)。
5) 生成交付报告并通知用户。

**注意**:
- 每个任务必须包含单元测试。
- 遇到编译失败触发 Auto-Fix。
