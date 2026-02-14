#!/usr/bin/env pwsh
# .agent/scripts/Watch-Memory.ps1
# Real-time Memory Watchdog: Monitors .pb file changes and updates status lock.

param(
    [int]$ThresholdMB = 2,
    [bool]$ShowToasts = $true
)

# 1. Setup Paths
$ScriptDir = $PSScriptRoot
$AgentRoot = Resolve-Path "$ScriptDir\..\.."
$MemoryDir = Join-Path $AgentRoot ".agent\memory"
$StatusFile = Join-Path $MemoryDir "watchdog_status.lock"
$TempFile = Join-Path $MemoryDir "watchdog_status.tmp"

# Dynamic detection for Axiom Paths
$HomeDir = [Environment]::GetFolderPath("UserProfile")
if ([string]::IsNullOrEmpty($HomeDir)) {
    $HomeDir = $HOME
}

if ([string]::IsNullOrEmpty($HomeDir)) {
    Write-Host "Error: Could not determine HOME directory." -ForegroundColor Red
    exit 1
}

$ConversationsDir = Join-Path $HomeDir ".gemini\axiom\conversations"

if (-not (Test-Path $ConversationsDir)) {
    Write-Host "Error: Conversations directory not found: $ConversationsDir" -ForegroundColor Red
    exit 1
}

Write-Host " [Watchdog] Starting Real-time Monitor..." -ForegroundColor Cyan
Write-Host "   Target: $ConversationsDir" -ForegroundColor DarkGray
Write-Host "   Threshold: $ThresholdMB MB" -ForegroundColor DarkGray
Write-Host "   Status File: $StatusFile" -ForegroundColor DarkGray

# Global Cached State
$Global:LastCheck = @{
    FileName = ""
    SizeMB   = 0.0
    Status   = "NORMAL"
    Time     = 0 # timestamp
}

# 2. Define Action Block
$Action = {
    $FilePath = $Event.SourceEventArgs.FullPath
    $ChangeType = $Event.SourceEventArgs.ChangeType
    $FileName = $Event.SourceEventArgs.Name
    
    # We only care about .pb files
    if ($FileName -like "*.pb") {
        try {
            # Debounce: Wait a tiny bit for write to complete
            Start-Sleep -Milliseconds 200
            
            $Item = Get-Item $FilePath -ErrorAction SilentlyContinue
            if ($null -eq $Item) { return }
            
            $SizeMB = [math]::Round($Item.Length / 1MB, 4)
            $Status = "NORMAL"
            
            if ($SizeMB -ge $ThresholdMB) {
                $Status = "CRITICAL"
                $Color = "Red"
            }
            elseif ($SizeMB -ge ($ThresholdMB * 0.8)) {
                $Status = "WARNING"
                $Color = "Yellow"
            }
            else {
                $Color = "Green"
            }

            # --- OPTIMIZATION START ---
            $CurrentTime = [int64]((Get-Date).ToUniversalTime() - (Get-Date "1970-01-01")).TotalSeconds
            
            # Check if redundant update
            $IsSameFile = ($FileName -eq $Global:LastCheck.FileName)
            $IsSameStatus = ($Status -eq $Global:LastCheck.Status)
            $SizeDiff = [math]::Abs($SizeMB - $Global:LastCheck.SizeMB)
            $TimeSinceLast = $CurrentTime - $Global:LastCheck.Time

            # Rule 1: If exactly same status and size negligible change (< 0.01 MB), skip
            if ($IsSameFile -and $IsSameStatus -and ($SizeDiff -lt 0.01)) {
                return
            }
            
            # Update Cache
            $Global:LastCheck.FileName = $FileName
            $Global:LastCheck.SizeMB = $SizeMB
            $Global:LastCheck.Status = $Status
            $Global:LastCheck.Time = $CurrentTime
            # --- OPTIMIZATION END ---
            
            # Print Log
            $TimeStr = Get-Date -Format "HH:mm:ss"
            Write-Host (" [{0}] {1}: {2} -> {3} MB ({4})" -f $TimeStr, $ChangeType, $FileName, $SizeMB, $Status) -ForegroundColor $Color

            # Update Lock File Logic
            if ($Status -ne "NORMAL") {
                $Payload = @{
                    status     = $Status
                    size_mb    = $SizeMB
                    limit_mb   = $ThresholdMB
                    timestamp  = $CurrentTime
                    session_id = $FileName
                } | ConvertTo-Json -Compress
                
                $Payload | Set-Content -Path $TempFile -Encoding UTF8 -Force
                Move-Item -Path $TempFile -Destination $StatusFile -Force
            }
            else {
                # Clear lock file if back to normal (But only do it ONCE when status CHANGES to normal)
                if ($IsSameStatus -eq $false -and (Test-Path $StatusFile)) {
                    $Payload = @{ status = "NORMAL"; timestamp = $CurrentTime; session_id = $FileName } | ConvertTo-Json -Compress
                    $Payload | Set-Content -Path $TempFile -Encoding UTF8 -Force
                    Move-Item -Path $TempFile -Destination $StatusFile -Force
                    Write-Host " [Watchdog] cleared status lock." -ForegroundColor Gray
                }
            }
        }
        catch {
            Write-Host "Error processing event: $_" -ForegroundColor Red
        }
    }
}

# 3. Setup FileSystemWatcher
$Watcher = New-Object System.IO.FileSystemWatcher
$Watcher.Path = $ConversationsDir
$Watcher.Filter = "*.pb"
$Watcher.IncludeSubdirectories = $false
$Watcher.EnableRaisingEvents = $true

# Register Events
Register-ObjectEvent $Watcher "Changed" -Action $Action | Out-Null
Register-ObjectEvent $Watcher "Created" -Action $Action | Out-Null
Register-ObjectEvent $Watcher "Renamed" -Action $Action | Out-Null

Write-Host " [Watchdog] Monitoring active. Press Ctrl+C to stop." -ForegroundColor Green

# Keep script running
while ($true) {
    Start-Sleep -Seconds 1
}
