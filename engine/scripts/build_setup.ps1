# Build PersonaLock_Setup.exe via NSIS (optional — zip path works without this)
# Usage: .\scripts\build_setup.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$exe = Join-Path $Root "dist\PersonaLock\PersonaLock.exe"
if (-not (Test-Path $exe)) {
    Write-Host "Build PyInstaller first: .\scripts\build_consumer.ps1" -ForegroundColor Red
    exit 1
}

$makensis = Get-Command makensis -ErrorAction SilentlyContinue
if (-not $makensis) {
    $candidates = @(
        "${env:ProgramFiles(x86)}\NSIS\makensis.exe",
        "$env:ProgramFiles\NSIS\makensis.exe"
    )
    foreach ($c in $candidates) {
        if (Test-Path $c) { $makensis = @{ Source = $c }; break }
    }
}

if (-not $makensis) {
    Write-Host "NSIS not installed." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ship without it:" -ForegroundColor Green
    Write-Host "  .\scripts\package_for_janice.ps1  ->  release/PersonaLock-Portable.zip" -ForegroundColor White
    Write-Host ""
    Write-Host "To build PersonaLock_Setup.exe later:" -ForegroundColor Yellow
    Write-Host "  winget install NSIS.NSIS" -ForegroundColor White
    Write-Host "  .\scripts\build_setup.ps1" -ForegroundColor White
    exit 0
}

$nsis = $makensis.Source
Write-Host "Building PersonaLock_Setup.exe with NSIS..." -ForegroundColor Cyan
& $nsis "/DREPO_ROOT=$Root" (Join-Path $Root "packaging\installer.nsi")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$setup = Join-Path $Root "PersonaLock_Setup.exe"
$releaseSetup = Join-Path $Root "release\PersonaLock_Setup.exe"
if (Test-Path $setup) {
    New-Item -ItemType Directory -Force -Path (Join-Path $Root "release") | Out-Null
    Move-Item $setup $releaseSetup -Force
    Write-Host ""
    Write-Host "Output: $releaseSetup" -ForegroundColor Green
}
