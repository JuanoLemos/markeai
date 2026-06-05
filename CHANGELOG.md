# Changelog — MarketAI / servermktai

Todos los cambios notables en este proyecto se documentarán en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
### Changed
### Deprecated
### Removed
### Fixed
### Security

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
