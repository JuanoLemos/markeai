# VAIO — Server admin (reemplaza a Mavis)

## Tareas diarias

### 1. Verificar que el server esta vivo

```powershell
curl http://localhost:8050/api/ping
```

Si responde `{"running":true,"version":"1.5.2"...}` → OK. Si timeout → recovery.

### 2. Recovery si no responde

```powershell
taskkill /f /im python.exe
cd C:\xampp\htdocs\MarketAI
tray_watchdog.bat
```

### 3. Deploy ultimo codigo (desde server)

```powershell
curl -X POST http://localhost:8050/api/deploy -H "X-Auth-Token: mavis2026marketai"
```

### 4. Monitorear bot

```powershell
# Estado completo
curl http://localhost:8050/api/debug

# Posiciones abiertas
curl http://localhost:8050/api/positions

# Rechazos de gates
curl http://localhost:8050/api/gates/recent

# Ghost vs live
curl http://localhost:8050/api/ghost/compare
```

## Task Scheduler — KeepAlive

Ya configurado. Corre cada 5 min. Si el server no responde, lo reinicia solo. Verificar:

```powershell
Get-ScheduledTask -TaskName "MarketAI-KeepAlive" | Select-Object State
```

## Archivos de referencia

- `doc/server/RUNBOOK.md` — Recovery procedures
- `doc/server/INCIDENTS_2026-07-18.md` — Historial de crashes
- `scripts/keep_alive.ps1` — Watchdog externo
- `tray_watchdog.bat` — Auto-restart del tray

## Datos del server

| Campo | Valor |
|---|---|
| Repo | `C:\xampp\htdocs\MarketAI` |
| Dashboard local | `http://localhost:8050` |
| Token auth | `mavis2026marketai` |
| Version | 1.5.2 |
