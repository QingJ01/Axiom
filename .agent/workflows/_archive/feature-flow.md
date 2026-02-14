---
description: Feature Delivery Pipeline - 全自动交付流水线 (Powered by Codex Dispatcher)
---

# Feature Flow v3.0 (The Executor)

> **PRD Driven Development** 的核心引擎。
> 整合需求确认与自动化交付，全程由 Agent 主导。

---

## 触发条件

| 触发方式 | 说明 |
|---------|------|
| 用户确认 PRD 后说 "Go" / "确认" / "执行" | 自动进入 Feature Flow |
| `/feature-flow` 或 "开始交付" | 手动触发 |

---

## Phase 0: Pre-Flight Check (起飞前检查)

> **Mandatory**: 每次流水线启动前必须执行。

// turbo
1. **冲突检测**:
   ```bash
   git status --porcelain
   ```
   - 如果有未提交的修改 → 自动 Stash:
   ```bash
   git stash push -m "auto-stash-before-feature-flow"
   ```

// turbo
2. **创建检查点**:
   ```bash
   git tag checkpoint-$(date +%Y%m%d-%H%M%S)
   ```
   - 输出: "✓ 检查点已创建" → 便于后续回滚

---

## Phase 1: 定位 PRD

3. **自动发现 PRD**:
   - 查找 `docs/prd/*-dev.md` 中最近修改的文件
   - 如果找到多个，选择最新的
   - 如果找不到，询问用户输入路径

4. **确认 PRD**:
   - 显示 PRD 标题和任务数量
   - 询问用户: "准备执行此 PRD？(Y/n)"

---

## Phase 2: 调度执行 (核心)

> 这里调用 `/codex-dispatch` workflow，采用 Agent 原生调度模式。

5. **启动调度循环**:
   - 读取 PRD → 识别下一个任务 → 构造 Prompt → 启动 Worker
   - 监控 Worker 输出 → 处理问题 → 更新 PRD 状态
   - 循环直到所有任务完成或遇到阻塞

6. **进度汇报**:
   - 每完成一个任务，输出简短状态:
     ```
     ✅ T-001 完成 (1/10)
     ✅ T-002 完成 (2/10)
     🚫 T-003 阻塞 - 等待用户确认架构选择
     ⏭️ 跳过 T-004，先执行 T-005
     ...
     ```

---

## Phase 3: 完成与清理

7. **验证完成状态**:
   - 重新读取 PRD，检查所有任务状态
   - 统计: 完成数 / 阻塞数 / 总数

8. **生成总结**:
   ```
   🎉 Feature Flow 完成！
   
   📊 执行统计:
   - 已完成: X/Y 任务
   - 阻塞: Z 个
   - 总耗时: ~N 分钟
   
   📝 阻塞任务 (如有):
   - T-003: 等待用户确认...
   - T-007: 数据库迁移需要 DBA 审批...
   ```

// turbo
9. **恢复 Stash** (如果有):
   ```bash
   git stash pop
   ```

---

## Phase 4: 异常处理

### 🔴 Worker 失败

- 3 次重试后仍失败 → 标记 FAILED
- 询问用户:
  ```
  任务 T-00X 执行失败，是否要:
  1. 手动调试并重试
  2. 跳过此任务，继续其他
  3. 回滚到检查点并停止
  ```

### 🔴 全局阻塞 (无法继续)

- 当所有 PENDING 任务都被阻塞 → 无法继续
- 列出所有阻塞原因，等待用户一一处理

### 🔴 用户请求回滚

- 用户说 "/rollback" 或 "回滚"
- 执行:
  ```bash
  git reset --hard $(git describe --tags --abbrev=0 --match="checkpoint-*")
  ```
- 恢复到 Phase 0 创建的检查点

---

## 状态同步

整个流程中，Agent 需要保持以下状态同步:

| 状态源 | 更新时机 |
|-------|---------|
| PRD 文件 | 每个任务完成后立即更新 |
| `active_context.md` | 每个阻塞、跳过、完成时更新 |
| Git History | 每个任务完成后提交 |

---

## 使用示例

```
用户: 执行这个 PRD → docs/prd/feature-x-dev.md

Agent: 
  📋 检测到 PRD: Feature X (共 8 个任务)
  🔍 Pre-Flight Check...
  ✓ 无未提交修改
  ✓ 检查点 checkpoint-20260209-173200 已创建
  
  🚀 开始执行...
  
  ▶ T-001: 实现基础调度器
    [启动 Codex Worker]
    [监控中...]
    ✅ 完成 (1/8)
  
  ▶ T-002: 实现 Worker 封装器
    [启动 Codex Worker]
    [监控中...]
    ✅ 完成 (2/8)
  
  ▶ T-003: 实现交互式监控
    [启动 Codex Worker]
    🤔 Worker 提问: "监控数据存哪里？"
    → 我来回答: "存 .agent/logs/monitor.json"
    [重启并注入答案]
    ✅ 完成 (3/8)
  
  ... (继续循环)
  
  🎉 Feature Flow 完成！
  
  📊 执行统计:
  - 已完成: 7/8 任务
  - 阻塞: 1 个 (T-007 需要 DBA 确认)
  - 总耗时: ~23 分钟
```

---

## 与 codex-dispatch 的关系

```
feature-flow.md (上层封装)
    │
    ├── Pre-Flight Check (Git 操作)
    ├── PRD 发现与确认
    │
    └── 调用 codex-dispatch.md ← 核心调度循环
            │
            ├── 读取 PRD
            ├── 选择任务
            ├── 启动 Worker
            ├── 监控与干预
            └── 更新状态
```

`feature-flow` 是上层封装，负责 Git 操作和用户交互。
`codex-dispatch` 是核心调度器，负责实际的任务派发。
