---
description: Phase 2: 任务拆解流程
---

你将执行 Axiom v4.2 的 Phase 2 拆解工作流。

**目标**: 将 Rough PRD 转化为 Manifest 和详细的 Sub-PRDs。

**步骤**:
1) 读取工作流定义: `.agent/workflows/3-decomposing.md`。
2) 执行工期评估门禁。
3) 运行 `system-architect` 生成 Manifest (包含 DAG)。
4) 串行生成 Sub-PRDs。
5) 执行 PM Audit (一致性检查)。
6) 请求用户确认以进入 Phase 3。

**注意**:
- Manifest 必须包含完整的依赖关系。
- Sub-PRDs 必须自洽且与 Rough PRD 对齐。
