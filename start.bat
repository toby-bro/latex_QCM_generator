@echo off
echo 🚀 Starting QCM Generator...
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not installed.
    echo Please install Docker Desktop from: https://docs.docker.com/get-docker/
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not running.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

REM Start Docker Compose
echo 📦 Building and starting containers...
docker compose up --build -d

REM Wait a moment for the service to start
timeout /t 3 >nul

echo.
echo ✅ QCM Generator is now running!
echo.
echo 🌐 Open your browser and go to: http://localhost:5000
echo.
echo To stop the application, run: stop.bat
echo.
pause
