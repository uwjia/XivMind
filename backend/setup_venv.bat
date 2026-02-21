@echo off
setlocal enabledelayedexpansion

set VenvDir=venv
set BackendDir=%~dp0

echo === XivMind Backend Virtual Environment Setup ===

cd /d %BackendDir%

if exist %VenvDir% (
    echo.
    echo Virtual environment already exists at: %BackendDir%%VenvDir%
    echo.
    echo Please choose an option:
    echo   [1] Delete and recreate (remove old venv, create new one)
    echo   [2] Activate existing (keep current venv, just activate it)
    echo   [3] Exit (cancel operation)
    echo.
    
    set /p Choice="Enter your choice (1/2/3): "
    
    if "!Choice!"=="1" (
        echo Removing existing venv...
        rmdir /s /q %VenvDir%
    ) else if "!Choice!"=="2" (
        echo.
        echo To activate the virtual environment, please run:
        echo     %VenvDir%\Scripts\activate.bat
        echo.
        goto :eof
    ) else if "!Choice!"=="3" (
        echo Operation cancelled.
        goto :eof
    ) else (
        echo Invalid choice. Operation cancelled.
        goto :eof
    )
)

echo.
echo Select PyTorch version:
echo   [1] CPU only (smaller, no GPU support)
echo   [2] GPU with CUDA 12.8 (requires NVIDIA GPU)
echo   [3] GPU with CUDA 11.8 (requires NVIDIA GPU)
echo.

set /p TorchChoice="Enter your choice (1/2/3): "

echo Creating new virtual environment...
python -m venv %VenvDir%

echo Upgrading pip...
%VenvDir%\Scripts\python.exe -m pip install --upgrade pip

echo Installing base dependencies...
%VenvDir%\Scripts\pip.exe install setuptools>=68.0.0

if "!TorchChoice!"=="1" (
    echo Installing PyTorch (CPU version)...
    %VenvDir%\Scripts\pip.exe install torch --index-url https://download.pytorch.org/whl/cpu
) else if "!TorchChoice!"=="2" (
    echo Installing PyTorch (CUDA 12.8)...
    %VenvDir%\Scripts\pip.exe install torch --index-url https://download.pytorch.org/whl/cu128
) else if "!TorchChoice!"=="3" (
    echo Installing PyTorch (CUDA 11.8)...
    %VenvDir%\Scripts\pip.exe install torch --index-url https://download.pytorch.org/whl/cu118
) else (
    echo Invalid choice. Installing CPU version by default...
    %VenvDir%\Scripts\pip.exe install torch --index-url https://download.pytorch.org/whl/cpu
)

echo Installing dependencies...
%VenvDir%\Scripts\pip.exe install -r requirements.txt

echo Installing dev dependencies...
%VenvDir%\Scripts\pip.exe install pytest pytest-asyncio==0.23.6

echo.
echo === Setup Complete ===
echo.
echo Virtual environment created at: %BackendDir%%VenvDir%
echo.
echo To activate the virtual environment, run:
echo     %VenvDir%\Scripts\activate.bat
echo.
echo To run tests:
echo     pytest tests/
echo.
