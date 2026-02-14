---
description: R&D Implementation Workflow - 研发交付流水线 (Manifest 驱动)
---

# R&D Implementation Workflow

> 本工作流承接 PRD 拆解阶段，基于 `manifest.md` 驱动并行开发与交付。

## 1. 启动准备
- **Trigger**: 用户确认 `docs/tasks/{TaskID}/summary.md`，或直接调用 `/feature-flow`。
- **Input**: `docs/tasks/{TaskID}/manifest.md`。

## 2. 任务调度循环 (The Loop)
系统将反复执行以下步骤，直到 Manifest 中所有任务标记为 `[x]`。

### 2.1 DAG 分析与分发
- **[系统指令]**: 读取 `manifest.md`。
- **[系统指令]**: 识别所有状态为 `[ ]` 且前置依赖已满足 (`[x]`) 的任务集合。
- **[系统指令]**:
  - 如果集合为空但仍有未完成任务 -> 报错 "Deadlock detected" (循环依赖)。
  - 如果集合为空且无未完成任务 -> 跳转 [3. 交付验收]。
  - 如果集合不为空 -> **并行启动** Codex Worker (Max 3)。

### 2.2 执行单元 (Execution Unit)
对每个分发的任务 (e.g., T-101)，执行以下 Prompt：

```bash
# 1. Generate Unique Prompt File
# File: .agent/prompts/TASK_{SubTaskID}_{TIMESTAMP}.md
# Content: (See codex-dispatch.md for template)

# 2. Execute via File Injection (Safe Pattern)
codex exec --json --dangerously-bypass-approvals-and-sandbox "Execute task defined in .agent/prompts/TASK_{SubTaskID}_{TIMESTAMP}.md"
```

> **Note**: For the full implementation logic (monitoring, turn-based resume, manifest closure), refer to `codex-dispatch.md`.


### 2.3 状态同步
- **[系统指令]**: 轮询 Worker 状态。
- **[系统指令]**: 
  - 成功 -> 在 `manifest.md` 中将对应任务打钩 `[x]`。
  - 失败 -> 记录错误日志，暂停该分支，请求人工介入。

## 3. 交付验收 (Final Gate)
- **Action**: 运行全量集成测试/回归测试。
- **Checklist**:
  - [ ] 所有 Unit Tests 通过。
  - [ ] Integration Tests 通过。
  - [ ] Manifest 100% 完成。
- **Output**: 提示用户 "Feature {TaskID} Ready for Release".
