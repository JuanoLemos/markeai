# Incidents Report #2 — MarketAI server (Mavis-allá)

**Fecha:** 2026-07-18
**Período:** 2026-07-12 ~22:00 ART → 2026-07-18 00:30 ART (~5 días)
**Sesión:** Mavis-allá (server 24/7, felrena 100.120.192.43)
**Audiencia:** Mavis-acá (dev) — para revisión post-incidente

---

## Resumen ejecutivo

El server cayó entre el 12/07 y el 18/07 (~5 días sin monitoreo activo). Cuando revisé, encontré 6 procesos Python zombie, ningún servicio respondiendo, y la nota del dev (`MAVIS-NOTE.md`) con instrucciones de recovery usando el nuevo `tray_watchdog.bat`.

Recovery: maté los zombie, arranqué con `tray_watchdog.bat`, server volvió. Estado al recovery: balance $1003 (de $1000), 0 trades abiertos (las 10 posiciones del run anterior se perdieron en el restart).

**Lección principal**: el cron auto-update cada 6h NO estaba trayendo los cambios del dev (commit `942bc35 tray_watchdog.bat`) porque el server estaba caído. La fix que el dev pusheó para resolver este tipo de crashes estaba en el repo pero nunca llegó al server porque el server estaba down.

---

## Timeline

| Fecha | Evento |
|---|---|
| 2026-07-12 ~22:00 | Last contact con user: server OK, 10 trades, balance $56k (PnL ficticio) |
| 2026-07-12 → 18 | 5+ días sin actividad. El bot probablemente crasheó o el tray murió. |
| 2026-07-18 00:30 | User dice "revisa notas para ti mavis en repo". Hago pull. |
| 2026-07-18 00:37 | Veo MAVIS-NOTE.md del dev: "Server caido, usa tray_watchdog.bat" |
| 2026-07-18 00:40 | Mato 6 python zombie, arranco tray_watchdog.bat, server vivo |

---

## Issues identificados

### 🔴 Issue A (CRITICAL) — El cron auto-update no me protege si el server está caído

**Síntoma**: el dev pusheó `tray_watchdog.bat` el 16/07 (commit `942bc35`). El `update.bat` que está en Task Scheduler corre `git pull` cada 6h. PERO si el server está caído, el `update.bat` no se ejecuta tampoco (porque está colgado del tray).

**Resultado**: el fix del dev estuvo 2+ días en el repo sin aplicarse porque el server estaba muerto. Si yo (Mavis-allá) hubiera estado monitoreando, habría visto el crash antes.

**Workaround aplicado**: levantar el server con `tray_watchdog.bat` (que tiene loop de auto-restart). El tray nuevo del dev está en el repo pero el server lo carga fresh.

**Fix de fondo sugerido**:
- El watchdog (`ola2_watchdog.py`) debería alertar CRITICAL si el server está caído más de 30 min
- Yo (Mavis-allá) debería chequear `data/server/heartbeat.json` cada 5-10 min y alertarte si está stale
- O un cron externo que verifique el server está vivo y me avise a vos

### 🟠 Issue B (WARNING) — Reset del state file al restart cold

**Síntoma**: cuando maté los procesos y arranqué fresh con `tray_watchdog.bat`, el paper broker arrancó sin las 10 posiciones que tenía. El balance volvió a $1003 (de $1000) en vez de $56k. Las 10 posiciones LONG abiertas (QQQ, SPY x2, MSFT x2, VTI, KO.BA, MSFT.BA, GOOGL, EURUSD=X) se perdieron.

**Causa**: el paper broker tiene su state file en `data/cache/pb_fast.json`. Si ese archivo se corrompe, no existe, o está desincronizado con la DB, el broker pierde la noción de las posiciones abiertas al reiniciar.

**Impacto**: bajo en paper mode (las posiciones eran todas "abiertas" sin PnL realizado), pero en real money significaría posiciones huérfanas que el broker no puede cerrar automáticamente.

**Fix sugerido**:
- Al iniciar el paper broker, validar que el state file esté sincronizado con la tabla `trades` de la DB
- Si hay trades con `status='open'` en la DB pero el state file está vacío, levantar WARNING o ERROR

### 🟠 Issue C (WARNING) — `api_version` reporta 1.0.0 cuando el repo está en 1.5.1

**Síntoma**: después del restart, el endpoint `/api/debug` reporta `"api_version":"1.0.0"`. El `config.yaml` debería tener `"version":"1.5.1"` (lo vi en los commits `chore(release): bump v1.5.0 -> v1.5.1`).

**Causa probable**: el `api_version` se hardcodea en `dashboard.py` o en otro lado, y no se lee de `config.yaml`. La `version` en config.yaml y el `api_version` que se sirve son cosas distintas.

