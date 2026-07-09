# Run all automatable ship-queue gates in order
# Usage: .\scripts\ship_queue.ps1
# Human steps after this: release/DAVE-QUICK-TEST.txt -> EMAIL-TO-JANICE.txt -> Janice laptop

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Remove-Item Env:ARDEN_SMOKE_BRAIN -ErrorAction SilentlyContinue
Remove-Item Env:PERSONALOCK_SMOKE_BRAIN -ErrorAction SilentlyContinue

Write-Host "PersonaLock ship queue (automated gates)" -ForegroundColor Cyan
Write-Host ""

$steps = @(
    @{ Name = "1/4 Preflight"; Script = { & (Join-Path $Root "scripts\preflight_ship.ps1") | Out-Null } },
    @{ Name = "2/4 Install simulation"; Script = { & (Join-Path $Root "scripts\simulate_janice_install.ps1") | Out-Null } },
    @{ Name = "3/4 Memory persistence"; Script = {
        if (Test-Path (Join-Path $Root ".env")) {
            Get-Content (Join-Path $Root ".env") | ForEach-Object {
                if ($_ -match "^([^#=]+)=(.*)$") {
                    [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
                }
            }
        }
        $env:ARDEN_EDITION = "consumer"
        python (Join-Path $Root "scripts\test_memory_persist.py")
        if ($LASTEXITCODE -ne 0) { throw "memory persist failed" }
    }},
    @{ Name = "4/4 Groq brain smoke"; Script = {
        if (-not $env:GROQ_API_KEY) {
            Write-Host "    SKIP (no GROQ_API_KEY)" -ForegroundColor Yellow
            return
        }
        $env:ARDEN_EDITION = "consumer"
        $env:ARDEN_SMOKE_BRAIN = "1"
        python main_gui_assistant.py smoke-test
        if ($LASTEXITCODE -ne 0) { throw "brain smoke failed" }
    }}
)

$fail = 0
foreach ($step in $steps) {
    Write-Host "$($step.Name) ... " -NoNewline
    try {
        & $step.Script
        Write-Host "OK" -ForegroundColor Green
    } catch {
        Write-Host "FAIL" -ForegroundColor Red
        Write-Host "    $($_.Exception.Message)" -ForegroundColor Red
        $fail++
        break
    }
}

Write-Host ""
if ($fail -eq 0) {
    Write-Host "AUTO QUEUE COMPLETE" -ForegroundColor Green
    Write-Host ""
    Write-Host "Human queue (you):" -ForegroundColor Yellow
    Write-Host "  5. Dave GUI test     -> release/DAVE-QUICK-TEST.txt"
    Write-Host "  6. Email Janice      -> release/EMAIL-TO-JANICE.txt + zip"
    Write-Host "  7. Janice laptop     -> finish line"
    Write-Host ""
    Write-Host "Track progress: SHIP_QUEUE.md"
} else {
    Write-Host "QUEUE STOPPED - fix failure and re-run .\scripts\ship_queue.ps1" -ForegroundColor Red
    exit 1
}
