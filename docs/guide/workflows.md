# 工作流使用说明

本页关注“怎么跑流程”，原理解释请看 `concepts/how-it-works`。

## 核心命令组

- `/start`：恢复上下文，进入可执行状态
- `/status`：查看任务进度、守卫状态、关键指标
- `/feature-flow`：进入实施主链路
- `/analyze-error`：诊断并处理错误
- `/suspend`：保存现场并退出
- `/reflect` / `/evolve`：做复盘与知识沉淀

## 标准执行链路

1. `/start` 恢复当前状态
2. 明确需求，进入 Draft -> Review -> Decompose
3. 确认后进入 `/feature-flow`
4. 过程中用 `/status` 跟踪
5. 失败时进入 `/analyze-error`
6. 完成后 `/reflect`，离开前 `/suspend`

## 错误处理三出口

当 `/analyze-error` 触发后，通常有三种出口：

- **自动修复**：置信度足够高时直接修复并重验
- **回滚**：回到检查点，避免继续污染
- **阻塞升级**：标记 BLOCKED，等待人工决策

## 什么时候用哪条命令

- 刚打开会话，不确定上下文：`/start`
- 不知道系统在做什么：`/status`
- 连续失败、定位不清：`/analyze-error`
- 准备结束会话：`/suspend`
- 需要沉淀经验：`/reflect`，然后 `/evolve`

## 团队协作建议

- 每次任务切换前先看一次 `/status`
- 关键失败不要跳过 `/analyze-error`
- 每日收尾执行 `/suspend`，保证次日可恢复
- 周期性运行 `/evolve`，让知识库持续更新