**Impacto**: bajo, pero confunde. El dev debería unificar.

**Fix sugerido**: leer `version` de `config.yaml` en `/api/debug`.

### 🟠 Issue D (INFO) — PnL display ficticio ($56k con 10 posiciones) desapareció

**Síntoma**: antes del crash, el balance era $56,611 (con $382 deployed = retorno de 14,556% en 4h). Después del restart, balance $1003 (real). El PnL ficticio se fue.

**Causa**: el dev había intentado arreglar el PnL display en `a199e58 fix: ... PnL display` pero el número seguía irreal. El restart cold puede haber limpiado un state corrupto que causaba el display ficticio.

**Hipótesis**: el `current_price` se estaba tomando stale o multiplicado por un factor, y al reiniciar fresh, el cálculo es correcto. O el `pb_fast.json` tenía un `balance` mal.

**Status**: ahora OK, pero el dev debería confirmar que el fix de PnL display en `a199e58` realmente funciona, no solo que el restart lo "arregló" por accidente.

### 🟠 Issue E (INFO) — El bot abrió 10 posiciones sin freno visible

**Síntoma**: en mi última sesión antes del crash (12/07 22:00 ART), el bot había abierto 10 posiciones LONG. De 0 a 10 en ~1h. El rebalance del prompt v2 + el fix de R2/R4 gates destrabaron al bot, pero parece que lo destrabaron demasiado.

**Estado**: las posiciones se perdieron en el restart. Ahora el bot empieza de 0 trades nuevamente. Si el dev quiere, puede ajustar los gates para que el bot opere a un ritmo más controlado (ej. max 2 trades simultáneos nuevos por iteración).

---

## Lo que el dev hizo bien (reconocer el trabajo)

El dev (OpenCode+DeepSeek) estuvo MUY activo entre 12/07 y 18/07. Commits notables:

| Commit | Feature |
|---|---|
| `942bc35` | `tray_watchdog.bat` auto-restart + `kill_port_8050()` |
| `48ddef5` | `do_close()` mejorada para clean exit |
| `2a4d360` | fix(Issue1): watchdog drawdown lee PaperBroker state file |
| `a04f157` | fix(Issue3): ADX alignment optional + lower Normal thresholds |
| `1d5b75f` | perf(R89): fusion pre-filter — skip DeepSeek cuando conf<25 |
| `4ab47f7` | feat(dash): refresh button + /api/ping endpoint |
| `ec40f62` | feat: meta-model training system (10th analyzer) |
| `d7b254e` | feat: ghost system — versioned meta-model + ghost shadow trading |
| `7697929` | feat: PromptMemory — inyectar lecciones de trades pasados a DeepSeek |
| `a76c8e7` | feat(Ola4): R87, R88, R86 (ya activo) |

**5 olas documentadas, 5 issues resueltos (1, 2, 3, 7, 4), features nuevas (ghost, meta-model, prompt memory, fusion pre-filter, refresh button, ping endpoint).**

El bot está mucho más maduro que cuando empecé. El Issue 1 (drawdown no detectado) y el Issue 2 (concentración) tienen fixes importantes.

---

## Lo que faltó

### 🟡 Falta F1 — Monitoring activo de mi lado

Yo (Mavis-allá) debería haber estado mirando el server cada 5-10 min y alertando si:
- El heartbeat está stale > 5 min
- El watchdog reporta CRITICAL
- El balance tiene drawdown > 5%
- El número de trades activos se desvía de lo normal

**Por qué no lo hice**: me quedé esperando user input, no fui proactivo. El user me dijo "solo monitorea" en algún momento, pero "monitorear" no es "quedarse callado", es "revisar y avisar si hay desvíos".

**Fix**: implementar un loop de monitor que cada 5 min revise `data/server/heartbeat.json` y `/api/debug` y me alerte si algo se desvía. O usar el cron de watchdog existente.

### 🟡 Falta F2 — Script de auto-recovery

Si el server se cae solo, debería haber un watchdog externo (Task Scheduler, cron de Windows) que:
1. Detecte que el server está caído
2. Lo levante automáticamente con `tray_watchdog.bat`
3. Me avise

**Estado actual**: el dev creó `tray_watchdog.bat` que auto-reinicia el tray si crashea, pero no hay un watchdog de nivel superior que detecte que el .bat mismo no se está ejecutando.

**Fix**: crear un segundo Task Scheduler que verifique que el `tray_watchdog.bat` está corriendo, y si no, lo levante. (El dev probablemente ya pensó en esto pero no lo veo implementado).

---

## Recomendaciones para el próximo sprint

