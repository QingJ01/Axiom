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
   - 获得确认后，根据选择执行安装：
     - **Gemini CLI**: `mkdir -p ~/.gemini` -> 复制 `.agent/adapters/gemini-cli/GEMINI-CLI.md` 到 `~/.gemini/GEMINI.md` (或项目级)
     - **Claude Code**: `mkdir -p ~/.claude` -> 复制 `.agent/adapters/claude-code/CLAUDE-CODE.md` 到 `~/.claude/CLAUDE.md` (或项目级)
     - **Codex CLI**: `mkdir -p ~/.codex` -> 复制 `.agent/adapters/codex/CODEX.md` 到 `~/.codex/config.md` (或项目级)
     - **OpenCode CLI**: `mkdir -p ~/.opencode` -> 复制 `.agent/adapters/opencode/OPENCODE.md` 到 `~/.opencode/OPENCODE.md` (或项目级)
     - **Copilot**: `mkdir -p .github` -> 复制 `.agent/adapters/copilot/copilot-instructions.md` 到 `.github/copilot-instructions.md`
   - *注意*: 遇到目标文件存在时，先重命名 backup。

4) **新手引导**:
   - 安装完成后，输出简短指南：
     - "✅ 初始化完成！试试 `/draft [需求]` 或 `/status`。"
     - "📖 详情请阅读 `README.md`。"

5) **兼容性**:
   - 检查并创建 `.agents` -> `.agent` 的软链接。
