---
description: 统一配置模板 — 多模型后端抽象层
version: 1.0
updated: 2026-02-09
---

# Agent Config — 多模型配置中心

本文件定义 Axiom 的模型后端配置。通过切换 `ACTIVE_PROVIDER`，
可以在不修改工作流/规则的情况下适配不同 AI 模型。

---

## 1. Active Provider (当前激活)

```yaml
ACTIVE_PROVIDER: gemini
```

> 可选值: `gemini_cli` | `claude_code` | `codex` | `opencode` | `gemini` | `claude` | `copilot`

---

## 2. Provider Definitions

### 2.1 Gemini (Google)

```yaml
gemini:
  display_name: "Gemini (Google AI)"
  global_config_path: "~/.gemini/GEMINI.md"
  adapter_path: ".agent/adapters/gemini/GEMINI.md"
  
  # API 能力映射
  capabilities:
    file_read: "view_file"
    file_write: "replace_file_content"
    file_create: "create_file"
    run_command: "run_command"
    search: "search_files"
  
  # 项目命令
  commands:
    run: "flutter run"
    test: "flutter test"
    analyze: "flutter analyze"
    build: "flutter build"
  
  # 特性开关
  features:
    json_output: true
    streaming: true
    function_calling: true
    context_window: 1000000
    supports_exec_mode: true
```

### 2.2 Claude (Anthropic)

```yaml
claude:
  display_name: "Claude (Anthropic)"
  global_config_path: "~/.claude/CLAUDE.md"
  adapter_path: ".agent/adapters/claude/CLAUDE.md"
  
  capabilities:
    file_read: "read_file"
    file_write: "replace_string_in_file"
    file_create: "create_file"
    run_command: "run_in_terminal"
    search: "grep_search"
  
  commands:
    run: "flutter run"
    test: "flutter test"
    analyze: "flutter analyze"
    build: "flutter build"
  
  features:
    json_output: false
    streaming: true
    function_calling: true
    context_window: 200000
    supports_exec_mode: false
```

### 2.3 Copilot / GPT (OpenAI)

```yaml
copilot:
  display_name: "Copilot / GPT (OpenAI)"
  global_config_path: "~/.copilot/copilot-instructions.md"
  adapter_path: ".agent/adapters/copilot/copilot-instructions.md"
  
  capabilities:
    file_read: "read_file"
    file_write: "replace_string_in_file"
    file_create: "create_file"
    run_command: "run_in_terminal"
    search: "semantic_search"
  
  commands:
    run: "flutter run"
    test: "flutter test"
    analyze: "flutter analyze"
    build: "flutter build"
  
  features:
    json_output: false
    streaming: true
    function_calling: true
    context_window: 128000
    supports_exec_mode: false
```

### 2.4 Codex CLI (OpenAI)

```yaml
codex:
  display_name: "Codex CLI"
  global_config_path: "~/.codex/config.md"
  adapter_path: ".agent/adapters/codex/CODEX.md"

  capabilities:
    file_read: "read"
    file_write: "edit"
    file_create: "write"
    run_command: "bash"
    search: "grep/glob"

  commands:
    run: "flutter run"
    test: "flutter test"
    analyze: "flutter analyze"
    build: "flutter build"

  features:
    json_output: true
    streaming: true
    function_calling: true
    context_window: 200000
    supports_exec_mode: true
```

### 2.5 OpenCode CLI

```yaml
opencode:
  display_name: "OpenCode CLI"
  global_config_path: "~/.opencode/OPENCODE.md"
  adapter_path: ".agent/adapters/opencode/OPENCODE.md"

  capabilities:
    file_read: "read"
    file_write: "edit"
    file_create: "write"
    run_command: "bash"
    search: "grep/glob"

  commands:
    run: "flutter run"
    test: "flutter test"
    analyze: "flutter analyze"
    build: "flutter build"

  features:
    json_output: false
    streaming: true
    function_calling: true
    context_window: 200000
    supports_exec_mode: true
```

### 2.6 Gemini CLI

```yaml
gemini_cli:
  display_name: "Gemini CLI"
  global_config_path: "~/.gemini/GEMINI.md"
  adapter_path: ".agent/adapters/gemini-cli/GEMINI-CLI.md"

  capabilities:
    file_read: "view_file"
    file_write: "replace_file_content"
    file_create: "create_file"
    run_command: "run_command"
    search: "find_by_name"

  commands:
    run: "flutter run"
    test: "flutter test"
    analyze: "flutter analyze"
    build: "flutter build"

  features:
    json_output: true
    streaming: true
    function_calling: true
    context_window: 1000000
    supports_exec_mode: true
```

