# PersonaLock Desktop — Phase 0 bootstrap
# Run from repo root: .\scripts\bootstrap.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  PersonaLock Desktop Bootstrap" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Docker + Neo4j
Write-Host "[1/4] Neo4j (Docker)..." -ForegroundColor Yellow
docker compose up -d
if ($LASTEXITCODE -ne 0) { throw "docker compose failed" }

$neo4jReady = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:7474" -TimeoutSec 2 -UseBasicParsing
        if ($r.StatusCode -eq 200) { $neo4jReady = $true; break }
    } catch {}
    Start-Sleep -Seconds 1
}
if ($neo4jReady) {
    Write-Host "  Neo4j ready at http://localhost:7474" -ForegroundColor Green
} else {
    Write-Host "  Neo4j not responding yet — check: docker compose logs neo4j" -ForegroundColor Red
}

# 2. Ollama embeddings
Write-Host "[2/4] Ollama embeddings..." -ForegroundColor Yellow
try {
    $tags = ollama list 2>&1
    if ($tags -match "nomic-embed-text") {
        Write-Host "  nomic-embed-text present" -ForegroundColor Green
    } else {
        Write-Host "  Pulling nomic-embed-text..." -ForegroundColor Yellow
        ollama pull nomic-embed-text
    }
} catch {
    Write-Host "  Ollama not reachable — start ollama serve" -ForegroundColor Red
}

# 3. KoboldCpp brain
Write-Host "[3/4] KoboldCpp brain (port 5001)..." -ForegroundColor Yellow
try {
    $models = Invoke-RestMethod -Uri "http://127.0.0.1:5001/v1/models" -TimeoutSec 5
    $name = $models.data[0].id
    Write-Host "  KoboldCpp ready — model: $name" -ForegroundColor Green
} catch {
    Write-Host "  KoboldCpp not reachable — start your CUDA 11 build on :5001" -ForegroundColor Red
}

# 4. Smoke hint
Write-Host "[4/4] Next step..." -ForegroundColor Yellow
Write-Host "  python main_base_assistant.py chat" -ForegroundColor White
Write-Host ""
