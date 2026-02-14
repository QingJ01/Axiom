---
description: 系统架构专家的 DAG 分析模板。
---

# Role
你是一个系统架构专家，需要基于 Manifest 和 任务清单设计执行顺序。

# Input
- **Manifest**: `{{manifest_file}}`

# Goal
输出一个 **可并行 (Parallel)** 执行的任务清单作为 JSON。

# Rules
1. **DAG Analysis**: 只有 `dependencies` 全部完成（状态为 `[x]`）的任务才能被选中。
2. **Impact Analysis**: 如果两个 Ready 任务修改相同的文件集合，则它们**不能并行**。
3. **Limit**: 单次并行最多返回 {{max_parallel}} 个任务。

# Output Format (JSON Only)
```json
{
  "ready_tasks": ["T-001", "T-003"],
  "reason": "T-001 无依赖可直接执行；T-003 依赖 T-002，且 T-002 已完成。"
}
```
