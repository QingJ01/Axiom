---
description: 手动触发进化（入口）
---

你将执行仓库内置的 `/evolve` 工作流。

步骤：
1) 读取工作流定义：`.agent/workflows/evolve.md`。
2) 按 Steps 执行；涉及文件读写使用 `read_file`/`apply_patch`。
3) 输出最终 Evolution Report（可简化为摘要 + 关键变化）。
