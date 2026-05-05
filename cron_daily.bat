@echo off
cd /d "%~dp0"
call venv\Scripts\activate
python orchestrator.py --mode cron --task daily
