# MarketAI — Roadmap de Desarrollo v1.3.0

Sistema de Trading Multi-Capa con DeepSeek AI.

---

## FASE 0: Fundación

**Objetivo: Estructura base funcionando**

| ID | Item | Prioridad | Estado | Depende de |
|----|------|-----------|--------|------------|
| R01 | Crear estructura de directorios | P1 | ✅ | — |
| R02 | Definir arquitectura de 5 capas | P1 | ✅ | — |
| R03 | Documentar plan y roadmap | P1 | ✅ | — |
| R04 | Instalar dependencias (pip install) | P1 | ✅ | R01 |
| R05 | Configurar .env con API keys | P1 | ✅ | R01 |
| R06 | Verificar acceso a datos (Polymarket, Yahoo Finance) | P1 | ✅ | R05 |

---

## FASE 1: Recolección de Datos

**Objetivo: Datos fluyendo correctamente**

| ID | Item | Prioridad | Estado | Depende de |
|----|------|-----------|--------|------------|
| R07 | collector_polymarket.py — CLOB API + DNS bypass | P1 | ✅ | R06 |
| R08 | collector_yfinance.py — Forex, Acciones, DXY, VIX | P1 | ✅ | R06 |
| R09 | collector_news.py — NewsAPI + RSS fallback | P2 | ✅ | R06 |
| R10 | database.py — SQLite WAL schema | P1 | ✅ | R01 |

**Hito 1:** `tests/test_collectors.py` pasa ✅

---

## FASE 2: Analizadores

**Objetivo: Señales de trading desde cada capa**

| ID | Item | Prioridad | Estado | Depende de |
|----|------|-----------|--------|------------|
| R11 | technical.py — RSI, MACD, Bollinger, EMAs | P1 | ✅ | R08 |
| R12 | onchain.py — Etherscan V2 (USDC flows) | P2 | ✅ | R08 |
| R13 | sentiment.py — Clasificación bullish/bearish | P2 | ✅ | R09 |
| R14 | orderbook.py — Bid/ask imbalance, depth | P2 | ✅ | R07 |
| R15 | fundamental.py — P/E, market cap, beta | P1 | ✅ | R08 |
| R16 | macro.py — DXY, VIX tracking | P2 | ✅ | R08 |
| R17 | cross_asset.py — SPY/QQQ divergencia | P2 | ✅ | R08 |
| R18 | adx_regime.py — Trend strength filter | P2 | ✅ | R08 |
| R19 | ict_smc.py — Order blocks, FVG, liquidity sweep | P2 | ✅ | R08 |

**Hito 2:** 9 analizadores en formato consistente ✅

---

## FASE 3: Motor de Decisión

**Objetivo: DeepSeek tomando decisiones informadas**

| ID | Item | Prioridad | Estado | Depende de |
|----|------|-----------|--------|------------|
| R20 | fusion.py — Pesos por capa/mercado, threshold 55/45 | P1 | ✅ | R11-R19 |
| R21 | decider.py — Dual prompts, JSON parsing, fallback WAIT | P1 | ✅ | R20 |

**Hito 3:** DeepSeek responde con señales coherentes ✅

---

## FASE 4: Ejecución

**Objetivo: Operaciones ejecutándose automáticamente**

| ID | Item | Prioridad | Estado | Depende de |
|----|------|-----------|--------|------------|
| R22 | paper_broker.py — Slippage, trailing, partial TP | P1 | ✅ | R21 |
| R23 | risk_engine.py — Kelly 25%, circuit breakers | P1 | ✅ | R21 |
| R24 | entry_filters.py — Session hours, correlation | P1 | ✅ | R21 |
| R25 | executor_polymarket.py — Stub (requiere keys Polygon) | P2 | ~ | R22 |
| R26 | executor_traditional.py — Alpaca/OANDA stub | P2 | ~ | R22 |

**Hito 4:** Paper trading funcional con dual profile ✅

---

## FASE 5: Auto-Aprendizaje

**Objetivo: Sistema que mejora solo con el uso**

| ID | Item | Prioridad | Estado | Depende de |
|----|------|-----------|--------|------------|
| R27 | journal.py — Post-mortem automático de cada trade | P2 | ✅ | R22 |
| R28 | strategy_evolver.py — Analiza trades, sugiere ajustes | P3 | ✅ | R27 |
| R29 | backtest.py — Walk-forward con Sharpe, profit factor | P2 | ✅ | R22 |

