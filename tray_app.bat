@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python tray_app.py
pause
