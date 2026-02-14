# Axiom — Claude Code 适配器
# Provider: Claude Code
# Version: 4.3 | Updated: 2026-02-14

## 0. 强制规则
- 语言: 中文。
- 风格: 极简，不解释显而易见内容。
- 任务完成后: 先验证再宣告完成。

## 1. 启动协议
1. 读取 `.agent/memory/active_context.md`。
2. 如存在 `.agent/`，加载项目决策与用户偏好。
3. 按用户意图读取对应 workflow 并执行。

## 2. 能力映射
- 文件读取: `read_file`
- 文件修改: `replace_string_in_file`
- 搜索: `grep_search` / `semantic_search`
- 命令执行: `run_in_terminal`

## 3. 推荐执行策略
- 先定位后读取再编辑。
- 改动后执行：`flutter analyze && flutter test`。
- 大任务拆分为原子步骤，逐步验证。

## 4. 兼容说明
- 支持对话式工作流执行。
- 如需长链调度，建议由 PM 驱动 Worker 循环。

_Axiom — Claude Code Adapter_
