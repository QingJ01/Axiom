---
id: k-004
title: Context Completeness Pattern (上下文完整性模式)
category: architecture
tags: [memory, context, best-practice]
created: 2026-02-08
confidence: 0.95
references: []
---

## Summary
在 `active_context.md` 的 **Current Goal** 中，必须包含所有执行任务所需的**关键参数**（如文件路径、API Key、配置项），而不仅仅是任务描述。

## Problem (问题)
用户在会话 A 中说 "处理某个目录下的项目"。  
Agent 在会话 A 的上下文中记住了路径，但只在 `active_context.md` 中写了 "处理项目"。  
当用户在会话 B 说 "继续" 时，新 Agent 读取记忆后不知道源项目的具体路径。

## Root Cause (根因)
**隐式依赖**: 关键信息（路径）只存在于会话上下文（短期记忆），未持久化到 `active_context.md`（长期记忆）。

## Solution (解决方案)
在 `Current Goal` 中使用结构化格式明确记录所有关键参数：

```markdown
## 1. Current Goal
> [任务描述]

**Source**: [源路径/源数据]  
**Target**: [目标路径/目标状态]  
**Key Params**: [其他关键参数]  
**Strategy**: [执行策略]
```

## Code Example
```markdown
## 1. Current Goal
> **Feature Implementation**: 实现用户认证模块

**Source**: `/path/to/project`  
**Target**: 完整的登录注册功能  
**Key Params**: API Endpoint = `https://api.example.com`  
**Strategy**: 使用 prd-crafter-pro 多角色协作
```

## Related Knowledge
- k-001: Global Configuration Pattern
- k-002: Evolution Engine Architecture
