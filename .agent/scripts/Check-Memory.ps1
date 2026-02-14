
param (
    [Parameter(Mandatory=$true)]
    [string]$SessionId,
    
    [int]$Threshold = 2
)

$ErrorActionPreference = "SilentlyContinue"

# 1. Define Paths
$AgentRoot = Resolve-Path "$PSScriptRoot\..\.."
$MemoryDir = Join-Path $AgentRoot ".agent\memory"
$TargetFile = Join-Path $MemoryDir "active_context.md"
$StatusFile = Join-Path $MemoryDir "watchdog_status.lock"
$TempFile = Join-Path $MemoryDir "watchdog_status.tmp"

# 2. Check Context Load (Latest PB File Size)
$Status = "NORMAL"
$SizeMB = 0

# Path to Axiom Conversations Directory
# Dynamic detection for Windows ($env:USERPROFILE) and macOS/Linux ($env:HOME)
$HomeDir = if ($env:USERPROFILE) { $env:USERPROFILE } else { $env:HOME }
$ConversationsDir = Join-Path $HomeDir ".gemini\axiom\conversations"

if (Test-Path $ConversationsDir) {
    # Get the most recently modified .pb file
    $LatestPb = Get-ChildItem -Path $ConversationsDir -Filter "*.pb" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    
    if ($LatestPb) {
        $SizeBytes = $LatestPb.Length
        $SizeMB = [math]::Round($SizeBytes / 1MB, 4)
        
        Write-Host " [Watchdog] Monitoring: $($LatestPb.Name) ($SizeMB MB)" -ForegroundColor DarkGray
        
        # Threshold handling
        if ($SizeMB -ge $Threshold) {
            $Status = "CRITICAL"
        } elseif ($SizeMB -ge ($Threshold * 0.8)) {
            $Status = "WARNING"
        }
    } else {
         Write-Host " [Watchdog] No .pb files found to monitor." -ForegroundColor Yellow
    }
} else {
    Write-Host " [Watchdog] Conversations directory not found: $ConversationsDir" -ForegroundColor Red
}

# 3. Create JSON Payload
$Payload = @{
    status = $Status
    size_mb = $SizeMB
    limit_mb = $Threshold
    timestamp = [int64]((Get-Date).ToUniversalTime() - (Get-Date "1970-01-01")).TotalSeconds
    session_id = $SessionId
} | ConvertTo-Json -Compress

# 4. Atomic Write
try {
    $Payload | Set-Content -Path $TempFile -Encoding UTF8 -Force
    Move-Item -Path $TempFile -Destination $StatusFile -Force
} catch {
    # Silent fail, maybe log if verbose
    if ($PSBoundParameters['Verbose']) {
        Write-Error $_
    }
}
