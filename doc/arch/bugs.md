# Bugs — MarketAI

**Actualizado:** 2026-05-29 | **Total:** 12 activos

---

## P1 — Críticos (7)

### B-01 — Trades cerrados nunca se persisten en DB

| Campo | Detalle |
|-------|---------|
| **Archivo** | `orchestrator.py:475` |
| **Severidad** | P1 — Pérdida de datos |
| **Descripción** | `self.db.close_trade(0, c["exit_price"], ...)` hardcodea `trade_id=0`. El `UPDATE trades SET ... WHERE id=0` no encuentra ninguna fila. Todas las salidas de posiciones se pierden silenciosamente en la base de datos. |
| **Causa** | PaperBroker devuelve trades con `id`, pero el orchestrator no lo propaga a `close_trade`. |
| **Impacto** | DB incompleta. Equity curve, win rate, y métricas históricas son incorrectas. |
| **Estado** | Resuelto |
| **Fix** | `orchestrator.py:260` captura `db_trade_id` de `insert_trade()`; `paper_broker.py:142` incluye `_db_id` en resultado de `close_position`; `orchestrator.py:477-481` usa `_db_id` en vez de hardcoded 0 + warning si falta |

### B-02 — VIX > 30 es código muerto en macro analyzer

| Campo | Detalle |
|-------|---------|
| **Archivo** | `analyzers/macro.py:19-24` |
| **Severidad** | P1 — Lógica incorrecta |
| **Descripción** | La condición `vix > 25` se evalúa antes que `vix > 30`. Como 30 > 25, un VIX >= 30 siempre entra en la rama `> 25` (score 40) y nunca llega a la rama `> 30` (score 25, "pánico"). |
| **Causa** | Orden incorrecto de condiciones if/elif. |
| **Impacto** | En mercado de pánico (VIX alto), el analyzer da score alcista (40) en vez de defensivo (25). Señal incorrecta en condiciones extremas. |
| **Estado** | Resuelto |
| **Fix** | `analyzers/macro.py:19-22` — intercambiado orden de `elif vix > 30` (score 25) y `elif vix > 25` (score 35). Ahora la condición extrema se evalúa primero. |

### B-03 — Cálculo de cantidad incorrecto en executor tradicional

| Campo | Detalle |
|-------|---------|
| **Archivo** | `execution/executor_traditional.py:136` |
| **Severidad** | P1 — Pérdida financiera potencial |
| **Descripción** | `qty = max(1, int(size_usd / 100))` asume que cada acción cuesta ~$100, lo cual es falso para la mayoría de activos. Debería calcular `size_usd / current_price`. |
| **Causa** | Fórmula hardcodeada sin obtener precio de mercado. |
| **Impacto** | Órdenes con cantidad incorrecta al pasar a real. SPY a $500+ compraría 1 acción en vez de la fracción correcta para el position sizing. |
| **Estado** | Resuelto |
| **Fix** | `execution/executor_traditional.py:136` — reemplazado `"qty": max(1, int(size_usd/100))` por `"notional": str(size_usd)` (órdenes en USD en vez de acciones). Además, `orchestrator.py:268` — guard para evitar KeyError con `trade["id"]` de Alpaca. |

### B-04 — Clases CSS inexistentes en sandbox.html

| Campo | Detalle |
|-------|---------|
| **Archivo** | `templates/sandbox.html:15,36,39,42` |
| **Severidad** | P1 — UI rota |
| **Descripción** | El template usa `.panel-h`, `.btn-neg`, `.btn-warn`, `.form-row` — ninguna existe en `static/style.css`. Los headers de panel, botones de reset/limpiar, y formularios se renderizan sin estilo. |
| **Causa** | Clases de un CSS anterior o de backup no migradas al CSS activo. |
| **Impacto** | Página `/sandbox` inusable visualmente. Botones sin color, formularios sin layout. |
| **Estado** | Resuelto |
| **Fix** | `static/style.css` — agregado `.form-row` + `.btn-warn`. `templates/sandbox.html` — reemplazado `.panel-h`→`.panel-header` (existía), `.btn-neg`→`.btn-danger` (existía). |

