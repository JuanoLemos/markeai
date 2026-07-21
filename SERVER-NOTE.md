# Server Admin — Instrucciones

## URGENTE: Fix KeepAlive ventana invisible

La task de Task Scheduler abre ventana cada 5 min. Corregir:

```powershell
Unregister-ScheduledTask -TaskName "MarketAI-KeepAlive" -Confirm:$false -ErrorAction SilentlyContinue

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File C:\xampp\htdocs\MarketAI\scripts\keep_alive.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -Hidden
Register-ScheduledTask -TaskName "MarketAI-KeepAlive" -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force
```

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
