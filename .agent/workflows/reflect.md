---
description: Reflect Workflow - 反思工作流，总结经验并提取知识
---

# /reflect - 反思工作流

执行自动反思，总结本次会话的经验教训。

## Trigger
- 用户输入 `/reflect` 或 "反思"
- 状态从 EXECUTING 变为 ARCHIVING 时自动触发

## Steps

### Step 1: 读取会话状态
// turbo
1. 读取 `.agent/memory/active_context.md`
2. 解析任务完成情况

### Step 2: 生成反思报告
1. 分析本次会话：
   - 任务完成率 = 已完成 / 总任务数
   - 自动修复次数 = `auto_fix_attempts`
   - 回滚次数 = (检查 History)
2. 按照 `reflection_log.md` 模板生成报告

### Step 3: 提取知识
1. 识别 "What Went Well" 中的可复用经验
2. 如果有新知识，创建知识条目：
   - 文件: `.agent/memory/knowledge/k-xxx-title.md`
   - 更新 `knowledge_base.md` 索引

### Step 4: 提取 Action Items
1. 识别 "What Could Improve" 中的改进点
2. 将 Action Items 添加到 `active_context.md` 任务队列：
   ```markdown
   - [ ] [REFLECTION] Action description
   ```

### Step 5: 追加到反思日志
// turbo
1. 将反思报告追加到 `reflection_log.md`
2. 更新统计数据

### Step 6: 输出报告
1. 向用户展示反思摘要
2. 列出新提取的知识和 Action Items

## Output Format
```markdown
## 💭 反思完成

### 📊 本次会话统计
- 任务完成: X/Y
- 自动修复: X 次
- 回滚: X 次

### ✅ 做得好
- ...

### ⚠️ 待改进
- ...

### 💡 新知识
- k-xxx: [Title]

### 🎯 Action Items
- [ ] [Action 1]
- [ ] [Action 2]
```
