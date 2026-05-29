# Changelog — MarketAI / servermktai

## v1.2.1 — 2026-05-29
- Fix: B-01 — trades cerrados ahora persisten en DB (close_trade recibía id=0)
- Fix: B-02 — VIX > 30 ya no es código muerto en macro analyzer
- Fix: B-03 — executor tradicional usa notional USD en vez de qty=$100/share
- Fix: Guard para KeyError en real mode (Alpaca IDs en PaperBroker)
- Change: Adaptación de comandos a estándar OpenCode global
- Change: Bug tracker (doc/documentos/bugs.md) con 34 bugs, 22 resueltos

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
