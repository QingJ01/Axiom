
---
description: AI Expert Review Board - 并行专家评审流程
---

# AI Expert Review Board (v1.0)

> 多角色并发评审与智能仲裁系统。

## 1. 技能描述 (Description)
本技能模拟了一个顶级的“产品评审委员会”。它不只是写 PRD，而是通过 4 个独立的专家 Agent (UX, Domain, Critic, Tech) 对需求进行全方位的“拷问”和“打磨”，确保最终进入开发的需求是高质量的。

## 2. 使用方法 (Usage)
在 Axiom 中，通过 Workflow 触发：
- `/review-board [需求描述]`

## 3. 核心流程 (Steps)

### Step 1: 👮 PM Gatekeeper (智能门禁)
- **Action**: 调用 `role_pm_gatekeeper.md`
- **Goal**: 过滤离谱需求，确保清晰度。
- **Output**: `PRD_Draft.md` (或驳回)

### Step 2: 🚀 Parallel Review (并行评审)
- **Action**: 并行启动 4 个 Codex Worker 进程 (Sub-Agents)。
- **Inputs**: PRD Draft (`.agent/memory/reviews/{sid}/prd.md`)
- **Process**:
    1. **UX Worker**: Generates `Review_UX.md`
    2. **Domain Worker**: Generates `Review_Domain.md`
    3. **Critic Worker**: Generates `Review_Critic.md`
    4. **Tech Worker**: Generates `Review_Tech.md`
- **Wait**: 主 Agent 等待所有 Worker 完成任务。

### Step 3: ⚖️ Arbitration (仲裁汇总)
- **Action**: 调用 `role_aggregator.md`
- **Input**: 上一步的 4 份报告 + PRD Draft
- **Output**: `Final_Review_Summary.md`

### Step 4: 🛠️ Auto-Fix (自动自愈)
- **Action**: PM 根据 `Final_Review_Summary.md` 重新生成 PRD。
- **Output**: `PRD_Final_v1.0.md`

## 4. 文件结构
- `prompts/`: 存放各角色 Prompt
- `logs/`: 存放评审过程的中间产物 (可选)
