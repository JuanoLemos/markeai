@echo off
REM ═══════════════════════════════════════════
REM MarketAI - Auto Update
REM Pull del repo + reinstall deps + restart orchestrator
REM Uso: update.bat  (sin args)
REM ═══════════════════════════════════════════

setlocal enabledelayedexpansion
cd /d "%~dp0"

set "LOG_FILE=%~dp0update.log"
set "VENV_PY=venv\Scripts\python.exe"

echo [%date% %time%] === Update iniciado === >> "%LOG_FILE%"

REM ── 1. git pull ──
echo [%date% %time%] git pull... >> "%LOG_FILE%"
git pull origin main >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    echo [%date% %time%] ERROR: git pull fallo >> "%LOG_FILE%"
    exit /b 1
)

REM ── 2. Si requirements.txt cambio, reinstalar ──
git diff HEAD@{1} HEAD --name-only 2>nul | findstr /I "requirements.txt" >nul
if not errorlevel 1 (
    echo [%date% %time%] requirements.txt cambio - reinstalando deps... >> "%LOG_FILE%"
    "%VENV_PY%" -m pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
)

REM ── 3. Apagar orchestrator de forma limpia (STOP file) ──
echo [%date% %time%] Creando STOP file para restart limpio... >> "%LOG_FILE%"
echo stop > STOP
timeout /t 5 /nobreak >nul

REM ── 4. Si el tray esta corriendo, lo reinicia el solo (auto-recovery) ──
REM     Si NO hay tray, arrancamos el orchestrator directo.
tasklist /FI "IMAGENAME eq python.exe" 2>nul | find /I "tray_app.py" >nul
if errorlevel 1 (
    echo [%date% %time%] Tray no detectado, arrancando orchestrator directo... >> "%LOG_FILE%"
    start "" /min "%VENV_PY%" orchestrator.py --mode loop
) else (
    echo [%date% %time%] Tray detectado, el levantara el orchestrator solo >> "%LOG_FILE%"
)

echo [%date% %time%] === Update completado === >> "%LOG_FILE%"
endlocal
exit /b 0