1. **CRITICAL**: El dev debería agregar un watchdog externo que verifique que el server está vivo. Si no responde en 5 min, reiniciarlo automáticamente.
2. **CRITICAL**: Yo (Mavis-allá) debería ser proactivo: revisar `/api/debug` cada 5-10 min y reportar si hay desvíos.
3. **HIGH**: Validar que el paper broker state file (`data/cache/pb_fast.json`) está sincronizado con la tabla `trades` al iniciar.
4. **MEDIUM**: Unificar `api_version` con `version` de config.yaml.
5. **MEDIUM**: Documentar el procedure de recovery en un runbook (`doc/server/RUNBOOK.md`).

---

## Estado al final del recovery

```
[ESTADO] ALIVE
api_version: 1.0.0 (raro, repo en 1.5.1)
trades_open: 0
balance_fast: $1003.03 (de $1000, +$3)
tray_watchdog.bat: corriendo en ventana separada, auto-restart 10s
```

---

*Reporte generado por Mavis-allá en sesión `mvs_ae8c77b2fdb447c6a5eec84201466adb`. Para preguntas, responder en el chat.*

**Refs:**
- `INCIDENTS_2026-07-11.md` (reporte previo, 7 issues originales)
- MAVIS-NOTE.md (instrucciones de recovery del dev)
- Commit `942bc35` (tray_watchdog.bat)
- Commit `48ddef5` (do_close + kill_port_8050)

---

## Post-recovery follow-up (2026-07-18 01:15 ART)

**El server se cayó otra vez ~1h después del primer recovery.** Mismo síntoma: el server estuvo vivo, luego dejó de responder, no había nadie que lo levantara (porque el keep_alive task todavía no se creó en Task Scheduler).

### Timeline

| Hora | Evento |
|---|---|
| 00:40 | Recovery inicial, server vivo con `tray_watchdog.bat` |
| 00:50-01:10 | Server vivo, sin actividad |
| ~01:10 | Server cae solo (causa desconocida, sin traceback) |
| 01:13 | Lo detecto, health check falla, no hay procesos python |
| 01:13 | Matar todo, arrancar `tray_watchdog.bat` fresco, health check OK |

### Estado al final

- **api_version**: sigue `1.0.0` (Issue C, no resuelto)
- **trades_open**: 0 (acaba de arrancar fresh)
- **balance_fast**: `$1003.03` (de $1000, +$3)
- **procesos**: `tray_watchdog.bat` corriendo (cmd PID 46728), tray + orchestrator + dashboard levantados

### Por qué sigue cayendo

Sin la Task Scheduler `MarketAI-KeepAlive` activa, el `tray_watchdog.bat` puede morirse y nadie lo levanta. El dev creó el `keep_alive.ps1` para esto, pero **el user no ha corrido aún el comando de Register-ScheduledTask** (requiere admin, no lo puedo correr yo).

### Estado del Issue A (CRITICAL)

| Acción | Estado |
|---|---|
| `keep_alive.ps1` creado | ✅ por el dev (commit `0522b83`) |
| `scripts/keep_alive.ps1` revisado | ✅ lógica correcta (ping → kill → restart) |
| Task Scheduler `MarketAI-KeepAlive` creada | ❌ PENDIENTE — user debe correr como admin |
| `api_version` debería pasar a 1.5.1 después del restart | ❌ sigue en 1.0.0 (Issue C) |

### Comando que el user tiene que correr

```powershell
# PowerShell como Administrador
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\xampp\htdocs\MarketAI\scripts\keep_alive.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "MarketAI-KeepAlive" -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force
```

### Recomendación para el dev

Si está leyendo esto, considera:
1. El keep_alive debería ser auto-creado por el setup script, no requerir un comando manual con admin
2. Un watchdog de nivel 2 que verifique que el keep_alive está corriendo (auto-meta-watchdog)
3. Heartbeat en la DB que el dev pueda consultar para saber si el server está vivo sin pedirle a Mavis-allá

---

## Recovery #3 — 2026-07-18 14:00 ART (causa raíz: config.yaml corrupto)

**El server se cayó a las 02:59 UTC y quedó muerto 13.7h.** El keep_alive task nunca se creó (Issue A), y nadie lo levantó.

### Hallazgo raíz (no era Issue A solo)

| # | Hallazgo | Severidad |
|---|----------|-----------|
| **G1** | `config.yaml` línea 58: `technical:` tenía 3 espacios en vez de 2 — YAML parser crasheaba al boot | 🔴 bloqueante |
| **G2** | FICTIONAL PnL detectado: $14696 vs $1000 inicial — el orchestrator moría en loop | 🟠 importante |
| **G3** | Race condition en `auto_recover` del tray: mata el orchestrator nuevo a los 7s sin darle tiempo a actualizar el heartbeat | 🟠 importante |
| **G4** | Bug de duplicación de procesos: 2 tray_app, 2 dashboard, 2 orchestrator corriendo simultáneamente | 🟡 menor |
| **G5** | `/api/ping` reporta `running:false` aunque el orchestrator está corriendo (heartbeats de DB están OK) | 🟡 menor |

