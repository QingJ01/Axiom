---
description: 报错分析与修复（入口）
---

你将执行仓库内置的 `analyze-error` 工作流。

步骤：
1) 读取工作流定义：`.agent/workflows/analyze-error.md`。
2) 优先收集本地日志与 git diff；不要默认上网。
3) 给出 1-3 个修复方案；高置信度才自动改代码。