### B-05 — kill_services() mata TODOS los procesos Python del sistema

| Campo | Detalle |
|-------|---------|
| **Archivo** | `tray_app.py:138-149` |
| **Severidad** | P1 — Destructivo |
| **Descripción** | Original: `Get-Process -Name python* \| Stop-Process -Force` mataba cualquier proceso Python en el sistema, no solo los de MarketAI. |
| **Causa** | Filtro demasiado amplio. |
| **Impacto** | Si el usuario tiene Jupyter, otra app Flask, o cualquier script Python corriendo, el botón "Kill Services" los destruye todos. |
| **Estado** | Resuelto |
| **Fix** | `tray_app.py` — `kill_services()` ahora mata `loop_process` via Popen.kill() directa + llama a `_cleanup_old()` que filtra por `CommandLine -match 'orchestrator\|dashboard'`. |

### B-06 — /api/positions lee estado de archivo obsoleto

| Campo | Detalle |
|-------|---------|
| **Archivo** | `dashboard.py` — `api_positions()` |
| **Severidad** | P1 — Datos inconsistentes |
| **Descripción** | `/api/positions` lee `paper_broker_state.json` (singular, legacy), mientras que el sistema real escribe a `pb_normal.json` y `pb_fast.json`. Las posiciones inyectadas con `trigger_broker=true` nunca aparecen en esta ruta. |
| **Causa** | No se actualizó al migrar a perfiles duales. |
| **Impacto** | Dashboard muestra posiciones incorrectas. Sandbox inject no se refleja en overview. |
| **Estado** | Resuelto |
| **Fix** | `dashboard.py` — `api_positions()` ahora mergea posiciones de ambos perfiles via `_profile_from_file()`. `api_close_position()` busca y elimina del perfil correcto. `api_daily_brief()` suma posiciones de ambos perfiles. `api_stats()` suma balance y mergea trade_logs de ambos. |

### B-07 — División por cero en equity chart del overview

| Campo | Detalle |
|-------|---------|
| **Archivo** | `templates/overview.html` — función `loadEquity()` |
| **Severidad** | P1 — Crash visual |
| **Descripción** | `((last-first)/first*100).toFixed(2)` produce `Infinity` si `first` (balance inicial) es 0. |
| **Causa** | Sin guard clause para `first === 0`. |
| **Impacto** | Equity chart muestra NaN/Infinity, rompe tooltips y escalas. Ocurre si se resetea broker a $0 desde sandbox. |
| **Estado** | Resuelto |
| **Fix** | `templates/overview.html:509,561` — ambas divisiones envueltas en ternaria `first!==0? ... : "0.00"`. |

---

## P2 — Importantes (9)

### B-08 — SL/TP defaults inconsistentes entre código y config

| Campo | Detalle |
|-------|---------|
| **Archivos** | `execution/paper_broker.py` vs `config.yaml` (profiles) |
| **Severidad** | P2 — Inconsistencia |
| **Descripción** | `PaperBroker.__init__` usa `stop_loss_pct=5.0, take_profit_pct=10.0`. Pero `config.yaml` declara `sl_default: 2.0, tp_default: 5.0` por perfil. El código usa stops 2.5x más anchos de lo configurado. |
| **Causa** | El PaperBroker no lee SL/TP de config.yaml; el orchestrator le pasa los valores correctos en `open_position()`, pero los defaults del constructor son distintos. |
| **Impacto** | Si alguna llamada a `open_position()` omite SL/TP, usa valores incorrectos. |
| **Estado** | Abierto |

### B-09 — correlation_threshold inconsistente

| Campo | Detalle |
|-------|---------|
| **Archivos** | `execution/entry_filters.py:15` vs `config.yaml` |
| **Severidad** | P2 — Inconsistencia |
| **Descripción** | `entry_filters.py` hardcodea `CORRELATION_THRESHOLD = 0.80`. `config.yaml` tiene `risk.correlation_threshold: 0.85`. El código usa 0.80, la config dice 0.85. |
| **Causa** | Umbral duplicado sin single source of truth. |
| **Impacto** | Filtro de correlación más permisivo de lo declarado en configuración. |
| **Estado** | Abierto |

