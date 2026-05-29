# MarketAI - Roadmap de Desarrollo

## Hoja de Ruta: Sistema de Trading Multi-Capa

---

## FASE 0: Fundación
**Objetivo: Estructura base funcionando**

- [x] Crear estructura de directorios
- [x] Definir arquitectura de 5 capas
- [x] Documentar plan y roadmap
- [x] Instalar dependencias (`pip install -r requirements.txt`)
- [x] Configurar `.env` con API keys
- [x] Verificar acceso a datos (Polymarket, Yahoo Finance)

---

## FASE 1: Recolección de Datos
**Objetivo: Datos fluyendo correctamente**

| Código | Estado | Descripción |
|--------|--------|-------------|
| `collector_polymarket.py` | ✅ | Conexión CLOB API + DNS bypass, order book, tickers activos |
| `collector_yfinance.py` | ✅ | Forex, Acciones, DXY, VIX, fundamentos |
| `collector_news.py` | ✅ | NewsAPI + CryptoPanic + RSS fallback, rate limit 1/iter |
| `database.py` | ✅ | SQLite WAL: trades, signals, market_data, strategy_performance |

**Hito 1:** `tests/test_collectors.py` pasa ✅

---

## FASE 2: Analizadores
**Objetivo: Señales de trading desde cada capa**

| Código | Estado | Descripción |
|--------|--------|-------------|
| `technical.py` | ✅ | RSI, MACD, Bollinger, EMAs, S/R, ATR, volumen |
| `onchain.py` | ✅ | Etherscan V2 (USDC inflows/outflows, wallets únicos) |
| `sentiment.py` | ✅ | Clasificación bullish/bearish por keywords |
| `orderbook.py` | ✅ | Desbalance bid/ask, profundidad, spread |
| `fundamental.py` | ✅ | P/E, market cap, beta, dividend yield, earnings date |
| `macro.py` | ✅ | DXY, VIX tracking |
| `cross_asset.py` | ✅ | SPY/QQQ divergencia, USD strength patterns |
| `adx_regime.py` | ✅ | Trend strength filter (ADX > 25) |
| `ict_smc.py` | ✅ | Order blocks, FVG, liquidity sweep |

**Hito 2:** 9 analizadores en formato consistente ✅

---

## FASE 3: Motor de Decisión
**Objetivo: DeepSeek tomando decisiones informadas**

| Código | Estado | Descripción |
|--------|--------|-------------|
| `fusion.py` | ✅ | Pesos por capa/mercado, threshold 55/45, score=50 excluido |
| `decider.py` | ✅ | Dual prompts (Normal conservador, Fast agresivo), JSON parsing, fallback WAIT |

**Hito 3:** DeepSeek responde con señales coherentes ✅

---

## FASE 4: Ejecución
**Objetivo: Operaciones ejecutándose automáticamente**

| Código | Estado | Descripción |
|--------|--------|-------------|
| `paper_broker.py` | ✅ | Slippage 0.1%, comisiones, ATR trailing, partial TP, time-exit, break-even |
| `risk_engine.py` | ✅ | Fractional Kelly (25%), circuit breakers, position sizing ATR |
| `entry_filters.py` | ✅ | Session hours (Normal 18h, Fast 22h), correlation filter |
| `executor_polymarket.py` | ~ | Stub listo (requiere keys wallet Polygon) |
| `executor_traditional.py` | ~ | API Alpaca/OANDA implementadas (requiere keys reales) |

**Hito 4:** Paper trading funcional con dual profile ✅

---

## FASE 5: Auto-Aprendizaje
**Objetivo: Sistema que mejora solo con el uso**

| Código | Estado | Descripción |
|--------|--------|-------------|
| `journal.py` | ✅ | Post-mortem automático de cada trade |
| `strategy_evolver.py` | ✅ | Analiza trades, sugiere ajustes |
| `backtest.py` | ✅ | Walk-forward con Sharpe, profit factor, max drawdown |

**Hito 5:** El sistema sugiere mejoras después de cada 10 trades ✅

---

## FASE 6: Alertas y Orquestación
**Objetivo: Sistema 24/7 completo**

| Código | Estado | Descripción |
|--------|--------|-------------|
| `notifier.py` | ✅ | Telegram + Discord webhook |
| `orchestrator.py` | ✅ | Loop con dual profile, 9 analizadores, cron, time-exit |

**Hito 6:** Sistema corriendo 24/7 con alertas ✅

---

## FASE 7: Sistema Completo
**Objetivo: Dashboard, tray app, mejoras de calidad de vida**

| Componente | Estado | Descripción |
|------------|--------|-------------|
| Dashboard web | ✅ | Flask + 9 páginas, 6 temas visuales, equity curve, Daily Brief |
| Tray app | ✅ | VBS launcher, dual PnL tooltip, auto-restart loop, pulse dot |
| Backtest vía run_replay | ✅ | Full pipeline en vez de RSI/EMA legacy |
| Dual profile | ✅ | Normal + Fast simultáneos con SL/TP/confianza independientes |
| On-chain analyzer | ✅ | Etherscan V2, scoring real |
| News RSS fallback | ✅ | Yahoo Finance RSS + Google News RSS cuando NewsAPI falla |

---

## FASE 8: Producción
**Objetivo: Operación real controlada**

