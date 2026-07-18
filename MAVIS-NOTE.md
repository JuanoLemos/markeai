# Mavis — Instrucciones post-recuperacion

ISP cambió, IP ahora es 192.168.100.4. Todo lo demas funciona igual.

## 1. Arrancar con watchdog

En PowerShell, en C:\xampp\htdocs\MarketAI:

```powershell
tray_watchdog.bat
```

No cerrar esa ventana. Si el tray crashea, el .bat lo revive en 10s.

## 2. Task Scheduler (una sola vez, como Administrador)

Esto verifica cada 5 min que el server este vivo y lo revive si no:

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\xampp\htdocs\MarketAI\scripts\keep_alive.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "MarketAI-KeepAlive" -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force
```

## 3. Datos del server

| Campo | Valor |
|---|---|
| Repo | `C:\xampp\htdocs\MarketAI` |
| Dashboard | `http://192.168.100.4:8050` (LAN) o `http://100.120.192.43:8050` (Tailscale) |
| Token auth | `mavis2026marketai` |
| IP Tailscale felrena | 100.120.192.43 |
| IP Tailscale dev | 100.125.180.6 |
| Version | 1.5.2 |

## 4. Comandos utiles

```powershell
# Ver server local
curl http://localhost:8050/api/ping

# Ver estado completo
curl http://localhost:8050/api/debug

# Matar todo y reiniciar
taskkill /f /im python.exe
tray_watchdog.bat
```

## 5. Archivos de referencia

- `doc/server/RUNBOOK.md` — Recovery procedures
- `doc/server/INCIDENTS_2026-07-18.md` — Reporte del crash
- `scripts/keep_alive.ps1` — Watchdog externo
