@echo off
title MarketAI — Dashboard
cd /d "%~dp0"

echo [1/3] Buscando proceso en puerto 8050...
set KILLED=0
for /f "tokens=5" %%p in ('netstat -aon 2^>nul ^| findstr ":8050 " ^| findstr "LISTENING"') do (
    echo  Deteniendo PID %%p en puerto 8050
    taskkill /F /PID %%p >nul 2>&1
    set KILLED=1
)
if %KILLED%==0 echo  Ningun proceso escuchando en 8050.
timeout /t 1 /nobreak >nul

echo [2/3] Activando entorno virtual...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: no se encontro venv\Scripts\activate
    pause
    exit /b 1
)

echo [3/3] Iniciando dashboard en http://localhost:8050
echo  Cierra esta ventana para detener el servidor.
echo.
python dashboard.py
echo.
echo  El servidor se detuvo.
pause
