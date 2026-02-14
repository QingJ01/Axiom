---
description: 调度 Codex 执行 PRD 任务（入口）
---

你将执行仓库内置的 `codex-dispatch` 工作流。

步骤：
1) 读取工作流定义：`.agent/workflows/codex-dispatch.md`。
2) 按照调度循环执行（定位 PRD → 选择任务 → 构造 Worker Prompt → 启动/监控 → 干预 → 更新 PRD）。
3) 重要：只保留必要事件与摘要，严格执行“上下文压缩”步骤，避免保留完整 JSONL。
4) 任何涉及 `.agent/memory/...` 的路径，改用 `.agent/memory/...`。
