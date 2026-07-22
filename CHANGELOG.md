# Changelog — MarketAI / servermktai

Todos los cambios notables en este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.3] — 2026-07-21

### Fixed
- Anti-duplicate orchestrator: lockfile + orphan scan periódico previene procesos duplicados
- PnL filter `ABS(pnl_usd) < 1000` elimina trades ficticios sin filtro de fecha
- Excluir `lost_recovery` del realized PnL (eliminaba otro ficticio)
- Grace period 90s en `auto_recover` + `/api/ping` lee `motor_heartbeat` (G3+G5)
- Indentación línea 58 en `config.yaml` (technical: faltaba 1 espacio)
- `kill_port_8050()` en `restart_all_clean`: mata dashboard viejo antes de restart
- VAIO-NOTE.md duplicado eliminado, consolidado a SERVER-NOTE.md

### Changed
- Diligencia v2.7.1 → v3.0.0: `doc/vaio/` + worker autónomo 24/7, VS Code Tunnels + Cloudflare Tunnel, GUIA_CONTROL_REMOTO.md, AGENTS.md +Asistente VAIO-Server
- Deprecate Mavis branding: MAVIS-NOTE → SERVER-NOTE, limpieza de referencias
- KeepAlive Task Scheduler fix: ventana invisible + pull latest code
- VAIO-NOTE.md con instrucciones de admin del server
- MAVIS-NOTE actualizado con nueva IP y recovery instructions
- RUNBOOK.md + `_version()` error logging (Mavis recommendations 4+5)
- Post-recovery follow-up: documentado crash del server a las 01:13

## [1.5.2] — 2026-07-18

### Added
- `scripts/keep_alive.ps1` — external watchdog que verifica el server cada 5 min via Task Scheduler
- `doc/server/INCIDENTS_2026-07-18.md` — reporte de Mavis sobre crash de 5 días (Issue A-D)

### Fixed
- Server ahora se auto-recupera aunque el tray crashee (keep_alive lo revive cada 5 min)

### Changed
- `MAVIS-NOTE.md` actualizado con instrucciones de recovery y setup de Task Scheduler

## [1.5.1] — 2026-07-19

### Added
- PromptMemory: inyección de lecciones de trades pasados en el prompt de DeepSeek (Técnicas 1+2+3: memoria, reglas SHARP, críticas Moira)
- `engine/prompt_memory.py` — clase `PromptMemory` con `record_lesson()` y `get_lessons()`
- Tabla `prompt_memory` en SQLite para persistencia de lecciones

### Changed
- `decider.py`: `_build_prompt()` recibe `prompt_memory` opcional e inyecta hasta 3 lecciones por ticker
- `pipeline.py`: hook post-close de trades → graba lección automáticamente
- `core.py`: inicializa `PromptMemory` al boot

## [1.5.0] — 2026-07-18

### Added
- Meta-model training system: `scripts/train_historical.py` + `scripts/train_weekly.py` (RandomForest classifier basado en scores de analizadores históricos)
- `analyzers/meta_model.py` — 10° capa de análisis que aprende de datos históricos
- Ghost system: versionado de modelos + shadow trading en paralelo (`/api/ghost/compare`)
- `tray_watchdog.bat` — wrapper que revive el tray automáticamente si crashea
- `doc/olas/marketai-ola-06.md` — Wave manifest para Producción + IA 2.0

### Fixed
- `tray_app.py`: `do_close()` ahora llama a `kill_port_8050()` — mata procesos fantasma antes de cerrar
- `tray_app.py`: `main()` corre `kill_port_8050()` antes de arrancar servicios — elimina Issue 6 (procesos duplicados)

### Changed
- `DILIGENCIA.md`: v2.6.4 → v2.7.1 (33 comandos fundamentales, sistema /ola)
- `ROADMAP.md` reorganizado en Olas 0-5 con dependencias y entregables
- Sesión completa de ~18 horas: 11 fixes aplicados (prompt v3, risk gates, security auth, deploy remoto, drawdown detection, PnL ficticio, Normal profile, refresh button, tray merge, fusion pre-filter, ghost system)

## [1.4.0] — 2026-07-15

