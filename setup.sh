#!/usr/bin/env bash
# ============================================================
#  Axiom — 初始化向导 (macOS / Linux)
#  用法: bash setup.sh [target_dir]
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${1:-}"

# ── 颜色 ──────────────────────────────────────────────────
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
MAGENTA='\033[0;35m'
GRAY='\033[0;90m'
RED='\033[0;31m'
NC='\033[0m'

step()  { echo -e "\n${CYAN}🔧 $1${NC}"; }
ok()    { echo -e "   ${GREEN}✅ $1${NC}"; }
info()  { echo -e "   ${GRAY}ℹ️  $1${NC}"; }
warn()  { echo -e "   ${YELLOW}⚠️  $1${NC}"; }
prompt(){ echo -en "   ${YELLOW}$1${NC}"; }

# ── Banner ────────────────────────────────────────────────
echo ""
echo -e "${MAGENTA}   ╔══════════════════════════════════════════╗${NC}"
echo -e "${MAGENTA}   ║   🌌 Axiom — Setup        ║${NC}"
echo -e "${MAGENTA}   ║   给你的 AI 编程助手装上大脑              ║${NC}"
echo -e "${GRAY}   ║   https://github.com/flockmaster/axiom║${NC}"
echo -e "${MAGENTA}   ╚══════════════════════════════════════════╝${NC}"
echo ""

# ============================================================
# Step 1: 选择目标项目
# ============================================================
step "Step 1/6 — 设置目标项目"

if [ -z "$TARGET_DIR" ]; then
    prompt "请输入你的项目路径 (留空 = 当前目录): "
    read -r TARGET_DIR
    [ -z "$TARGET_DIR" ] && TARGET_DIR="$(pwd)"
fi
TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd)" || { echo -e "   ${RED}❌ 路径不存在${NC}"; exit 1; }
ok "目标目录: $TARGET_DIR"

# 检测是否已初始化
if [ -f "$TARGET_DIR/.agent/memory/active_context.md" ]; then
    warn "检测到该项目已安装 Axiom (.agent/ 已存在)。"
    prompt "是否覆盖配置？(y/N): "
    read -r overwrite
    [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ] && { echo -e "   👋 已取消。"; exit 0; }
fi

# ============================================================
# Step 2: 项目信息
# ============================================================
step "Step 2/6 — 项目信息"

prompt "项目名称: "
read -r PROJECT_NAME
[ -z "$PROJECT_NAME" ] && PROJECT_NAME="$(basename "$TARGET_DIR")"

echo ""
echo -e "   ${YELLOW}选择技术栈:${NC}"
echo "     [1] Flutter / Dart"
echo "     [2] React / TypeScript"
echo "     [3] Vue / TypeScript"
echo "     [4] Python / Django"
echo "     [5] Node.js / Express"
echo "     [6] Go / Gin"
echo "     [0] 自定义"
prompt "输入编号 (默认 1): "
read -r stack_choice
[ -z "$stack_choice" ] && stack_choice="1"

