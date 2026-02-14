# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased] - 2026-02-10

- meta: convert workflows for Copilot compatibility
  - Added `.github/copilot-instructions.md` and `.github/prompts/*` (status, feature-flow, codex-dispatch, export, rollback, knowledge, patterns, evolve, reflect, analyze-error, start, suspend, meta)
  - Updated workflow files under `.agent/workflows/` to be Copilot-friendly:
    - Unified memory paths to `.agent/memory/...`
    - Replaced PowerShell snippets with macOS/zsh equivalents
    - Replaced `view_file`/`replace_file_content` with `read_file`/`apply_patch` guidance
    - Added explicit context-compression guidance for `codex-dispatch`
    - Completed and clarified `suspend` workflow
  - Committed and pushed on branch `main` (see commit `meta: convert workflows for Copilot compatibility`)

---

*(This file was generated automatically by the agent.)*