### Added
- Diligencia v2.6.4 → v2.7.1: sync metodología (33 comandos, sistema /ola)

### Added
- `POST /api/deploy`: deploy remoto — git pull + restart orchestrator desde el navegador
- Same-ticker check en R2 gate (correlation.py): bloquea duplicados como SPY+SPY
- `pnl_from_db` en `/api/debug`: PnL real desde la DB para comparar con balance del state file

### Changed
- `ROADMAP.md` reorganizado en 6 olas (Ola 0-5) con dependencias y entregables
- `doc/olas/` creado con 7 archivos: template + cada ola con scope, agentes, estado
- Prompt v3 (`decider.py`): WAIT como fallback, no default. Pre-mortem modulador, no bloqueador. Convergencia: 1 capa ≥60 o 2 capas ≥50.
- Config: Normal `min_confluence` 2→1, stocks `min_confidence` 30→25, forex 45→30
- Sidebar desktop simplificado: de 10 a 6 links alineados con bottom nav mobile
- Strategy lifespan: tray_app rewrite completo (Mavis)

### Fixed
- `strategy_used` en pipeline.py: ahora usa `decision['signal']` en vez de `fused['signal']`
- R2 gate `max_position_size` 8%→12%, effective_n 4→2 (Mavis)
- Normal `forex.min_confidence` 45→30
- Dashboard `_summarize_state`: usa `initial_balance` real del state file, no hardcoded 1000
- Tray_app test actualizado tras rewrite de Mavis

### Fixed
- Diligencia v2.7.0 → v2.6.3: corregido tag falso de MiniMax, alineado con metodología oficial
- `execution/entry_filters.py`: eliminado `correlation_check` obsoleto (reemplazado por R2 gate)
- `tests/test_ola1_p2_fixes.py`: removidos tests B-09 (cubiertos por test_risk_gates.py)
- `tests/test_bot_actions.py`: removidos tests de correlation_check legacy

### Added
- Diligencia v2.6.3 → v2.7.0: sync estructural (sistema de olas disponible via /ola)
- 5 risk gates R1-R5 pre-trade (cascade R4→R5→R1→R2→R3 en `orchestrator/pipeline.py`)
  - R1 sector cap, R2 correlación, R3 effective-N, R4 max open, R5 max size
  - Tabla `gate_rejections` (pendiente R87) — por ahora parsea `orchestrator.log`
- Prompt v2 DeepSeek (`engine/decider.py`): WAIT es el default, pre-mortem antes de sellar, 4 ejemplos few-shot (LONG/SHORT/WAIT-contradicción/WAIT-pre-mortem), reasoning estructurado `signal(conf) | capas: X+Y | riesgo: Z`, awareness del pipeline R1-R5, formato de salida conciso
- Dashboard mobile-first (wireframe v2 aplicado):
  - `static/style.css` reescrito con paleta warm dark (sage/terracotta/mustard), Outfit + JetBrains Mono
  - `templates/base.html`: app-header sticky mobile + bottom nav 5 tabs (Inicio/Posiciones/Gates/Historial/Ajustes) + sidebar desktop (>960px)
  - `templates/overview.html`: 4 cards (HOY, Posición destacada, Gates mini, Equity total) con sparklines
  - `templates/gates.html`: feed de rechazos por gate
- Endpoint `GET /api/overview/pnl`: 3 números honestos (hoy, realizado, no_realizado) + desde + balance + equity
- Endpoint `GET /api/gates/recent`: chips R1-R5 + rechazos 24h (parsea `orchestrator.log`)
- `tests/test_overview_pnl.py`: 16 tests para `/api/overview/pnl` (mark-to-market, no-invención, regresión anti-PnL ficticio Issue 7)
- `doc/arch/r80_trading_ai_repos.md` — R80 cierre: 6 repos top trading AI analizados
- `INDEX.md` (raíz) — índice de docs críticos (creado en este sync)

### Changed
- `ROADMAP.md`: +R80 cerrado, R85-R88 siguen 🔴 pendientes
- `DILIGENCIA.md`: v2.6.3 → v2.7.0
- `README.md`: tests 143 → 159, nota del rediseño mobile-first
- `AGENTS.md`: $NEWS_FILE removido (huérfana, no existe `news.txt`)
- `doc/arch/palomas.md` — creado (placeholder, faltaba en estructura)