case "$stack_choice" in
    1) SDK="Flutter";  LANG="Dart";       ARCH="MVVM";              LINT="flutter_lints"; FMT="dart format";   CMD_RUN="flutter run";                  CMD_TEST="flutter test";           CMD_ANALYZE="flutter analyze";  CMD_BUILD="flutter build" ;;
    2) SDK="React";    LANG="TypeScript";  ARCH="Component";         LINT="eslint";        FMT="prettier";      CMD_RUN="npm run dev";                  CMD_TEST="npm test";               CMD_ANALYZE="npm run lint";     CMD_BUILD="npm run build" ;;
    3) SDK="Vue";      LANG="TypeScript";  ARCH="Composition API";   LINT="eslint";        FMT="prettier";      CMD_RUN="npm run dev";                  CMD_TEST="npm test";               CMD_ANALYZE="npm run lint";     CMD_BUILD="npm run build" ;;
    4) SDK="Django";   LANG="Python";      ARCH="MTV";               LINT="flake8";        FMT="black";         CMD_RUN="python manage.py runserver";   CMD_TEST="python manage.py test";  CMD_ANALYZE="flake8 .";         CMD_BUILD="N/A" ;;
    5) SDK="Express";  LANG="JavaScript";  ARCH="MVC";               LINT="eslint";        FMT="prettier";      CMD_RUN="npm start";                    CMD_TEST="npm test";               CMD_ANALYZE="npm run lint";     CMD_BUILD="npm run build" ;;
    6) SDK="Gin";      LANG="Go";          ARCH="Clean Architecture";LINT="golint";        FMT="gofmt";         CMD_RUN="go run .";                     CMD_TEST="go test ./...";          CMD_ANALYZE="go vet ./...";     CMD_BUILD="go build" ;;
    0) prompt "SDK/框架: "; read -r SDK
       prompt "语言: ";     read -r LANG
       prompt "架构: ";     read -r ARCH
       LINT="N/A"; FMT="N/A"; CMD_RUN="N/A"; CMD_TEST="N/A"; CMD_ANALYZE="N/A"; CMD_BUILD="N/A" ;;
    *) SDK="Flutter"; LANG="Dart"; ARCH="MVVM"; LINT="flutter_lints"; FMT="dart format"; CMD_RUN="flutter run"; CMD_TEST="flutter test"; CMD_ANALYZE="flutter analyze"; CMD_BUILD="flutter build" ;;
esac

ok "项目: $PROJECT_NAME | $SDK / $LANG / $ARCH"

# ============================================================
# Step 3: 选择 AI 工具
# ============================================================
step "Step 3/6 — 选择你的 AI 编程工具"

echo "     [1] Gemini CLI"
echo "     [2] Claude Code"
echo "     [3] Codex CLI"
echo "     [4] OpenCode CLI"
echo "     [5] GitHub Copilot (VS Code / JetBrains)"
prompt "输入编号 (默认 1): "
read -r ai_choice
[ -z "$ai_choice" ] && ai_choice="1"

case "$ai_choice" in
    1) PROVIDER="gemini_cli";  DISPLAY="Gemini CLI";  ADAPTER="adapters/gemini-cli/GEMINI-CLI.md";        GLOBAL_DIR="$HOME/.gemini"; GLOBAL_FILE="GEMINI.md" ;;
    2) PROVIDER="claude_code"; DISPLAY="Claude Code"; ADAPTER="adapters/claude-code/CLAUDE-CODE.md";     GLOBAL_DIR="$HOME/.claude"; GLOBAL_FILE="CLAUDE.md" ;;
    3) PROVIDER="codex";       DISPLAY="Codex CLI";   ADAPTER="adapters/codex/CODEX.md";                  GLOBAL_DIR="$HOME/.codex"; GLOBAL_FILE="config.md" ;;
    4) PROVIDER="opencode";    DISPLAY="OpenCode CLI"; ADAPTER="adapters/opencode/OPENCODE.md";          GLOBAL_DIR="$HOME/.opencode"; GLOBAL_FILE="OPENCODE.md" ;;
    5) PROVIDER="copilot";     DISPLAY="Copilot";     ADAPTER="adapters/copilot/copilot-instructions.md"; GLOBAL_DIR="$HOME/.copilot"; GLOBAL_FILE="copilot-instructions.md" ;;
    *) PROVIDER="gemini_cli";  DISPLAY="Gemini CLI";  ADAPTER="adapters/gemini-cli/GEMINI-CLI.md";        GLOBAL_DIR="$HOME/.gemini"; GLOBAL_FILE="GEMINI.md" ;;
esac
ok "AI 工具: $DISPLAY"

# ============================================================
# Step 4: 复制文件并初始化
# ============================================================
step "Step 4/6 — 安装 Axiom 到项目"
TODAY="$(date +%Y-%m-%d)"

AGENT_SRC="$SCRIPT_DIR/.agent"
AGENT_DST="$TARGET_DIR/.agent"

