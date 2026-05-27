# Roadmap de Mejoras de Trading — MarketAI

## Hoja de ruta detallada para implementar mejoras de efectividad y gestión de riesgo.

---

## Fase 1 — Protección de Ganancias (Sprint 1)

### 1A — ATR Trailing Stop

**Archivo:** `execution/paper_broker.py` → modificar `check_stops()`

**Objetivo:** Que el stop-loss se mueva hacia adelante a medida que el precio se mueve a favor, asegurando ganancias.

**Comportamiento:**
```
1. Position LONG opened at $100
2. Price moves to $105 (ATR = $2)
3. Trailing stop = 105 - (2 × 2.5) = 100 → SL at $100
4. Price moves to $110 → trailing stop = 110 - 5 = 105 → SL at $105
5. Price drops to $105 → STOP LOSS at $105 (gain of $5 secured)
```

**Código a agregar en `check_stops()`:**
```python
# After SL/TP checks, before time-exit:
for pid, pos in list(self.positions.items()):
    ticker = pos["ticker"]
    price = current_prices.get(ticker)
    if not price:
        continue
    atr = self._get_atr(pos)  # stored or recalculated
    if atr and atr > 0:
        if pos["signal"] == "LONG":
            new_sl = price - atr * 2.5
            pos["stop_loss_pct"] = max(new_sl / pos["entry_price"] - 1, pos["stop_loss_pct"])
        elif pos["signal"] == "SHORT":
            new_sl = price + atr * 2.5
            pos["stop_loss_pct"] = max(1 - new_sl / pos["entry_price"], pos["stop_loss_pct"])
```

**Tests:**
| Test | Escenario | Expected |
|---|---|---|
| trailing_atr_long_up | LONG position, price sube +2x ATR | SL se mueve arriba del entry |
| trailing_atr_long_stop | LONG price sube luego baja hasta trailing | Stop-loss se activa en trailing |
| trailing_atr_short_down | SHORT price baja (a favor) | SL se mueve abajo del entry |
| trailing_atr_no_move | Price no se mueve | SL no cambia |

---

### 1B — Break-even Stop

**Archivo:** `execution/paper_broker.py` → modificar `check_stops()`

**Objetivo:** Cuando el precio se mueve lo suficiente a favor, mover el SL al precio de entrada para garantizar que la operación no termine en pérdida.

**Comportamiento:**
```
1. Position LONG at $100, original SL at $95
2. Price reaches $102 (1.5x ATR away) → break-even trigger
3. SL moved from $95 to $100 (entry price)
4. If price drops back to $100 → STOP LOSS at $100 (0 loss)
```

**Código:**
```python
# In check_stops, before trailing stop:
for pid, pos in list(self.positions.items()):
    ticker = pos["ticker"]
    price = current_prices.get(ticker)
    if not price:
        continue
    entry = pos["entry_price"]
    be_trigger = self._get_be_trigger(pos)
    if be_trigger is None:
        continue  # break-even already applied or not available
    if pos["signal"] == "LONG":
        if (price - entry) / entry >= be_trigger:
            pos["stop_loss_pct"] = 0  # SL at 0% = entry price
            pos["_be_applied"] = True
    elif pos["signal"] == "SHORT":
        if (entry - price) / entry >= be_trigger:
            pos["stop_loss_pct"] = 0
            pos["_be_applied"] = True
```

**Tests:**
| Test | Escenario | Expected |
|---|---|---|
| be_long_triggered | LONG con precio +1.5x ATR | SL se mueve a entry |
| be_short_triggered | SHORT precio baja 1.5x ATR | SL se mueve a entry |
| be_not_triggered | Price no llega al trigger | SL original no cambia |
| be_price_reverts | LONG precio sube (BE), luego baja a entry | Stop loss se activa en entry |
| be_once_only | BE solo se aplica 1 vez | Flag `_be_applied` previene doble aplicación |

---

### 1C — Session Entry Filter

**Archivo:** `orchestrator.py` → nuevo método `_session_filter()`

**Objetivo:** Evitar operar en horarios de baja liquidez, mejorando la calidad de las señales.

**Reglas:**
- Forex: solo operar durante London (07:00-16:00 UTC) o NY (13:00-22:00 UTC) sessions
- Overlap London+NY (13:00-16:00 UTC) = mejor momento
- Stocks: solo operar durante horario de mercado (09:30-16:00 ET)
- Polymarket: sin filtro de sesión (24/7)

**Tests:**
| Test | Escenario | Expected |
|---|---|---|
| session_forex_london | Forex 10:00 UTC | ✅ Permitido |
| session_forex_ny | Forex 15:00 UTC | ✅ Permitido |
| session_forex_sydney | Forex 04:00 UTC (Sydney) | ❌ Bloqueado |
| session_forex_lunch | Forex 12:00 UTC (Tokyo lunch) | ❌ Bloqueado |
| session_stocks_market | Stocks 11:00 ET (market hours) | ✅ Permitido |
| session_stocks_pre | Stocks 08:00 ET (pre-market) | ❌ Bloqueado |
| session_polymarket_any | Polymarket cualquier hora | ✅ Permitido |

