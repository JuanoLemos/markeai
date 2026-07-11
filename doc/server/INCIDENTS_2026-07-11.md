# Incidents Report — MarketAI server (Mavis-allá)

**Fecha:** 2026-07-11
**Período analizado:** 2026-07-10 21:00 ART → 2026-07-11 16:00 ART (~19 horas)
**Sesión:** Mavis-allá (server 24/7, felrena 100.120.192.43)
**Audiencia:** Mavis-acá (dev) — para triage y fixes en próximo push
**Última actualización:** 2026-07-11 16:00 ART (Issue 7 agregado tras evidencia del dashboard)

---

## Resumen ejecutivo

El server corrió 19h en paper mode, watchdog activo, sin intervención. Resultado neto:

- ✅ Server uptime: 100%, ningún crash de proceso
- ✅ DeepSeek respondiendo con decisiones reales (LONG con conf 33-70)
- ✅ 11 trades abiertos en stocks (todos LONG, mismo signal)
- ❌ **Drawdown -39.8% ($1000 → $602.06) sin que el watchdog lo detectara**
- ❌ Concentración de 11 posiciones simultáneas en activos correlacionados
- ❌ 0 trades cerrados en 19h (todos zombies)
- ❌ **Dashboard reporta PnL ficticio de +$10,736.92 (ganancia falsa)**
- ⚠️ 7 issues identificados que requieren fix de diseño (no workarounds)

Los workarounds aplicados in-place (`config.yaml` + `entry_filters.py`) están list abajo pero **no resuelven el problema de fondo** — solo permiten que el bot abra trades para evidenciar el resto de los gaps.

---

## Issues identificados

### 🔴 Issue 1 (CRITICAL) — Watchdog no detecta drawdown con trades abiertos

**Síntoma:** El check `check_drawdown` en `ola2_watchdog.py` solo evalúa trades con `exit_time` populated:

```python
# ola2_watchdog.py:147-150
row_today = cur.execute(
    "SELECT ROUND(COALESCE(SUM(pnl_usd), 0), 2) FROM trades "
    "WHERE DATE(exit_time) = DATE('now') AND exit_reason != 'lost_recovery'"
).fetchone()
```

Con 11 trades open 18h, `exit_time IS NULL` para todos → query devuelve 0 → check reporta "ok".

**Evidencia:**
- Real: balance cayó de $1000 a $602.06
- Watchdog reportó status="ok" durante todo el período
- 0 incidents de drawdown generados

**Impacto:** El server puede perder 100% de la cuenta sin que el watchdog alerte.

**Fix recomendado:** Calcular drawdown también con mark-to-market de posiciones abiertas, o usar `portfolio.total_pnl` directamente. La tabla `portfolio` ya tiene el dato (`balance_usd`, `total_pnl` columnas).

```python
# Propuesta: leer drawdown de portfolio
cur.execute("SELECT balance_usd, total_pnl FROM portfolio ORDER BY timestamp DESC LIMIT 1")
balance, total_pnl = cur.fetchone()
pct = (total_pnl / INITIAL_BALANCE) * 100
```

---

### 🔴 Issue 2 (CRITICAL) — Bot abre N posiciones correlacionadas sin límite efectivo

**Síntoma:** El bot abrió 11 trades LONG simultáneos (SPY, QQQ, AAPL, MSFT, GOOGL, AMZN, IVV, EEM, IWM, XLK + 1 más) en 3 minutos. Todos LONG, todos stocks, todos ultra-correlacionados. 100% de exposición.

**Causa raíz:** El `correlation_check` en `pipeline.py:111-115` solo dispara cuando YA hay posiciones abiertas. La primera posición pasa sin filtro de correlación (no hay nada contra qué correlacionar). El bot abusa de esto y abre 11 antes de que el filtro entre en juego.

**Evidencia:**
- 11 trades con `signal=LONG`, todos `market=fast_stocks`
- `entry_time` agrupados en 3 min (03:36:48 → 03:39:45 UTC)
- `portfolio` muestra `open_positions=11` simultáneamente

**Fix recomendado:** El `correlation_check` debe evaluar la concentración sectorial / correlación agregada, no solo pairwise. Alternativamente, agregar un `max_open_positions_per_market` global (no per-profile) que se valide ANTES de abrir.

---

### 🟠 Issue 3 (WARNING) — Filtro de exposición (`max_total_exposure_pct`) no se aplica

**Síntoma:** `config.yaml` define `max_total_exposure_pct: 0.40` (40% del balance). El bot abrió 11 posiciones que suman ~$398 de un balance inicial de $1000. 40% en teoría OK, pero con el drawdown el balance efectivo es $602, y $398/$602 = 66% de exposición real, mucho más que el límite.

