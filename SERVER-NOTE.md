# Server Admin — Instrucciones

## ✅ CORREGIDO: Tasks invisibles (2026-07-22)

Ambas tasks de 5 min ahora corren con `-WindowStyle Hidden` y `-Hidden`:

| Task | Hidden | Ejecuta |
|---|---|---|
| MarketAI-KeepAlive | True | `powershell.exe ... keep_alive.ps1` |
| MarketAI-Watchdog | True | `pythonw.exe ... ola2_watchdog.py` |

Si se necesita recrear manualmente, usar los comandos abajo.

## Hacer pull del ultimo codigo

```powershell
cd C:\xampp\htdocs\MarketAI
git pull origin main
```

## Verificar server

```powershell
curl http://localhost:8050/api/ping            # ¿Vivo?
curl http://localhost:8050/api/debug           # Estado completo
curl http://localhost:8050/api/positions       # Posiciones abiertas
curl http://localhost:8050/api/gates/recent    # Rechazos de gates
curl http://localhost:8050/api/ghost/compare   # Ghost vs live
```

## Recovery si no responde

```powershell
taskkill /f /im python.exe
cd C:\xampp\htdocs\MarketAI
tray_watchdog.bat
```

## Deploy ultimo codigo

```powershell
curl -X POST http://localhost:8050/api/deploy -H "X-Auth-Token: mavis2026marketai"
```

## Datos

| Campo | Valor |
|---|---|
| Repo | `C:\xampp\htdocs\MarketAI` |
| Dashboard | `http://localhost:8050` |
| Token | `mavis2026marketai` |
| Version | 1.5.2 |
