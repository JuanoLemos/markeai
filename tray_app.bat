@echo off
cd /d "%~dp0"
start /B "" "venv\Scripts\python.exe" "tray_app.py"
exit
