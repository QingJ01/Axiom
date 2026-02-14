# 安装与运行

## 一键安装（推荐）

## macOS / Linux

```bash
bash setup.sh /path/to/your-project
```

## Windows (PowerShell)

```powershell
pwsh setup.ps1 -TargetDir "D:\your-project"
```

## 安装器会做什么

- 安装/更新目标项目 `.agent/`
- 创建 `.agents` 兼容入口（优先链接，失败回退复制）
- 初始化或保留记忆文件（`project_decisions.md`、`active_context.md`）
- 补齐 `.gitignore` 规则
- 可选写入 AI 工具全局配置

## 覆盖安装行为

- 采用增量更新，不直接清空你的业务目录
- 会优先保留记忆与配置
- 建议安装前先提交一次 Git 作为检查点

## 首次运行

安装完成后，在目标项目中对 AI 输入：

```text
/start
```

## 检查项

- `.agent/memory/project_decisions.md` 存在
- `.agent/memory/active_context.md` 存在
- `/status` 可正常返回状态
