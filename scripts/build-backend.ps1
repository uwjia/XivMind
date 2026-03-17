$ErrorActionPreference = "Stop"

Write-Host "Building XivMind Python Backend..." -ForegroundColor Cyan

$backendDir = Join-Path $PSScriptRoot "..\backend"
$distDir = Join-Path $backendDir "dist"

if (Test-Path $distDir) {
    Write-Host "Cleaning previous build..." -ForegroundColor Yellow
    Remove-Item -Path $distDir -Recurse -Force
}

Write-Host "Checking Python environment..." -ForegroundColor Yellow

Push-Location $backendDir

$venvPath = Join-Path $backendDir ".venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv .venv
}

$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Host "Failed to activate virtual environment" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install pyinstaller

if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
}

Write-Host "Building executable with PyInstaller..." -ForegroundColor Yellow

$hiddenImports = @(
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "pydantic",
    "pydantic_settings",
    "loguru",
    "httpx",
    "aiofiles",
    "aiosqlite",
    "lancedb",
    "pyarrow",
    "sentence_transformers",
    "transformers",
    "torch",
    "numpy",
    "pandas"
)

$collectData = @(
    "lancedb",
    "pyarrow",
    "sentence_transformers",
    "transformers"
)

$hiddenImportArgs = $hiddenImports | ForEach-Object { "--hidden-import=$_" }
$collectDataArgs = $collectData | ForEach-Object { "--collect-data=$_" }

$pyinstallerArgs = @(
    "--name=xivmind-backend",
    "--onedir",
    "--noconsole",
    "--clean",
    "--noconfirm"
) + $hiddenImportArgs + $collectDataArgs + @(
    "--add-data=app;app",
    "--add-data=static;static",
    "--add-data=skills;skills",
    "--add-data=subagents;subagents",
    "--runtime-hook=runtime_hook.py",
    "run_backend.py"
)

& pyinstaller $pyinstallerArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "PyInstaller build failed!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "Backend build completed successfully!" -ForegroundColor Green
Write-Host "Output directory: $distDir\xivmind-backend" -ForegroundColor Cyan

Pop-Location
