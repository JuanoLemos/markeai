# Changelog — MarketAI / servermktai

Todos los cambios notables en este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Diligencia v1.18.1 → v2.6.3: comandos sincronizados (45 activos), $PALOMA_MAIN_PLAN en AGENTS.md, DILIGENCIA.md actualizado
- Search GitHub AI trading repos: investigación de técnicas IA trading (100+ repos analizados)
- R80: Informe repos trading — investigación de técnicas AI en GitHub (FASE 8)

### Changed
- ROADMAP.md: +R80 en FASE 8
### Deprecated
### Removed
### Fixed
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
[Unreleased]: https://github.com/usuario/MarketAI/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/usuario/MarketAI/releases/tag/v1.3.0
[1.2.1]: https://github.com/usuario/MarketAI/releases/tag/v1.2.1
[1.2.0]: https://github.com/usuario/MarketAI/releases/tag/v1.2.0
[1.1.0]: https://github.com/usuario/MarketAI/releases/tag/v1.1.0
[1.0.0]: https://github.com/usuario/MarketAI/releases/tag/v1.0.0
-->

## Archivos relacionados

- `ROADMAP.md` — Roadmap del proyecto
- `CHECKLIST.md` — Checklist de implementación
- `AGENTS.md` — Variables de ruta y comandos
- `DILIGENCIA.md` — Sello de metodología
