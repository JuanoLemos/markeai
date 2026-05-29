# Los 5 Motores de MarketAI

## Cómo funciona el sistema por dentro — explicado simple

---

MarketAI no es un solo programa. Son **5 motores independientes** que trabajan en cadena. Cada uno resuelve una parte del problema de trading automatizado.

El flujo completo:

```
MERCADO (precios, noticias, blockchain)
   ↓
1️⃣ ANÁLISIS → 9 analizadores miran el mercado
   ↓
2️⃣ FUSIÓN → combina las 9 opiniones en 1 señal
   ↓
3️⃣ DECISIÓN → DeepSeek IA decide si operar
   ↓
4️⃣ RIESGO → verifica límites de seguridad
   ↓
5️⃣ EJECUCIÓN → paper broker abre, monitorea, cierra
   ↓
JOURNAL (todo queda registrado)
```

Cada ~15 minutos, los 5 motores se activan para los 3 mercados (forex, stocks, polymarket). En cada ciclo analizan 13 tickers (5 pares forex + 7 acciones + 1 polymarket).

---

## 1. Motor de Análisis — 9 analizadores

**Archivos:** `analyzers/*.py`

Miran el mercado desde 9 ángulos distintos. Cada uno da una opinión independiente.

| Analizador | Qué mira | Ejemplo de señal |
|---|---|---|
| **Técnico** | Gráficos de precio (RSI, MACD, Bollinger, EMAs) | RSI en 35, cerca de oversold → LONG |
| **Fundamental** | Empresa (P/E, market cap, beta, dividendos) | P/E < 15, infravalorado → LONG |
| **Macro** | Economía global (VIX, DXY) | VIX > 30, miedo extremo → SHORT |
| **Sentimiento** | Noticias financieras | 70% bullish en noticias → LONG |
| **On-chain** | Blockchain (USDC transfers, ballenas) | Grandes depósitos al exchange → SHORT |
| **Orderbook** | Órdenes de compra/venta | Bid/ask imbalance > 2:1 → subiendo → LONG |
| **Cross-Asset** | Correlación entre mercados | SPY subiendo, DXY bajando → riesgo activo → LONG |
| **ICT/SMC** | Patrones institucionales (FVG, Order Blocks) | FVG sin llenar cerca del precio → LONG |
| **ADX Regime** | Fuerza de la tendencia | ADX > 25 trending, ADX < 20 lateral → ajusta estrategia |

**Salida de cada analizador:**
```python
{"signal": "LONG", "score": 72, "reasoning": "RSI oversold bounce", "details": {...}}
```

Cada uno entrega: señal (LONG/SHORT/WAIT), score (0-100), y una explicación breve.

---

## 2. Motor de Fusión

**Archivo:** `engine/fusion.py`

Toma las 9 opiniones y las combina en una sola señal usando **pesos configurables**.

**Cómo funciona:**
```
Técnico: LONG  score=70  peso 30%
Macro:   SHORT score=45  peso 25%  
ICT:     LONG  score=65  peso 10%
...etc...
   ↓
Fusión = suma(score × peso) / suma(pesos)
   ↓
Señal compuesta:
   Score ≥ 55 → LONG
   Score ≤ 45 → SHORT
   Score 45-55 → WAIT (neutro)
```

**Ejemplo real:**
```
2 capas activas:
  Técnico: LONG (score=57, peso=0.30)
  Macro:   SHORT (score=45, peso=0.25)

Fusión: (57×0.30 + 45×0.25) / (0.30+0.25)
       = (17.1 + 11.25) / 0.55
       = 28.35 / 0.55
       = 48.7 (WAIT, neutro)
```

Los pesos se configuran en `config.yaml` → `layers:`. Cada capa tiene peso distinto por mercado (forex, stocks, polymarket).

---

## 3. Motor de Decisión (DeepSeek)

**Archivo:** `engine/decider.py`

DeepSeek (IA) revisa el resultado de la fusión y decide si ejecutar o no. Es el **filtro de calidad final**.

**Lo que recibe DeepSeek:**
```
MERCADO: FOREX - EURUSD
Precio actual: 1.1011

Capas activas:
  - técnica: SHORT (score:49) - rsi neutral, ema bajista
  - macro: SHORT (score:45) - dxy débil

Fusión: SHORT (score:47.3, confianza:80)
```

**Lo que decide DeepSeek:**
```python
{"signal": "SHORT", "confidence": 70, "stop_loss_pct": 2, "take_profit_pct": 4}
```
O si no está segura:
```python
{"signal": "WAIT", "confidence": 0}
```