# === 4.1.0 智能备份 (Smart Backup) ===
MEMORY_RESTORED=false
BACKUP_DIR="/tmp/agent_os_backup_$(date +%s)"

if [ -d "$AGENT_DST" ]; then
    info "检测到现有 Axiom，启动 [智能无损更新] 模式..."
    mkdir -p "$BACKUP_DIR"
    
    # 备份记忆 (Memory)
    if [ -d "$AGENT_DST/memory" ]; then
        cp -r "$AGENT_DST/memory" "$BACKUP_DIR/"
        info "已备份记忆库 (Memory) -> $BACKUP_DIR"
    fi
    
    # 备份配置 (Config)
    if [ -f "$AGENT_DST/config/agent_config.md" ]; then
        mkdir -p "$BACKUP_DIR/config"
        cp "$AGENT_DST/config/agent_config.md" "$BACKUP_DIR/config/"
        info "已备份配置文件 (Config)"
    fi

    # 备份完整 .agent（用于兜底恢复）
    cp -r "$AGENT_DST" "$BACKUP_DIR/agent_full"
    info "已备份完整 .agent -> $BACKUP_DIR"
fi

# 4.1 复制 .agent/
if [ "$AGENT_SRC" != "$AGENT_DST" ]; then
    mkdir -p "$AGENT_DST"
    cp -r "$AGENT_SRC"/. "$AGENT_DST/"
    ok "已更新系统核心 (.agent/) → $AGENT_DST"
else
    ok ".agent/ 已在当前目录，跳过复制"
fi

# === 4.1.1 恢复备份 (Restore) ===
if [ -d "$BACKUP_DIR" ]; then
    info "正在恢复用户数据..."
    
    # 恢复记忆
    if [ -d "$BACKUP_DIR/memory" ]; then
        if [ "$(find "$BACKUP_DIR/memory" -mindepth 1 -print -quit)" ]; then
            cp -r "$BACKUP_DIR/memory"/. "$AGENT_DST/memory/"
        fi
        ok "记忆库已恢复 (Memory Restored)"
        MEMORY_RESTORED=true
    fi
    
    # 恢复配置
    if [ -f "$BACKUP_DIR/config/agent_config.md" ]; then
        cp "$BACKUP_DIR/config/agent_config.md" "$AGENT_DST/config/agent_config.md"
        ok "配置已恢复 (Config Restored)"
    fi
    
    rm -rf "$BACKUP_DIR"
fi

# 4.1.1.1 Flutter 规范包（可选）
if [ "$SDK" = "Flutter" ]; then
    prompt "是否下载 flutter-ai-advanced-template 规范包？(y/N): "
    read -r install_flutter_template
    if [ "$install_flutter_template" = "y" ] || [ "$install_flutter_template" = "Y" ]; then
        if ! command -v git >/dev/null 2>&1; then
            warn "未检测到 git，跳过规范包下载"
        else
            mkdir -p "$AGENT_DST/templates"
            if [ -d "$AGENT_DST/templates/flutter-ai-advanced-template" ]; then
                info "已存在 flutter-ai-advanced-template，跳过下载"
            else
                git clone --depth 1 https://github.com/flockmaster/flutter-ai-advanced-template.git \
                    "$AGENT_DST/templates/flutter-ai-advanced-template"
                ok "已下载 flutter-ai-advanced-template"
            fi
        fi
    fi
fi

# 4.1.2 复制 .github/（Copilot prompts）
GITHUB_SRC="$SCRIPT_DIR/.github"
GITHUB_DST="$TARGET_DIR/.github"
if [ -d "$GITHUB_SRC" ]; then
    mkdir -p "$GITHUB_DST"
    cp -r "$GITHUB_SRC"/. "$GITHUB_DST/"
    ok "已复制 .github/ → $GITHUB_DST"
else
    info "仓库中无 .github/，跳过复制"
fi

# 4.2 清除 __pycache__
find "$AGENT_DST" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
ok "已清理 __pycache__"