**Hito 5:** El sistema sugiere mejoras después de cada 10 trades ✅

---

## FASE 6: Alertas y Orquestación

**Objetivo: Sistema 24/7 completo**

| ID | Item | Prioridad | Estado | Depende de |
|----|------|-----------|--------|------------|
| R30 | notifier.py — Telegram + Discord webhook | P2 | ✅ | R09 |
| R31 | orchestrator.py — Loop dual profile, cron, time-exit | P1 | ✅ | R22-R30 |

**Hito 6:** Sistema corriendo 24/7 con alertas ✅

---

## FASE 7: Sistema Completo

**Objetivo: Dashboard, tray app, mejoras de calidad de vida**

| ID | Item | Prioridad | Estado | Depende de |
|----|------|-----------|--------|------------|
| R32 | Dashboard web — Flask + 9 páginas, 6 temas | P1 | ✅ | R31 |
| R33 | Tray app — VBS launcher, tooltip, auto-restart | P2 | ✅ | R31 |
| R34 | Backtest vía run_replay | P2 | ✅ | R29 |
| R35 | Dual profile — Normal + Fast simultáneos | P1 | ✅ | R31 |
| R36 | On-chain analyzer — Etherscan V2 scoring | P2 | ✅ | R12 |
| R37 | News RSS fallback — Yahoo Finance + Google News | P2 | ✅ | R09 |

---

## FASE 8: Producción

**Objetivo: Operación real controlada**

| ID | Item | Prioridad | Estado | Depende de |
|----|------|-----------|--------|------------|
| R38 | Paper trading 2-4 semanas (validación) | P1 | 🔄 | R31 |
| R80 | Informe repos trading — investigación de técnicas AI en GitHub | P2 | ✅ | — |
| R81 | Split orchestrator.py → orchestrator/ package (core/pipeline/replay) | P1 | ✅ | — |
| R82 | Crash recovery auto-reconciliación DB↔JSON al boot (B-N1/N2/N3) | P1 | ✅ | — |
| R83 | Refactor analyzers → BaseAnalyzer + _utils (B-23/24/25) | P2 | ✅ | — |
| R84 | request_id por iteración + orchestrator.err.log separado | P2 | ✅ | — |
| R39 | Micro-montos reales ($10-50 por operación) | P1 | ⏳ | R38 |
| R40 | Monitoreo diario con ajustes manuales | P1 | ⏳ | R39 |
| R41 | Estrategia madura → capital progresivo | P2 | ⏳ | R40 |
| R42 | Modo replay histórico para QA sin APIs live | P2 | ⏳ | R38 |
| R80 | Informe repos trading — investigación de técnicas AI en GitHub | P2 | ⏳ | — |
| R85 | Risk code-enforced: validate_trade gatekeeper estilo swarm-trader | P1 | ✅ | R23 |
| R86 | Time-exit configurable: minimal_roi table estilo Freqtrade | P1 | 🔴 Pendiente | R24 |
| R87 | Prevención posiciones contradictorias: single Portfolio Manager bottleneck | P1 | 🔴 Pendiente | R22 |
| R88 | Walk-forward validation con purging-and-embargo (ML4T pattern) | P2 | 🔴 Pendiente | R29 |

