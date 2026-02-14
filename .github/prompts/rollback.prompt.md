---
description: 回滚到上一个 Git checkpoint（入口）
---

你将执行仓库内置的 `/rollback` 工作流。

步骤：
1) 读取工作流定义：`.agent/workflows/rollback.md`。
2) 读取 `.agent/memory/active_context.md` 获取 `last_checkpoint`。
3) 在执行 `git reset --hard` 与 `git clean -fd` 前，必须向用户再次确认。
4) 将工作流中的 PowerShell 片段改为 macOS/zsh 下的命令。
