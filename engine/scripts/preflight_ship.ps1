# Pre-ship checklist - run before sending zip to Janice
# Usage: .\scripts\preflight_ship.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Remove-Item Env:ARDEN_SMOKE_BRAIN -ErrorAction SilentlyContinue
Remove-Item Env:PERSONALOCK_SMOKE_BRAIN -ErrorAction SilentlyContinue

Write-Host "PersonaLock preflight (Janice ship)" -ForegroundColor Cyan
Write-Host ""

$fail = 0

function Check($label, [scriptblock]$block) {
    Write-Host "  $label ... " -NoNewline
    try {
        & $block
        Write-Host "OK" -ForegroundColor Green
    } catch {
        Write-Host "FAIL" -ForegroundColor Red
        Write-Host "    $($_.Exception.Message)" -ForegroundColor Red
        $script:fail++
    }
}

Check "Release zip exists" {
    $z = Join-Path $Root "release\PersonaLock-Portable.zip"
    if (-not (Test-Path $z)) {
        throw "Missing $z - run package_for_janice.ps1"
    }
    $mb = [math]::Round((Get-Item $z).Length / 1MB, 1)
    Write-Host "(${mb} MB) " -NoNewline
}

Check "Install-Sam.ps1 exists" {
    if (-not (Test-Path (Join-Path $Root "release\Install-Sam.ps1"))) {
        throw "Missing installer script"
    }
}

Check "Unit tests" {
    python test_sqlite_memory.py | Out-Null
    python test_consumer_bootstrap.py | Out-Null
    python test_brain_backends.py | Out-Null
}

Check "Consumer smoke (python + exe)" {
    & (Join-Path $Root "scripts\smoke_test_consumer.ps1") | Out-Null
}

Check "Zip extract + exe smoke" {
    $zip = Join-Path $Root "release\PersonaLock-Portable.zip"
    $tmpdir = Join-Path $env:TEMP "personalock-preflight-$([guid]::NewGuid().ToString('N').Substring(0,8))"
    New-Item -ItemType Directory -Path $tmpdir | Out-Null
    try {
        Expand-Archive -Path $zip -DestinationPath $tmpdir -Force
        $exe = Join-Path $tmpdir "PersonaLock.exe"
        if (-not (Test-Path $exe)) {
            throw "PersonaLock.exe not in zip root"
        }
        $proc = Start-Process -FilePath $exe -ArgumentList "smoke-test" -WorkingDirectory $tmpdir -Wait -PassThru -NoNewWindow
        if ($proc.ExitCode -ne 0) {
            throw "exe smoke-test exit $($proc.ExitCode)"
        }
    } finally {
        Remove-Item $tmpdir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "  NSIS setup (optional) ... " -NoNewline
$setup = Join-Path $Root "release\PersonaLock_Setup.exe"
if (Test-Path $setup) {
    Write-Host "OK (PersonaLock_Setup.exe found)" -ForegroundColor Green
} else {
    Write-Host "SKIP (use zip + Install-Sam.ps1)" -ForegroundColor Yellow
}

Write-Host ""
if ($fail -eq 0) {
    Write-Host "PREFLIGHT PASSED - safe to send release/PersonaLock-Portable.zip" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next: Dave double-click test, then email Janice (see release/EMAIL-TO-JANICE.txt)" -ForegroundColor Yellow
} else {
    Write-Host "PREFLIGHT FAILED - $fail check(s) need attention" -ForegroundColor Red
    exit 1
}
