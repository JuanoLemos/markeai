@echo off
chcp 65001 >nul
cd /d C:\xampp\htdocs\MarketAI

:restart
echo [%date% %time%] Starting tray...
venv\Scripts\python.exe tray_app.py
echo [%date% %time%] Tray exited (code %errorlevel%). Restarting in 10s...
timeout /t 10 /nobreak >nul
goto restart
