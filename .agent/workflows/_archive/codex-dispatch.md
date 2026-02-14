---
description: 自动派发 Codex 任务流水线
---

# Codex Task Dispatcher v4.0 (Parallel & Manifest-Driven)

> **核心理念**: 基于 `docs/architecture/03_Workflow_Implementation.md` 规范，实现 **Manifest 驱动** 的并行调度循环。
> **无需脚本解析**，完全由 Agent (PM) 主导，Worker (Codex) 闭环执行。

---

## 1. 触发方式

| 用户说... | Agent 行为 |
|----------|-----------|
| "执行 PRD" / "开始调度" | 检查状态，识别路径 (Fast Track 或 Sub-Workflow) |
| "继续交付" / "推进进度" | 读取 Manifest，解锁 DAG 节点 |
| "/feature-flow" | 启动全自动交付流水线 |

---

## 2. 调度逻辑 (The DAG Loop)

### Step 1: 文档定位 📄
1.  **优先级 1**: 查找 `docs/tasks/T-{ID}/manifest.md` (已拆解的大任务)。
2.  **优先级 2**: 查找 `docs/prd/*-dev.md` (小任务或新需求)。
3.  **Action**: 读取文件并注入当前上下文。

### Step 2: DAG 拓扑分析 🕸️
Agent 作为一个智力实体，需要解析任务间的依赖关系：
1.  **识别无依赖节点 (Set)**: 找出所有 `Pre: None` 或 `Dependencies` 已全部勾选为 `[x]` 的任务。
2.  **并发决策**: 
    - 如果 Set 包含多个任务，准备 **并行分发**。
    - **限制**: 每次物理启动最多 **3** 个并行 Worker。

### Step 3: 构造专家级 Prompt 📝
根据选中的任务，严格遵循 `docs/03` 的 Prompt 模板：

```markdown
# Role
你是一个资深的全栈工程师 (Senior Full-Stack Engineer)，负责执行原子化任务。

# Task Context
- **Task ID**: {T-xxx}
- **Description**: {任务名称}
- **Dependency**: {已完成的前置依赖列表}

# Input Artifacts (请首先阅读)
1. **Manifest**: `docs/tasks/T-{ID}/manifest.md` (了解全景)
2. **Sub-PRD**: {任务文档路径} (核心需求)
3. **Global Map**: {全景图路径} (如有)

# Constraints (严格遵守)
1. **Scope**: 仅修改 Sub-PRD 要求的代码，严禁修改其他模块。
2. **Testing**: 必须编写对应的单元测试，并确保 `Pass Rate 100%`。
3. **Convention**: 遵循项目现有的目录结构和命名规范。
4. **Communication**: 遇到模糊需求，必须提问 (Output: QUESTION)。

# Execution Steps
1. READ input artifacts carefully.
2. DESIGN & CODE the implementation.
3. TEST your code (fix if failed).
4. **UPDATE STATUS**: Modify `manifest.md` (or PRD file), change `[ ] T-{ID}` to `[x] T-{ID}`.

# Final Output
- Output `TASK {ID} COMPLETED` only after the checkbox is checked.
```

### Step 4: 启动与监控 🚀
1.  **调用命令**:
    ```bash
    codex exec --json --dangerously-bypass-approvals-and-sandbox "{Structured_Prompt}"
    ```
2.  **异步等待 (Exponential Backoff)**:
    - **策略**: 初始等待 **30s** -> 递增 +120s -> 最大等待 **600s** (10分钟)。
    - **Loop (Parallel Check)**:
      1. **遍历**: 对 Active Task List 中的每个任务 ID (PID) 进行 `command_status` 检查。
      2. **处理**:
         - **Done**: 收集 Output，触发后处理 (Git/Status Update)，从 List 移除。
         - **Running**: 保留。
      3. **等待**: 如果 List 非空，WaitDurationSeconds 递增后继续下一轮。
    - **超时**: 单个任务累计耗时 > 10分钟 -> 强杀 -> 标记 FAILED。

3.  **JSONL 解析与完成判定**:
    - PM 必须实时解析终端输出的 JSONL 流。
    - **关键事件**:
      - `{"type":"item.completed", "item":{"type":"agent_message", "text":"TASK ... COMPLETED"}}` -> **成功 (Success)**
      - `{"type":"turn.completed"}` (且无上述 Success 消息) -> **需要检查 (Check)**
      - `{"type":"error"}` -> **失败 (Error)**
    - **判定逻辑 (High Priority)**:
      1. **首要信号**: 检测到 `{"type":"turn.completed", "usage":{...}}`。
         - 这意味着 Codex 认为自己干完了（无论是成功回复还是执行完毕）。
         - **操作**: 立即终止轮询，视为任务结束。
      2. **次要信号**: 检测到 `agent_message` 包含 `COMPLETED`。
         - 用于双重确认成功状态。
      3. **收尾**: 读取 Output 并分析是否包含 Question（如有则触发 Resume，否则视为 Done）。

### Step 6: 交互与干预 (Turn-Based Interaction)

Codex 在非交互模式下通过 **Turn-Based (回合制)** 机制工作：
1.  **Worker 挂起**: 若 Codex 需要提问，它会输出 Problem Message 并自动结束当前 Turn (Exit 0)。
2.  **PM 介入**:
    - 捕获 Output 中的 `agent_message` (e.g., "QUESTION: ...")。
    - 捕获 `thread_id` (Session ID)。
    - **决策**: 查询知识库或询问用户。
3.  **Resume 恢复**:
    - 使用 `codex exec resume {SESSION_ID} ...` 注入答案。
    - 启动新的 Turn 继续任务。

```bash
# 示例: 回答 Worker 提问并继续
codex exec resume {SESSION_ID} --json --dangerously-bypass-approvals-and-sandbox "Answer: 使用 --color-primary。请继续执行。"
```

---

## 4. 状态汇报规范
每完成一个调度周期，PM 输出：
```markdown
📊 **进度报告 (Task T-xxx)**
- ✅ 子任务 T-001: 已完成 (Commit: abc123)
- ⏳ 子任务 T-002: 执行中 (Parallel 1/3)
- 🕸️ 解锁依赖: T-003, T-004 已准备就绪
```

---

_Codex Dispatcher v4.0 — Powered by Axiom_
