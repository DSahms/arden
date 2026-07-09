# Build Arden Desktop consumer edition (Brittany path)
# Usage: .\scripts\build_arden_consumer.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "Arden Desktop consumer build" -ForegroundColor Cyan
Write-Host "Output: dist\Arden\Arden.exe" -ForegroundColor Yellow
Write-Host ""

python -m pip show pyinstaller 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    python -m pip install pyinstaller
}

if (Test-Path "requirements-gui.txt") {
    Write-Host "Installing GUI extras (Pillow, pypdf, python-docx)..." -ForegroundColor Yellow
    python -m pip install -r requirements-gui.txt
}

$env:ARDEN_EDITION = "consumer"
python -m PyInstaller packaging/arden.spec --noconfirm
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Build OK: dist\Arden\Arden.exe" -ForegroundColor Green
Write-Host "Next: .\scripts\package_for_brittany.ps1" -ForegroundColor Yellow
