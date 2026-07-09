# Simulate Janice install path (no GUI) - extract zip, install, smoke exe
# Usage: .\scripts\simulate_janice_install.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Remove-Item Env:ARDEN_SMOKE_BRAIN -ErrorAction SilentlyContinue
Remove-Item Env:PERSONALOCK_SMOKE_BRAIN -ErrorAction SilentlyContinue

$zip = Join-Path $Root "release\PersonaLock-Portable.zip"
if (-not (Test-Path $zip)) {
    Write-Host "Run package_for_janice.ps1 first" -ForegroundColor Red
    exit 1
}

$extract = Join-Path $env:TEMP "personalock-janice-sim-$([guid]::NewGuid().ToString('N').Substring(0,8))"
$installDest = Join-Path $env:LOCALAPPDATA "PersonaLock\App-sim-test"

Write-Host "Simulating Janice install" -ForegroundColor Cyan
Write-Host "  Extract: $extract"
Write-Host "  Install: $installDest"
Write-Host ""

try {
    Expand-Archive -Path $zip -DestinationPath $extract -Force

    if (Test-Path $installDest) {
        Remove-Item $installDest -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $installDest | Out-Null

    $skip = @(
        "Install-Sam.ps1", "Uninstall-Sam.ps1",
        "README-FOR-JANICE.txt", "EMAIL-TO-JANICE.txt", "DAVE-QUICK-TEST.txt"
    )
    Get-ChildItem $extract | Where-Object { $skip -notcontains $_.Name } |
        Copy-Item -Destination $installDest -Recurse -Force

    $exe = Join-Path $installDest "PersonaLock.exe"
    if (-not (Test-Path $exe)) {
        throw "PersonaLock.exe missing after simulated install"
    }

    $proc = Start-Process -FilePath $exe -ArgumentList "smoke-test" -WorkingDirectory $installDest -Wait -PassThru -NoNewWindow
    if ($proc.ExitCode -ne 0) {
        throw "smoke-test failed with exit $($proc.ExitCode)"
    }

    $smokeLog = Join-Path $env:LOCALAPPDATA "PersonaLock\smoke-last.txt"
    if (Test-Path $smokeLog) {
        Write-Host "Smoke log: $(Get-Content $smokeLog -Raw)"
    }

    Write-Host ""
    Write-Host "Janice install simulation PASSED" -ForegroundColor Green
    Write-Host "Installed test copy: $installDest"
    Write-Host "Remove with: Remove-Item '$installDest' -Recurse -Force"
} finally {
    Remove-Item $extract -Recurse -Force -ErrorAction SilentlyContinue
}
