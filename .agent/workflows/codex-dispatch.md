---
description: 兼容入口 - Codex 调度工作流
---

# /codex-dispatch - Compatibility Entry

## Purpose
- 为历史命令 `/codex-dispatch` 保留兼容入口。
- 当前建议流程参考 `.agent/workflows/4-implementing.md` 与相关 manifest。

## Steps
1. 按任务清单读取 Manifest。
2. 使用当前实现流程执行并回写状态。

## Notes
- 如需旧版实现细节，可参考 `_archive/codex-dispatch.md`。
