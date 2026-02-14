# ============================================================
# Axiom — Post-commit Guard (T-302) [Windows]
#
# PowerShell 版本，适用于 Windows Git 环境
# ============================================================

$GUARD_NAME = "Axiom Guard"
$CHECKPOINT_INTERVAL = 1800  # 30 分钟

# ── 1. 获取上一个 checkpoint tag ──
$lastCP = git tag -l "checkpoint-*" --sort=-creatordate 2>$null | Select-Object -First 1
$createTag = $false

if (-not $lastCP) {
    $createTag = $true
} else {
    try {
        $lastCPTime = [int](git log -1 --format="%ct" $lastCP 2>$null)
        $currentTime = [int](Get-Date -UFormat %s)
        $diff = $currentTime - $lastCPTime
        if ($diff -gt $CHECKPOINT_INTERVAL) {
            $createTag = $true
        }
    } catch {
        $createTag = $true
    }
}

# ── 2. 创建 checkpoint tag ──
if ($createTag) {
    $tagName = "checkpoint-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    $result = git tag $tagName 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ [$GUARD_NAME] 检查点已创建: $tagName" -ForegroundColor Green
    } else {
        Write-Host "⚠️  [$GUARD_NAME] 检查点创建失败 (非阻断)" -ForegroundColor Yellow
    }
}

# ── 3. 统计本次提交变更 ──
try {
    $changedFiles = (git diff --name-only HEAD~1 HEAD 2>$null) | Measure-Object | Select-Object -ExpandProperty Count
    $agentFiles = (git diff --name-only HEAD~1 HEAD 2>$null) | Where-Object { $_ -like ".agent/*" } | Measure-Object | Select-Object -ExpandProperty Count

    if ($agentFiles -gt 0) {
        Write-Host "📊 [$GUARD_NAME] 本次提交: $changedFiles 文件 (其中 $agentFiles 个 Agent 文件)" -ForegroundColor Cyan
    }
} catch {
    # 静默忽略
}

exit 0
