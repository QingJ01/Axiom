# 快速开始

本页目标：10 分钟内把 Axiom 安装进你的项目并跑通第一条任务。

## 前置条件

- 你已有一个本地项目目录
- 已安装一个 AI 工具（Gemini/Claude/Codex/OpenCode/Copilot 之一）
- 推荐安装 Git

## Step 1: 安装 Axiom

### macOS / Linux

```bash
git clone https://github.com/QingJ01/axiom.git
cd axiom
bash setup.sh /path/to/your-project
```

### Windows (PowerShell)

```powershell
git clone https://github.com/QingJ01/axiom.git
cd axiom
.\setup.ps1 -TargetDir "D:\your-project"
```

如果你安装了 PowerShell 7，可替代为：

```powershell
pwsh .\setup.ps1 -TargetDir "D:\your-project"
```

## Step 2: 验证安装结果

目标项目根目录应出现：

- `.agent/`
- `.gitignore` 中 Axiom 规则

## Step 3: 启动系统

在你的 AI 对话窗口输入：

```text
/start
```

再输入：

```text
/status
```

## Step 4: 跑第一条任务

直接输入一个明确需求，例如：

```text
实现一个最小登录页，包含邮箱和密码校验，并补充测试。
```

## 成功标准

- 能看到系统进入可执行状态（IDLE 或任务状态）
- 能接收并执行任务
- 执行过程中产生结构化上下文更新

## 常见平台问题

- Windows 报错“无法识别 `pwsh`”：说明未安装 PowerShell 7，改用 `.\setup.ps1`
- Linux/macOS 报权限问题：先确认用 `bash setup.sh ...` 启动脚本