### 2.7 Claude Code

```yaml
claude_code:
  display_name: "Claude Code"
  global_config_path: "~/.claude/CLAUDE.md"
  adapter_path: ".agent/adapters/claude-code/CLAUDE-CODE.md"

  capabilities:
    file_read: "read_file"
    file_write: "replace_string_in_file"
    file_create: "create_file"
    run_command: "run_in_terminal"
    search: "grep_search"

  commands:
    run: "flutter run"
    test: "flutter test"
    analyze: "flutter analyze"
    build: "flutter build"

  features:
    json_output: false
    streaming: true
    function_calling: true
    context_window: 200000
    supports_exec_mode: true
```

---

## 3. Shared Settings (跨模型共享)

```yaml
shared:
  # 项目信息
  project:
    name: "Axiom"
    type: "flutter"
    language: "dart"
    
  # Axiom 路径
  paths:
    memory: ".agent/memory"
    rules: ".agent/rules"
    skills: ".agent/skills"
    workflows: ".agent/workflows"
    guards: ".agent/guards"
    evolution: ".agent/evolution"
    dispatcher: ".agent/dispatcher"
    config: ".agent/config"
    adapters: ".agent/adapters"
  
  # 守卫配置
  guards:
    pre_commit_warning: true      # Pre-commit 警告 (不阻断)
    post_commit_checkpoint: true  # Post-commit 自动检查点
    checkpoint_interval_min: 30   # 检查点最小间隔 (分钟)
    watchdog_timeout_min: 30      # 看门狗超时 (分钟)
    watchdog_interval_min: 5      # 看门狗检查间隔 (分钟)
  
  # 进化引擎配置
  evolution:
    min_confidence: 0.5           # 知识最低 Confidence
    seed_confidence: 0.85         # 种子知识初始 Confidence
    decay_days: 30                # Confidence 衰减周期 (天)
    decay_amount: 0.1             # 每周期衰减值
    max_learning_queue: 50        # 学习队列最大长度
    pattern_min_occurrences: 3    # 模式最小出现次数
  
  # Dispatcher 配置
  dispatcher:
    max_restarts: 3               # 单任务最大重启次数
    default_timeout_sec: 600      # 默认超时 (秒)
    timeout_tiers:                # 超时梯度
      simple: 600                 # 10 分钟
      medium: 900                 # 15 分钟
      complex: 1200               # 20 分钟
    prompt_max_tokens: 4000       # Prompt 最大 Token
    compress_threshold: 4000      # 压缩阈值 Token
```

---

## 4. How to Switch Provider (切换指南)

### 步骤 1: 修改本文件
将 `ACTIVE_PROVIDER` 从当前值改为目标模型:
```yaml
ACTIVE_PROVIDER: claude_code   # 改为 claude_code / codex / opencode / gemini_cli / copilot
```

### 步骤 2: 复制适配器文件
```bash
# Claude 用户
cp .agent/adapters/claude/CLAUDE.md ~/.claude/CLAUDE.md

# Claude Code 用户
cp .agent/adapters/claude-code/CLAUDE-CODE.md ~/.claude/CLAUDE.md

# Codex CLI 用户
cp .agent/adapters/codex/CODEX.md ~/.codex/config.md

# OpenCode CLI 用户
cp .agent/adapters/opencode/OPENCODE.md ~/.opencode/OPENCODE.md

# Gemini CLI 用户
cp .agent/adapters/gemini-cli/GEMINI-CLI.md ~/.gemini/GEMINI.md

# Copilot 用户
cp .agent/adapters/copilot/copilot-instructions.md ~/.copilot/copilot-instructions.md
```

### 步骤 3: 验证
执行 `/status` 确认配置生效。

---

## 5. Provider Compatibility Matrix

| 功能 | Gemini CLI | Claude Code | Codex CLI | OpenCode CLI |
|------|------------|-------------|-----------|--------------|
| 工作流执行 | ✅ | ✅ | ✅ | ✅ |
| PRD 生成 | ✅ | ✅ | ✅ | ✅ |
| 知识收割 | ✅ | ✅ | ✅ | ✅ |
| Git 守卫 | ✅ | ✅ | ✅ | ✅ |
| Dispatcher (自动调度) | ✅ | ✅ | ✅ | ✅ |
| JSONL 事件流 | ⚠️ 按版本 | ⚠️ 按版本 | ✅ | ⚠️ 按版本 |
| Session 看门狗 | ✅ | ✅ | ✅ | ✅ |
| 反思引擎 | ✅ | ✅ | ✅ | ✅ |

> ⚠️ = 功能可用但有限制，详见各适配器文档
