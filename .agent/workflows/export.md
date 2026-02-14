---
description: Export Command - 导出 Axiom 系统为可移植压缩包
---

# /export - 系统导出

从当前项目中提取 **Axiom** 的完整或模板版本，生成可复用的压缩包。

## Trigger
- 用户输入 `/export` 或 `/export template` 或 `/export full`

## 导出模式

### 模式 1: Template (模板导出) - 默认
用于创建新项目时的干净起点。

**包含**:
- `.agent/` 目录结构（当前主结构：memory/skills/workflows）
- `.github/`（Copilot 配置与 Prompt Files）
- `.gemini/GEMINI.md.example`（如存在）
- `README.md`

**清空/重置**:
- `active_context.md` → 重置为初始模板
- `knowledge/` → 清空，只保留 `.gitkeep`
- `evolution/*.md` → 重置为初始模板
- `history/` → 清空

**保留**:
- 所有工作流定义 (`workflows/*.md`)
- 所有技能定义 (`skills/*/SKILL.md`)
- 路由规则 (`rules/router.rule`)
- 状态机定义 (`state_machine.md`)
- 用户偏好模板 (`user_preferences.md`)
- 项目决策模板 (`project_decisions.md`)

### 模式 2: Full (完整导出)
用于备份或迁移整个系统状态。

**包含**: 所有文件，原样打包。

## Steps

### Step 0: 解析项目根目录
// turbo
1. 优先使用 Git 根目录作为 `PROJECT_ROOT`：`git rev-parse --show-toplevel`。
2. 若非 Git 仓库，则使用当前工作目录作为 `PROJECT_ROOT`。
3. 回显：`Project root: $PROJECT_ROOT`。

### Step 1: 确定导出模式
// turbo
1. 解析用户输入，确定是 `template` 还是 `full`。
2. 默认为 `template`。

### Step 2: 创建临时目录
```bash
exportDir="$(mktemp -d -t axiom-export-XXXXXXXX)"
echo "Export temp dir: $exportDir"
```

```powershell
$exportDir = Join-Path $env:TEMP ("axiom-export-" + [System.Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $exportDir -Force | Out-Null
Write-Host "Export temp dir: $exportDir"
```

### Step 3: 复制系统文件
```bash
rsync -a "$PROJECT_ROOT/.agent" "$exportDir/" 2>/dev/null || true
[ -d "$PROJECT_ROOT/.github" ] && rsync -a "$PROJECT_ROOT/.github" "$exportDir/"
[ -d "$PROJECT_ROOT/.gemini" ] && rsync -a "$PROJECT_ROOT/.gemini" "$exportDir/"
[ -f "$PROJECT_ROOT/README.md" ] && rsync -a "$PROJECT_ROOT/README.md" "$exportDir/"
```

```powershell
if (Test-Path "$PROJECT_ROOT/.agent") { Copy-Item "$PROJECT_ROOT/.agent" "$exportDir" -Recurse -Force }
if (Test-Path "$PROJECT_ROOT/.github") { Copy-Item "$PROJECT_ROOT/.github" "$exportDir" -Recurse -Force }
if (Test-Path "$PROJECT_ROOT/.gemini") { Copy-Item "$PROJECT_ROOT/.gemini" "$exportDir" -Recurse -Force }
if (Test-Path "$PROJECT_ROOT/README.md") { Copy-Item "$PROJECT_ROOT/README.md" "$exportDir" -Force }
```

### Step 4: Template 模式清理 (仅 template 模式)
1. 重置 `active_context.md`:
   ```yaml
   ---
   session_id: null
   task_status: IDLE
   auto_fix_attempts: 0
   last_checkpoint: null
   stash_applied: false
   ---
   ```
2. 清空 `knowledge/` 目录，保留 `.gitkeep`
3. 重置 `evolution/` 目录下的所有文件为初始模板
4. 清空 `history/` 目录

### Step 5: 生成压缩包
```bash
zipName="axiom-export-$(date +%Y%m%d).zip"
outputPath="$PROJECT_ROOT/$zipName"
(cd "$exportDir" && zip -rq "$outputPath" .)
echo "Output: $outputPath"
```

```powershell
$zipName = "axiom-export-$(Get-Date -Format yyyyMMdd).zip"
$outputPath = Join-Path $PROJECT_ROOT $zipName
Compress-Archive -Path (Join-Path $exportDir "*") -DestinationPath $outputPath -Force
Write-Host "Output: $outputPath"
```

### Step 6: 清理临时目录
```bash
rm -rf "$exportDir"
```

```powershell
Remove-Item $exportDir -Recurse -Force
```

### Step 7: 输出结果
报告压缩包位置和大小。

## Output Format
```markdown
## 📦 Export Complete

**Mode**: Template / Full
**Output**: `axiom-export-20260208.zip`
**Size**: X KB
**Location**: `[PROJECT_ROOT]/axiom-export-20260208.zip`

### Included
- `.agent/` (workflows, skills, rules, memory templates)
- `.gemini/GEMINI.md.example`
- `README.md`

### Usage
1. 解压到新项目根目录
2. 编辑 `.agent/memory/project_decisions.md` 配置项目信息
3. 如存在 `.gemini/GEMINI.md.example`，复制其内容到全局配置
4. 输入 `/start` 开始使用
```

## 使用示例

| 命令 | 效果 |
|-----|-----|
| `/export` | 导出模板版本（干净） |
| `/export template` | 同上 |
| `/export full` | 导出完整版本（含所有知识） |
