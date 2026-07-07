@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.━━ MarketAI Deploy ━━
echo.

echo.1. git pull...
git pull origin master
if %errorlevel% neq 0 (
    echo.ERROR: git pull failed
    pause
    exit /b 1
)

echo.2. docker compose down...
docker compose down

echo.3. docker compose up -d --build...
docker compose up -d --build

echo.4. Checking services...
timeout /t 5 /nobreak >nul
docker compose ps

echo.
echo.Deploy complete. Dashboard: http://localhost:8050
