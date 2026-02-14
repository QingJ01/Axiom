---
id: k-001
title: Global Configuration Pattern (全局配置模式)
category: architecture
tags: [config, axiom, gemini]
created: 2026-02-08
confidence: 0.9
references: [evolution-engine-v1]
---

## Summary
为了确保 Agent 在不同项目中行为一致，核心逻辑（路由、门禁、状态机）应存储在用户级全局配置中，而不是项目级配置。

## Details
项目的 `.agent/` 目录定义了项目特有的记忆和技能，但 Agent 的"本能"（如看到 .agent 目录就自动读取 active_context.md）必须由全局配置驱动。

**最佳实践**:
1. 全局配置位置: `~/.gemini/GEMINI.md`
2. 项目内提供模板: `.gemini/GEMINI.md.example`
3. README 中明确说明配置步骤

## Code Example
```markdown
# GEMINI.md snippet
## 1. 启动协议
当工作目录下存在 `.agent/` 目录时：
1. **读取记忆**: 立即调用 `view_file` 读取 `active_context.md`
```
