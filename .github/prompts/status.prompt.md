---
description: 显示系统仪表盘（入口）
---

你将执行仓库内置的 `/status` 工作流。

步骤：
1) 读取工作流定义：`.agent/workflows/status.md`。
2) 按照工作流的 Steps 执行。
3) 任何涉及 `.agent/memory/...` 的路径，改用 `.agent/memory/...`。
4) 输出时遵循工作流的 Output Format，但避免输出大段原始日志，只保留摘要。
