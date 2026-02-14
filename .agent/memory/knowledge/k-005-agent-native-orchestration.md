---
id: k-005
title: Agent Native Orchestration (纯 Agent 编排)
category: architecture
tags: [architecture, orchestration, anti-pattern]
created: 2026-02-09
confidence: 0.9
references: [user-feedback]
---

# Agent Native Orchestration

## 核心理念
**Agent Native** 指的是系统的核心逻辑流转完全由 Agent 的思考过程（Thought Process）驱动，而不是被封装在一个黑盒脚本（Script）中。

## Anti-Pattern (反模式): Script Orchestration
- **定义**: 使用 Shell/Python 脚本来控制任务循环（如 `while true` 循环派发）。
- **优点**: 高效、低成本、无需 Agent 持续介入。
- **缺点**:
  - **丧失控制权**: 一旦脚本启动，Master Agent 沦为旁观者。
  - **不透明**: 用户无法在运行时干预或微调。
  - **上下文断裂**: 脚本无法像 Agent 那样灵活处理突发状况。

## Best Practice (最佳实践): Pure Agent Loop
- **定义**: 每一个任务的分发都由 Agent 的一次 Tool Call 显式触发。
- **实现方式**:
  1. **Master Agent** 读取状态。
  2. **Master Agent** 决定下一个动作。
  3. **Master Agent** 调用 Worker。
  4. **Master Agent** 观察结果。
  5. 重复上述过程。
- **代价**: 更高的 Token 消耗和延迟。
- **收益**: 极致的灵活性和控制力。符合 "Human-in-the-Loop" 的高级形态。

## 废弃组件
以下组件已废弃，仅保留供参考：
- `.agent/skills/task-dispatcher/scripts/dispatch_task.sh` → 已被 Agent 原生调度替代
- `codex_dispatcher/parser.py` → 硬编码解析，可选使用但非必需

## 当前实现
- **codex-dispatch.md v3.0**: Agent 原生调度 workflow
- **feature-flow.md v3.0**: 整合 Pre-Flight 检查的完整交付流水线

## 决策记录
- **2026-02-09**: 用户拒绝使用 `dispatch_task.sh`，要求回归纯 Agent 编排。
- **2026-02-09 17:40**: 完成 v3.0 实施，codex-dispatch.md 和 feature-flow.md 重写为 Agent 原生版本。
