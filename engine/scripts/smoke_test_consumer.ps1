# Consumer edition smoke test — dev + built exe
# Usage: .\scripts\smoke_test_consumer.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Arden consumer smoke test" -ForegroundColor Cyan

$env:ARDEN_EDITION = "consumer"
python main_gui_assistant.py smoke-test
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$exe = Join-Path $Root "dist\Arden\Arden.exe"
if (Test-Path $exe) {
    Write-Host ""
    Write-Host "Testing built exe..." -ForegroundColor Yellow
    $proc = Start-Process -FilePath $exe -ArgumentList "smoke-test" -Wait -PassThru -NoNewWindow
    if ($proc.ExitCode -ne 0) { exit $proc.ExitCode }
} else {
    Write-Host "Skipping exe test (run build_arden_consumer.ps1 first)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "All smoke tests passed." -ForegroundColor Green
