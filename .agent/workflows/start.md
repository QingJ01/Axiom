---
description: Zero-Touch Boot - 零触感启动，自动接力任务
---

# Start Workflow (Silent Boot)

Agent 开窗后的第一反应，用于偷偷读取上下文。

1. **读取上下文**（Copilot 环境用 `read_file`）
   - **Check**: Look for PENDING tasks in `.agent/memory/active_context.md`.
2. **Decision Point**:
   - **IF PENDING**: Output "Detected unfinished task [Task-ID]. Resume?"
   - **IF IDLE**: Output "System ready. What's next?"
3. **Environment Check**:
   - **Run**: `flutter doctor` (若当前项目是 Flutter；仅在异常时提示)。
