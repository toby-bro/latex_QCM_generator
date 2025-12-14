@echo off
echo ========================================
echo Stopping QCM Generator...
echo ========================================
echo.

REM Stop Docker Compose
docker compose down

echo.
echo ========================================
echo QCM Generator stopped successfully!
echo ========================================
echo.
echo To start again, run: start.bat
echo.
pause