### B-10 — Fusion confidence excede 100 sin clamp

| Campo | Detalle |
|-------|---------|
| **Archivo** | `engine/fusion.py:55` |
| **Severidad** | P2 — Datos incorrectos |
| **Descripción** | `confidence = int(deviation * total_layers * 2)` puede producir valores >100 (ej: 10 capas con weighted_score=95 → confidence=900). Sin clamp a [0,100]. |
| **Causa** | Sin `max(0, min(100, confidence))` en el return. |
| **Impacto** | El prompt de DeepSeek recibe confidence >100 cuando el contrato dice "0-100". Puede confundir al LLM. |
| **Estado** | Resuelto |
| **Fix** | `engine/fusion.py:56` — agregado `confidence = max(0, min(100, confidence))` antes del return. |

### B-11 — Prompt de DeepSeek nunca recibe open_positions reales

| Campo | Detalle |
|-------|---------|
| **Archivo** | `orchestrator.py:203` → `engine/decider.py:88` |
| **Severidad** | P2 — Contexto incompleto |
| **Descripción** | `active_positions = market_data.get("open_positions", [])` nunca encuentra datos porque el orchestrator no incluye `open_positions` en `market_data`. |
| **Causa** | `_analyze_*` no recolecta posiciones abiertas del broker. |
| **Impacto** | DeepSeek decide SIN saber qué posiciones ya están abiertas. Puede abrir posiciones redundantes o contradictorias. |
| **Estado** | Resuelto |
| **Fix** | `orchestrator.py:203` — `decide()` ahora recibe `{**market_data, "open_positions": pb.get_positions()}`. El prompt muestra las posiciones reales de cada perfil. |

### B-12 — Clase Backtester importada pero nunca usada

| Campo | Detalle |
|-------|---------|
| **Archivos** | `orchestrator.py:36,107` + `learning/backtest.py` |
| **Severidad** | P2 — Dead code |
| **Descripción** | `Backtester` se importa e instancia en `init_components`, pero `run_backtest()` delega en `run_replay()`. La clase Backtester completa es código muerto en producción. |
| **Causa** | Backtest legacy (RSI+EMA) reemplazado por pipeline completo, pero no se eliminó. |
| **Impacto** | Confusión de mantenimiento. Dos motores de backtest coexisten. |
| **Estado** | Resuelto |
| **Fix** | `orchestrator.py:36,107` — removido `from learning.backtest import Backtester` y `self.backtester = Backtester()`. `run_backtest()` usa `self.run_replay()`. Clase `Backtester` se conserva en `learning/backtest.py` para tests. |

### B-13 — Señal fused recalculada por cada ticker dentro del mismo mercado

| Campo | Detalle |
|-------|---------|
| **Archivo** | `orchestrator.py:174` |
| **Severidad** | P2 — Rendimiento |
| **Descripción** | `fused = self.fusion.fuse(layer_results, market)` se ejecuta dentro del loop `for ticker in target_tickers`. La fusión solo depende de `layer_results` y `market`, constantes dentro del loop. Para 7 tickers de stocks, se recalcula 7 veces idéntico. |
| **Causa** | `fused` debería calcularse una vez antes del loop de tickers. |
| **Impacto** | 7x llamadas innecesarias a `FusionEngine.fuse()` por iteración del mercado stocks. |
| **Estado** | Abierto |

### B-14 — Formatos de error inconsistentes entre endpoints

| Campo | Detalle |
|-------|---------|
| **Archivo** | `dashboard.py` — múltiples endpoints |
| **Severidad** | P2 — API inconsistente |
| **Descripción** | Cuatro formatos distintos: `{"error": str}`, `{"ok": false, "error": str}`, `[]` silencioso, `False` silencioso. El helper `api()` del frontend traga todo y retorna `{}`. |
| **Impacto** | Frontend no puede distinguir "sin datos" de "error 500". Fallas silenciosas. |
| **Estado** | Abierto |

### B-15 — api() helper traga todos los errores HTTP

