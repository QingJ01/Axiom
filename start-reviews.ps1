$prdFile = "docs/prd/memory-watchdog-lite-rough.md"
$reviewDir = "docs/reviews/memory-watchdog-lite"
$rolesDir = ".agent/prompts/roles"

if (-not (Test-Path $reviewDir)) { New-Item -ItemType Directory -Path $reviewDir -Force | Out-Null }

$roles = @("ux_director", "product_director", "tech_lead", "domain_expert", "critic")
$jobs = @()

foreach ($role in $roles) {
    $rolePath = "$rolesDir/$role.md"
    $outputPath = "$reviewDir/$role-review.md"
    
    if (-not (Test-Path $rolePath)) {
        Write-Host "Error: Role file not found: $rolePath" -ForegroundColor Red
        continue
    }

    # Convert paths to Windows backslashes for cmd.exe reliability
    $winRolePath = $rolePath.Replace("/", "\")
    $winPrdFile = $prdFile.Replace("/", "\")
    $winOutputPath = $outputPath.Replace("/", "\")

    Write-Host "Starting review for $role..."
    # Pipe role + PRD content into agent-runner (codex wrapper)
    # Determine PowerShell executable
    $PSExe = if (Get-Command pwsh -ErrorAction SilentlyContinue) { "pwsh" } else { "powershell" }
    $p = Start-Process -FilePath "cmd" -ArgumentList "/c type ""$winRolePath"" ""$winPrdFile"" | $PSExe -File "".agent/scripts/agent-runner.ps1"" - > ""$winOutputPath""" -PassThru -WindowStyle Hidden
    $jobs += $p
}

Write-Host "Waiting for 5 parallel review processes to complete..."
$jobs | Wait-Process
Write-Host "All reviews completed."
