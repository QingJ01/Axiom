# 配置说明

## 核心配置文件

- `.agent/config/agent_config.md`
- `.agent/memory/project_decisions.md`
- `.agent/memory/user_preferences.md`
- `.agent/memory/active_context.md`

## `agent_config.md`

- `ACTIVE_PROVIDER`：当前使用的 AI 适配器
- 其他 provider 相关参数

## `project_decisions.md`

- 技术栈、架构模式、编码规范
- `Known Issues`：已知问题与修复方案

## `user_preferences.md`

- 沟通语言
- 输出风格
- 开发习惯（如是否自动提交）

## `active_context.md`

- `task_status`、`session_id`、`last_checkpoint`
- 当前任务队列与短期记忆摘要

## 修改建议

- 先改 `project_decisions.md`（技术基线）
- 再改 `user_preferences.md`（行为偏好）
- `active_context.md` 建议由系统自动维护
