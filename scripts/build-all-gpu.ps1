$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  XivMind Windows Desktop Build Script " -ForegroundColor Cyan
Write-Host "  (GPU Version with CUDA 12.8)          " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$projectRoot = Join-Path $PSScriptRoot ".."
Push-Location $projectRoot

Write-Host "[1/3] Building Frontend..." -ForegroundColor Yellow
& (Join-Path $PSScriptRoot "build-frontend.ps1")
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "[2/3] Building Backend (GPU)..." -ForegroundColor Yellow
& (Join-Path $PSScriptRoot "build-backend-gpu.ps1")
if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "[3/3] Building Electron application with electron-builder (GPU)..." -ForegroundColor Yellow
npm run build:desktop-gpu
if ($LASTEXITCODE -ne 0) {
    Write-Host "Electron build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Build completed successfully! " -ForegroundColor Green
Write-Host "  (GPU Version)                 " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Output directory: $projectRoot\release" -ForegroundColor Cyan
Write-Host ""

Pop-Location
