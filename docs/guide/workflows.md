# 工作流说明

## 核心工作流

- `/start`：启动并恢复上下文
- `/feature-flow`：兼容入口，转到实施主流程
- `/analyze-error`：错误分析与修复
- `/status`：系统仪表盘
- `/suspend`：保存现场并暂停
- `/rollback`：回滚到检查点
- `/reflect`：复盘学习
- `/evolve`：触发知识进化

## 典型执行顺序

1. `/start`
2. 提需求（或 `/feature-flow`）
3. 失败时 `/analyze-error`
4. 进度追踪 `/status`
5. 收尾 `/reflect` -> `/suspend`

## 错误工作流的三种出口

- 自动修复（高置信度）
- 回滚到检查点
- 标记阻塞并跳过当前任务

## 何时用哪条命令

- 看不到上下文：先 `/start`
- 不确定系统在做什么：`/status`
- 连续报错：`/analyze-error`
- 下班或中断：`/suspend`