**Causa probable:** El límite se evalúa al momento de abrir (con balance pre-trade). No se reevalúa cuando el balance baja. El bot sigue abriendo porque el límite "se cumplió" antes.

**Fix recomendado:** Re-evaluar `max_total_exposure_pct` cada vez que se intenta abrir, usando el balance ACTUAL de `portfolio`, no el inicial. Si el límite se excedió, no abrir más hasta que se cierren posiciones.

---

### 🟠 Issue 4 (WARNING) — `session_hours` ignora profile para stocks

**Síntoma:** En `entry_filters.py:78-81`, el filtro de horario para stocks usa la misma ventana `14 <= utc_hour < 21` tanto para `normal` como para `fast`. Solo `forex` distingue profile. Resultado: el profile `fast` se bloquea a las 3 UTC igual que `normal`.

**Causa:** El bloque `if market == "stocks":` no tiene la rama `if profile == "fast":` que sí tiene `forex`. Bug histórico.

**Workaround aplicado (in-place):** Agregada la rama para `fast` que retorna `True` (24/7). Ver commit/log.

**Fix recomendado:** Mismo patrón que `forex`: definir ventanas permisivas para `fast` en stocks también. Ej. `0 <= utc_hour < 22` o `True` (24/7 crypto-style). Decisión de diseño que requiere tu input.

---

### 🟠 Issue 5 (WARNING) — Watchdog `loop_alive` genera falsos positivos por cadencia del orchestrator

**Síntoma:** El watchdog reporta `loop_alive: warning` cada 5 min con `age_min: 5-15` aunque el orchestrator está vivo y trabajando. 18 incidents `loop_alive` en 18h.

**Causa:** El orchestrator solo escribe `motor_heartbeat` cuando corre `run_iteration()`. Los intervals son forex=60min, stocks=60min, polymarket=15min. Entre iteraciones, el orchestrator duerme 30s sin escribir heartbeat. El watchdog threshold es 5min → 100% de los gaps caen en warning.

**Evidencia:** Los 18 incidents `*.json` en `data/server/incidents/` son todos del mismo tipo, mismo mensaje, mismo range de age.

**Fix recomendado:** Dos opciones:
- (a) El orchestrator debería escribir un heartbeat liviano cada N segundos desde el `time.sleep()` del loop principal, no solo en iteraciones.
- (b) Subir el threshold `LOOP_STALE_WARN_MIN` a algo que matchee la cadencia real (15+ min). Trade-off: detección más lenta de loop realmente muerto.

**Recomendación:** (a) — el heartbeat debería reflejar "estoy vivo", no "estoy iterando".

---

### ⚠️ Issue 6 (INFO) — Duplicación de procesos en `tray_app.py`

**Síntoma:** El tray arranca 2 instancias de orchestrator + 2 de dashboard. Llevamos así desde el setup inicial. El sistema funciona (8050 escucha, DB escribe) pero consume 2x recursos.

**Causa probable:** Race condition en `_cleanup_old()` + `start_loop()` + el tick de auto-recovery. Cuando el tray detecta que `loop_process` murió, arranca uno nuevo sin verificar si ya hay otro orchestrator corriendo (huérfano de runs anteriores).

**Fix recomendado:** El `tick()` del tray debería:
1. Listar procesos python con `orchestrator` en cmdline
2. Si hay más de 1, matar los extras
3. Si hay 0, arrancar uno
4. Si hay 1, no hacer nada (asumir que es el suyo)

Esto no es bloqueante (el bot funciona) pero es ruido.

---

### 🔴 Issue 7 (CRITICAL) — `portfolio.total_pnl` reporta valor ficticio inflado

**Síntoma:** El dashboard muestra capital total $12,736.92 con ganancia +$10,736.92 (+536.8%), pero la realidad es drawdown -39.8%. El `portfolio.total_pnl` se congela en un valor estático que no refleja el estado real.

**Evidencia (snapshots de `portfolio` cada 15 min):**
```
id=195 ts=18:07:31 total_pnl=-397.94   (correcto, refleja realidad)
id=197 ts=18:22:34 total_pnl=+10736.92  ← SALTO de -397 a +10737
id=199 ts=18:38:15 total_pnl=+10736.92  (idéntico, no se mueve)
id=201 ts=18:50:29 total_pnl=+10736.92  (idéntico, no se mueve)
```

El PnL reportado:
- Saltó de -$397.94 a +$10,736.92 entre dos snapshots (15 min)
- Se mantiene constante en +$10,736.92 desde entonces (debería oscilar con precios de mercado si fuera MTM real)
- Los 11 trades en la tabla `trades` siguen con `pnl_usd=0.0` y `status=open` — no hay un trade cerrado que justifique el PnL

