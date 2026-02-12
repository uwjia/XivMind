@echo off
setlocal EnableDelayedExpansion

echo ==========================================
echo   XivMind Backend Service
echo ==========================================

cd /d "%~dp0"

REM Python version to use
set PYTHON_CMD=py -3.12

if "%1"=="" goto start
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="install" goto install
if "%1"=="dev" goto dev
goto usage

:check_python
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.12 not found.
    echo Please install Python 3.12 from: https://www.python.org/downloads/
    exit /b 1
)
exit /b 0

:install
call :check_python
if errorlevel 1 exit /b 1

echo Installing dependencies...

REM Remove old venv if exists
if exist "venv" (
    echo Removing old virtual environment...
    rd /s /q venv
)

echo Creating virtual environment with Python 3.12...
%PYTHON_CMD% -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment.
    exit /b 1
)

REM Activate venv and install
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing requirements...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    exit /b 1
)

echo.
echo Dependencies installed successfully!
goto end

:start
call :check_python
if errorlevel 1 exit /b 1

echo Starting backend service...

REM Check if venv exists
if not exist "venv" (
    echo Virtual environment not found. Running install first...
    call :install
    if errorlevel 1 exit /b 1
)

call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo Dependencies not found. Installing...
    python -m pip install -r requirements.txt
)

echo Starting uvicorn server...
start "XivMind Backend" cmd /k "cd /d %~dp0 && venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo.
echo Backend service started!
echo   - API Docs: http://localhost:8000/docs
echo   - ReDoc: http://localhost:8000/redoc
goto end

:dev
call :check_python
if errorlevel 1 exit /b 1

echo Starting backend in development mode...
if exist "venv" (
    call venv\Scripts\activate.bat
)
uvicorn app.main:app --reload --port 8000
goto end

:stop
echo Stopping backend service...
taskkill /FI "WINDOWTITLE eq XivMind Backend*" /F 2>nul
if errorlevel 1 (
    echo No running service found.
) else (
    echo Backend service stopped.
)
goto end

:usage
echo Usage: %~nx0 {start^|stop^|install^|dev}
echo.
echo Commands:
echo   start   - Start backend service (background)
echo   stop    - Stop backend service
echo   install - Install dependencies
echo   dev     - Start in development mode (foreground with reload)
echo.
echo Requirements:
echo   - Python 3.12 must be installed
echo   - Download from: https://www.python.org/downloads/
exit /b 1

:end
endlocal
