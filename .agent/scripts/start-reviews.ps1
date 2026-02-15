#!/usr/bin/env pwsh

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Args
)

$ScriptDir = $PSScriptRoot
$Runner = Join-Path $ScriptDir "agent-runner.ps1"

if (-not (Test-Path $Runner)) {
    Write-Error "agent-runner.ps1 not found: $Runner"
    exit 1
}

# Route review execution through watchdog-aware runner.
# The command text keeps compatibility with previous docs/tests.
$ReviewPrompt = if ($Args.Count -gt 0) { $Args -join " " } else { "执行 review 流程" }
& pwsh -NoProfile -File $Runner --prompt "$ReviewPrompt" "codex exec"