| Paso | Estado | Descripción |
|------|--------|-------------|
| 8.1 | En progreso | Paper trading 2-4 semanas (validación) |
| 8.2 | Pendiente | Micro-montos reales ($10-50 por operación) |
| 8.3 | Pendiente | Monitoreo diario con ajustes manuales |
| 8.4 | Pendiente | Estrategia madura → capital progresivamente mayor |
| 8.5 | Pendiente | Modo replay histórico para QA sin APIs live |

---

## FASE 9: Mejoras Continuas
**Objetivo: Refinamiento basado en experiencia real**

| Mejora | Estado | Descripción |
|--------|--------|-------------|
| ATR trailing stop | ✅ | Stop dinámico que sigue tendencia |
| Partial TP (50%) | ✅ | TP1 cierra mitad, resto sigue con SL a BE |
| Break-even stop | ✅ | SL sube a precio entrada al alcanzar TP1 |
| Time-exit | ✅ | Cierre por tiempo según mercado + estado |
| Correlation filter | ✅ | Evita posiciones correlacionadas |
| Session filter | ✅ | Horas de mercado activo por perfil |
| Kelly criterion | ✅ | Fracción 25% para position sizing |
| Circuit breakers | ✅ | Daily loss 10%, max drawdown |
| Auto-restart loop | ✅ | Tray revive loop si muerto >30s |
| sessionStorage backtest | ✅ | Persiste estado al cambiar pestañas |
| Timeout backtest 900s | ✅ | 15 min para pipeline completo |
| API status vía log time | ✅ | Verifica loop con mtime <60s |
| Endpoint /api/debug | ✅ | Traza fuentes de datos para depuracion |
| Pagina /sandbox | ✅ | Controles manuales de broker + debug |
| Retencion configurable de senales | ✅ | prune_signals() con purga >90d |
| Tabla backtest_runs | ✅ | Snapshot de config + resultados |
| POST /api/debug/inject-signal | ✅ | Pruebas sinteticas en vivo |
| CHANGELOG.md | ✅ | Historial de versiones en doc/ |
| POST /api/debug/reset-broker | ✅ | Resetear perfil a $1000 |
| POST /api/debug/motors-clear | ✅ | Limpiar heartbeats |

---

## Métricas de Éxito

| Indicador | Objetivo | Cómo medirlo |
|-----------|----------|--------------|
| Win rate | >55% | `python orchestrator.py --mode report` |
| Sharpe ratio | >1.0 | Backtest dashboard o `--mode backtest` |
| Profit factor | >1.5 | Ganancia bruta / pérdida bruta |
| Max drawdown | <15% | Peak-to-trough máximo en dashboard |
| Señales por día | 2-5 | Trades ejecutados en paper broker |
| Tests | 95/95 | `python -m pytest tests/ -v` |

---

## Apéndice — Especificaciones de Mejoras Implementadas

Este apéndice documenta las especificaciones técnicas detalladas de cada mejora de Fase 9, para referencia durante mantenimiento futuro.

### ATR Trailing Stop

**Archivo:** `execution/paper_broker.py` → `check_stops()`

Comportamiento:
```
1. Position LONG opened at $100
2. Price moves to $105 (ATR = $2)
3. Trailing stop = 105 - (2 x 2.5) = 100 → SL at $100
4. Price moves to $110 → trailing stop = 110 - 5 = 105 → SL at $105
5. Price drops to $105 → STOP LOSS at $105 (gain of $5 secured)
```

### Break-even Stop

**Archivo:** `execution/paper_broker.py` → `check_stops()`

Comportamiento:
```
1. Position LONG at $100, original SL at $95
2. Price reaches $102 (1.5x ATR away) → break-even trigger
3. SL moved from $95 to $100 (entry price)
4. If price drops back to $100 → STOP LOSS at $100 (0 loss)
```

### Session Entry Filter

**Archivo:** `execution/entry_filters.py`

Reglas:
- Normal profile: 18h/día (sesiones principales London + NY)
- Fast profile: 22h/día (incluye overlap extendido)
- Polymarket: sin filtro de sesión (24/7)

### ADX Market Regime Analyzer

**Archivo:** `analyzers/adx_regime.py`

| ADX | Régimen | Señal |
|---|---|---|
| > 25 | Trending | Seguir tendencia (LONG/SHORT según dirección) |
| < 20 | Ranging | Mean reversion, esperar |
| 20-25 | Transición | WAIT — no operar |

### Correlation Entry Filter

**Archivo:** `execution/entry_filters.py`

Reglas:
- EUR/USD + GBP/USD correlation ≈ 0.85 → no abrir ambas SHORT
- EUR/USD SHORT + USD/JPY LONG = USD play en ambas → no permitido
- Mismo mercado + misma dirección → bloqueado
- Mercados distintos → siempre permitido

### Partial Take-Profit

**Archivo:** `execution/paper_broker.py` → `check_stops()`

| Perfil | TP1 | TP2 |
|---|---|---|
| Normal | 2% → cerrar 50% | 5% → cerrar 50% restante |
| Fast | 0.8% → cerrar 50% | 1.5% → cerrar 50% restante |

SL ajustado a break-even tras TP1. Si el tamaño de posición es < $10, no aplicar partial TP.
