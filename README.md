# Axiom

![Axiom Logo](./logo.svg)

在线文档：`https://axiomdocs.vercel.app/`

给 AI 编程助手提供可持续的工程化运行环境：让它具备长期记忆、可验证流程和跨工具协作能力，而不是每轮对话都从零开始。

## 项目用途

Axiom 的核心目标是把「AI 编码」从一次性问答升级为可管理的研发流程。它主要解决四个问题：

- **会话遗忘**：通过 `.agent/memory` 持久化项目决策、上下文和偏好。
- **流程失控**：通过 `.agent/workflows` 强制关键阶段和门禁。
- **协作不一致**：通过 `.agent/adapters` 统一不同 AI 工具行为。
- **复盘缺失**：通过 `/reflect` 和 `/evolve` 沉淀经验为可复用知识。

## 核心功能

- **记忆系统**：保存 `project_decisions.md`、`active_context.md`、用户偏好与演化产物。
- **流程系统**：覆盖 Draft -> Review -> Decompose -> Implement 全流程。
- **门禁系统**：在提交、验证、回滚等关键节点做强制检查。
- **错误恢复**：支持 `/analyze-error` 诊断、自动修复、回滚与阻塞升级。
- **多工具适配**：支持 Gemini CLI、Claude Code、Codex CLI、OpenCode、Copilot。

## 30 秒安装（主推安装器）

推荐使用 **Axiom Manager 安装器（GUI）**：

1. 从 Release 下载并安装 Axiom Manager
2. 启动后选择目标项目目录
3. 选择 Provider 并执行安装

安装器详细步骤见：`docs/guide/install-and-upgrade.md`

命令行安装仅作为备用方案。

## 命令行安装（备用）

```bash
git clone https://github.com/QingJ01/axiom.git
cd axiom

# macOS / Linux
bash setup.sh /path/to/your-project
```

```powershell
# Windows PowerShell
.\setup.ps1 -TargetDir "D:\your-project"

# 如果你安装了 PowerShell 7，也可用
pwsh .\setup.ps1 -TargetDir "D:\your-project"
```

安装后在目标项目中输入：

```text
/start
/status
```

## 适用与边界

适用：

- 需要 AI 连续多天协作开发
- 需求复杂，需要先评审再实现
- 希望流程可审计、可回滚、可复盘

不适用：

- 一次性脚本/临时实验
- 不希望引入流程约束的纯自由对话场景

## 文档入口

- 快速开始：`docs/guide/quickstart.md`
- 安装与升级（详细）：`docs/guide/install-and-upgrade.md`
- 项目用途与边界：`docs/concepts/purpose-and-scope.md`
- 功能地图：`docs/concepts/feature-map.md`
- 系统工作原理：`docs/concepts/how-it-works.md`
- 原理 Q&A：`docs/concepts/principle-qa.md`
- 命令参考：`docs/guide/commands.md`

## 常见问题

### 会污染业务代码吗？

默认不会。Axiom 主要写入 `.agent/` 和文档目录，对业务代码侵入低。

### 可以逐步接入吗？

可以。先从 `/start` + `/status` + `/suspend` 三条命令开始，再逐步使用评审与门禁能力。

### 如何验证安装成功？

至少确认：`.agent/` 目录存在、`/status` 可返回状态、安装器执行成功。

## 灵感来源

- AgentOS: `https://github.com/flockmaster/AgentOS`

## License

MIT
