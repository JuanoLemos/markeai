# Changelog — MarketAI / servermktai

## v1.3.0 — 2026-06-01
- New: Fase A — 8 ETFs (IVV, EEM, IWM, XLK, XLF, GLD, TLT, VTI) + 2 index funds (VFIAX, FXAIX) agregados
- New: Fase C — 7 CEDEARs .BA (KO, AAPL, MSFT, GOOGL, WMT, VIST, GGAL) con USD/ARS conversion
- New: BYMA session hours (12-19 UTC) para tickers .BA
- New: Matriz de correlación expandida con 10 ETFs + 7 CEDEARs + cross-refs
- New: get_usd_ars_rate() en collector_yfinance
- Fix: _analyze_stocks() ahora pasa todos los 24 tickers a get_stocks() para precios completos
- Fix: Kill Services cierra tray app completamente (stop_loop + _cleanup_old + do_exit)
- Fix: B-16 — os._exit(0) → sys.exit(0) en do_exit()
- Change: Diligencia v1.0→v1.4 — $INCIDENTS, doc/arch/incidentes.md, 21 comandos copiados
- Change: AGENTS.md actualizado con 33 comandos, tablas de rutas y comandos sincronizadas
- Change: 98/98 tests pasan, 35 bugs (23 resueltos, 12 activos)

## v1.2.1 — 2026-05-29
- Fix: B-01 — trades cerrados ahora persisten en DB (close_trade recibía id=0)
- Fix: B-02 — VIX > 30 ya no es código muerto en macro analyzer
- Fix: B-03 — executor tradicional usa notional USD en vez de qty=$100/share
- Fix: Guard para KeyError en real mode (Alpaca IDs en PaperBroker)
- Change: Adaptación de comandos a estándar OpenCode global
- Change: Bug tracker ($BUGS) con 34 bugs, 22 resueltos

## v1.2.0 — 2026-05-28
- New: Pagina /sandbox con controles manuales (inyectar senal, reset broker, limpiar motors)
- New: POST /api/debug/inject-signal — pruebas sinteticas en DB + broker
- New: POST /api/debug/reset-broker — reset perfil a $1000
- New: POST /api/debug/motors-clear — purga heartbeats
- Fix: StatusMarketAi renombrado, incluye Bot status
- Fix: Risk snapshot dual profile (Normal + Fast)
- Fix: DeepSeek health check cache (60s) + modelo desde config
- Docs: Checklist + roadmap + AGENTS.md sincronizados con features actuales

## v1.1.0 — 2026-05-28
- Fix: Risk snapshot ahora lee ambos profiles (Normal + Fast)
- Fix: DeepSeek health check con cache (60s) + modelo correcto desde config
- New: StatusMarketAi grid con Bot status en Overview
- New: Endpoint /api/debug para trazabilidad de fuentes de datos
- New: Tabla backtest_runs en DB para snapshots de config + resultados
- New: prune_signals() para retencion configurable (90d)
- New: CHANGELOG.md
- New: Heartbeats DB en orchestrator (loop, data, fusion, deepseek, execution)
- Change: Unificacion de roadmaps (roadmap + roadmap_mejoras)
- Change: Docs reorganizados en doc/ (documentos, guias, informes, skills)

## v1.0.0 — 2026-05-28
- Version inicial unificada
- Dual profiles (Normal + Fast)
- 9 analizadores, dashboard 9 paginas, 6 temas
- System tray con auto-restart
- ATR trailing, partial TP, break-even, time-exit
- 95 tests
