# Codex CLI Best Practices (Windows)

## ID: k-026
## Category: Tooling
## Confidence: 0.95

### 1. The PowerShell Argument Hell
在 Windows PowerShell 环境下直接传递包含换行符、JSON、特殊符号的 Prompt 是极其危险的。
CLI 参数解析器经常会截断或错误转义字符串，导致 Codex 接收到残缺的指令。

### 2. Solution: File Injection
不要使用 `codex exec "{long_prompt}"`，而应始终使用：
`codex exec "Read instructions from PROMPT_FILE.md"`

### 3. Execution Flags
- **Mandatory**: `--dangerously-bypass-approvals-and-sandbox` (在 Agent 信任环境下)
- **Output**: `--json` (用于程序化监控)

### 4. Encoding
PowerShell 的 `Set-Content` 默认编码在不同版本下不一致（ANSI vs UTF-16 vs UTF-8）。
**Rule**: 始终显式指定 `-Encoding UTF8`。
