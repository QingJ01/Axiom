param([int]$Interval = 2)

$HomeDir = if ($env:USERPROFILE) { $env:USERPROFILE } else { $env:HOME }
if (-not $HomeDir) {
    Write-Host "Error: Could not determine HOME directory." -ForegroundColor Red
    exit 1
}

$TargetDir = Join-Path $HomeDir ".gemini\axiom\conversations"
Write-Host "Polling $TargetDir every $Interval seconds..." -ForegroundColor Cyan

$LastTime = $null
$LastSize = 0

while ($true) {
    if (Test-Path $TargetDir) {
        $Latest = Get-ChildItem -Path $TargetDir -Filter "*.pb" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        
        if ($Latest) {
            $CurrentTime = $Latest.LastWriteTime
            $CurrentSize = $Latest.Length
            
            # If time changed or size changed
            if ($LastTime -ne $CurrentTime -or $LastSize -ne $CurrentSize) {
                $SizeMB = [math]::Round($CurrentSize / 1MB, 4)
                Write-Host " [POLL] Change Detected: $($Latest.Name)" -ForegroundColor Yellow
                Write-Host "    Time: $CurrentTime"
                Write-Host "    Size: $SizeMB MB"
                
                $LastTime = $CurrentTime
                $LastSize = $CurrentSize
            }
        }
    }
    Start-Sleep -Seconds $Interval
}
