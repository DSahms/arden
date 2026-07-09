# One-shot Brittany ship: build, package, acceptance
# Usage: .\scripts\ship_brittany.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "=== Arden Brittany ship loop ===" -ForegroundColor Cyan

& (Join-Path $PSScriptRoot "build_arden_consumer.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& (Join-Path $PSScriptRoot "package_for_brittany.ps1")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Running acceptance suite..." -ForegroundColor Yellow
python main_gui_assistant.py acceptance-test
$code = $LASTEXITCODE

Write-Host ""
if ($code -eq 0) {
    Write-Host "Ship loop complete — release\Arden-Portable.zip" -ForegroundColor Green
} else {
    Write-Host "Acceptance had failures — fix before emailing Brittany" -ForegroundColor Red
}
exit $code
