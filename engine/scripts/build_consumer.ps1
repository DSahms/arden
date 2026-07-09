# Build PersonaLock Consumer Edition (skeleton)
# Full installer requires: pip install pyinstaller + NSIS (future)
# Usage: .\scripts\build_consumer.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "PersonaLock Consumer Build (skeleton)" -ForegroundColor Cyan
Write-Host "Finish line: PersonaLock_Setup.exe for Janice" -ForegroundColor Yellow
Write-Host ""

python -m pip show pyinstaller 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    python -m pip install pyinstaller
}

$env:ARDEN_EDITION = "consumer"
python -m PyInstaller packaging/personalock.spec --noconfirm
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Output: dist/PersonaLock/PersonaLock.exe" -ForegroundColor Green
Write-Host ""
Write-Host "Installer (requires NSIS):" -ForegroundColor Yellow
Write-Host "  makensis packaging/installer.nsi" -ForegroundColor White
Write-Host "  -> PersonaLock_Setup.exe" -ForegroundColor Green
Write-Host ""
Write-Host "Dev test GUI:" -ForegroundColor Yellow
Write-Host "  `$env:ARDEN_CONFIG='assistant_config.consumer.yml'" -ForegroundColor White
Write-Host "  python main_gui_assistant.py chat" -ForegroundColor White
