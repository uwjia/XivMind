@echo off
setlocal EnableDelayedExpansion

echo ==========================================
echo   Install PyTorch from Local Wheels
echo ==========================================

cd /d "%~dp0"

REM Default wheel directory (can be changed)
set WHEEL_DIR=D:\Downloads

echo.
echo Local wheel files should be in: %WHEEL_DIR%
echo Expected files:
echo   - torch-2.8.0+cu128-cp312-cp312-win_amd64.whl
echo   - torchvision-0.23.0+cu128-cp312-cp312-win_amd64.whl
echo.

set /p WHEEL_DIR="Enter wheel directory path (or press Enter for default): "

REM Check if venv exists
if not exist "venv" (
    echo.
    echo ERROR: Virtual environment not found!
    echo.
    echo Please run the following command first to create the virtual environment:
    echo   start.bat install
    echo.
    echo Or for development mode:
    echo   start.bat dev
    echo.
    exit /b 1
)

REM Check if wheel files exist
set TORCH_WHEEL=%WHEEL_DIR%\torch-2.8.0+cu128-cp312-cp312-win_amd64.whl
set TORCHVISION_WHEEL=%WHEEL_DIR%\torchvision-0.23.0+cu128-cp312-cp312-win_amd64.whl

if not exist "%TORCH_WHEEL%" (
    echo ERROR: torch wheel not found at: %TORCH_WHEEL%
    echo.
    echo Please download from: https://download.pytorch.org/whl/cu128/torch/
    exit /b 1
)

if not exist "%TORCHVISION_WHEEL%" (
    echo ERROR: torchvision wheel not found at: %TORCHVISION_WHEEL%
    echo.
    echo Please download from: https://download.pytorch.org/whl/cu128/torchvision/
    exit /b 1
)

echo Found wheel files:
echo   - %TORCH_WHEEL%
echo   - %TORCHVISION_WHEEL%
echo.

call venv\Scripts\activate.bat

echo Installing PyTorch from local wheels...
pip install "%TORCH_WHEEL%" "%TORCHVISION_WHEEL%"

if errorlevel 1 (
    echo ERROR: Failed to install PyTorch.
    exit /b 1
)

echo.
echo Installing pillow (required by torchvision)...
pip install pillow>=9.0.0

echo.
echo ==========================================
echo   Installation Complete!
echo ==========================================
echo.
echo To verify PyTorch GPU:
echo   python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
echo.

endlocal
