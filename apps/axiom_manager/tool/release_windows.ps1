param(
    [ValidateSet("unsigned", "signed")]
    [string]$Mode = "unsigned",
    [string]$BuildName = "1.0.0",
    [string]$BuildNumber = "1",
    [bool]$Clean = $true
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) {
    throw "flutter not found. Please install Flutter and add it to PATH."
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git not found. Please install Git and add it to PATH."
}
if (-not (Get-Command cmake -ErrorAction SilentlyContinue)) {
    throw "cmake not found. Please install CMake and add it to PATH."
}

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$ReleaseDir = Join-Path $ProjectRoot "dist/windows/$Mode"
$BundleDir = Join-Path $ReleaseDir "axiom-manager-windows-$Mode"
$ZipPath = Join-Path $ReleaseDir "axiom-manager-windows-$Mode.zip"

Write-Host "[1/4] flutter pub get"
Push-Location $ProjectRoot
try {
    if ($Clean) {
        Write-Host "[prep] flutter clean (refresh icon resources)"
        flutter clean
    }

    flutter pub get

    Write-Host "[2/4] build windows release"
    flutter build windows --release --build-name $BuildName --build-number $BuildNumber
}
finally {
    Pop-Location
}

$SourceDir = Join-Path $ProjectRoot "build/windows/x64/runner/Release"
if (-not (Test-Path $SourceDir)) {
    throw "Build output not found: $SourceDir"
}

Write-Host "[3/4] prepare dist directory"
if (Test-Path $BundleDir) { Remove-Item $BundleDir -Recurse -Force }
if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
New-Item -ItemType Directory -Path $BundleDir -Force | Out-Null
Copy-Item "$SourceDir\*" $BundleDir -Recurse -Force

if ($Mode -eq "signed") {
    Write-Warning "Signed mode placeholder only. Integrate signtool here."
}

Write-Host "[4/4] create zip"
Compress-Archive -Path (Join-Path $BundleDir "*") -DestinationPath $ZipPath -Force

Write-Host "Done"
Write-Host "Bundle: $BundleDir"
Write-Host "Zip:    $ZipPath"
