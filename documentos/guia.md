# MarketAI - Guía Completa del Sistema

## Sistema de Trading Multi-Capa con OpenCode + DeepSeek

---

## 1. Introducción

MarketAI es un sistema de trading automatizado de **5 capas** inspirado en la arquitectura de Hermes Agent. Utiliza **OpenCode con DeepSeek** como motor de razonamiento para analizar múltiples fuentes de datos en paralelo y ejecutar decisiones de trading informadas.

### Mercados Soportados
| Mercado | Fuente | Ejecución |
|---------|--------|-----------|
| **Polymarket** | CLOB API | Paper / Real (Polygon USDC) |
| **Forex** | Yahoo Finance + OANDA | Paper / Real (con keys) |
| **Acciones** | Yahoo Finance | Paper / Real (con keys) |

---

## 2. Arquitectura (5 Capas)

```
CAPA 1: RECOLECCIÓN
  ├── collector_polymarket.py → CLOB API
  ├── collector_yfinance.py → Forex + Acciones
  └── collector_news.py → Sentimiento

CAPA 2: ANÁLISIS PARALELO (OpenCode subagentes)
  ├── technical.py      → RSI, MACD, Bollinger, EMAs
  ├── onchain.py        → Actividad on-chain, whales
  ├── sentiment.py      → NLP de noticias
  ├── orderbook.py      → Desbalance bid/ask, spread
  ├── fundamental.py    → P/E, earnings, volumen
  ├── macro.py          → DXY, tasas, CPI
  └── cross_asset.py    → Correlaciones entre mercados

CAPA 3: MOTOR DE DECISIÓN
  ├── fusion.py         → Normaliza y pesa señales
  └── decider.py        → DeepSeek decide LONG/SHORT/WAIT

CAPA 4: EJECUCIÓN
  ├── paper_broker.py   → Simulación sin riesgo
  ├── executor_polymarket.py → Real Polymarket
  └── executor_traditional.py → Real Forex/Acciones

CAPA 5: AUTO-APRENDIZAJE
  ├── journal.py            → Registro post-trade
  ├── strategy_evolver.py   → Mejora continua de estrategias
  └── backtest.py           → Validación histórica
```

---

## 3. Flujo de Operación (Cada 15 min)

1. **Orquestador** despierta y lanza recolección paralela
2. **4 subagentes OpenCode** analizan en paralelo (técnico, on-chain/sentimiento, order book/fundamental, cross-asset)
3. **Fusion** normaliza scores (0-100) con pesos configurables
4. **DeepSeek** recibe prompt estructurado y decide:
   ```json
   { "signal": "LONG|SHORT|WAIT", "confidence": 0-100,
     "entry_price": float, "position_size_usd": float,
     "stop_loss_pct": float, "take_profit_pct": float }
   ```
5. **Ejecutor** (paper o real) coloca la orden
6. **Journal** registra trade en `trade_journal.md`
7. **Alerta** Telegram/Discord notifica resultado

---

## 4. Estrategias de Trading Incluidas

| Estrategia | Mercado | Descripción |
|------------|---------|-------------|
| Polymarket Order Book Imbalance | Polymarket | LONG cuando bid/ask > 2:1 en favor YES/NO |
| Macro Momentum | Forex | Operar alineado con DXY + tasa de interés |
| Earnings Momentum | Acciones | Post-earnings con gap + volumen confirmado |
| Sentiment Fade | Todos | Contrarian cuando sentimiento extremo (>85% o <15%) |
| Cross-Asset Arbitrage | Multi | Desviaciones estadísticas entre mercados correlacionados |

---

## 5. Gestión de Riesgos

- **Position sizing**: Máximo 5% del capital por operación
- **Stop-loss**: Obligatorio, configurable por mercado
- **Take-profit**: Escalonado (50% en TP1, 50% en TP2)
- **Daily loss limit**: Detiene operaciones del día al alcanzarlo
- **Correlation filter**: No abrir posiciones opuestas en mercados altamente correlacionados

---

## 6. Mapeo Hermes → OpenCode

| Hermes Agent | MarketAI (OpenCode + DeepSeek) |
|---|---|
| Multi-agent paralelo | `task` tool con 4 subagentes |
| Skills auto-generados | `write` → strategies/*.md |
| Memoria persistente SQLite | SQLite + database.py |
| Natural-language cron | schedule en Python + bash |
| Multi-platform alerts | python-telegram-bot |
| Model routing | DeepSeek solo para decisión; pandas para análisis |
| Watchdog | Monitoring de logs vía OpenCode |
| MCP serve | Analizadores con interfaz analyze() estándar |

---

## 7. Monitoreo y Alertas

- **Telegram**: Alertas de entrada, salida, stop-loss, take-profit
- **Discord**: Opcional, mismo canal
- **Dashboard local**: Archivos JSON en `data/cache/` legibles por OpenCode
- **Métricas registradas**: Sharpe ratio, win rate, profit factor, max drawdown
