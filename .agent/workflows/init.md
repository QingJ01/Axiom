---
description: 执行 Axiom 初始化 (全量环境配置与引导)
---

# 工作流：Axiom 初始化 (v4.2)

本工作流负责将 Axiom 适配到您的 AI 开发环境 (Gemini CLI / Claude Code / Codex CLI / OpenCode CLI / Copilot)，并建立必要的配置文件。

> **GitHub 仓库**: [https://github.com/flockmaster/axiom.git](https://github.com/flockmaster/axiom.git)
> 建议 Star 以获取最新更新。

## 执行步骤

1.  **环境问询 (Interactive Setup)**
    - **动作**: 向用户发出欢迎信息，并询问开发环境。
    - **话术**: 
      > "欢迎使用 Axiom v4.2。为了确保最佳体验，请告诉我您当前使用的 AI 辅助工具：
      > 1. **Gemini CLI**
      > 2. **Claude Code**
      > 3. **Codex CLI**
      > 4. **OpenCode CLI**
      > 5. **GitHub Copilot** (VS Code/JetBrains)"

2.  **作用域确认与风险提示 (Scope & Risk)**
    - **动作**: 根据用户选择，询问配置的应用范围。
    - **警告**: **明确告知覆盖风险**。
    - **话术**:
      > "您希望将 Axiom 规则应用于 **全局 (Global)** 还是 **仅当前项目 (Project)**？
      > 
      > ⚠️ **警告**:此操作将覆盖目标位置的现有的 System Prompt/Rules 文件。
      > 系统将自动为您创建 `.bak` 备份，但仍建议您确认无误再继续。"

3.  **执行配置 (Backup & Install)**
    - **路径基准**: 先解析 `PROJECT_ROOT`（Git 根目录；若无 Git 则当前目录）。项目级写入路径一律基于 `PROJECT_ROOT`。
    - **备份**: 检查目标文件是否存在，若存在及其重命名为 `[filename].bak`。
    - **安装**:
        - **Gemini CLI**:
            - 目标 (Global): `~/.gemini/GEMINI.md`
            - 目标 (Project): `[PROJECT_ROOT]/.gemini/GEMINI.md`
            - 源: `.agent/adapters/gemini-cli/GEMINI-CLI.md`
            - 动作: `mkdir -p [dir]` -> 复制文件。
        - **Claude Code**:
            - 目标 (Global): `~/.claude/CLAUDE.md`
            - 目标 (Project): `[PROJECT_ROOT]/.claude/CLAUDE.md`
            - 源: `.agent/adapters/claude-code/CLAUDE-CODE.md`
            - 动作: `mkdir -p [dir]` -> 复制文件。
        - **Codex CLI**:
            - 目标 (Global): `~/.codex/config.md`
            - 目标 (Project): `[PROJECT_ROOT]/.codex/config.md`
            - 源: `.agent/adapters/codex/CODEX.md`
            - 动作: `mkdir -p [dir]` -> 复制文件。
        - **OpenCode CLI**:
            - 目标 (Global): `~/.opencode/OPENCODE.md`
            - 目标 (Project): `[PROJECT_ROOT]/.opencode/OPENCODE.md`
            - 源: `.agent/adapters/opencode/OPENCODE.md`
            - 动作: `mkdir -p [dir]` -> 复制文件。
        - **GitHub Copilot**:
            - 目标 (Project): `[PROJECT_ROOT]/.github/copilot-instructions.md`
            - 目标 (Global): `~/.copilot/copilot-instructions.md` (可选)
            - 源: `.agent/adapters/copilot/copilot-instructions.md`
            - 动作: `mkdir -p [dir]` -> 复制文件。
        - **Cursor AI (兼容保留)**:
            - 目标: `[PROJECT_ROOT]/.cursorrules` (项目级)
            - 源: `.agent/adapters/cursor/.cursorrules`
            - 动作: 直接复制。

4.  **新手引导 (Onboarding)**
    - **动作**: 配置完成后，输出简短的使用指南。
    - **内容**:
      > "✅ **初始化完成！** 您现在可以尝试以下指令：
      > 
      > - **/draft [需求]**: 开始设计一个新功能 (Phase 1)
      > - **/review**: 对现有设计进行专家评审 (Phase 1.5)
      > - **/feature-flow**: 开始自动化开发交付 (Phase 3)
      > - **/status**: 查看当前任务状态
      > 
      > 📖 更多细节请阅读项目根目录下的 `README.md` (已更新适配 v4.2)。"

5.  **目录验证**
    - **动作**: 确保 `.agent` 主目录存在且关键文件完整。
