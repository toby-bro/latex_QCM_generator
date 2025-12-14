@echo off
echo ========================================
echo Starting QCM Generator...
echo ========================================
echo.

REM Check for updates
echo Checking for updates...
git pull
if errorlevel 1 (
    echo [WARNING] Could not check for updates. Continuing anyway...
)
echo.

if exist docker-compose.prod.yml (
    REM This overwrites docker-compose.yml with the prod version
    copy /Y docker-compose.prod.yml docker-compose.yml >nul
    echo Production configuration applied.
) else (
    echo [ERROR] docker-compose.prod.yml was not found.
    echo Cannot switch to production configuration.
    pause
    exit /b 1
)
echo.
REM ---------------------------------------------------------

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed.
    echo Please install Docker Desktop from: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Start Docker Compose
echo Pulling latest image and starting containers...
docker compose pull
docker compose up -d

REM Wait a moment for the service to start
timeout /t 3 >nul

echo.
echo ========================================
echo QCM Generator is now running!
echo ========================================
echo.
echo Open your browser and go to: http://localhost:5000
echo.
echo To stop the application, run: stop.bat
echo.
pause
