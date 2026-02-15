# 故障排查

排查顺序建议：先目录与文件，再命令行为，最后看日志与回滚。

## `/start` 后没有恢复上下文

检查项：

1. `.agent/memory/active_context.md` 是否存在
2. frontmatter 是否包含 `session_id`、`task_status`
3. 是否在正确项目根目录执行命令

处理：修复后再次执行 `/start`。

## `/status` 信息不完整

检查项：

1. `.agent/memory/evolution/` 是否存在
2. `.agent/config/agent_config.md` 是否存在
3. 最近是否手动修改过 memory 文件格式

处理：恢复标准模板后重试 `/status`。

## 提交被 pre-commit 阻断

常见原因：

- Flutter 项目下 `flutter analyze` 失败
- Flutter 项目下 `flutter test` 失败
- 合并冲突未解决

处理：

1. 先修复 analyze/test 失败
2. 清理冲突标记后再提交

## 错误修复循环

现象：同一错误反复出现，自动修复多次失败。

处理：

1. 执行 `/analyze-error` 并保留完整日志
2. 检查 `project_decisions.md` 的 Known Issues
3. 达到上限后切换到回滚或 BLOCKED 决策

## Windows 提示“无法识别 pwsh”

说明：你的环境未安装 PowerShell 7。

处理：

1. 直接运行 `.\setup.ps1 -TargetDir "你的项目路径"`
2. 或安装 PowerShell 7 后再用 `pwsh`

## `/export` 后找不到导出包

处理：

1. 先看命令输出的 `Location`
2. 默认在项目根目录，形如 `axiom-export-YYYYMMDD.zip`
3. 确认执行命令时当前路径是目标项目

## 仍无法解决

- 收集：命令输入、完整错误输出、最近变更文件
- 进入 `/analyze-error`
- 必要时执行回滚并附上 checkpoint 信息
