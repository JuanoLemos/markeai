# RUNBOOK — MarketAI Server Recovery

Procedimientos de recuperacion para el administrador del server.

---

## Server no responde (timeout en :8050)

```
1. Verificar si hay proceso vivo:
   netstat -ano | findstr :8050

   Si muestra LISTENING en 0.0.0.0:8050 → server vivo. Probar desde navegador.

2. Si no hay LISTENING o la pagina no carga:
   taskkill /f /im python.exe
   cd C:\xampp\htdocs\MarketAI
   tray_watchdog.bat

3. Verificar que responda:
   curl http://localhost:8050/api/ping
   curl http://localhost:8050/api/debug
```

## Balance corrupto o PnL ficticio

```
Si el balance muestra numeros imposibles (ej: $30k en vez de ~$1000):

Desde dev PC (requiere token):
  Invoke-RestMethod -Method Post -Uri http://192.168.1.34:8050/api/debug/reset-broker
    -Headers @{"X-Auth-Token"="mavis2026marketai"}
    -Body '{"profile":"fast"}'

Desde la notebook (sin token):
  Remove-Item C:\xampp\htdocs\MarketAI\data\cache\pb_fast.json -Force
  # El auto-detox lo hace solo al reiniciar si el balance > 3x
```

## Bot no abre trades (0 trades en 4h+)

```
1. Verificar que DeepSeek responde:
   curl http://localhost:8050/api/health
   -> deepseek: true

2. Verificar sesion de mercado:
   Stocks: 14-21 UTC (lunes a viernes)
   Forex: 24/5
   El fix R89 bloquea llamadas fuera de sesion.

3. Revisar ultimos logs:
   Get-Content C:\xampp\htdocs\MarketAI\orchestrator.log -Tail 50

4. Forzar deploy con ultimo codigo:
   Invoke-RestMethod -Method Post -Uri http://localhost:8050/api/deploy
     -Headers @{"X-Auth-Token"="mavis2026marketai"}
```

## Deploy remoto (dev PC)

```
Invoke-RestMethod -Method Post -Uri http://192.168.1.34:8050/api/deploy
  -Headers @{"X-Auth-Token"="mavis2026marketai"}
```

## Comandos utiles

```powershell
# Estado completo del bot
curl http://localhost:8050/api/debug

# Posiciones abiertas
curl http://localhost:8050/api/positions

# Rechazos de risk gates (ultimas 24h)
curl http://localhost:8050/api/gates/recent

# Ghost system: comparacion live vs ghost
curl http://localhost:8050/api/ghost/compare

# Monitorear logs en vivo
Get-Content C:\xampp\htdocs\MarketAI\orchestrator.log -Tail 20 -Wait
```

## Archivos relacionados

- `scripts/keep_alive.ps1` — Watchdog externo via Task Scheduler
- `tray_watchdog.bat` — Auto-restart del tray si crashea
- `SERVER-NOTE.md` — Instrucciones activas para el server admin
- `INCIDENTS_2026-07-18.md` — Reporte de incidente previo
