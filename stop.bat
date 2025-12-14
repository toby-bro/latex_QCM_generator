@echo off
echo 🛑 Stopping QCM Generator...
echo.

REM Stop Docker Compose
docker compose down

echo.
echo ✅ QCM Generator has been stopped successfully!
echo.
echo To start again, run: start.bat
echo.
pause
