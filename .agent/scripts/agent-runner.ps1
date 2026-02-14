#!/usr/bin/env pwsh
# .agent/scripts/agent-runner.ps1
# Agent Execution Lifecycle Manager
# 1. Pre-Execution: Check Watchdog Status -> Inject Prompt if needed.
# 2. Execution: Run the Agent (Codex Worker).
# 3. Post-Execution: Update Memory Status (for next turn).

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$CodexArgs
)

# 1. Resolve Environment
$ScriptDir = $PSScriptRoot
$AgentRoot = Resolve-Path "$ScriptDir\..\.."
$ContextFile = Join-Path $AgentRoot ".agent\memory\active_context.md"
$CheckScript = Join-Path $ScriptDir "Check-Memory.ps1"

# 2. Extract Session ID (default: 'unknown')
$SessionId = "unknown"
if (Test-Path $ContextFile) {
    try {
        $Content = Get-Content $ContextFile -Raw -ErrorAction SilentlyContinue
        if ($Content -match 'session_id:\s*"?([^"\r\n]+)"?') {
            $SessionId = $Matches[1].Trim()
        }
    } catch {
        # Ignore read errors
    }
}

# 3. Pre-Execution Hook: Check Watchdog Status & Inject Prompt
$StatusLockFile = Join-Path $AgentRoot ".agent\memory\watchdog_status.lock"
$WatchdogStatus = "NORMAL"
$InjectionPre = ""
$InjectionPost = ""

if (Test-Path $StatusLockFile) {
    try {
        $JsonContent = Get-Content $StatusLockFile -Raw -ErrorAction SilentlyContinue | ConvertFrom-Json
        if ($JsonContent.status) { $WatchdogStatus = $JsonContent.status }
    } catch {
        # Default to NORMAL on error
    }
}
# Debug Output (Hidden in production or used for verbose logging)
# Write-Host " [Watchdog-Debug] Status: $WatchdogStatus" -ForegroundColor Cyan

if ($WatchdogStatus -eq "WARNING") {
    $InjectionPost = "`n`n[Warning: Memory Limit Approaching. Please be concise.]"
    Write-Host " [Watchdog] Injecting WARNING prompt." -ForegroundColor Yellow
} elseif ($WatchdogStatus -eq "CRITICAL") {
    $InjectionPre = "[CRITICAL: Memory Limit Reached. Please run /suspend immediately.]`n`n"
    Write-Host " [Watchdog] Injecting CRITICAL prompt." -ForegroundColor Red
}

# 4. Define Post-Execution Hook Function
function Invoke-MemoryUpdate {
    if (Test-Path $CheckScript) {
        # Write-Host " [Watchdog] Updating memory status..." -ForegroundColor DarkGray
        
        # Run detached to avoid blocking user response
        try {
            # Use 'powershell' (Windows 5.1+) or 'pwsh' (Core 6+)
            $PSExe = if (Get-Command pwsh -ErrorAction SilentlyContinue) { "pwsh" } else { "powershell" }
            $p = Start-Process -FilePath $PSExe -ArgumentList "-NoProfile", "-File", "`"$CheckScript`"", "-SessionId", "`"$SessionId`"" -PassThru -WindowStyle Hidden -ErrorAction SilentlyContinue
            
            # Wait up to 2 seconds (Failsafe)
            if ($null -ne $p) {
                if ($p.WaitForExit(2000)) {
                    # Completed
                } else {
                    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
                    # Write-Host " [Watchdog] Update timed out." -ForegroundColor DarkYellow
                }
            }
        } catch {
            Write-Host " [Watchdog] Failed to execute status update: $_" -ForegroundColor DarkYellow
        }
    }
}

# 5. Execution Phase (Run Worker)
try {
    # Check if input is being piped
    if ($MyInvocation.ExpectingInput) {
        $InputContent = $Input | Out-String
        # Inject warning/critical messages into the prompt stream
        $FinalInput = "${InjectionPre}${InputContent}${InjectionPost}"
        $FinalInput | codex exec @CodexArgs
    } else {
        # Direct execution without stdin injection
        if ($WatchdogStatus -ne "NORMAL") {
             Write-Host " [Watchdog] Alert: Status is $WatchdogStatus (Input injection skipped for non-interactive mode)." -ForegroundColor Yellow
        }
        codex exec @CodexArgs
    }
} finally {
    # 6. Post-Execution Phase
    Invoke-MemoryUpdate
}
