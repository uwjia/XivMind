$ErrorActionPreference = "Stop"

Write-Host "Building XivMind Frontend..." -ForegroundColor Cyan

$projectRoot = Join-Path $PSScriptRoot ".."

Push-Location $projectRoot

Write-Host "Installing dependencies..." -ForegroundColor Yellow
npm install

Write-Host "Building Vue application..." -ForegroundColor Yellow
npm run build

if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "Frontend build completed successfully!" -ForegroundColor Green
Write-Host "Output directory: $projectRoot\dist" -ForegroundColor Cyan

Pop-Location
