---
description: 执行 Feature Flow（入口）
---

你将执行仓库内置的 `feature-flow` 工作流。

步骤：
1) 读取工作流定义：`.agent/workflows/feature-flow.md`。
2) 按 Phase 顺序执行。
3) 所有命令在 macOS/zsh 下运行，必要时将 PowerShell 改写为等价的 zsh 命令。
4) 任何涉及 `.agent/memory/...` 的路径，改用 `.agent/memory/...`。
5) 过程中避免把 Codex JSONL 全量灌入上下文：只记录每个任务的一行摘要（参考 `codex-dispatch` 的“上下文压缩”规则）。