| Campo | Detalle |
|-------|---------|
| **Archivo** | `templates/base.html` — función `api()` |
| **Severidad** | P2 — UX |
| **Descripción** | `catch { return {} }` hace que cualquier error de red, 500, o 404 se trate como "sin datos". El usuario ve spinners eternos o estados vacíos. |
| **Impacto** | Fallas del backend invisibles para el usuario y el desarrollador. |
| **Estado** | Abierto |

### B-16 — os._exit(0) en tray_app bypassa cleanup de Python

| Campo | Detalle |
|-------|---------|
| **Archivo** | `tray_app.py` — `do_exit()` |
| **Severidad** | P2 — Integridad de datos |
| **Descripción** | `os._exit(0)` mata el proceso sin ejecutar `atexit`, `__del__`, o `finally`. Archivos sin flush, DB sin cerrar correctamente. |
| **Causa** | Debería usar `sys.exit(0)` después de detener servicios limpiamente. |
| **Impacto** | Posible corrupción de SQLite WAL o pérdida de últimas escrituras al salir. |
| **Estado** | Abierto |

---

## P3 — Mejoras (18)

| ID | Archivo | Descripción | Estado |
|----|---------|-------------|--------|
| B-17 | `analyzers/technical.py:3` | `from scipy import stats` — import muerto | Resuelto |
| B-18 | `engine/fusion.py:1` | `import numpy as np` — import muerto | Resuelto |
| B-19 | `learning/backtest.py` | 6 imports muertos + `self.results` + 2 parámetros | Resuelto |
| B-20 | `learning/strategy_evolver.py` | `json`, `Optional` + 2 parámetros muertos | Resuelto |
| B-21 | `learning/journal.py` | `datetime`, `timezone` — imports muertos | Resuelto |
| B-22 | `alerts/notifier.py` | `datetime`, `timezone`, `Optional` — imports muertos | Resuelto |
| B-23 | `analyzers/adx_regime.py`, `ict_smc.py` | `_silent_import()` duplicado → extraer a `_utils.py` | Abierto |
| B-24 | `analyzers/adx_regime.py`, `ict_smc.py`, `technical.py` | `_ensure_cols()` duplicado → extraer a `_base.py` | Abierto |
| B-25 | 9 analyzers | `_empty_result()` duplicado → clase base `BaseAnalyzer` | Abierto |
| B-26 | `analyzers/__init__.py` | `ADXRegimeAnalyzer` no está en `__all__` | Resuelto |
| B-27 | `tests/test_bot_actions.py:363,372` | Tests escriben a `data/cache/` en vez de `tmp_path` | Abierto |
| B-28 | `analyzers/adx_regime.py` + `ict_smc.py` | 0 tests para analyzers en pipeline activo | Abierto |
| B-29 | `orchestrator.py`, `dashboard.py`, `alerts/` | 0 tests de integración | Abierto |
| B-30 | `.gitignore` | Faltan `*.bak` y `*.log` (dashboard.log, tray.log) | Resuelto |
| B-31 | `config.yaml` | Sección `global` duplicada de `orchestrator` (dead config) | Resuelto |
| B-32 | `config.yaml` | `min_confidence: ''` (string vacío) en 3 mercados | Resuelto |
| B-33 | `config.yaml` | `enabled: 1` en layers (debería ser `true`) | Resuelto |
| B-34 | `tray_app.py` | `wmic` deprecado en Windows 10+, usar `Get-CimInstance` | Resuelto |

---

## Resumen

| Métrica | Valor |
|---------|-------|
| Total bugs | 34 |
| P1 — Críticos | 7 (7 resueltos) |
| P2 — Importantes | 9 (3 resueltos) |
| P3 — Mejoras | 18 (12 resueltos) |
| Abiertos | 12 |
| En progreso | 0 |
| Cerrados | 22 |

---

## Historial de cambios

| Fecha | Cambio |
|------|--------|
| 2026-05-29 | Creación inicial con 34 bugs detectados en `/debug all` |
| 2026-05-29 | Resueltos P3: B-26 (__all__), B-30 (.gitignore), B-31 (global dead), B-32 (string vacío), B-33 (enabled int), B-34 (wmic) |
| 2026-05-29 | Resuelto B-12 (Backtester dead code) |
