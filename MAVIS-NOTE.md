# Mavis — Setup: Keep Alive + Recovery

Vi tu reporte de incidente (INCIDENTS_2026-07-18.md). Buen analisis.

## Issue A (CRITICAL) — Watchdog externo via Task Scheduler

Ejecuta esto UNA SOLA VEZ en la notebook (PowerShell como Administrador):

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\xampp\htdocs\MarketAI\scripts\keep_alive.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "MarketAI-KeepAlive" -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force
```

Esto ejecuta `keep_alive.ps1` cada 5 minutos. Si el server no responde, mata zombies y lo levanta con `tray_watchdog.bat`.

Funciona aunque la notebook se reinicie (Task Scheduler se recupera solo).

## Issue C — api_version

El `_version()` lee de config.yaml. Si muestra 1.0.0 es porque el dashboard que esta corriendo cargo un config viejo. Despues del proximo restart completo (tray -> Update & Restart) deberia mostrar 1.5.1.

## Para monitorear el server desde aca (dev PC)

```powershell
# Ver estado
Invoke-RestMethod http://192.168.1.34:8050/api/debug | ConvertTo-Json

# Ver rechazos de gates
Invoke-RestMethod http://192.168.1.34:8050/api/gates/recent | ConvertTo-Json
```
