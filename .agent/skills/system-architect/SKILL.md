---
name: system-architect
description: A specialist skill focused on decomposing complex PRDs into atomic architecture, task manifests, and DAGs.
---

# System Architect Skill (系统架构师)

## 1. Overview (概述)
该技能充当 **System Architect**。它接收经过评审验证的 Rough PRD，并将其分解为清晰原子的工程任务 (`T-xxx`)。它负责生成 **Manifest** 和 **Global Architecture**。

**重要规则**: 请全程使用**中文**进行思考和输出。

## 2. Input (输入)
- **Rough PRD**: `docs/prd/[name]-rough.md` (真理之源)。
- **Project Structure**: `lib/` 和 `test/` (必须尊重现有模式)。

## 3. Actions (执行步骤)

### Step 1: Global Architecture (全局架构)
- **Identify Structure**: 涉及哪些包/模块？
- **Define DAG**: 依赖关系是什么？(e.g., API 先于 Models，然后是 UI)。
- **Create Diagram**: 绘制 `graph TD` 展示技术流向。

### Step 2: Task Decomposition (任务原子化)
- **Granularity**: 任务应代表单个内聚的工作单元 (e.g., "登录界面 UI", "认证仓库")。
- **Constraints**: > 1 个文件变更, < 1 天工作量。
- **Naming**: `T-{ID}` (e.g., `T-001`)。

### Step 3: Manifest Generation (清单生成)
- **Create Folder**: `docs/tasks/[feature/id]/`。
- **Create Manifest**: `docs/tasks/[feature/id]/manifest.md`。

## 4. Output Logic (Manifest)

**File**: `docs/tasks/[feature/id]/manifest.md`

```markdown
# Task Manifest: [Feature Name]

## 1. Architecture Map (Global Context)
```mermaid
graph TD
  [Start] --> [Component A]
```

## 2. Task List (DAG)
> Checklist format. Order implies dependency.

- [ ] **T-101: [Title]**
  - Path: `docs/tasks/[feature/id]/sub_prds/[snake_case_name].md`
  - Context: [Brief Description]
  - Depends On: [None | T-xxx]

- [ ] **T-102: [Title]**
  - Path: `docs/tasks/[feature/id]/sub_prds/[snake_case_name].md`
  - Context: [Description]
  - Depends On: T-101
```

## 5. Usage Example
**Input**: PRD for "Login".

**Output**: `docs/tasks/login-v1/manifest.md` with:
- T-001: Auth Repository (API + Local Storage).
- T-002: Login Bloc/Provider (State Management).
- T-003: Login Screen (UI).
