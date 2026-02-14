---
description: Rollback Command - 回滚到上一个 Git 检查点
---

# /rollback - 回滚操作

将项目回滚到上一个 Git 检查点，撤销所有后续修改。

## Trigger
- 用户输入 `/rollback` 或 "回滚" / "撤销"

## ⚠️ 警告
此操作会**丢弃**自上次检查点以来的所有代码修改。请确认后执行。

## Steps

### Step 1: 读取当前检查点
// turbo
1. 读取 `.agent/memory/active_context.md`
2. 获取 `last_checkpoint` 字段

### Step 2: 确认回滚
输出警告信息，要求用户确认：
```markdown
⚠️ **Rollback Confirmation**

将回滚到: `checkpoint-20260208-021900`
以下修改将被丢弃:
- [列出自检查点以来的 commit]

**确认回滚请输入 "Yes" 或 "确认"**
```

### Step 3: 执行回滚 (用户确认后)
```bash
# 1. 重置到检查点
git reset --hard [checkpoint-tag]

# 2. 清理未跟踪文件
git clean -fd
```

### Step 4: 更新状态
1. 将 `task_status` 更新为 `IDLE`
2. 清空当前任务队列
3. 记录回滚操作到 History

### Step 5: 报告结果

## Output Format
```markdown
## ⏪ Rollback Complete

**Rolled back to**: `checkpoint-20260208-021900`
**Discarded commits**: X
**State**: IDLE

### Next Steps
1. 检查代码状态: `git status`
2. 重新开始任务或描述新需求
```

## 回滚失败处理
如果回滚失败（如检查点不存在）：
1. 列出所有可用的检查点 `git tag -l "checkpoint-*"`
2. 让用户选择要回滚到的检查点
