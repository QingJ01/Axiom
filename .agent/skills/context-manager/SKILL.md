---
name: context-manager
description: Axiom 记忆系统。负责读写短期记忆、长期记忆及用户偏好，并维护任务队列状态。
---

# Context Manager Skill (v2.0)

本技能通过文件系统 (`.agent/memory/`) 实现 Agent 的外部记忆和状态管理。

## 核心操作

### 1. `read_context` (启动/唤醒)
> 读取当前活跃上下文，恢复现场。
- **Action**: 读取 `.agent/memory/active_context.md`。
- **Output**: 
    - "Context loaded. Last session ended at [Task-X]."
    - If `Task Queue` has PENDING items: "检测到未完成的任务，是否继续？"

### 2. `update_progress` (进度更新)
> 任务每推进一步，都要记录。
- **Input**: `task_id`, `status` (PENDING/DONE/BLOCKED), `summary`.
- **Action**: 修改 `active_context.md` 中的 `Task Queue`。
- **Archive Trigger**: 若所有任务完成，将详情追加到 `history/task_archive_YYYYMM.md`。

### 3. `save_decision` (长期记忆)
> 记录关键技术决策。
- **Input**: `decision_type` (Architecture/Lib/Rule), `content`.
- **Action**: 追加到 `.agent/memory/project_decisions.md`。
- **Check**: 如果与现有决策冲突，需标记旧决策为 `[Deprecated]` 并移动到 `## 6. Deprecated`。

### 4. `update_state` (状态机更新) [NEW]
> 更新 Agent 的状态机状态。
- **Input**: `new_state` (IDLE/PLANNING/CONFIRMING/EXECUTING/AUTO_FIX/BLOCKED/ARCHIVING).
- **Action**: 
  1. 验证状态转换是否合法（参考 `state_machine.md`）。
  2. 更新 `active_context.md` 的 frontmatter 中的 `task_status`。
- **Output**: "State: [OLD] → [NEW]"

### 5. `create_checkpoint` (创建检查点) [NEW]
> 在关键节点创建 Git 检查点。
- **Action**: 
  1. 执行 `git tag checkpoint-YYYYMMDD-HHMMSS`
  2. 更新 `active_context.md` 中的 `last_checkpoint`
- **Output**: "✓ Checkpoint: checkpoint-20260208-010800"

### 6. `record_error` (记录错误) [NEW]
> 将错误模式写入长期记忆。
- **Input**: `error_type`, `root_cause`, `fix_solution`, `scope`.
- **Action**: 追加到 `project_decisions.md` 的 `## 5. Known Issues`。
- **Format**: `| 日期 | 错误类型 | 根因分析 | 修复方案 | 影响范围 |`

### 7. `archive_task` (归档任务) [NEW]
> 将已完成的任务归档到历史记录。
- **Input**: `task_id`, `summary`, `commit_hash`.
- **Action**: 
  1. 追加到 `history/task_archive_YYYYMM.md`
  2. 在 `active_context.md` 的 `History` 中添加摘要链接
  3. 清空任务的详细计划
- **Format**: 
  ```markdown
  ## Task-001: [Summary]
  - **Completed**: 2026-02-08 01:08
  - **Commit**: abc123
  - **Files Changed**: [list]
  ```

## 文件结构规范
- Context file: `.agent/memory/active_context.md`
- State Machine: `.agent/memory/state_machine.md`
- Decisions file: `.agent/memory/project_decisions.md`
- Preferences file: `.agent/memory/user_preferences.md`
- History folder: `.agent/memory/history/`

## 状态验证规则
调用 `update_state` 时，必须检查转换是否合法：
```
IDLE → PLANNING ✓
PLANNING → CONFIRMING ✓
CONFIRMING → EXECUTING ✓
AUTO_FIX → EXECUTING ✓ (修复成功)
AUTO_FIX → BLOCKED ✓ (3次失败)
...
EXECUTING → IDLE ✗ (非法，必须经过 ARCHIVING)
```
