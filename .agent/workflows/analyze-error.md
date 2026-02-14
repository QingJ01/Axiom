---
description: Panic Button - 错误智能分析与修复
---

# Error Analysis Workflow

当 `feature-flow` 遇到熔断（3次修复失败）或用户直接抛出报错时触发。

## Phase 1: Log Collection (日志收集)
1. **收集构建日志**: 读取 `flutter run` / `flutter analyze` 的完整输出。
2. **收集测试日志**: 读取 `flutter test` 的失败详情。
3. **收集 Git 状态**: `git diff HEAD~1` 查看最近的代码变更。

## Phase 2: Diff Analysis (差异分析)
4. **获取检查点**: 读取 `active_context.md` 中的 `last_checkpoint`。
5. **对比差异**: `git diff [last_checkpoint]..HEAD`
6. **定位变更文件**: 识别出问题可能出在哪些文件。

## Phase 3: Root Cause Analysis (根因分析)
7. **模式匹配**: 
   - 检查 `project_decisions.md` 的 `Known Issues` 是否有类似错误。
   - **IF Match**: 直接应用历史修复方案。
8. **外部搜索**: 如确需外部资料，优先让用户提供链接/关键词；在 Copilot 环境下可用 `fetch_webpage` 读取指定 URL 内容。
9. **AI 推理**: 基于上下文分析可能的根因。

## Phase 4: Resolution (解决方案)
10. **Option A - Auto-Fix (高置信度)**:
    - 置信度 > 80%: 自动应用修复
    - 重新运行验证

11. **Option B - Rollback (回滚)**:
    - 执行: `git reset --hard [last_checkpoint]`
    - 清理: `git stash drop` (如有)
    - 输出: "已回滚到检查点 [tag]"

12. **Option C - Skip Task (跳过任务)**:
    - 将当前 Task 标记为 `BLOCKED`
    - 继续执行队列中的下一个任务
    - 输出: "Task-X 已跳过，请后续手动处理"

## Phase 5: Learning (学习记录)
13. **记录错误模式**: 
    - 将此错误的模式写入 `project_decisions.md` 的 `## Known Issues`
    - 格式: `| 日期 | 错误类型 | 根因分析 | 修复方案 | 影响范围 |`
14. **更新草稿区**: 在 `active_context.md` 的 Scratchpad 中记录此次错误的简要描述。

## Quick Reference (快速参考)

```bash
# 查看最近的检查点
git tag | grep checkpoint | tail -5

# 查看检查点到现在的变更
git diff checkpoint-YYYYMMDD-HHMMSS..HEAD --stat

# 基于检查点创建修复分支（更安全）
git checkout -b fix-from-checkpoint checkpoint-YYYYMMDD-HHMMSS

# 查看错误历史
grep -n "Known Issues" .agent/memory/project_decisions.md
```