**Causa probable:** Cuando se abrió el último de los 11 trades, el sistema calculó un PnL esperado (¿suma de position_size_usd * take_profit_pct? ¿mark-to-market con factor mal?) y lo asignó a `portfolio.total_pnl`. La fórmula de cálculo está mal y produce un número sin relación con el resultado real. Posibles bugs:
- `position_size_usd` interpretado en centavos en vez de dólares
- Factor de apalancamiento fantasma
- Suma duplicada por la duplicación de orchestrators (Issue 6) — ambos escriben al mismo `portfolio` table
- Cálculo de MTM con precio de take_profit en vez de precio actual

**Impacto:** El usuario ve un dashboard que dice "estás ganando $10,000" cuando en realidad está perdiendo 40%. Riesgo de que tome decisiones (o peor, que muestre a terceros) basadas en números falsos.

**Fix recomendado:**
- Auditar la función que escribe `portfolio.total_pnl` (probablemente en `execution/paper_broker.py` o `orchestrator/core.py`)
- Comparar el cálculo contra el delta real: `SUM(trades.pnl_usd WHERE status='closed') + SUM(unrealized_pnl WHERE status='open')`
- El unrealized_pnl debe usar precios actuales de yfinance, no el take_profit
- Considerar kill-switch: si `|total_pnl| > balance_usd * 2`, log warning — número claramente mal

---

## Workarounds aplicados in-place (commiteados en e0bbeea)

| Archivo | Cambio | Razón |
|---|---|---|
| `config.yaml` | `profiles.normal.per_market.stocks.min_confidence: 45 → 30` | Habilitar que el bot abra trades para evidenciar Issues 1-3 |
| `execution/entry_filters.py` | Agregada rama `if profile == "fast": return True` en session_hours para stocks | Workaround de Issue 4 |

Ambos cambios commiteados en `e0bbeea` y pusheados. El usuario aprobó mantenerlos como fixes legítimos.

---

## Estado del server al momento del reporte (2026-07-11 16:00 ART)

| Métrica | Valor |
|---|---|
| Procesos | 6 (2 tray, 2 dash, 2 orch — Issue 6) |
| Uptime | tray 17h, dash 17h, orch 15h (después del fix) |
| DB | 2.4 MB, 11 trades, 7825 heartbeats, 202 portfolio entries |
| Balance | $602.06 (de $1000 inicial, -39.8%) — **REALIDAD** |
| Dashboard PnL | +$10,736.92 — **FICTICIO, Issue 7** |
| Open positions | 11 LONG stocks (sin cerrar) |
| Watchdog última corrida | ~15:50 ART, status=warning (loop_alive falso positivo) |
| Auto-update cron | 3 corridas (04:18, 10:18, 16:18), "Already up to date" |
| Próxima auto-update | 22:18 ART (6h después) |

---

## Recomendación de prioridad de fixes

1. **Issue 7** (PnL ficticio en dashboard) — **máxima prioridad**. El usuario está viendo números falsos. Riesgo de tomar decisiones malas basado en esto. **Nuevo, agregado en update 16:00 ART.**
2. **Issue 1** (drawdown no detectado) — **máxima prioridad**. Es el gap más peligroso. Sin esto, el server puede perder todo silenciosamente.
3. **Issue 2** (concentración sin límite efectivo) — **alta**. El bot puede duplicar exposición sin que nada lo frene.
4. **Issue 3** (límite de exposición no se reevalúa) — **alta**. Relacionado con Issue 2.
5. **Issue 5** (heartbeat falso positivo) — **media**. Ruido en logs, no peligro operacional.
6. **Issue 4** (session_hours fast en stocks) — **baja**. Workaround aplicado, decisión de diseño pendiente.
7. **Issue 6** (duplicación de procesos) — **baja**. Funcional, solo consumo extra. **Posible causa raíz de Issue 7** — dos orchestrators escribiendo al mismo portfolio.

---

## Preguntas abiertas para Mavis-acá

1. ¿El drawdown check debería leer de `portfolio` (mark-to-market) o los trades cerrados? Propongo portfolio.
2. ¿El `max_total_exposure_pct` se evalúa con balance inicial o actual? Propongo actual.
3. ¿El `correlation_check` debería ser pairwise o agregado? Propongo ambos.
4. ¿El heartbeat debería escribirse cada N segundos (loop principal) o solo en iteraciones? Propongo cada N.
5. ¿Workarounds en `config.yaml` y `entry_filters.py` van al repo o se revierten? Mi voto: van al repo, son fixes legítimos.
6. **¿La duplicación de orchestrators (Issue 6) está causando el PnL ficticio (Issue 7)?** Si ambos escriben al mismo `portfolio`, podría duplicar PnL. **A investigar primero.**

---

*Reporte generado por Mavis-allá en sesión `mvs_ae8c77b2fdb447c6a5eec84201466adb`. Para preguntas, responder en el chat.*
