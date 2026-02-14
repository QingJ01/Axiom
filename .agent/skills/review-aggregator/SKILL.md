---
name: review-aggregator
description: Aggregates reviews from 5 experts, resolves conflicts, prioritizes content, and updates the PRD. Also syncs the result to Feishu Docs.
---

# Review Aggregator Skill (评审聚合者)

## 1. Overview (概述)
该技能充当 **首席 PM**。它接收来自专家评审团（UX, Product, Domain, Tech, Critic）的输入，根据严格的层级解决冲突，并生成最终的 "Rough Design" PRD。它还确保文档同步到云端（飞书）。

**重要规则**: 请全程使用**中文**进行思考和输出。即使输入包含英文，最终产出也必须是中文。

## 2. Input (输入)
- **Original Draft**: `docs/prd/[name]-draft.md`
- **Review Artifacts**:
  - `review_ux.md`
  - `review_product.md`
  - `review_domain.md`
  - `review_tech.md`
  - `review_critic.md`

## 3. Conflict Resolution Hierarchy (The Gavel - 冲突仲裁)
当专家意见不一致时，使用此优先级顺序：
1.  🔴 **Safety & Security** (Critic): 不可协商。
2.  🔧 **Technical Feasibility** (Tech): 硬性约束。
3.  👔 **Strategic Alignment** (Product Director): P0/P1 范围。
4.  💰 **Business Value** (Domain): 逻辑正确性。
5.  ✨ **UX** (UX Director): 优化建议。

## 4. Actions (执行步骤)

### Step 1: Synthesis (综合)
- 合并所有 "Pass" 和 "Optimization" 建议。
- 对于 "Reject" 或 "Blocker" 项目，应用仲裁层级。
- 重写草稿中的 `User Stories` 和 `Requirements`。
- 如果逻辑发生变化，更新 `Flowchart`。
- **这里强调：生成的 PRD 内容必须翻译为精炼、专业的中文。**

### Step 2: Documentation (The Final Artifacts)
- **Summary**: 创建 `docs/reviews/[name]/summary.md` 列出关键决策和放弃的项目。
- **Final Rough PRD**: 更新 `docs/prd/[name]-rough.md`。**确保文件名以 `-rough.md` 结尾。**

### Step 3: Cloud Sync (Feishu)
- **Call Skill**: `feishu-doc-assistant` (or use `feishu-doc-creator`).
- **Action**: Create a new Feishu Doc named "PRD: [Feature Name] (Rough)".
- **Content**:
  - Title: [Feature Name]
  - Body: Combine `summary.md` + `rough.md`.
- **Output**: Get the visible URL.

## 5. Output Format (输出格式)

**File**: `docs/reviews/[name]/summary.md`

```markdown
# Review Summary: [Feature Name]

## 1. Key Decisions (关键决策)
- [Conflict]: [Role] 解决 -> [决策结果]

## 2. Scope Changes (范围变更)
- Removed: ...
- Added: ...

## 3. Feishu Link
- [Feishu Doc](URL)
```