**Dos prompts distintos:**
- **Normal**: pide ≥2 capas en acuerdo, score >55. Conservador.
- **Fast**: acepta ≥1 capa, score >45. Más agresivo, entra más temprano.

DeepSeek puede decir WAIT aunque la fusión diga SHORT. Es su trabajo — frena señales débiles.

---

## 4. Motor de Riesgo

**Archivo:** `execution/risk_engine.py`

Antes de ejecutar la orden, verifica que no se viole ninguna regla de seguridad.

**Lo que verifica:**
```
1. Tamaño de posición
   ¿La operación excede el 5% del balance? → La ajusta

2. Exposición total
   ¿La suma de todas las posiciones abiertas supera el 40% del capital? → Bloquea

3. Límite de pérdida diaria
   ¿Perdiste más del 10% hoy? → Bloquea (circuit breaker)

4. Drawdown máximo
   ¿El balance actual está 15% por debajo del máximo histórico? → Bloquea

5. Kelly criterion
   ¿Tu historial de trades muestra expectativa negativa? → Bloquea
```

**Además calcula:**
- Tamaño óptimo según Kelly (quarter Kelly = 25% del recomendado)
- Stop loss basado en ATR (volatilidad del mercado)
- Circuit breakers automáticos

**Salida:** `{puede_operar: True/False, tamaño_ajustado: $32.50}`

---

## 5. Motor de Ejecución (Paper Broker)

**Archivo:** `execution/paper_broker.py`

Ejecuta la orden y monitorea la posición hasta que se cierra. Es el que realmente "hace la operación" (en simulación).

**Abrir posición:**
```
1. Aplica slippage (0.1% = el precio real de entrada difiere ligeramente)
2. Cobra comisión (0.1% sobre el tamaño)
3. Guarda posición con SL y TP
```

**Monitorear (cada 30 segundos):**
```
- ¿Precio tocó el Stop Loss? → Cierra (pérdida)
- ¿Precio tocó el Take Profit? → Cierra (ganancia)
- ¿Precio avanzó a favor? → Mueve stop (trailing stop) ← ASEGURA GANANCIAS
- ¿Precio se movió lo suficiente? → Break-even (SL a precio de entrada) ← EVITA PÉRDIDAS
- ¿Pasó el tiempo máximo? → Cierra por tiempo (time exit condicional)
- ¿Se alcanzó el TP parcial? → Cierra 50%, deja SL a break-even
```

**Cerrar posición:**
```
1. Calcula PnL (ganancia/pérdida)
2. Aplica slippage y comisión
3. Registra en journal y base de datos
4. Actualiza balance
```

**Dos perfiles de ejecución (Normal y Fast):**
| Parámetro | Normal | Fast |
|---|---|---|
| Stop Loss | 2% | 0.5% |
| Take Profit | 5% | 1.5% |
| Duración | 2-5 días | Horas |
| Cobertura horaria | 18h/día | 22h/día |
| Confluencia | ≥2 capas | ≥1 capa |

---

## El flujo completo (cada ~15 minutos)

```
INICIO → ¿Hay señal? → ¿Pasa filtros? → ¿DeepSeek OK? → ¿Riesgo? → Ejecutar → Monitorear

   ┌──────────────────────────────┐
   │ Loop principal (orchestrator)│
   │ Corre cada 15 minutos        │
   └──────────┬───────────────────┘
              │
   ┌──────────▼───────────────────┐
   │ 1. Datos de mercado         │
   │ 2. 9 analizadores           │
   │ 3. Fusión                   │
   │ 4. Filtros (sesión, hora,   │
   │    correlación, Kelly)      │
   │ 5. DeepSeek                 │
   │ 6. Riesgo + Tamaño          │
   │ 7. Ejecutar (Normal y Fast) │
   └──────────┬───────────────────┘
              │
   ┌──────────▼───────────────────┐
   │ Monitoreo (cada 30s)        │
   │ - Stop Loss                 │
   │ - Take Profit               │
   │ - Trailing Stop             │
   │ - Break-even                │
   │ - Time exit                 │
   └──────────────────────────────┘
```

Para verlo en acción: abrí `http://localhost:8050` → Overview → las tarjetas muestran el resultado del último ciclo de motores. Los logs en `/logs` muestran cada paso del flujo.

---

*MarketAI — Documentación técnica simplificada. v1.2.*