### Deprecated
### Removed
- $NEWS_FILE de `AGENTS.md` (variable sin archivo target)

### Fixed
- P&L ficticio (Issue 7) — `/api/overview/pnl` lee SOLO de la DB y paper broker state, cero cálculos inventados

### Security

## [1.4.0] — 2026-07-10

### Added — Ola 1: Estabilidad
- **B-N1**: Crash recovery. `MarketAIOrchestrator._reconcile_db_with_brokers()` cierra trades zombis al boot
- **B-N2**: Auto-reconciliación DB↔JSON. Schema migration defensivo (ALTER TABLE para `position_id` en DBs viejas)
- **B-N3**: `check_stops_and_evolve()` ahora recolecta precios para AMBOS brokers (no solo el alias `paper_broker`)
- **B-08**: `PaperBroker` acepta `default_sl_pct` y `default_tp_pct` desde config del profile
- **B-09**: `correlation_check()` acepta `threshold` desde config (single source of truth)
- **B-13**: `fused` se calcula UNA vez por mercado (no por ticker) — 7x speedup en stocks
- **B-14**: `api_error(msg, code)` helper en `dashboard.py` para errores JSON consistentes
- **B-15**: `api()` JS en `base.html` distingue errores HTTP (`_error`, `_status`, `_message`)
- **B-16**: Verificado `sys.exit(0)` en `tray_app.do_exit()`
- **B-23/24/25**: Refactor analyzers → `BaseAnalyzer` (empty_result, ensure_cols) + `analyzers/_utils.py` (silent_import). 9 analyzers heredan de BaseAnalyzer
- **B-27**: `test_bot_actions.py:363,372` ahora usan `tmp_path` en vez de paths reales
- **B-28**: Tests para analyzers en pipeline activo
- **B-29**: Tests de integración del orchestrator
- **`orchestrator/` package**: split de `orchestrator.py` (35KB, 712 líneas) en 4 archivos: `core.py`, `pipeline.py`, `replay.py`, `__init__.py`. Entry point `orchestrator.py` (1.5KB) solo CLI
- **Logging**: `request_id` por iteración (formato `iter-YYYYMMDDHHMMSS-XXXXXX`), `orchestrator.err.log` separado para ERROR+
- **Tests**: 98 → 143 tests (+45)
- **`scripts/close_zombies.py`**: one-shot para cerrar trades zombis del crash del 01/06 (32 trades)
- **R80**: `doc/arch/r80_trading_ai_repos.md` — investigación de 6 repos top trading AI
- **`doc/guias/guia_arquitectura_ola1.md`**: guía de la nueva arquitectura
- **`doc/mecanicas/MECANICA-RECOVERY.md`**: mecánica de auto-reconciliación

### Changed
- `README.md`: tests 95 → 143, mención del split de orchestrator y BaseAnalyzer
- `orchestrator.py` (raíz) ahora es solo entry-point; la lógica vive en `orchestrator/`
- `orchestrator/{core,pipeline,replay}.py`: mejor organización, sin lógica duplicada

### Fixed
- B-13 (real): Fused recalculado por cada ticker dentro del mismo mercado (7x speedup)
- Drift DB↔JSON: 32 trades zombis del crash del 01/06 marcados como `lost_recovery`

### Deprecated
- `paper_broker_state.json` (legacy singular) — sistema usa `pb_normal.json` + `pb_fast.json`

### Removed
- 8 archivos `.bak_*` sueltos (trashados en Ola 0)
- Carpeta `.bak_2026-05-05/` (trashada en Ola 0)

## [1.3.0] — 2026-06-01

### Added
- Fase A — 8 ETFs (IVV, EEM, IWM, XLK, XLF, GLD, TLT, VTI) + 2 index funds (VFIAX, FXAIX)
- Fase C — 7 CEDEARs .BA (KO, AAPL, MSFT, GOOGL, WMT, VIST, GGAL) con USD/ARS conversion
- BYMA session hours (12-19 UTC) para tickers .BA
- Matriz de correlación expandida con 10 ETFs + 7 CEDEARs + cross-refs
- `get_usd_ars_rate()` en collector_yfinance

