---
description: 会话收尾与接力摘要（入口）
---

你将执行仓库内置的 `suspend` 工作流。

步骤：
1) 读取工作流定义：`.agent/workflows/suspend1.md`。
2) 更新 `.agent/memory/active_context.md` 的关键信息（状态、checkpoint、scratchpad）。
3) 输出“接力摘要”，用于下次会话快速恢复。
