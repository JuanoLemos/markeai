# MarketAI - Roadmap de Desarrollo

## Hoja de Ruta: Sistema de Trading Multi-Capa

---

## FASE 0: Fundación (Semana 1)
**Objetivo: Estructura base funcionando**

- [x] Crear estructura de directorios
- [x] Definir arquitectura de 5 capas
- [x] Documentar plan y roadmap
- [ ] Instalar dependencias (`pip install -r requirements.txt`)
- [ ] Configurar `.env` con API keys
- [ ] Verificar acceso a datos (Polymarket, Yahoo Finance)

---

## FASE 1: Recolección de Datos (Semanas 1-2)
**Objetivo: Datos fluyendo correctamente**

| Código | Sprint | Descripción |
|--------|--------|-------------|
| `collector_polymarket.py` | 1 | Conexión CLOB API, order book YES/NO, tickers activos |
| `collector_yfinance.py` | 1 | Forex (EUR/USD, GBP/USD, USD/JPY) + Acciones (SPY, QQQ, stocks) |
| `collector_news.py` | 2 | CryptoPanic para crypto, NewsAPI para general, RSS feeds |
| `database.py` | 1 | SQLite: trades, signals, market_data, strategy_performance |
| `__init__.py` (cada módulo) | 1 | Paquetes Python para imports |

**Hito 1:** Los 3 colectores devuelven datos limpios → `tests/test_collectors.py` pasa

---

## FASE 2: Analizadores (Semanas 2-3)
**Objetivo: Señales de trading desde cada capa**

| Código | Sprint | Descripción |
|--------|--------|-------------|
| `technical.py` | 2 | RSI(14), MACD(12,26,9), Bollinger(20,2), EMA(9,21,50), soporte/resistencia |
| `onchain.py` | 2 | Polyscan, whale alerts, exchange flows |
| `sentiment.py` | 2 | NLP de titulares con DeepSeek, score bullish/bearish/neutral |
| `orderbook.py` | 3 | Desbalance bid/ask, profundidad 5 niveles, spread relativo |
| `fundamental.py` | 3 | P/E, market cap, earnings fecha, volumen relativo |
| `macro.py` | 3 | DXY, VIX, tasas de interés de referencia, CPI |
| `cross_asset.py` | 3 | Matriz de correlación rolling 30d, z-score de desviaciones |

**Hito 2:** Cada analyzer devuelve `{"signal": "...", "score": 0-100, "reasoning": "..."}` consistente

---

## FASE 3: Motor de Decisión (Semana 3)
**Objetivo: DeepSeek tomando decisiones informadas**

| Código | Sprint | Descripción |
|--------|--------|-------------|
| `fusion.py` | 3 | Normalización con pesos configurables por capa y mercado |
| `decider.py` | 3 | Prompt engineering para DeepSeek, parsing de respuesta JSON |
| Prompt templates | 3 | Variantes por mercado (Polymarket vs Forex vs Acciones) |

**Hito 3:** DeepSeek responde con señales coherentes en paper trading

---

## FASE 4: Ejecución (Semanas 3-4)
**Objetivo: Operaciones ejecutándose automáticamente**

| Código | Sprint | Descripción |
|--------|--------|-------------|
| `paper_broker.py` | 3 | Simulación total: slippage 0.1%, comisiones, fills parciales |
| `executor_polymarket.py` | 4 | Conexión wallet Polygon, approval USDC, place_order |
| `executor_traditional.py` | 4 | Estructura lista para Alpaca/OANDA (requiere keys) |

**Hito 4:** Paper trading funcional con journal automático

---

## FASE 5: Auto-Aprendizaje (Semana 4)
**Objetivo: Sistema que mejora solo con el uso**

| Código | Sprint | Descripción |
|--------|--------|-------------|
| `journal.py` | 4 | Post-mortem automático de cada trade |
| `strategy_evolver.py` | 5 | OpenCode lee journal → sugiere ajustes a master_strategy.md |
| `backtest.py` | 5 | Walk-forward sobre datos históricos con métricas Sharpe |

**Hito 5:** El sistema sugiere mejoras después de cada 10 trades

---

## FASE 6: Alertas y Orquestación (Semana 5)
**Objetivo: Sistema 24/7 completo**

| Código | Sprint | Descripción |
|--------|--------|-------------|
| `notifier.py` | 5 | Telegram + Discord embeds con resumen visual |
| `orchestrator.py` | 5 | Loop principal con scheduling y gestión de errores |
| Config refinamiento | 5 | Ajuste de pesos por capa basado en performance histórica |

**Hito 6:** Sistema corriendo 24/7 con alertas y auto-recuperación

---

## FASE 7: Producción (Semana 5+)
**Objetivo: Operación real controlada**

| Paso | Descripción |
|------|-------------|
| 7.1 | Paper trading 2-4 semanas (validación) |
| 7.2 | Micro-montos reales ($10-50 por operación) |
| 7.3 | Monitoreo diario con ajustes manuales |
| 7.4 | Estrategia madura → capital progresivamente mayor |
| 7.5 | Dashboard web para monitoreo en tiempo real |

---

## Hitos Clave

```
Semana 1: Fundamentos + Datos
     │
     ▼
Semana 2: Analizadores funcionando
     │
     ▼
Semana 3: DeepSeek decidiendo + Paper trading
     │
     ▼
Semana 4: Auto-aprendizaje activo
     │
     ▼
Semana 5: Sistema 24/7 completo
     │
     ▼
Semana 5+: Producción real micro-montos
```

---

## Métricas de Éxito

| Indicador | Objetivo | Cómo medirlo |
|-----------|----------|--------------|
| Win rate | >55% | Trades ganadores / total trades |
| Sharpe ratio | >1.0 | (Retorno - libre riesgo) / desviación estándar |
| Profit factor | >1.5 | Ganancia bruta / pérdida bruta |
| Max drawdown | <15% | Peak-to-trough máximo |
| Señales por día | 2-5 | Trades ejecutados |
| Latencia decisión | <30s | Desde recolección hasta orden |
