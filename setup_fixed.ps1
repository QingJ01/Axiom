#!/usr/bin/env pwsh
# Deprecated wrapper: use setup.ps1

param(
    [string]$TargetDir = ""
)

$ErrorActionPreference = "Stop"

Write-Host "[Axiom] setup_fixed.ps1 已弃用，自动转发到 setup.ps1" -ForegroundColor Yellow

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$mainSetup = Join-Path $scriptDir "setup.ps1"

if (-not (Test-Path $mainSetup)) {
    throw "未找到 setup.ps1: $mainSetup"
}

if ($TargetDir -ne "") {
    & $mainSetup -TargetDir $TargetDir
} else {
    & $mainSetup
}
