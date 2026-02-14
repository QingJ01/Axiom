# Axiom — OpenCode CLI 适配器
# Provider: OpenCode CLI
# Version: 4.3 | Updated: 2026-02-14

## 0. 强制规则
- 全程中文。
- 仅做必要变更，避免越界修改。
- 每个任务结束必须给出验证证据。

## 1. 启动协议
1. 读取 `.agent/memory/active_context.md`。
2. 读取 `.agent/memory/project_decisions.md` 与 `.agent/memory/user_preferences.md`。
3. 匹配并读取 `.agent/workflows/*.md` 后执行。

## 2. 能力映射
- 文件读取: `read`
- 文件写入: `edit` / `write`
- 代码搜索: `glob` / `grep`
- 终端执行: `bash`

## 3. 运行策略
- 默认走 Agent Native Orchestration。
- 对需要长时执行的任务，按 manifest 原子化推进。
- 失败重试上限 3 次，超限标记 BLOCKED。

## 4. 质量门禁
- 代码变更后执行 `flutter analyze`、`flutter test`。
- 未通过门禁禁止宣告 DONE。

_Axiom — OpenCode CLI Adapter_
