---
description: Phase 1: 需求澄清与 PRD 初稿生成工作流
---

# 工作流：PRD 起草 (Phase 1)

本工作流旨在澄清您的想法，并将其转化为结构化的 PRD 初稿。

## 执行步骤

1.  **需求澄清循环 (Clarification Loop)**
    - **动作**: 对用户输入运行 `requirement-analyst` 技能。
    - **检查**:
        - 若结果为 `REJECT` (拒绝): 停止并向用户解释原因。
        - 若结果为 `CLARIFY` (需澄清) (< 90%): 向用户询问生成的问题。等待回复。使用新输入重复步骤 1。
        - 若结果为 `PASS` (通过) (> 90%): 进入步骤 2。

2.  **生成 PRD 初稿 (Generate Draft)**
    - **动作**: 使用通过验证的需求上下文，运行 `product-design-expert` 技能。
    - **输出**: 新文件生成于 `docs/prd/[name]-draft.md`。

3.  **用户评审门禁 (User Gate)**
    - **动作**: 向用户展示 PRD 初稿的路径。
    - **询问**: "PRD 初稿已就绪。是否进入专家评审阶段？"
    - **路径**:
        - **是**: 触发工作流 `.agent/workflows/2-reviewing.md`.
        - **否**: 在此停止。
