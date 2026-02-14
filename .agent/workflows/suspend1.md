---
description: Session Suspend - 会话收尾，保存状态，生成总结
---

# Suspend Workflow (收尾工作流)
当用户说 "暂停" / "休息" / "保存" / "suspend" 或主动结束会话时触发。
用于**主动保存当前状态**，确保下次会话能够无缝接力。
## Phase 1: 状态快照 (State Snapshot)
1. **获取当前时间**: 记录会话结束时间
2. **收集进度信息**:
   - 当前正在执行的 Task ID
   - Task Queue 中的 PENDING / DONE / BLOCKED 统计
   - Scratchpad 中的临时笔记
## Phase 2: 更新记忆文件 (Memory Update)
// turbo (自动执行记忆更新)
3. **更新 active_context.md**:
   ```yaml
   ---
   session_id: "[当前会话ID]"
   task_status: IDLE  # 或保持 EXECUTING 如果任务未完成
   auto_fix_attempts: 0
   last_checkpoint: "[最近的 checkpoint tag]"
   last_session_end: "2026-02-08 01:30"
   ---
   ```

4. **写入位置**:
   - 文件路径: `.agent/memory/active_context.md`
   - 使用 Copilot 工具 `apply_patch` 更新 YAML frontmatter 与必要的 Scratchpad

## Phase 3: 会话总结 (Summary)
5. **生成简短总结**:
   - 本次会话做了什么（1-3 句）
   - 当前阻塞点（如有）
   - 下一步最优先的 1-3 个动作

## Phase 4: 输出
6. 输出一段可直接复制到下次会话的“接力摘要”，格式：
   ```markdown
   ## 🔁 接力摘要
   - 当前任务: {T-xxx / 无}
   - 状态: {IDLE/EXECUTING/BLOCKED}
   - 最近检查点: {checkpoint-tag / 无}
   - 阻塞: {无 / 一句话}
   - 下一步: 1) ... 2) ...
   ```