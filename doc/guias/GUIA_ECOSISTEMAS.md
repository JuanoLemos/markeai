# Guía de Ecosistemas — MarketAI

**Propósito:** Mapa de ecosistemas y fuentes de datos del sistema de trading.

---

## Ecosistemas

| Ecosistema | Fuente | Mercado | Estado |
|---|---|---|---|
| Acciones US | Yahoo Finance | stocks (SPY, QQQ, AAPL, MSFT, GOOGL, AMZN, TSLA) | ✅ |
| ETFs US | Yahoo Finance | stocks (IVV, EEM, IWM, XLK, XLF, GLD, TLT, VTI) | ✅ |
| Index Funds | Yahoo Finance | stocks (VFIAX, FXAIX) | ✅ |
| CEDEARs AR | Yahoo Finance .BA | stocks (KO, AAPL, MSFT, GOOGL, WMT, VIST, GGAL) | ✅ |
| Forex | Yahoo Finance | forex (EUR/USD, GBP/USD, USD/JPY) | ✅ |
| Crypto | Polymarket CLOB | polymarket | ✅ |
| News | NewsAPI + RSS | sentimiento | ✅ |
| On-Chain | Etherscan V2 | actividad USDC | ✅ |

## Reglas de Frontera

- CEDEARs dependen de tasa USD/ARS viva desde `USDARS=X`
- CEDEARs operan solo en BYMA hours (12-19 UTC)
- No abrir posición en subyacente US + CEDEAR simultáneamente (correlación 0.98)
