# 快速开始

本页目标：10 分钟完成 Axiom 接入并跑通一条最小闭环任务。

## 前置条件

- 已有本地项目目录（建议已初始化 Git）
- 已安装一个 AI 工具（Gemini/Claude/Codex/OpenCode/Copilot）
- 已阅读 `guide/install-and-upgrade`

## Step 1: 安装

### macOS / Linux

```bash
git clone https://github.com/QingJ01/axiom.git
cd axiom
bash setup.sh /path/to/your-project
```

### Windows PowerShell

```powershell
git clone https://github.com/QingJ01/axiom.git
cd axiom
.\setup.ps1 -TargetDir "D:\your-project"
```

## Step 2: 验证目录

目标项目应包含：

- `.agent/`
- `.agent/memory/active_context.md`
- `.agent/memory/project_decisions.md`

## Step 3: 启动系统

在 AI 会话依次输入：

```text
/start
/status
```

若 `/status` 返回状态与任务信息，说明核心链路可用。

## Step 4: 跑最小任务

输入一个明确需求，例如：

```text
实现一个最小登录页，包含邮箱和密码校验，并补充测试。
```

执行过程中建议使用：

- `/status` 跟踪阶段
- `/analyze-error` 处理失败
- `/suspend` 在中断前保存现场

## 成功标准

- 系统进入可执行状态（IDLE 或任务态）
- 能持续接收并执行任务
- 会话中断后可通过 `/start` 恢复现场

## 常见问题

- Windows 报错找不到 `pwsh`：直接使用 `.\setup.ps1`
- Linux/macOS 权限问题：通过 `bash setup.sh ...` 执行
- `/status` 信息缺失：检查 `active_context.md` frontmatter 字段