Referencias: [swarm-trader](https://github.com/zhound420/swarm-trader), [freqtrade](https://github.com/freqtrade/freqtrade), [ai-hedge-fund](https://github.com/virattt/ai-hedge-fund), [ML4T](https://github.com/stefan-jansen/machine-learning-for-trading)

---

## FASE 9: Mejoras Continuas

**Objetivo: Refinamiento basado en experiencia real**

| ID | Item | Prioridad | Estado | Depende de |
|----|------|-----------|--------|------------|
| R43 | ATR trailing stop | P1 | ✅ | R22 |
| R44 | Partial TP (50%) | P1 | ✅ | R22 |
| R45 | Break-even stop | P1 | ✅ | R22 |
| R46 | Time-exit por mercado + estado | P1 | ✅ | R24 |
| R47 | Correlation filter | P1 | ✅ | R24 |
| R48 | Session filter por perfil | P1 | ✅ | R24 |
| R49 | Kelly criterion fracción 25% | P1 | ✅ | R23 |
| R50 | Circuit breakers (daily loss 10%) | P1 | ✅ | R23 |
| R51 | Auto-restart loop (tray revive >30s) | P1 | ✅ | R33 |
| R52 | sessionStorage backtest persistence | P2 | ✅ | R34 |
| R53 | Timeout backtest 900s | P2 | ✅ | R34 |
| R54 | API status vía log time | P2 | ✅ | R31 |
| R55 | Endpoint /api/debug | P2 | ✅ | R32 |
| R56 | Página /sandbox | P2 | ✅ | R32 |
| R57 | Retención configurable de señales (prune) | P2 | ✅ | R31 |
| R58 | Tabla backtest_runs en DB | P2 | ✅ | R34 |
| R59 | POST /api/debug/inject-signal | P2 | ✅ | R32 |
| R60 | CHANGELOG.md en raíz | P1 | ✅ | — |
| R61 | POST /api/debug/reset-broker | P2 | ✅ | R32 |
| R62 | POST /api/debug/motors-clear | P2 | ✅ | R32 |

---

## Fase A: Expansión de tickers (ETFs + Index Funds)

**Objetivo: Agregar 8 ETFs de amplio mercado y 2 fondos indexados.**

| ID | Item | Prioridad | Estado | Depende de |
|----|------|-----------|--------|------------|
| R63 | 8 ETFs + 2 index funds en config.yaml | P1 | ✅ | R08 |
| R64 | Matriz de correlación expandida en entry_filters | P1 | ✅ | R24 |
| R65 | 98 tests pasan | P1 | ✅ | R63-R64 |
| R66 | Analizador fundamental con métricas ETF (Fase B) | P2 | ⏳ | R15 |

---

## Fase C: CEDEARs Argentina (BYMA)

**Objetivo: Soportar tickers .BA con conversión USD/ARS y horario BYMA.**

| ID | Item | Prioridad | Estado | Depende de |
|----|------|-----------|--------|------------|
| R67 | 7 CEDEARs .BA en config.yaml | P1 | ✅ | R08 |
| R68 | get_usd_ars_rate() en collector_yfinance | P1 | ✅ | R08 |
| R69 | Precios ARS → pseudo-USD en orchestrator | P1 | ✅ | R68 |
| R70 | BYMA session hours 12-19 UTC | P1 | ✅ | R24 |
| R71 | Correlación CEDEAR vs subyacente (0.98) | P1 | ✅ | R24 |
| R72 | _analyze_stocks() pasa 24 tickers completos | P1 | ✅ | R31 |

---

## Fase D: Diligencia — Salud estructural del proyecto

**Objetivo: Mantener integridad de la estructura Diligencia durante y después de adaptaciones.**

| ID | Item | Prioridad | Estado | Depende de |
|----|------|-----------|--------|------------|
| R73 | Verificar $variables en AGENTS.md | P1 | ✅ | — |
| R74 | Verificar comandos sin paths hardcodeados | P1 | ✅ | — |
| R75 | OPENCODE.md y metodología reflejen estructura real | P1 | ✅ | — |
| R76 | Ciclos de instancia ejecutables | P1 | ✅ | — |
| R77 | Sin directorios legacy con contenido residual | P1 | ✅ | — |
| R78 | DILIGENCIA.md coincida con estructura real | P1 | ✅ | — |
| R79 | Dependencias entre archivos de autoridad | P1 | ✅ | — |

---

## Métricas de Éxito

| ID | Indicador | Objetivo | Cómo medirlo |
|----|-----------|----------|--------------|
| M01 | Win rate | >55% | `python orchestrator.py --mode report` |
| M02 | Sharpe ratio | >1.0 | Backtest dashboard o `--mode backtest` |
| M03 | Profit factor | >1.5 | Ganancia bruta / pérdida bruta |
| M04 | Max drawdown | <15% | Peak-to-trough en dashboard |
| M05 | Señales por día | 2-5 | Trades ejecutados en paper broker |
| M06 | Tests | 98/98 | `python -m pytest tests/ -v` |

---

## Archivos relacionados

- `CHECKLIST.md` — Checklist de implementación
- `CHANGELOG.md` — Historial de versiones
- `AGENTS.md` — Variables de ruta y comandos
- `DILIGENCIA.md` — Sello de metodología
