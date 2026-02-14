---
description: Phase 2: 复杂 PRD 任务拆解与子文档生成工作流
---

# 工作流：任务拆解 (Phase 2)

本工作流将“粗设” PRD 拆解为 Manifest 任务清单和详细的 Sub-PRD 文档。

## 前置条件
- 最终版粗设 PRD 存在于 `docs/prd/[name]-rough.md`。

## 执行步骤

1.  **工作量评估门禁 (Workload Gate)**
    - **动作**: 评估任务工期是否 > 1 天。
    - **路径**:
        - **小任务 (< 1 天)**: 跳过拆解。创建单任务 Manifest。直接进入 Phase 3。
        - **大任务 (> 1 天)**: 进入步骤 2。

2.  **架构设计 (Manifest)**
    - **动作**: 运行 `system-architect` 技能。
    - **输入**: `docs/prd/[name]-rough.md`。
    - **输出**: `docs/tasks/[id]/manifest.md` (包含 DAG 和空任务列表)。

3.  **串行生成子 PRD (Sequential Sub-PRD Generation)**
    - **动作**: 遍历 `manifest.md` 中的任务列表。
    - **循环**: 对每个 `T-xxx` 任务：
        - 读取 `.agent/rules/provider_router.rule`，解析 `WORKER_EXEC`。
        - 运行 `{WORKER_EXEC}`，使用角色 `.agent/prompts/roles/sub_prd_writer.md`。
        - **上下文**: 传递 `rough.md`, `manifest.md`, 以及 *前序* Sub-PRD 的摘要 (确保一致性)。
        - **输出**: `docs/tasks/[id]/sub_prds/[task_name].md`。

4.  **PM 审计 (一致性检查)**
    - **动作**: Agent (PM) 读取所有生成的 Sub-PRD。
    - **检查**:
        - **对齐性**: 是否实现了 `rough.md` 的要求？
        - **自洽性**: 跨 Sub-PRD 的 UI/数据定义是否匹配？ (如：相同的用户模型)。
    - **修复**: 若发现冲突，自动触发对特定 Sub-PRD 的修复。

5.  **用户确认门禁 (User Confirmation Gate)**
    - **动作**: 展示 Manifest 和 Sub-PRD 列表。
    - **询问**: "任务拆解已完成。一致性检查通过。是否准备开发？"
    - **路径**:
        - **是**: 触发工作流 `.agent/workflows/4-implementing.md`.
        - **否**: 在此停止。
