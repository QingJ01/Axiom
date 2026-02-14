#!/usr/bin/env pwsh
# ============================================================
#  Axiom — 初始化向导 (Windows / PowerShell)
#  用法: pwsh setup.ps1 [-TargetDir <path>]
# ============================================================

param(
    [string]$TargetDir = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# ── 颜色辅助 ──────────────────────────────────────────────
function Write-Step  { param($msg) Write-Host "`n🔧 $msg" -ForegroundColor Cyan }
function Write-Ok    { param($msg) Write-Host "   ✅ $msg" -ForegroundColor Green }
function Write-Info  { param($msg) Write-Host "   ℹ️  $msg" -ForegroundColor DarkGray }
function Write-Warn  { param($msg) Write-Host "   ⚠️  $msg" -ForegroundColor Yellow }

# ── Banner ────────────────────────────────────────────────
Write-Host ""
Write-Host "   ╔══════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "   ║   🌌 Axiom — Setup        ║" -ForegroundColor Magenta
Write-Host "   ║   给你的 AI 编程助手装上大脑              ║" -ForegroundColor Magenta
Write-Host "   ║   https://github.com/flockmaster/axiom║" -ForegroundColor DarkGray
Write-Host "   ╚══════════════════════════════════════════╝" -ForegroundColor Magenta
Write-Host ""

# ============================================================
# Step 1: 选择目标项目
# ============================================================
Write-Step "Step 1/6 — 设置目标项目"

if ($TargetDir -eq "") {
    Write-Host "   请输入你的项目路径 (留空 = 当前目录): " -NoNewline -ForegroundColor Yellow
    $TargetDir = Read-Host
    if ($TargetDir -eq "") { $TargetDir = Get-Location }
}
$TargetDir = Resolve-Path $TargetDir -ErrorAction SilentlyContinue
if (-not $TargetDir -or -not (Test-Path $TargetDir)) {
    Write-Host "   ❌ 路径不存在: $TargetDir" -ForegroundColor Red
    exit 1
}
Write-Ok "目标目录: $TargetDir"

# 检测是否已初始化
if (Test-Path "$TargetDir\.agent\memory\active_context.md") {
    Write-Warn "检测到该项目已安装 Axiom (.agent/ 已存在)。"
    Write-Host "   是否覆盖配置？(y/N): " -NoNewline -ForegroundColor Yellow
    $overwrite = Read-Host
    if ($overwrite -ne "y" -and $overwrite -ne "Y") {
        Write-Host "   👋 已取消。" -ForegroundColor Gray
        exit 0
    }
}

# ============================================================
# Step 2: 项目信息
# ============================================================
Write-Step "Step 2/6 — 项目信息"

Write-Host "   项目名称: " -NoNewline -ForegroundColor Yellow
$ProjectName = Read-Host
if ($ProjectName -eq "") { $ProjectName = Split-Path -Leaf $TargetDir }

Write-Host ""
Write-Host "   选择技术栈:" -ForegroundColor Yellow
Write-Host "     [1] Flutter / Dart"
Write-Host "     [2] React / TypeScript"
Write-Host "     [3] Vue / TypeScript"
Write-Host "     [4] Python / Django"
Write-Host "     [5] Node.js / Express"
Write-Host "     [6] Go / Gin"
Write-Host "     [0] 自定义"
Write-Host "   输入编号 (默认 1): " -NoNewline -ForegroundColor Yellow
$stackChoice = Read-Host
if ($stackChoice -eq "") { $stackChoice = "1" }

$TechStacks = @{
    "1" = @{ sdk = "Flutter"; lang = "Dart"; arch = "MVVM"; lint = "flutter_lints"; fmt = "dart format"; run = "flutter run"; test = "flutter test"; analyze = "flutter analyze"; build = "flutter build" }
    "2" = @{ sdk = "React";   lang = "TypeScript"; arch = "Component"; lint = "eslint"; fmt = "prettier"; run = "npm run dev"; test = "npm test"; analyze = "npm run lint"; build = "npm run build" }
    "3" = @{ sdk = "Vue";     lang = "TypeScript"; arch = "Composition API"; lint = "eslint"; fmt = "prettier"; run = "npm run dev"; test = "npm test"; analyze = "npm run lint"; build = "npm run build" }
    "4" = @{ sdk = "Django";  lang = "Python"; arch = "MTV"; lint = "flake8"; fmt = "black"; run = "python manage.py runserver"; test = "python manage.py test"; analyze = "flake8 ."; build = "N/A" }
    "5" = @{ sdk = "Express"; lang = "JavaScript"; arch = "MVC"; lint = "eslint"; fmt = "prettier"; run = "npm start"; test = "npm test"; analyze = "npm run lint"; build = "npm run build" }
    "6" = @{ sdk = "Gin";     lang = "Go"; arch = "Clean Architecture"; lint = "golint"; fmt = "gofmt"; run = "go run ."; test = "go test ./..."; analyze = "go vet ./..."; build = "go build" }
}

if ($stackChoice -eq "0") {
    Write-Host "   SDK/框架: " -NoNewline; $customSdk = Read-Host
    Write-Host "   语言: " -NoNewline;     $customLang = Read-Host
    Write-Host "   架构: " -NoNewline;     $customArch = Read-Host
    $stack = @{ sdk = $customSdk; lang = $customLang; arch = $customArch; lint = "N/A"; fmt = "N/A"; run = "N/A"; test = "N/A"; analyze = "N/A"; build = "N/A" }
} else {
    $stack = $TechStacks[$stackChoice]
    if (-not $stack) { $stack = $TechStacks["1"] }
}

Write-Ok "项目: $ProjectName | $($stack.sdk) / $($stack.lang) / $($stack.arch)"

# ============================================================
# Step 3: 选择 AI 工具
# ============================================================
Write-Step "Step 3/6 — 选择你的 AI 编程工具"

Write-Host "     [1] Gemini CLI"
Write-Host "     [2] Claude Code"
Write-Host "     [3] Codex CLI"
Write-Host "     [4] OpenCode CLI"
Write-Host "     [5] GitHub Copilot (VS Code / JetBrains)"
Write-Host "   输入编号 (默认 1): " -NoNewline -ForegroundColor Yellow
$aiChoice = Read-Host
if ($aiChoice -eq "") { $aiChoice = "1" }

$providers = @{
    "1" = @{ name = "gemini_cli";  display = "Gemini CLI";  adapter = "adapters/gemini-cli/GEMINI-CLI.md"; globalDir = "$env:USERPROFILE\.gemini"; globalFile = "GEMINI.md" }
    "2" = @{ name = "claude_code"; display = "Claude Code"; adapter = "adapters/claude-code/CLAUDE-CODE.md"; globalDir = "$env:USERPROFILE\.claude"; globalFile = "CLAUDE.md" }
    "3" = @{ name = "codex";       display = "Codex CLI";  adapter = "adapters/codex/CODEX.md"; globalDir = "$env:USERPROFILE\.codex"; globalFile = "config.md" }
    "4" = @{ name = "opencode";    display = "OpenCode CLI"; adapter = "adapters/opencode/OPENCODE.md"; globalDir = "$env:USERPROFILE\.opencode"; globalFile = "OPENCODE.md" }
    "5" = @{ name = "copilot";     display = "Copilot";    adapter = "adapters/copilot/copilot-instructions.md"; globalDir = "$env:USERPROFILE\.copilot"; globalFile = "copilot-instructions.md" }
}
$provider = $providers[$aiChoice]
if (-not $provider) { $provider = $providers["1"] }
Write-Ok "AI 工具: $($provider.display)"

# ============================================================
# Step 4: 复制文件并初始化
# ============================================================
Write-Step "Step 4/6 — 安装 Axiom 到项目"
$today = Get-Date -Format "yyyy-MM-dd"

# 4.1 复制 .agent/ 目录
$agentSrc = Join-Path $ScriptDir ".agent"
$agentDst = Join-Path $TargetDir ".agent"

# === 4.1.0 智能备份 (Smart Backup) ===
$memoryRestored = $false
$backupDir = Join-Path $env:TEMP "agent_os_backup_$(Get-Random)"

if (Test-Path $agentDst) {
    Write-Info "检测到现有 Axiom，启动 [智能无损更新] 模式..."
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    
    # 备份记忆 (Memory)
    if (Test-Path "$agentDst\memory") {
        Copy-Item "$agentDst\memory" $backupDir -Recurse -Force
        Write-Info "已备份记忆库 (Memory) -> $backupDir"
    }
    
    # 备份配置 (Config)
    if (Test-Path "$agentDst\config\agent_config.md") {
        New-Item -ItemType Directory -Path "$backupDir\config" -Force | Out-Null
        Copy-Item "$agentDst\config\agent_config.md" "$backupDir\config" -Force
        Write-Info "已备份配置文件 (Config)"
    }

    # 备份完整 .agent（用于兜底恢复）
    Copy-Item $agentDst "$backupDir\agent_full" -Recurse -Force
    Write-Info "已备份完整 .agent -> $backupDir"
}

if ($agentSrc -ne $agentDst) {
    if (-not (Test-Path $agentDst)) {
        New-Item -ItemType Directory -Path $agentDst -Force | Out-Null
    }
    Copy-Item "$agentSrc\*" $agentDst -Recurse -Force
    Write-Ok "已更新系统核心 (.agent/) → $agentDst"
} else {
    Write-Ok ".agent/ 已在当前目录，跳过复制"
}

# === 4.1.1 恢复备份 (Restore) ===
if (Test-Path $backupDir) {
    Write-Info "正在恢复用户数据..."
    
    # 恢复记忆
    if (Test-Path "$backupDir\memory") {
        $memoryItems = Get-ChildItem -Path "$backupDir\memory" -Force
        if ($memoryItems.Count -gt 0) {
            Copy-Item "$backupDir\memory\*" "$agentDst\memory" -Recurse -Force
        }
        Write-Ok "记忆库已恢复 (Memory Restored)"
        $memoryRestored = $true
    }
    
    # 恢复配置
    if (Test-Path "$backupDir\config\agent_config.md") {
        Copy-Item "$backupDir\config\agent_config.md" "$agentDst\config\agent_config.md" -Force
        Write-Ok "配置已恢复 (Config Restored)"
    }
    
    Remove-Item $backupDir -Recurse -Force
}

# 4.1.2 建立 .agents 兼容层（Junction -> .agent）
$agentsDst = Join-Path $TargetDir ".agents"
if (Test-Path $agentsDst) { Remove-Item $agentsDst -Recurse -Force }
try {
    New-Item -ItemType Junction -Path $agentsDst -Target ".agent" | Out-Null
    Write-Ok "已创建兼容层 (.agents -> .agent)"
} catch {
    try {
        New-Item -ItemType Junction -Path $agentsDst -Target $agentDst | Out-Null
        Write-Warn "相对 Junction 创建失败，已回退为绝对路径 Junction"
    } catch {
        Copy-Item $agentDst $agentsDst -Recurse -Force
        Write-Warn "Junction 创建失败，已降级为目录复制 (.agents/)"
    }
}

# 4.1.1.1 Flutter 规范包（可选）
if ($stack.sdk -eq "Flutter") {
    Write-Host "   是否下载 flutter-ai-advanced-template 规范包？(y/N): " -NoNewline -ForegroundColor Yellow
    $installFlutterTemplate = Read-Host
    if ($installFlutterTemplate -eq "y" -or $installFlutterTemplate -eq "Y") {
        $gitCmd = Get-Command git -ErrorAction SilentlyContinue
        if (-not $gitCmd) {
            Write-Warn "未检测到 git，跳过规范包下载"
        } else {
            $templateDir = Join-Path $agentDst "templates\flutter-ai-advanced-template"
            if (Test-Path $templateDir) {
                Write-Info "已存在 flutter-ai-advanced-template，跳过下载"
            } else {
                New-Item -ItemType Directory -Force -Path (Split-Path $templateDir) | Out-Null
                git clone --depth 1 https://github.com/flockmaster/flutter-ai-advanced-template.git $templateDir
                Write-Ok "已下载 flutter-ai-advanced-template"
            }
        }
    }
}

# 4.1.2 复制 .github/（Copilot prompts）
$githubSrc = Join-Path $ScriptDir ".github"
$githubDst = Join-Path $TargetDir ".github"
if (Test-Path $githubSrc) {
    if (-not (Test-Path $githubDst)) {
        New-Item -ItemType Directory -Path $githubDst -Force | Out-Null
    }
    Copy-Item "$githubSrc\*" $githubDst -Recurse -Force
    Write-Ok "已复制 .github/ → $githubDst"
} else {
    Write-Info "仓库中无 .github/，跳过复制"
}

# 4.2 清除 __pycache__
Get-ChildItem -Path $agentDst -Filter "__pycache__" -Recurse -Directory | Remove-Item -Recurse -Force
Write-Ok "已清理 __pycache__"

# 4.3 写入 project_decisions.md (仅在未恢复时)
if (-not $memoryRestored -or -not (Test-Path "$agentDst\memory\project_decisions.md")) {
    $decisionsContent = @"
---
project_name: $ProjectName
last_updated: $today
---

# Project Decisions (长期记忆 - 架构决策)

这里记录本项目中不可动摇的"宪法级"技术决策。
**更新机制**: 仅在重大架构变更时由架构师 Agent 更新。
**遗忘机制**: 新方案替代旧方案时，旧方案移至 Deprecated，一周后删除。

## 1. Tech Stack
- SDK: $($stack.sdk)
- Language: $($stack.lang)

## 2. Architecture
- Pattern: $($stack.arch)

## 3. Coding Standards
- Lint: ``$($stack.lint)``
- Formatting: ``$($stack.fmt)``
- Naming: (请根据语言规范填写)

## 4. Third-Party Libs (Whitelist)
> 在此登记项目允许使用的第三方库

| 库名 | 用途 | 添加日期 |
|------|------|---------|
| (示例) | (示例用途) | $today |

## 5. Known Issues (错误模式学习)

| 日期 | 错误类型 | 根因分析 | 修复方案 | 影响范围 |
|------|---------|---------|---------|---------|

## 6. Deprecated (废弃决策归档)
<!-- 旧决策被覆盖后移至此处，保留一周后删除 -->

## 7. UI/UX Standards (Mandatory)
> 仅供前端项目使用，后端项目请忽略
- **Design System**: (如有, 请填入路径)
- **Design Philosophy**: (e.g. Glassmorphism, Brutalism)
- **Icon Set**: (e.g. Lucide, FontAwesome)
- **Verification**: UI 变更必须经过 PM 视觉验收

"@
    Set-Content -Path "$agentDst\memory\project_decisions.md" -Value $decisionsContent -Encoding UTF8
    Write-Ok "已初始化 project_decisions.md"
} else {
    Write-Info "保留现有 project_decisions.md (Skip Init)"
}

# 4.4 重置 active_context.md (如果需要)
if (-not $memoryRestored -or -not (Test-Path "$agentDst\memory\active_context.md")) {
    $contextContent = @"
---
task_status: IDLE
last_session: $today
current_task: null
---

# Active Context (短期记忆 - 当前任务)

> 系统已初始化。输入 ``/start`` 开始你的第一个任务。

## Current Task
无

## History
| 日期 | 任务 | 状态 | 详情链接 |
|------|------|------|---------|

"@
    Set-Content -Path "$agentDst\memory\active_context.md" -Value $contextContent -Encoding UTF8
    Write-Ok "已重置 active_context.md"
} else {
    Write-Info "保留现有 active_context.md (Skip Reset)"
}

# 4.5 更新 agent_config.md 中的 ACTIVE_PROVIDER
$configPath = "$agentDst\config\agent_config.md"
if (Test-Path $configPath) {
    # 只有当用户显式选择的 Provider 与配置文件不同时，才更新配置（或强制同步当前选择）
    # 这里我们假设用户重新 Setup 是为了切换 Provider 或修复，所以更新是安全的。
    # 但如果 Config 是恢复回来的，可能已经是正确的。
    # 简单起见，既然用户在 Step 3 选了 Provider，我们就更新它。
    (Get-Content $configPath -Raw) -replace 'ACTIVE_PROVIDER:\s*\w+', "ACTIVE_PROVIDER: $($provider.name)" |
        Set-Content $configPath -Encoding UTF8
    Write-Ok "已更新 ACTIVE_PROVIDER: $($provider.name)"
}

# 4.6 写入 .gitignore 追加
$gitignorePath = Join-Path $TargetDir ".gitignore"
$agentIgnoreBlock = @"

# === Axiom ===
# 动态文件 (不入库)
.agent/memory/active_context.md
.agent/memory/history/
.agent/memory/evolution/workflow_metrics.md
.agent/memory/evolution/learning_queue.md
.agent/memory/evolution/reflection_log.md
.agent/memory/evolution/pattern_library.md
# agents (compat)
.agents/memory/active_context.md
.agents/memory/history/
.agents/memory/evolution/workflow_metrics.md
.agents/memory/evolution/learning_queue.md
.agents/memory/evolution/reflection_log.md
# 编译缓存
.agent/**/__pycache__/
.agents/**/__pycache__/
"@

if (Test-Path $gitignorePath) {
    $existingLines = Get-Content $gitignorePath
    $rulesToEnsure = @(
        ".agent/memory/active_context.md",
        ".agent/memory/history/",
        ".agent/memory/evolution/workflow_metrics.md",
        ".agent/memory/evolution/learning_queue.md",
        ".agent/memory/evolution/reflection_log.md",
        ".agent/memory/evolution/pattern_library.md",
        ".agents/memory/active_context.md",
        ".agents/memory/history/",
        ".agents/memory/evolution/workflow_metrics.md",
        ".agents/memory/evolution/learning_queue.md",
        ".agents/memory/evolution/reflection_log.md",
        ".agent/**/__pycache__/",
        ".agents/**/__pycache__/"
    )
    $missingRules = @()
    foreach ($rule in $rulesToEnsure) {
        if (-not ($existingLines -contains $rule)) {
            $missingRules += $rule
        }
    }

    if ($missingRules.Count -gt 0) {
        $appendBlock = "`n# === Axiom (补充) ===`n" + ($missingRules -join "`n") + "`n"
        Add-Content -Path $gitignorePath -Value $appendBlock -Encoding UTF8
        Write-Ok "已补齐 .gitignore 缺失规则 ($($missingRules.Count) 条)"
    } else {
        Write-Info ".gitignore 已包含 Axiom 关键规则，跳过"
    }
} else {
    Set-Content -Path $gitignorePath -Value $agentIgnoreBlock.TrimStart() -Encoding UTF8
    Write-Ok "已创建 .gitignore"
}

# ============================================================
# Step 5: 安装全局配置
# ============================================================
Write-Step "Step 5/6 — 安装 AI 全局配置"

$adapterSrc = Join-Path $agentDst $provider.adapter
$globalDirExpanded = $ExecutionContext.InvokeCommand.ExpandString($provider.globalDir)
$globalFilePath = Join-Path $globalDirExpanded $provider.globalFile

# 智能判断：对于支持本地 Context 的 Provider (Gemini CLI)，默认跳过全局配置
$isSmartContext = ($provider.name -eq "gemini_cli")

if ($isSmartContext) {
    Write-Info "检测到 Gemini CLI 智能上下文:"
    Write-Info "   系统会自动直接加载项目级配置 (.agent/adapters/...)"
    Write-Info "   无需安装全局配置，避免 Context 重复和 Token 浪费。"
    
    Write-Host "   是否强制安装全局配置？(y/N) [推荐 N]: " -NoNewline -ForegroundColor Yellow
    $confirm = Read-Host
    $shouldInstall = ($confirm -eq "y" -or $confirm -eq "Y")
} else {
    Write-Host "   将把 Axiom 规则安装到:" -ForegroundColor Yellow
    Write-Host "   → $globalFilePath" -ForegroundColor White
    Write-Host ""
    Write-Host "   是否安装？(Y/n) [默认 Y]: " -NoNewline -ForegroundColor Yellow
    $confirm = Read-Host
    $shouldInstall = ($confirm -eq "" -or $confirm -eq "y" -or $confirm -eq "Y")
}

if ($shouldInstall) {
    if (-not (Test-Path $globalDirExpanded)) {
        New-Item -ItemType Directory -Path $globalDirExpanded -Force | Out-Null
    }
    if (Test-Path $globalFilePath) {
        $backupPath = "$globalFilePath.bak"
        Copy-Item $globalFilePath $backupPath -Force
        Write-Info "已备份原文件 → $backupPath"
    }
    Copy-Item $adapterSrc $globalFilePath -Force
    Write-Ok "已安装全局配置到 $globalFilePath"
} else {
    Write-Ok "已跳过全局配置 (推荐)"
    if (-not $isSmartContext) {
        Write-Info "你可以之后手动复制:"
        Write-Info "  cp $adapterSrc $globalFilePath"
    }
}

# ============================================================
# Step 6 (可选): 检测 CLI 运行环境
# ============================================================
Write-Step "Step 6 (可选) — 检测 CLI 运行环境"

$codexAvailable = $false
$cliChecks = @(
    @{ name = "gemini"; label = "Gemini CLI" },
    @{ name = "claude"; label = "Claude Code" },
    @{ name = "codex"; label = "Codex CLI" },
    @{ name = "opencode"; label = "OpenCode CLI" }
)

foreach ($cli in $cliChecks) {
    try {
        $null = Get-Command $cli.name -ErrorAction Stop
        Write-Ok "$($cli.label) 已安装"
        if ($cli.name -eq "codex") { $codexAvailable = $true }
    } catch {
        Write-Info "$($cli.label) 未检测到"
    }
}

if (-not $codexAvailable) {
    Write-Info "Dispatcher 依赖 Codex CLI，安装方法: npm install -g @openai/codex"
}

# ============================================================
# 完成！
# ============================================================
Write-Host ""
Write-Host "   ╔══════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "   ║   🎉 安装完成！                          ║" -ForegroundColor Green
Write-Host "   ╚══════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "   📂 项目: $ProjectName" -ForegroundColor White
Write-Host "   🔧 技术栈: $($stack.sdk) / $($stack.lang)" -ForegroundColor White
Write-Host "   🤖 AI 工具: $($provider.display)" -ForegroundColor White
if ($codexAvailable) {
    Write-Host "   🎯 Dispatcher: ✅ 可用" -ForegroundColor White
} else {
    Write-Host "   🎯 Dispatcher: ⚠️ 需安装 Codex CLI" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "   👉 下一步:" -ForegroundColor Cyan
Write-Host "      1. 在 IDE 中打开项目" -ForegroundColor White
Write-Host "      2. 对 AI 说: /start" -ForegroundColor White
Write-Host "      3. 开始享受不再失忆的 AI 体验！" -ForegroundColor White
Write-Host ""