---

## Fase 2 — Calidad de Señal (Sprint 2)

### 2A — ADX Market Regime Analyzer

**Archivo:** `analyzers/adx_regime.py` (nuevo)

**Objetivo:** Detectar si el mercado está en tendencia (trending) o lateral (ranging) y ajustar la estrategia en consecuencia.

**Scoring:**
| ADX | Régimen | Señal recomendada |
|---|---|---|
| > 25 | Trending | Seguir tendencia (LONG/SHORT según dirección) |
| < 20 | Ranging | Mean reversion, esperar |
| 20-25 | Transición | WAIT — no operar |

**Output formato:**
```python
{"signal": "LONG/SHORT/WAIT", "score": 0-100, "reasoning": "ADX: 28, trending", "details": {"adx": 28, "regime": "trending", "trend_up": true}}
```

**Tests:**
| Test | Escenario | Expected |
|---|---|---|
| adx_trending_up | ADX=30, +DI > -DI | LONG score > 55 |
| adx_trending_down | ADX=35, -DI > +DI | SHORT score < 45 |
| adx_ranging | ADX=18 | WAIT score=50 |
| adx_transition | ADX=22 | WAIT score=50 |
| adx_strong_trend | ADX=45, +DI=35, -DI=12 | LONG score > 65 |

---

### 2B — Correlation Entry Filter

**Archivo:** `orchestrator.py` → nuevo método `_correlation_filter()`

**Objetivo:** Evitar tener múltiples posiciones en activos altamente correlacionados en la misma dirección.

**Comportamiento:**
```
- EUR/USD + GBP/USD correlation ≈ 0.85 ❌ No abrir ambas SHORT
- EUR/USD SHORT + USD/JPY LONG = USD play en ambas direcciones ❌ No
- AAPL + MSFT correlation ≈ 0.80 ⚠️ Reducir tamaño
- EUR/USD LONG + USD/JPY SHORT = USD play en ambas direcciones ❌ No
```

**Tests:**
| Test | Escenario | Expected |
|---|---|---|
| corr_forex_same_dir | EURUSD LONG + GBPUSD LONG | ❌ Bloqueado |
| corr_forex_diff_dir | EURUSD LONG + GBPUSD SHORT | ✅ Permitido |
| corr_stocks_same_sector | AAPL LONG + MSFT LONG | ⚠️ Reducido (no bloqueado) |
| corr_stocks_diff_sector | AAPL LONG + XOM LONG | ✅ Permitido |
| corr_forex_stocks | EURUSD LONG + SPY LONG | ✅ Permitido (mercados distintos) |

---

## Fase 3 — Escalado y Optimización (Sprint 3)

### 3A — Partial Take-Profit

**Archivo:** `execution/paper_broker.py` → modificar `check_stops()`

**Objetivo:** Cerrar parcialmente la posición en niveles de ganancia progresivos.

**Comportamiento:**
```
Normal profile:
  - TP1: 2% → cerrar 50% de la posición
  - TP2: 5% → cerrar 50% restante
  SL ajustado a break-even tras TP1

Fast profile:
  - TP1: 0.8% → cerrar 50%
  - TP2: 1.5% → cerrar 50%
```

**Tests:**
| Test | Escenario | Expected |
|---|---|---|
| partial_tp_tp1 | Precio alcanza TP1 | 50% se cierra, 50% queda abierto, SL a BE |
| partial_tp_tp2 | Precio alcanza TP2 | 50% restante se cierra |
| partial_tp_sl_after_tp1 | Precio llega a TP1, luego revierte a SL | Los 2 lotes se cierran: TP1 + SL |
| partial_tp_skip_if_small | Tamaño demasiado chico (< 10 USD) | No aplicar parcial, TP normal |
| partial_tp_fast_profile | Fast con TP1=0.8% y TP2=1.5% | Idem con otros porcentajes |

---

## Resumen de Archivos a Modificar

| Archivo | Fase | Líneas |
|---|---|---|
| `execution/paper_broker.py` | 1A, 1B, 3A | ~80 |
| `orchestrator.py` | 1C, 2B | ~50 |
| `analyzers/adx_regime.py` | 2A (NUEVO) | ~60 |
| `config.yaml` | 1C | ~8 |
| `tests/test_bot_actions.py` | Todas (NUEVO) | ~250 |

---

## Tests Forzados — Plan General

### `tests/test_bot_actions.py` (nuevo archivo)

Cubre todas las acciones posibles del bot usando datos sintéticos. Sin dependencia de APIs externas.

| Área de test | Tests | Mockea |
|---|---|---|
| **PaperBroker** | 15 tests | Datos sintéticos, precios mock |
| **Entry Filters** | 10 tests | Datetime, market_data mock |
| **Risk Engine** | 8 tests | Trade history, balance mock |
| **Exit Strategies** | 12 tests | Precios históricos mock |
| **Fusion + Decider** | 5 tests | Layer results sintéticos |
| **Circuit Breakers** | 6 tests | PnL, balance, drawdown mock |

**Total: ~56 tests nuevos.**
