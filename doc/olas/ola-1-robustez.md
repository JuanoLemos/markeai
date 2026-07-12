# Ola 1: Robustez

**Estado:** ✅ Completada
**Depende de:** Ola 0
**Agentes:** @sdd-implement, @sdd-verify

---

## Scope

Refactor arquitectónico y mejoras de calidad del sistema. Incluye la reestructuración del orchestrator como package, la jerarquía BaseAnalyzer, crash recovery automático, y todas las mejoras de la antigua Fase 9 (ATR trailing, partial TP, break-even, time-exit, correlation filter, Kelly, circuit breakers, endpoints debug).

| ID | Item | Prioridad | Estado |
|----|------|-----------|--------|
| R43 | ATR trailing stop | P1 | ✅ |
| R44 | Partial TP (50%) | P1 | ✅ |
| R45 | Break-even stop | P1 | ✅ |
| R46 | Time-exit por mercado + estado | P1 | ✅ |
| R47 | Correlation filter | P1 | ✅ |
| R48 | Session filter por perfil | P1 | ✅ |
| R49 | Kelly criterion fracción 25% | P1 | ✅ |
| R50 | Circuit breakers (daily loss 10%) | P1 | ✅ |
| R51 | Auto-restart loop (tray revive >30s) | P1 | ✅ |
| R52 | sessionStorage backtest persistence | P2 | ✅ |
| R53 | Timeout backtest 900s | P2 | ✅ |
| R54 | API status vía log time | P2 | ✅ |
| R55 | Endpoint /api/debug | P2 | ✅ |
| R56 | Página /sandbox | P2 | ✅ |
| R57 | Retención configurable de señales (prune) | P2 | ✅ |
| R58 | Tabla backtest_runs en DB | P2 | ✅ |
| R59 | POST /api/debug/inject-signal | P2 | ✅ |
| R60 | CHANGELOG.md en raíz | P1 | ✅ |
| R61 | POST /api/debug/reset-broker | P2 | ✅ |
| R62 | POST /api/debug/motors-clear | P2 | ✅ |
| R81 | Split orchestrator.py → orchestrator/ package | P1 | ✅ |
| R82 | Crash recovery auto-reconciliación DB↔JSON | P1 | ✅ |
| R83 | Refactor analyzers → BaseAnalyzer + _utils | P2 | ✅ |
| R84 | request_id por iteración + orchestrator.err.log | P2 | ✅ |

## Entregables

- [x] 200 tests pasando
- [x] Todos los endpoints de debug y control
- [x] Sistema de recovery automático al boot
- [x] Package orchestrator/ con core, pipeline, replay

## Archivos relacionados

- `ROADMAP.md` — Roadmap del proyecto
- `doc/guias/guia_arquitectura_ola1.md` — Guía de arquitectura