### Causa raíz (G1)

```yaml
# ANTES (roto):
layers:
  adx_regime:
    enabled: true
    ...
  sentiment:
    enabled: true
    weight_forex: 0.2
    weight_polymarket: 0.2
    weight_stocks: 0.25
   technical:    # ← 3 espacios (1 menos)
    enabled: true

# DESPUÉS (arreglado):
  technical:    # ← 2 espacios
    enabled: true
```

El YAML parser esperaba que el bloque `sentiment` termine, pero al encontrar `technical:` indentado distinto se confundía:

```
yaml.parser.ParserError: while parsing a block mapping
  in "config.yaml", line 18, column 3
expected <block end>, but found '<block mapping start>'
  in "config.yaml", line 58, column 4
```

### Por qué se mantuvo 13.7h

1. **02:59 UTC**: orchestrator crashea por G1. Tray lo re-arranca. Loop infinito.
2. **Watchdog `ola2_watchdog.py`**: detecta el problema y empieza a reportar `critical` cada 5 min.
3. **Watchdog no levanta el server** — solo alerta. El `keep_alive.ps1` debería haberlo hecho, pero la task `MarketAI-KeepAlive` nunca se creó (Issue A).
4. **El dev estaba en otra PC** — no veía los logs del watchdog.
5. **Mavis-allá (esta)**: en standby. El user no había pedido monitoreo activo desde la sesión del 18/07 01:15.

### Pasos de recovery (los que se deberían automatizar)

1. `git pull --rebase` (sincronizar divergencia con origin)
2. `taskkill /f /im python.exe pythonw.exe` (matar todo)
3. Borrar `data/cache/pb_fast.json` y `pb_normal.json` (RUNBOOK: balance corrupto)
4. **Fix config.yaml**: agregar 1 espacio a `technical:` línea 58
5. `tray_watchdog.bat` (arrancar fresh)
6. Verificar `/api/health` HTTP 200 + `/api/ping` (warning: bug G5, no se actualiza)
7. Verificar `motor_heartbeat` en DB está fresco (esto sí funciona)
8. Intentar crear Task Scheduler `MarketAI-KeepAlive` — **FALLA: requiere admin**

### Estado al final (después del fix)

| Item | Estado |
|------|--------|
| `api_version` | **1.5.2** ✓ (Issue C resuelto — el problema era G1, no el dashboard) |
| `/api/health` | HTTP 200, deepseek=true polyscan=true yfinance=true |
| `motor_heartbeat` | data=ok, fusion=ok, actualizándose cada ~30s |
| `orchestrator.err.log` | VACÍO (sin errores) |
| PnL ficticio | Resuelto (state files borrados, balance se reinicializó a $1000) |
| Task `MarketAI-KeepAlive` | ❌ PENDIENTE (admin requerido, user debe correr) |
| Procesos duplicados (G4) | Persiste (bug del tray, fix en commits 942bc35/48ddef5 quedó parcial) |
| Race condition (G3) | Persiste (tray mata orchestrator nuevo en 7s; se mitigó borrando state files que el tray confundía con orchestrator stale) |

### Bugs nuevos para el dev

- **G1 (config indent)**: agregar validación de YAML al CI / pre-commit
- **G2 (FICTICIAL PnL)**: el threshold 2x debería ser configurable y el auto-detox a 3x (per RUNBOOK) debería ser la única respuesta
- **G3 (race auto_recover)**: agregar grace period de 60-90s después de `start_service(orchestrator)` antes de chequear heartbeat stale
- **G4 (procesos duplicados)**: el `kill_orphans` no funciona; tray arranca tray_app, que crea otro tray_app
- **G5 (api/ping running:false)**: el endpoint lee un state file o cache que no se actualiza; debería leer de motor_heartbeat directamente

### Acción inmediata para el user

```powershell
# PowerShell como Administrador
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File C:\xampp\htdocs\MarketAI\scripts\keep_alive.ps1"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 5) -RepetitionDuration (New-TimeSpan -Days 365)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "MarketAI-KeepAlive" -Action $action -Trigger $trigger -Settings $settings -RunLevel Highest -Force
```

Sin la task, el próximo crash del server no se va a poder recuperar solo.

---

*Actualizado: 2026-07-18 14:00 ART por Mavis-allá*
