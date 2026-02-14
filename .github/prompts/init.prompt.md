---
description: 执行 Axiom 初始化 (交互式安装向导)
---

你将执行 Axiom (v4.2) 的初始化工作流。

**目标**: 通过交互式问答，将 Axiom 适配到用户的开发环境 (Gemini CLI / Claude Code / Codex CLI / OpenCode CLI / Copilot)。

**步骤**:
1) **环境问询**:
   - 向用户发出欢迎信息。
   - **必须询问**: "请问您当前使用的是哪种 AI 助手？(1. Gemini CLI, 2. Claude Code, 3. Codex CLI, 4. OpenCode CLI, 5. GitHub Copilot)"

2) **作用域与风险确认**:
   - 询问用户希望配置生效的范围 (仅当前项目 / 全局用户目录)。
   - **必须警告**: "此操作将覆盖目标位置的现有配置文件。系统会自动创建 `.bak` 备份。是否继续？"

3) **执行配置**:
   - 先解析 `PROJECT_ROOT`（优先 Git 根目录；否则当前目录）。
   - 项目级路径一律写入 `PROJECT_ROOT`，禁止直接用 `./`。
   - 获得确认后，根据选择执行安装：
     - **Gemini CLI**: `mkdir -p ~/.gemini` -> 复制 `.agent/adapters/gemini-cli/GEMINI-CLI.md` 到 `~/.gemini/GEMINI.md`（或 `[PROJECT_ROOT]/.gemini/GEMINI.md`）
     - **Claude Code**: `mkdir -p ~/.claude` -> 复制 `.agent/adapters/claude-code/CLAUDE-CODE.md` 到 `~/.claude/CLAUDE.md`（或 `[PROJECT_ROOT]/.claude/CLAUDE.md`）
     - **Codex CLI**: `mkdir -p ~/.codex` -> 复制 `.agent/adapters/codex/CODEX.md` 到 `~/.codex/config.md`（或 `[PROJECT_ROOT]/.codex/config.md`）
     - **OpenCode CLI**: `mkdir -p ~/.opencode` -> 复制 `.agent/adapters/opencode/OPENCODE.md` 到 `~/.opencode/OPENCODE.md`（或 `[PROJECT_ROOT]/.opencode/OPENCODE.md`）
     - **Copilot**: 复制到 `[PROJECT_ROOT]/.github/copilot-instructions.md`（或可选 `~/.copilot/copilot-instructions.md`）
   - *注意*: 遇到目标文件存在时，先重命名 backup。

4) **新手引导**:
   - 安装完成后，输出简短指南：
     - "✅ 初始化完成！试试 `/draft [需求]` 或 `/status`。"
     - "📖 详情请阅读 `README.md`。"

5) **目录校验**:
   - 检查 `.agent` 主目录存在，且 `memory/workflows/adapters` 目录完整。
