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
| `collector_news.py` | ✅ | NewsAPI + clasificación por keywords, caché |
| `database.py` | ✅ | SQLite: trades, signals, market_data, strategy_performance |

**Hito 1:** `tests/test_collectors.py` pasa ✅

---

## FASE 2: Analizadores
**Objetivo: Señales de trading desde cada capa**

| Código | Estado | Descripción |
|--------|--------|-------------|
| `technical.py` | ✅ | RSI, MACD, Bollinger, EMAs, S/R, ATR, volumen |
| `onchain.py` | ✅ | Polyscan API (USDC inflows/outflows, wallets únicos) + CLOB fallback |
| `sentiment.py` | ✅ | Clasificación bullish/bearish por keywords desde NewsAPI |
| `orderbook.py` | ✅ | Desbalance bid/ask, profundidad, spread |
| `fundamental.py` | ✅ | P/E, market cap, beta, dividend yield, earnings date |
| `macro.py` | ✅ | DXY, VIX tracking |
| `cross_asset.py` | ✅ | SPY/QQQ divergencia, USD strength patterns |

**Hito 2:** Cada analyzer devuelve formato consistente ✅

---

## FASE 3: Motor de Decisión
**Objetivo: DeepSeek tomando decisiones informadas**

| Código | Estado | Descripción |
|--------|--------|-------------|
| `fusion.py` | ✅ | Pesos configurables por capa y mercado, threshold 55/45 |
| `decider.py` | ✅ | Prompt engineering + JSON parsing + fallback WAIT |

**Hito 3:** DeepSeek responde con señales coherentes ✅

---

## FASE 4: Ejecución
**Objetivo: Operaciones ejecutándose automáticamente**

| Código | Estado | Descripción |
|--------|--------|-------------|
| `paper_broker.py` | ✅ | Slippage 0.1%, comisiones, SL/TP, balance persistente |
| `executor_polymarket.py` | ~ | Stub listo (requiere keys wallet Polygon) |
| `executor_traditional.py` | ~ | API Alpaca/OANDA implementadas (requiere keys reales) |

**Hito 4:** Paper trading funcional con journal automático ✅

---

## FASE 5: Auto-Aprendizaje
**Objetivo: Sistema que mejora solo con el uso**

| Código | Estado | Descripción |
|--------|--------|-------------|
| `journal.py` | ✅ | Post-mortem automático de cada trade a `trade_journal.md` |
| `strategy_evolver.py` | ✅ | Analiza trades, actualiza `master_strategy.md` |
| `backtest.py` | ✅ | Walk-forward con Sharpe, profit factor, max drawdown |

**Hito 5:** El sistema sugiere mejoras después de cada 10 trades ✅

---

## FASE 6: Alertas y Orquestación
**Objetivo: Sistema 24/7 completo**

| Código | Estado | Descripción |
|--------|--------|-------------|
| `notifier.py` | ✅ | Telegram + Discord webhook |
| `orchestrator.py` | ✅ | Loop principal con scheduling, stop file, errores manejados |

**Hito 6:** Sistema corriendo 24/7 con alertas ✅

---

## FASE 7: Sistema Completo
**Objetivo: Dashboard, tray app, cron, mejoras de calidad de vida**

| Componente | Estado | Descripción |
|------------|--------|-------------|
| Dashboard web | ✅ | Flask + 5 páginas, control start/stop loop, config editable |
| Discord notifier | ✅ | Webhook REST |
| On-chain analyzer | ✅ | Polyscan API v2, scoring real |
| Tray app | ✅ | Ventana minimizable a system tray con icono $ |
| Loop.bat / Dashboard.bat | ✅ | Lanzadores con venv automático |
| README.md | ✅ | Documentación principal |

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

## Métricas de Éxito

| Indicador | Objetivo | Cómo medirlo |
|-----------|----------|--------------|
| Win rate | >55% | `python orchestrator.py --mode report` |
| Sharpe ratio | >1.0 | Backtest `--mode backtest` |
| Profit factor | >1.5 | Ganancia bruta / pérdida bruta |
| Max drawdown | <15% | Peak-to-trough máximo |
| Señales por día | 2-5 | Trades ejecutados en paper broker |
| Tests | 46/46 | `python -m pytest tests/ -v` |
