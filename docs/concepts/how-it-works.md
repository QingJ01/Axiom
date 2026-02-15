# 系统工作原理

## 总览

Axiom 的运行机制可以概括为：

1. **记忆先行**：先读 `active_context.md` 恢复状态。
2. **路由决策**：根据用户意图进入对应 workflow。
3. **门禁约束**：关键节点必须满足可验证条件。
4. **产物落盘**：结果写入 memory/evolution，形成可追踪证据。

## 核心组件

### 1) Router（路由层）

- 负责将用户输入映射到 `/start`、`/status`、`/feature-flow` 等流程。
- 在新会话时优先触发记忆读取，避免无上下文执行。
- 定义见：`.agent/rules/router.rule`。

### 2) Workflows（流程层）

- 把复杂任务拆成可验证阶段：Draft -> Review -> Decompose -> Implement。
- 每个阶段有输入、动作、出口条件，失败可转入异常流程。
- 定义见：`.agent/workflows/*.md`。

### 3) Gatekeepers（门禁层）

- 在提交、阶段切换、回滚等高风险操作前进行约束。
- 示例：Flutter 项目提交前要求 `flutter analyze` + `flutter test` 通过。
- 定义见：`.agent/rules/gatekeepers.rule` 与 `.agent/guards/*`。

### 4) Memory（记忆层）

- `active_context.md`：当前会话状态与任务队列
- `project_decisions.md`：架构决策与已知问题
- `user_preferences.md`：用户长期偏好
- 读写器示例：`.agent/memory/context_manager.py`

### 5) Evolution（进化层）

- `/reflect`：总结本次会话表现与改进行动
- `/evolve`：处理学习队列并更新知识库/模式库
- 目标是让系统“越用越稳”，而不是反复踩同类坑

## 状态流转与失败恢复

常见状态：`IDLE`、`DRAFTING`、`REVIEWING`、`DECOMPOSING`、`IMPLEMENTING`、`BLOCKED`。

当发生失败时：

1. 收集日志与最近变更
2. 匹配历史已知问题
3. 给出三类出口：自动修复 / 回滚 / 标记阻塞
4. 将错误模式回写到长期记忆

## 为什么强调“证据优先”

因为口头“完成了”不等于可交付。Axiom 要求：

- 测试有结果
- 变更有记录
- 决策有出处
- 失败有回滚路径

这样做的收益是：可审计、可复盘、可持续协作。
