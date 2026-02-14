---
description: 兼容入口 - 开发交付流水线
---

# /feature-flow - Compatibility Entry

## Purpose
- 为历史命令 `/feature-flow` 保留兼容入口。
- 实际执行流程迁移到 `.agent/workflows/4-implementing.md`。

## Steps
1. 读取 `.agent/workflows/4-implementing.md`。
2. 严格按该流程执行开发与交付。

## Notes
- 新项目建议直接使用 `/implement` 或 Manifest 驱动入口。
