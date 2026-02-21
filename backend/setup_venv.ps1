$ErrorActionPreference = "Stop"

$VenvDir = "venv"
$BackendDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== XivMind Backend Virtual Environment Setup ===" -ForegroundColor Cyan

Set-Location $BackendDir

if (Test-Path $VenvDir) {
    Write-Host ""
    Write-Host "Virtual environment already exists at: $BackendDir\$VenvDir" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please choose an option:" -ForegroundColor White
    Write-Host "  [1] Delete and recreate (remove old venv, create new one)" -ForegroundColor White
    Write-Host "  [2] Activate existing (keep current venv, just activate it)" -ForegroundColor White
    Write-Host "  [3] Exit (cancel operation)" -ForegroundColor White
    Write-Host ""
    
    $Choice = Read-Host "Enter your choice (1/2/3)"
    
    switch ($Choice) {
        "1" {
            Write-Host "Removing existing venv..." -ForegroundColor Yellow
            Remove-Item -Recurse -Force $VenvDir
        }
        "2" {
            Write-Host ""
            Write-Host "To activate the virtual environment, please run:" -ForegroundColor Yellow
            Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor White
            Write-Host ""
            Write-Host "Or use dot-sourcing to keep activation in current shell:" -ForegroundColor Yellow
            Write-Host "    . .\setup_venv.ps1" -ForegroundColor White
            return
        }
        "3" {
            Write-Host "Operation cancelled." -ForegroundColor Yellow
            return
        }
        Default {
            Write-Host "Invalid choice. Operation cancelled." -ForegroundColor Red
            return
        }
    }
}

Write-Host ""
Write-Host "Select PyTorch version:" -ForegroundColor Cyan
Write-Host "  [1] CPU only (smaller, no GPU support)" -ForegroundColor White
Write-Host "  [2] GPU with CUDA 12.1 (requires NVIDIA GPU)" -ForegroundColor White
Write-Host "  [3] GPU with CUDA 11.8 (requires NVIDIA GPU)" -ForegroundColor White
Write-Host ""

$TorchChoice = Read-Host "Enter your choice (1/2/3)"

Write-Host "Creating new virtual environment..." -ForegroundColor Green
python -m venv $VenvDir

Write-Host "Upgrading pip..." -ForegroundColor Green
& ".\$VenvDir\Scripts\python.exe" -m pip install --upgrade pip

Write-Host "Installing base dependencies..." -ForegroundColor Green
& ".\$VenvDir\Scripts\pip.exe" install setuptools>=68.0.0

switch ($TorchChoice) {
    "1" {
        Write-Host "Installing PyTorch (CPU version)..." -ForegroundColor Green
        & ".\$VenvDir\Scripts\pip.exe" install torch --index-url https://download.pytorch.org/whl/cpu
    }
    "2" {
        Write-Host "Installing PyTorch (CUDA 12.1)..." -ForegroundColor Green
        & ".\$VenvDir\Scripts\pip.exe" install torch --index-url https://download.pytorch.org/whl/cu121
    }
    "3" {
        Write-Host "Installing PyTorch (CUDA 11.8)..." -ForegroundColor Green
        & ".\$VenvDir\Scripts\pip.exe" install torch --index-url https://download.pytorch.org/whl/cu118
    }
    Default {
        Write-Host "Invalid choice. Installing CPU version by default..." -ForegroundColor Yellow
        & ".\$VenvDir\Scripts\pip.exe" install torch --index-url https://download.pytorch.org/whl/cpu
    }
}

Write-Host "Installing dependencies..." -ForegroundColor Green
& ".\$VenvDir\Scripts\pip.exe" install -r requirements.txt

Write-Host "Installing dev dependencies..." -ForegroundColor Green
& ".\$VenvDir\Scripts\pip.exe" install pytest pytest-asyncio==0.23.6

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "Virtual environment created at: $BackendDir\$VenvDir" -ForegroundColor White
Write-Host ""
Write-Host "To activate the virtual environment, run:" -ForegroundColor Yellow
Write-Host "    .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host ""
Write-Host "To run tests:" -ForegroundColor Yellow
Write-Host "    pytest tests/" -ForegroundColor White
Write-Host ""