# 4.3 写入 project_decisions.md (仅在未恢复时)
if [ "$MEMORY_RESTORED" = "false" ] || [ ! -f "$AGENT_DST/memory/project_decisions.md" ]; then
    cat > "$AGENT_DST/memory/project_decisions.md" << EOF
---
project_name: $PROJECT_NAME
last_updated: $TODAY
---

# Project Decisions (长期记忆 - 架构决策)

这里记录本项目中不可动摇的"宪法级"技术决策。
**更新机制**: 仅在重大架构变更时由架构师 Agent 更新。
**遗忘机制**: 新方案替代旧方案时，旧方案移至 Deprecated，一周后删除。

## 1. Tech Stack
- SDK: $SDK
- Language: $LANG

## 2. Architecture
- Pattern: $ARCH

## 3. Coding Standards
- Lint: \`$LINT\`
- Formatting: \`$FMT\`
- Naming: (请根据语言规范填写)

## 4. Third-Party Libs (Whitelist)
> 在此登记项目允许使用的第三方库

| 库名 | 用途 | 添加日期 |
|------|------|---------|
| (示例) | (示例用途) | $TODAY |

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

EOF
    ok "已初始化 project_decisions.md"
else
    info "保留现有 project_decisions.md (Skip Init)"
fi

# 4.4 重置 active_context.md (如果需要)
if [ "$MEMORY_RESTORED" = "false" ] || [ ! -f "$AGENT_DST/memory/active_context.md" ]; then
    cat > "$AGENT_DST/memory/active_context.md" << EOF
---
task_status: IDLE
last_session: $TODAY
current_task: null
---

# Active Context (短期记忆 - 当前任务)

> 系统已初始化。输入 \`/start\` 开始你的第一个任务。

## Current Task
无

## History
| 日期 | 任务 | 状态 | 详情链接 |
|------|------|------|---------|

EOF
    ok "已重置 active_context.md"
else
    info "保留现有 active_context.md (Skip Reset)"
fi

# 4.5 更新 ACTIVE_PROVIDER
CONFIG_PATH="$AGENT_DST/config/agent_config.md"
if [ -f "$CONFIG_PATH" ]; then
    sed -i.bak "s/ACTIVE_PROVIDER: .*/ACTIVE_PROVIDER: $PROVIDER/" "$CONFIG_PATH" && rm -f "$CONFIG_PATH.bak"
    ok "已更新 ACTIVE_PROVIDER: $PROVIDER"
fi

# 4.6 .gitignore
GITIGNORE_PATH="$TARGET_DIR/.gitignore"
AGENT_IGNORE='
# === Axiom ===
# 动态文件 (不入库)
# agent (legacy)
.agent/memory/active_context.md
.agent/memory/history/
.agent/memory/evolution/workflow_metrics.md
.agent/memory/evolution/learning_queue.md
.agent/memory/reflection_log.md
.agent/memory/evolution/pattern_library.md
# 编译缓存
.agent/**/__pycache__/'

if [ -f "$GITIGNORE_PATH" ]; then
    rules_to_ensure=(
        ".agent/memory/active_context.md"
        ".agent/memory/history/"
        ".agent/memory/evolution/workflow_metrics.md"
        ".agent/memory/evolution/learning_queue.md"
        ".agent/memory/reflection_log.md"
        ".agent/memory/evolution/pattern_library.md"
        ".agent/**/__pycache__/"
    )

    missing_count=0
    for rule in "${rules_to_ensure[@]}"; do
        if ! grep -Fxq "$rule" "$GITIGNORE_PATH"; then
            if [ "$missing_count" -eq 0 ]; then
                {
                    echo ""
                    echo "# === Axiom (补充) ==="
                } >> "$GITIGNORE_PATH"
            fi
            echo "$rule" >> "$GITIGNORE_PATH"
            missing_count=$((missing_count + 1))
        fi
    done

    if [ "$missing_count" -gt 0 ]; then
        ok "已补齐 .gitignore 缺失规则 (${missing_count} 条)"
    else
        info ".gitignore 已包含 Axiom 关键规则，跳过"
    fi
else
    echo "$AGENT_IGNORE" > "$GITIGNORE_PATH"
    ok "已创建 .gitignore"
fi

# ============================================================
# Step 5: 安装全局配置
# ============================================================
step "Step 5/6 — 安装 AI 全局配置"

ADAPTER_SRC="$AGENT_DST/$ADAPTER"
GLOBAL_PATH="$GLOBAL_DIR/$GLOBAL_FILE"

IS_SMART_CONTEXT=false
if [ "$PROVIDER" = "gemini_cli" ]; then
    IS_SMART_CONTEXT=true
fi

if [ "$IS_SMART_CONTEXT" = true ]; then
    info "检测到 Gemini CLI 智能上下文:"
    info "   系统会自动直接加载项目级配置 (.agent/adapters/...)"
    info "   无需安装全局配置，避免 Context 重复和 Token 浪费。"
    prompt "是否强制安装全局配置？(y/N) [推荐 N]: "
    read -r install_global
    should_install=false
    if [ "$install_global" = "y" ] || [ "$install_global" = "Y" ]; then
        should_install=true
    fi
else
    echo -e "   ${YELLOW}将把 Axiom 规则安装到:${NC}"
    echo -e "   → $GLOBAL_PATH"
    echo ""
    prompt "是否安装？(Y/n) [默认 Y]: "
    read -r install_global
    should_install=false
    if [ "$install_global" = "" ] || [ "$install_global" = "y" ] || [ "$install_global" = "Y" ]; then
        should_install=true
    fi
fi

if [ "$should_install" = true ]; then
    mkdir -p "$GLOBAL_DIR"
    if [ -f "$GLOBAL_PATH" ]; then
        cp "$GLOBAL_PATH" "$GLOBAL_PATH.bak"
        info "已备份原文件 → $GLOBAL_PATH.bak"
    fi
    cp "$ADAPTER_SRC" "$GLOBAL_PATH"
    ok "已安装全局配置到 $GLOBAL_PATH"
else
    ok "已跳过全局配置 (推荐)"
    if [ "$IS_SMART_CONTEXT" = false ]; then
        info "你可以之后手动复制:"
        info "  cp $ADAPTER_SRC $GLOBAL_PATH"
    fi
fi

# ============================================================
# Step 6 (可选): 检测 CLI 运行环境
# ============================================================
step "Step 6 (可选) — 检测 CLI 运行环境"

CODEX_AVAILABLE=false
for cli in gemini claude codex opencode; do
    if command -v "$cli" &>/dev/null; then
        ok "$cli 已安装"
        if [ "$cli" = "codex" ]; then
            CODEX_AVAILABLE=true
        fi
    else
        info "$cli 未检测到"
    fi
done

if [ "$CODEX_AVAILABLE" = false ]; then
    info "Dispatcher 依赖 Codex CLI，安装方法: npm install -g @openai/codex"
fi

# ============================================================
# 完成！
# ============================================================
echo ""
echo -e "${GREEN}   ╔══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}   ║   🎉 安装完成！                          ║${NC}"
echo -e "${GREEN}   ╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "   📂 项目: ${NC}$PROJECT_NAME"
echo -e "   🔧 技术栈: ${NC}$SDK / $LANG"
echo -e "   🤖 AI 工具: ${NC}$DISPLAY"
if [ "$CODEX_AVAILABLE" = true ]; then
    echo -e "   🎯 Dispatcher: ${GREEN}✅ 可用${NC}"
else
    echo -e "   🎯 Dispatcher: ${YELLOW}⚠️ 需安装 Codex CLI${NC}"
fi
echo ""
echo -e "   ${CYAN}👉 下一步:${NC}"
echo "      1. 在 IDE 中打开项目"
echo "      2. 对 AI 说: /start"
echo "      3. 开始享受不再失忆的 AI 体验！"
echo ""
