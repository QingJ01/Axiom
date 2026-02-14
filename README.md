# Axiom

给 AI 编程助手提供可落地的「记忆 + 流程 + 协作」能力，让它在真实项目里持续可用，而不是每次对话都从零开始。

---

## 这是什么

Axiom 是一套可移植的项目内工作系统，核心是 `.agent/` 目录：

- 记忆层：保存项目决策、用户偏好、当前上下文
- 流程层：把需求评审、任务拆解、实现与验收串成闭环
- 协作层：兼容多种 AI 编码工具（Gemini/Claude/Codex/OpenCode/Copilot）

你可以把它理解为：**给 AI 的工程化运行时**。

---

## 30 秒安装

```bash
git clone https://github.com/QingJ01/axiom.git
cd axiom

# macOS / Linux
bash setup.sh /path/to/your-project

# Windows (PowerShell)
.\setup.ps1 -TargetDir "D:\your-project"
```

若已安装 PowerShell 7，可使用：`pwsh .\setup.ps1 -TargetDir "D:\your-project"`

安装向导会自动完成：

- 拷贝/更新目标项目的 `.agent/`
- 初始化或保留记忆文件（`project_decisions.md` / `active_context.md` 等）
- 追加必要的 `.gitignore` 规则
- 可选安装对应 AI 工具的全局指令文件

---

## 快速开始

在你的项目里对 AI 说：

```text
/start
```

常用指令：

- `/start`：加载记忆和上下文
- `/status`：查看当前任务与系统状态
- `/feature-flow`：从需求到交付的完整流程
- `/analyze-error`：分析并修复错误
- `/suspend`：保存现场并退出
- `/reflect` / `/evolve`：复盘与知识沉淀

---

## 目录结构

```text
Project Root/
├── .agent/                      # 唯一事实源（主系统）
│   ├── memory/                  # 记忆：项目决策/上下文/偏好
│   ├── workflows/               # 流程定义
│   ├── adapters/                # 工具适配器
│   └── ...
└── docs/                        # 文档与产物
```

说明：

- `.agent` 是主目录，请以它为准

---

## 设计原则

- Manifest-Driven：复杂任务先拆解，再执行
- Evidence-Based Gates：门禁依赖可验证产物，不靠口头状态
- Stateless Skills：技能本身尽量无副作用，状态放在 workflow/memory
- Incremental Delivery：小步迭代、可验证、可回滚

---

## 跨平台说明

- 预览文档站：`npm run docs:dev`
- 生成静态文档：`npm run docs:build`
- 本地预览构建产物：`npm run docs:preview`

---

## 安全与兼容策略（安装器）

当前安装脚本策略：

- 默认采用增量更新，避免粗暴删除目标项目已有目录
- 覆盖更新前会进行备份与恢复（记忆/配置优先）
- `.gitignore` 采用规则补齐，避免关键动态文件被误提交
- 对部分工具提供“跳过全局配置”的推荐路径，减少上下文重复

---

## 适用场景

- 需要 AI 连续多天协作开发，而不是一次性问答
- 需求复杂，必须先评审/拆解再实现
- 多人/多模型协作，希望行为可追踪、可复盘
- 希望把经验沉淀为项目长期记忆

---

## 常见问题


### 会污染我的业务代码吗？

不会。Axiom 主要落在 `.agent/` 与文档目录，对业务代码侵入很低。

### 支持哪些技术栈？

安装器内置了 Flutter/React/Vue/Django/Express/Gin 模板，也支持自定义。

### 支持哪些 AI 工具？

当前适配：Gemini CLI、Claude Code、Codex CLI、OpenCode CLI、GitHub Copilot。

---

## 开发与贡献

建议流程：

1. 先更新文档与工作流定义
2. 再改脚本（`setup.ps1` / `setup.sh`）
3. 最后做跨平台验证（语法 + 冒烟）

最少验证建议：

- `bash -n setup.sh`
- PowerShell 语法解析 `setup.ps1`
- `npm run docs:build`

---

## License

MIT
