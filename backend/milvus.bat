@echo off
setlocal

echo ==========================================
echo   XivMind - Milvus Docker Deployment
echo ==========================================

cd /d "%~dp0"

set COMPOSE_DIR=docker\compose
set COMPOSE_FILE=%COMPOSE_DIR%\milvus.yml
set COMPOSE_LITE_FILE=%COMPOSE_DIR%\milvus.lite.yml

if "%1"=="" goto usage
if "%1"=="start" goto start
if "%1"=="stop" goto stop
if "%1"=="restart" goto restart
if "%1"=="status" goto status
if "%1"=="logs" goto logs
if "%1"=="clean" goto clean
goto usage

:start
set USE_FILE=%COMPOSE_FILE%
if "%2"=="lite" set USE_FILE=%COMPOSE_LITE_FILE%
echo Starting Milvus services (%USE_FILE%)...
docker-compose -f %USE_FILE% up -d
echo.
echo Milvus is starting...
echo   - Milvus: http://localhost:19530
echo   - Attu (GUI): http://localhost:3000
if "%2" neq "lite" (
echo   - MinIO Console: http://localhost:9001 (minioadmin/minioadmin)
)
echo.
echo Waiting for Milvus to be ready...
timeout /t 10 /nobreak >nul
:wait_loop
curl -s http://localhost:9091/healthz >nul 2>&1
if errorlevel 1 (
    echo Still waiting...
    timeout /t 5 /nobreak >nul
    goto wait_loop
)
echo Milvus is ready!
goto end

:stop
echo Stopping Milvus services...
docker-compose -f %COMPOSE_FILE% down 2>nul
docker-compose -f %COMPOSE_LITE_FILE% down 2>nul
echo Milvus services stopped.
goto end

:restart
call :stop
call :start %2
goto end

:status
docker-compose -f %COMPOSE_FILE% ps 2>nul
docker-compose -f %COMPOSE_LITE_FILE% ps 2>nul
goto end

:logs
set USE_FILE=%COMPOSE_FILE%
if exist docker\compose\volumes\milvus-lite set USE_FILE=%COMPOSE_LITE_FILE%
docker-compose -f %USE_FILE% logs -f %2
goto end

:clean
echo WARNING: This will delete all data!
set /p confirm="Are you sure? (y/N): "
if /i "%confirm%"=="y" (
    docker-compose -f %COMPOSE_FILE% down -v 2>nul
    docker-compose -f %COMPOSE_LITE_FILE% down -v 2>nul
    rmdir /s /q docker\compose\volumes 2>nul
    echo All data cleaned.
) else (
    echo Cancelled.
)
goto end

:usage
echo Usage: %~nx0 {start^|stop^|restart^|status^|logs^|clean} [lite]
echo.
echo Commands:
echo   start [lite]  - Start Milvus services (lite = embedded mode, fewer containers)
echo   stop          - Stop Milvus services
echo   restart [lite]- Restart Milvus services
echo   status        - Show service status
echo   logs [service]- Show logs
echo   clean         - Remove all data (WARNING: destructive)
echo.
echo Modes:
echo   (default)     - Standard mode with separate etcd, MinIO containers
echo   lite          - Embedded mode (etcd/MinIO embedded in Milvus)
echo.
echo Compose files:
echo   %COMPOSE_FILE%
echo   %COMPOSE_LITE_FILE%
exit /b 1

:end
endlocal
