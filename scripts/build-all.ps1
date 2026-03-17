$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  XivMind Windows Desktop Build Script " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Join-Path $PSScriptRoot ".."
Push-Location $projectRoot

Write-Host "[1/4] Building Frontend..." -ForegroundColor Yellow
& (Join-Path $PSScriptRoot "build-frontend.ps1")
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "[2/4] Building Backend..." -ForegroundColor Yellow
& (Join-Path $PSScriptRoot "build-backend.ps1")
if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "[3/4] Installing Electron dependencies..." -ForegroundColor Yellow
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "npm install failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "[4/4] Building Electron application..." -ForegroundColor Yellow
npm run build:electron
if ($LASTEXITCODE -ne 0) {
    Write-Host "Electron build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Build completed successfully! " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Output directory: $projectRoot\release" -ForegroundColor Cyan
Write-Host ""

Pop-Location
