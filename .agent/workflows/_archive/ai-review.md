
---
description: AI Expert Review Board Workflow - 多角色并行评审
---

# AI 专家评审团工作流

> 本工作流将启动 AI 专家评审团，对您的需求进行全方位体检。

## 1. 启动门禁 (Gatekeeper)
- 调用 `role_pm_gatekeeper.md` 对用户需求进行初步评估。
  - 读取用户输入的需求。
  - 检查可行性与清晰度。
  - 如果通过，生成 PRD 初稿。
  - 如果不通过，直接与用户对话澄清。

## 2. 准备评审环境 (Setup)
- 生成唯一的 Session ID (如 `review-{timestamp}`)。
- 创建临时目录 `.agent/memory/reviews/{session_id}/`。
- 将当前 PRD 草稿写入 `.agent/memory/reviews/{session_id}/prd.md`。

## 3. 专家会诊 (Parallel Expert Review)
- **[系统指令]**: 为每个角色生成唯一的 Prompt 文件 (避免 CLI 参数转义问题)。
  - Format: `.agent/prompts/REVIEW_{ROLE}_{SESSION_ID}.md`

### 3.1 角色定义与 Prompt 生成
1. **UX Director**:
   - File: `.agent/prompts/REVIEW_UX_{SESSION_ID}.md`
   - Content:
     ```markdown
     # Role: Experience Director (UX)
     # Context: Read .agent/memory/reviews/{session_id}/prd.md
     # Standard: .agent/skills/ai-expert-review-board/prompts/role_ux_director.md
     # Output: Write report to .agent/memory/reviews/{session_id}/review_ux.md
     # Constraint: Direct output only.
     ```

2. **Domain Expert**:
   - File: `.agent/prompts/REVIEW_DOMAIN_{SESSION_ID}.md`
   - Content: (Similar structure, pointing to domain expert role)

3. **The Critic**:
   - File: `.agent/prompts/REVIEW_CRITIC_{SESSION_ID}.md`
   - Content: (Similar structure, pointing to critic role)

4. **Tech Lead**:
   - File: `.agent/prompts/REVIEW_TECH_{SESSION_ID}.md`
   - Content: (Similar structure, pointing to tech lead role)

5. **Product Director**:
   - File: `.agent/prompts/REVIEW_PD_{SESSION_ID}.md`
   - Content:
     ```markdown
     # Role: Product Director (PD)
     # Context: Read .agent/memory/reviews/{session_id}/prd.md
     # Standard: .agent/skills/ai-expert-review-board/prompts/role_product_director.md
     # Output: Write report to .agent/memory/reviews/{session_id}/review_pd.md
     # Constraint: Direct output only.
     ```

### 3.2 并行启动 (Parallel Launch)
使用 `run_command` (WaitMsBeforeAsync=500) 并行启动 4 个 Worker：

```bash
# UX
codex exec --json --dangerously-bypass-approvals-and-sandbox "Execute task defined in .agent/prompts/REVIEW_UX_{SESSION_ID}.md"

# Domain
codex exec --json --dangerously-bypass-approvals-and-sandbox "Execute task defined in .agent/prompts/REVIEW_DOMAIN_{SESSION_ID}.md"

# Critic
codex exec --json --dangerously-bypass-approvals-and-sandbox "Execute task defined in .agent/prompts/REVIEW_CRITIC_{SESSION_ID}.md"

# Tech
codex exec --json --dangerously-bypass-approvals-and-sandbox "Execute task defined in .agent/prompts/REVIEW_TECH_{SESSION_ID}.md"

# Product Director
codex exec --json --dangerously-bypass-approvals-and-sandbox "Execute task defined in .agent/prompts/REVIEW_PD_{SESSION_ID}.md"
```

### 3.3 监控与收割 (Harvesting)
- **Loop**: 轮询检查上述 5 个 Command ID 的状态。
- **Completion**: 只要检测到 `turn.completed` 或 `agent_message: COMPLETED`，即视为该角色完成。
- **Cleanup**: 任务完成后，删除对应的临时 Prompt 文件。

## 4. 仲裁与定稿 (Arbitration & Finalize)
- **[系统指令]**: 生成 `.agent/prompts/REVIEW_AGGREGATOR_{SESSION_ID}.md`。
- **Content**:
  ```markdown
  # Role: Aggregator
  # Input: .agent/memory/reviews/{session_id}/ (review_*.md) + prd.md
  # Output: .agent/memory/reviews/{session_id}/review_summary.md (Scientific Chinese)
  ```
- **Execute**: `codex exec ... "Execute task defined in ...AGGREGATOR..."`

- **[系统指令]**: 生成 `.agent/prompts/REVIEW_PM_{SESSION_ID}.md`。
- **Content**:
  ```markdown
  # Role: PM
  # Input: review_summary.md
  # Output: .agent/memory/reviews/{session_id}/prd_final.md (Scientific Chinese)
  ```
- **Execute**: `codex exec ... "Execute task defined in ...PM..."`

## 5. 结束
- 提示用户 PRD 已就绪，询问是否进入开发阶段。

