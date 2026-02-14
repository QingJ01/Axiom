---
description: Status Command — 结构化系统仪表盘 (T-308 增强版)
version: 2.0
updated: 2026-02-09
---

# /status - 系统仪表盘

显示系统当前的完整状态: 任务进度条 + 知识库统计 + 反思摘要 + 工作流指标趋势 + 模型配置。

## Trigger
- 用户输入 `/status` 或 "状态" / "进度"

## Steps

### Step 1: 读取核心状态
// turbo
1. 读取 `.agent/memory/active_context.md`
2. 解析 YAML frontmatter: `task_status`, `session_id`, `last_checkpoint`
3. 读取 `.agent/config/agent_config.md` 获取 `ACTIVE_PROVIDER`

### Step 2: 统计任务进度
// turbo
1. 统计 Task Queue 中各状态任务数量 (✅/⏳/🔄/🚫/❌)
2. 计算完成百分比
3. 生成进度条 (每 10% 一个 █ 字符)

### Step 3: 知识库 & 进化统计
// turbo
1. 读取 `.agent/memory/evolution/knowledge_base.md` — 统计知识条目数、分类分布
2. 读取 `.agent/memory/evolution/pattern_library.md` — 统计模式数量
3. 读取 `.agent/memory/evolution/learning_queue.md` — 统计待处理素材

### Step 4: 反思摘要
// turbo
1. 读取 `.agent/memory/reflection_log.md`
2. 提取最近 5 条反思摘要 (日期 + Session 名 + 关键 Learning)

### Step 5: 工作流指标趋势
// turbo
1. 尝试读取 `.agent/memory/evolution/workflow_metrics.md`
   - 若文件不存在，返回 `N/A`，不中断 `/status`
2. 提取各工作流最近一次执行记录
3. 计算全局统计 (总执行/成功率/平均耗时)

### Step 6: 守卫状态
// turbo
1. 检查 `.git/hooks/pre-commit` 是否存在 → 守卫安装状态
2. 检查 `.git/hooks/post-commit` 是否存在
3. 检查最近 checkpoint tag

### Step 7: 生成结构化仪表盘

## Output Format
```markdown
# 📊 Axiom — System Dashboard

## 🎯 System State
| Key | Value |
|-----|-------|
| Status | IDLE / EXECUTING / BLOCKED |
| Session | {session_id} |
| Provider | Gemini CLI / Claude Code / Codex CLI / OpenCode CLI / Legacy |
| Last Checkpoint | checkpoint-XXXXXXXX-XXXXXX |
| Uptime | X min since last context update |

---

## 📋 Task Progress

**Phase X: {Phase Name}**

| Status | Count | Tasks |
|--------|-------|-------|
| ✅ Done | X | T-101, T-102, ... |
| ⏳ Pending | X | T-301, T-302, ... |
| 🔄 In Progress | X | T-xxx |
| 🚫 Blocked | X | - |

**Overall**: ████████████████░░░░ 80% (16/20 tasks)

---

## 🧬 Evolution Stats

| Metric | Count | Details |
|--------|-------|---------|
| 📚 Knowledge Items | 25 | 15 arch / 3 pattern / 4 workflow / 2 tooling / 1 debug |
| 🔄 Active Patterns | X | X ACTIVE / X CANDIDATE |
| 📥 Learning Queue | X | X pending / X processed |
| 💭 Reflections | X | Last: 2026-02-09 |

---

## 💭 Recent Reflections (最近 5 条)

| Date | Session | Key Learning |
|------|---------|-------------|
| 2026-02-09 | Phase 2 Engine | 知识收割需要最低 Confidence 门槛 |
| ... | ... | ... |

---

## 📈 Workflow Metrics

| Workflow | Runs | Avg Duration | Success Rate | Last Run |
|----------|------|-------------|-------------|----------|
| feature-flow | X | Xmin | X% | 2026-02-09 |
| analyze-error | X | Xmin | X% | - |
| start | X | Xmin | X% | - |

---

## 🛡️ Guard Status

| Guard | Status | Details |
|-------|--------|---------|
| Pre-commit | ✅ Installed / ❌ Not installed | Warning-only |
| Post-commit | ✅ Installed / ❌ Not installed | Auto-checkpoint |
| Session Watchdog | ✅ Running / ⏸️ Stopped | Timeout: 30min |
| Last Checkpoint | checkpoint-xxx | X min ago |

---
*Dashboard generated at: {timestamp}*
*Axiom v4.2*
```
