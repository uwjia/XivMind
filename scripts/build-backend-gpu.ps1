$ErrorActionPreference = "Stop"

Write-Host "Building XivMind Python Backend (GPU Version)..." -ForegroundColor Cyan

Write-Host ""
Write-Host "This script builds the GPU version with PyTorch CUDA support." -ForegroundColor Yellow
Write-Host "Output: backend/dist/xivmind-backend-gpu" -ForegroundColor Yellow
Write-Host ""

$backendDir = Join-Path $PSScriptRoot "..\backend"
$distDir = Join-Path $backendDir "dist"

if (Test-Path $distDir) {
    Write-Host "Cleaning previous build..." -ForegroundColor Yellow
    Remove-Item -Path $distDir -Recurse -Force
}

Write-Host "Checking Python environment..." -ForegroundColor Yellow

Push-Location $backendDir

$venvPath = Join-Path $backendDir ".venv-gpu"
if (-not (Test-Path $venvPath)) {
    Write-Host "Virtual environment not found. Creating one..." -ForegroundColor Yellow
    python -m venv .venv-gpu
}

$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Host "Failed to activate virtual environment" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "Installing dependencies (GPU version with CUDA 12.8)..." -ForegroundColor Yellow
pip install --upgrade pip
pip install pyinstaller

if (Test-Path "requirements-gpu.txt") {
    pip install -r requirements-gpu.txt
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
    "sentence_transformers.SentenceTransformer",
    "sentence_transformers.models",
    "sentence_transformers.models.Transformer",
    "transformers",
    "transformers.AutoModel",
    "transformers.AutoTokenizer",
    "torch",
    "torch.cuda",
    "numpy",
    "pandas",
    "sklearn",
    "sklearn.utils",
    "sklearn.utils._cython_blas"
)

$collectAll = @(
    "sentence_transformers",
    "transformers",
    "torch"
)

$copyMetadata = @(
    "sentence_transformers",
    "transformers"
)

$hiddenImportArgs = $hiddenImports | ForEach-Object { "--hidden-import=$_" }
$collectAllArgs = $collectAll | ForEach-Object { "--collect-all=$_" }
$copyMetadataArgs = $copyMetadata | ForEach-Object { "--copy-metadata=$_" }

$pyinstallerArgs = @(
    "--name=xivmind-backend-gpu",
    "--onedir",
    "--noconsole",
    "--clean",
    "--noconfirm"
) + $hiddenImportArgs + $collectAllArgs + $copyMetadataArgs + @(
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

Write-Host "Backend (GPU) build completed successfully!" -ForegroundColor Green
Write-Host "Output directory: $distDir\xivmind-backend-gpu" -ForegroundColor Cyan

Pop-Location
