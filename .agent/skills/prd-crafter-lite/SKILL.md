---
name: prd-crafter-lite
description: 纯净版工程级 PRD 专家 (v4.0)。专注于生成高质量文档，内置需求澄清门禁和架构合规检查。
---

# PRD Crafter Lite (The Thinker)

本技能只负责**思考**和**规划**，不负责执行代码。它是 `feature-flow` 工作流的第一步。

## 0. Gatekeeper (需求澄清门禁)
> **Mandatory check before generation.**

- **Trigger**: 用户提出新需求。
- **Action**: 
  1. 读取 `.agent/memory/project_decisions.md` (架构约束).
  2. 检查用户需求是否模糊 (Missing Data Source / Unclear UI / Conflict with Decision).
  3. **IF Ambiguous**: 拒绝生成 PRD，输出澄清问题列表。
  4. **IF Clear**: Proceed to Generation.

## 1. Context-Aware Generation
- **读取记忆**: 引用 `project_decisions.md` 中的 Tech Stack (如 Flutter/MVVM) 自动填充技术方案章节。
- **任务拆解**: 必须将功能拆解为 `T-001`, `T-002` 等原子任务，且每个任务必须定义 **验证条件 (Acceptance Criteria)**。

## 2. Universal Template (通用模版)

```markdown
# PRD: [Feature Name]

## 1. Context & Goals
*   **Target**: 解决什么问题？
*   **Architecture Compliance**: 本功能如何符合 `project_decisions.md` 中的规范？

## 2. Technical Specs
*   **Business Logic**: ...
*   **Data Model**: ...
*   **API Interface**: ...

## 3. Atomic Task List (任务队列)
> Format: [ ] Task-ID: Description (Verify: Test/Screenshot)

- [ ] Task-001: [P0] 核心数据层实现
    *   Verify: `flutter test test/repository/xxx_test.dart`
- [ ] Task-002: [P1] 业务逻辑层实现
    *   Verify: Unit Test covering edge cases.
- [ ] Task-003: [P1] UI 界面实现
    *   Verify: Screenshot & Widget Test.

## 4. Risks & Mitigations
*   ...
```

## 3. Output Rule
- 生成 PRD 后，**必须** 显式请求用户确认："PRD 已生成，请确认是否开始执行？(Yes/No)"