### Fixed
- `_analyze_stocks()` ahora pasa todos los 24 tickers a `get_stocks()` para precios completos
- Kill Services cierra tray app completamente (`stop_loop` + `_cleanup_old` + `do_exit`)
- B-16 — `os._exit(0)` → `sys.exit(0)` en `do_exit()`

### Changed
- Diligencia v1.0 → v1.4 — `$INCIDENTS`, `doc/arch/incidentes.md`, 21 comandos copiados
- AGENTS.md actualizado con 33 comandos, tablas de rutas y comandos sincronizadas
- 98/98 tests pasan, 35 bugs (23 resueltos, 12 activos)

## [1.2.1] — 2026-05-29

### Fixed
- B-01 — trades cerrados ahora persisten en DB (`close_trade` recibía id=0)
- B-02 — VIX > 30 ya no es código muerto en macro analyzer
- B-03 — executor tradicional usa notional USD en vez de qty=$100/share
- Guard para KeyError en real mode (Alpaca IDs en PaperBroker)

### Changed
- Adaptación de comandos a estándar OpenCode global
- Bug tracker ($BUGS) con 34 bugs, 22 resueltos

## [1.2.0] — 2026-05-28

### Added
- Página `/sandbox` con controles manuales (inyectar señal, reset broker, limpiar motors)
- POST `/api/debug/inject-signal` — pruebas sintéticas en DB + broker
- POST `/api/debug/reset-broker` — resetear perfil a $1000
- POST `/api/debug/motors-clear` — purga heartbeats

### Fixed
- StatusMarketAi renombrado, incluye Bot status
- Risk snapshot dual profile (Normal + Fast)
- DeepSeek health check cache (60s) + modelo desde config

### Changed
- Docs: Checklist + roadmap + AGENTS.md sincronizados con features actuales

## [1.1.0] — 2026-05-28

### Added
- StatusMarketAi grid con Bot status en Overview
- Endpoint `/api/debug` para trazabilidad de fuentes de datos
- Tabla `backtest_runs` en DB para snapshots de config + resultados
- `prune_signals()` para retención configurable (90d)
- CHANGELOG.md
- Heartbeats DB en orchestrator (loop, data, fusion, deepseek, execution)

### Fixed
- Risk snapshot ahora lee ambos profiles (Normal + Fast)
- DeepSeek health check con cache (60s) + modelo correcto desde config

### Changed
- Unificación de roadmaps (roadmap + roadmap_mejoras)
- Docs reorganizados en `doc/` (documentos, guías, informes, skills)

## [1.0.0] — 2026-05-28

### Added
- Versión inicial unificada
- Dual profiles (Normal + Fast)
- 9 analizadores, dashboard 9 páginas, 6 temas
- System tray con auto-restart
- ATR trailing, partial TP, break-even, time-exit
- 95 tests

<!--
[Unreleased]: https://github.com/JuanoLemos/markeai/compare/v1.5.2...HEAD
[1.5.2]: https://github.com/JuanoLemos/markeai/releases/tag/v1.5.2
[1.5.1]: https://github.com/JuanoLemos/markeai/releases/tag/v1.5.1
[1.4.0]: https://github.com/JuanoLemos/markeai/releases/tag/v1.4.0
[1.3.0]: https://github.com/JuanoLemos/markeai/releases/tag/v1.3.0
[1.2.1]: https://github.com/JuanoLemos/markeai/releases/tag/v1.2.1
[1.2.0]: https://github.com/JuanoLemos/markeai/releases/tag/v1.2.0
[1.1.0]: https://github.com/JuanoLemos/markeai/releases/tag/v1.1.0
[1.0.0]: https://github.com/JuanoLemos/markeai/releases/tag/v1.0.0
-->

## Archivos relacionados

- `ROADMAP.md` — Roadmap del proyecto
- `CHECKLIST.md` — Checklist de implementación
- `AGENTS.md` — Variables de ruta y comandos
- `DILIGENCIA.md` — Sello de metodología
