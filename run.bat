@echo off
setlocal enabledelayedexpansion

REM DistroViz v3 - Zero-Config Startup Script for Windows
REM Validates Docker, builds images, starts services, and waits for healthy status

echo.
echo [INFO] Starting DistroViz v3...
echo.

REM Check if Docker is installed and running
echo [INFO] Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Check for Docker Compose
docker compose version >nul 2>&1
if errorlevel 1 (
    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Docker Compose is not available. Please ensure Docker Desktop includes Compose.
        pause
        exit /b 1
    )
    set COMPOSE_CMD=docker-compose
) else (
    set COMPOSE_CMD=docker compose
)

echo [SUCCESS] Docker is installed and running

REM Create necessary directories
echo [INFO] Setting up directories...
if not exist "data" mkdir data
echo [SUCCESS] Directories created

REM Copy environment file if it doesn't exist
if not exist ".env" (
    echo [INFO] Creating .env file from template...
    copy ".env.example" ".env" >nul
    echo [SUCCESS] Environment file created. You can customize .env if needed.
) else (
    echo [INFO] Using existing .env file
)

REM Stop any existing containers
echo [INFO] Stopping any existing containers...
%COMPOSE_CMD% ps -q >nul 2>&1
if not errorlevel 1 (
    %COMPOSE_CMD% down --remove-orphans
    echo [SUCCESS] Existing containers stopped
) else (
    echo [INFO] No existing containers to stop
)

REM Build and start services
echo [INFO] Building and starting services...
%COMPOSE_CMD% build --no-cache
if errorlevel 1 (
    echo [ERROR] Failed to build images
    pause
    exit /b 1
)
echo [SUCCESS] Images built successfully

%COMPOSE_CMD% up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)
echo [SUCCESS] Services started

REM Wait for services to be healthy
echo [INFO] Waiting for services to be healthy...
set /a attempt=1
set /a max_attempts=60

:wait_loop
if !attempt! gtr !max_attempts! (
    echo [WARNING] Services may not be fully healthy yet, but continuing...
    %COMPOSE_CMD% ps
    goto test_endpoints
)

REM Simple health check by attempting to connect
timeout /t 2 /nobreak >nul
curl -s -f "http://localhost:8000/api/health" >nul 2>&1
if not errorlevel 1 (
    curl -s -f "http://localhost:3000" >nul 2>&1
    if not errorlevel 1 (
        echo [SUCCESS] All services are healthy!
        goto test_endpoints
    )
)

set /a remainder=!attempt! %% 10
if !remainder! equ 0 (
    echo [INFO] Still waiting... (attempt !attempt!/!max_attempts!)
)

set /a attempt+=1
goto wait_loop

:test_endpoints
echo [INFO] Testing API endpoints...

REM Extract ports from .env file
set BACKEND_PORT=8000
set FRONTEND_PORT=3000

if exist ".env" (
    for /f "tokens=1,2 delims==" %%a in (.env) do (
        if "%%a"=="BACKEND_PORT" set BACKEND_PORT=%%b
        if "%%a"=="FRONTEND_PORT" set FRONTEND_PORT=%%b
    )
)

REM Test health endpoint
curl -s -f "http://localhost:!BACKEND_PORT!/api/health" >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] Health endpoint responding
) else (
    echo [WARNING] Health endpoint not responding yet
)

REM Test dashboard endpoint
curl -s -f "http://localhost:!BACKEND_PORT!/api/dashboard/summary" >nul 2>&1
if not errorlevel 1 (
    echo [SUCCESS] Dashboard API responding
) else (
    echo [WARNING] Dashboard API not responding yet
)

REM Print access information
echo.
echo ==========================================
echo [SUCCESS] DistroViz v3 is ready!
echo ==========================================
echo.
echo 🌐 Web Application: http://localhost:!FRONTEND_PORT!
echo 🔧 API Documentation: http://localhost:!BACKEND_PORT!/docs
echo ❤️  Health Check: http://localhost:!BACKEND_PORT!/api/health
echo.
echo 📊 Available Features:
echo   • Dashboard with KPIs and charts
echo   • Orders management interface
echo   • Real-time data updates
echo.
echo 🛠️  Management Commands:
echo   • View logs: %COMPOSE_CMD% logs -f
echo   • Stop services: %COMPOSE_CMD% down
echo   • Restart: run.bat
echo.
echo ==========================================
echo.
echo [SUCCESS] Startup complete! 🚀
echo.
echo Press any key to exit...
pause >nul