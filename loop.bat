@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python orchestrator.py --mode loop
pause
