# 功能地图

本页回答三个问题：Axiom 有哪些能力、每个能力怎么触发、结果会落到哪里。

## 能力矩阵

| 能力域 | 目标 | 典型输入 | 关键产出 | 主要位置 |
|---|---|---|---|---|
| 记忆管理 | 让 AI 保持连续性 | `/start`、上下文恢复 | 当前状态、任务队列、历史决策 | `.agent/memory/*` |
| 流程编排 | 把需求转为可执行任务 | 新需求、确认进入下阶段 | Draft/Review/Manifest/实施流转 | `.agent/workflows/*` |
| 质量门禁 | 避免低质量交付 | 提交代码、阶段切换 | 可验证通过/阻断信号 | `.agent/rules/*`、`.agent/guards/*` |
| 错误恢复 | 缩短排障路径 | 编译失败、测试失败、异常日志 | 根因分析、修复建议、回滚方案 | `.agent/workflows/analyze-error.md` |
| 进化学习 | 把经验沉淀为资产 | `/reflect`、`/evolve` | 反思日志、知识条目、模式库 | `.agent/evolution/*`、`.agent/memory/evolution/*` |
| 多工具协作 | 统一不同 AI 工具行为 | 切换 provider/终端 | 统一的命令入口与能力映射 | `.agent/adapters/*`、`.agent/config/*` |

## 命令到能力映射

| 命令 | 能力域 | 作用 |
|---|---|---|
| `/start` | 记忆管理 | 加载 active context，恢复会话现场 |
| `/status` | 记忆管理 + 门禁可视化 | 输出任务、指标、守卫状态 |
| `/feature-flow` | 流程编排 | 进入实施主链路 |
| `/analyze-error` | 错误恢复 | 收集日志、定位根因、给出修复路径 |
| `/suspend` | 记忆管理 | 保存会话快照并退出 |
| `/reflect` | 进化学习 | 生成反思与改进项 |
| `/evolve` | 进化学习 | 处理学习队列并更新知识资产 |
| `/rollback` | 错误恢复 + 门禁 | 回到检查点，控制损失范围 |

## 产物分层

- **短期运行态**：`active_context.md`、watchdog lock、临时报告
- **长期知识态**：`project_decisions.md`、knowledge/pattern 库
- **行为约束态**：rules/workflows/guards

建议实践：先理解命令，再理解产物，最后理解约束。这样能快速判断“某个问题应在流程、配置还是记忆层修复”。
