---
description: Evolve Workflow - 手动触发进化，处理学习队列并优化系统
---

# /evolve - 进化工作流

手动触发完整的进化周期，包括知识收割、模式检测、工作流优化。

## Trigger
- 用户输入 `/evolve` 或 "进化" / "学习" / "升级"

## Steps

### Step 1: 检查学习队列
// turbo
1. 读取 `.agent/memory/evolution/learning_queue.md`
2. 统计待处理素材数量

### Step 2: 处理学习素材
对于队列中每个素材：
1. 根据 `source_type` 调用对应处理器：
   - `code_change`: 分析代码变更，提取模式
   - `error_fix`: 提取错误解决方案，更新 Known Issues
   - `workflow_run`: 更新工作流指标
2. 生成知识条目或更新现有条目
3. 标记素材为已处理

### Step 3: 更新知识库
// turbo
1. 将新知识追加到 `knowledge_base.md`
2. 更新分类统计和标签云

### Step 4: 检测代码模式
1. 读取 `pattern_library.md`
2. 检查是否有新模式可以提升 (occurrences >= 3)
3. 更新模式库

### Step 5: 分析工作流效能
// turbo
1. 尝试读取 `workflow_metrics.md`（不存在则记为 `N/A`，不中断）
2. 计算各工作流指标：
   - 平均耗时
   - 成功率
   - 常见瓶颈
3. 如果有异常，生成优化建议

### Step 6: 处理反思日志
// turbo
1. 读取 `reflection_log.md`
2. 检查未完成的 Action Items
3. 统计知识产出

### Step 7: 生成进化报告
输出完整的进化报告给用户

## Output Format
```markdown
# 🧬 Evolution Report - YYYY-MM-DD

## 📚 Knowledge Updates
- **New**: X items
  - k-xxx: [Title]
- **Updated**: X items
- **Deprecated**: X items

## 🔄 Pattern Detection
- **New Patterns**: X
  - P-xxx: [Name]
- **Promoted**: X

## 📊 Workflow Insights
| Workflow | Avg Duration | Success Rate | Bottleneck |
|----------|--------------|--------------|------------|
| feature-flow | X min | X% | [Phase] |
| analyze-error | X min | X% | [Phase] |

### Optimization Suggestions
1. [Suggestion 1]
2. [Suggestion 2]

## 💭 Reflection Summary
- **Sessions Reflected**: X
- **Action Items**: X completed, Y pending

## 🎯 Recommended Next Steps
1. [High Priority Action]
2. [Medium Priority Action]

---
*Evolution Engine v1.0 | Total Knowledge: X items | Total Patterns: X*
```

## Post-Evolve Actions
1. 清理已处理的学习素材 (保留 7 天)
2. 归档过期的工作流详情 (90 天前)
3. 标记低置信度知识为 deprecated
