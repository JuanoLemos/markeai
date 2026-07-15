# Guía de Mecánica de Bots — MarketAI v1.4.0

Cómo funciona el sistema de trading explicado con analogías.

---

## 1. Los 9 analizadores = 9 asesores en una mesa

Imaginá 9 expertos sentados alrededor de una mesa. Cada uno mira el mercado desde su especialidad:

| Analizador | Analogía | Qué mira |
|---|---|---|
| **Técnico** | Un analista de gráficos con regla y compás | RSI, MACD, medias móviles, soportes/resistencias |
| **Fundamental** | Un contador que lee balances | P/E ratio, market cap, dividendos |
| **Macro** | Un economista mirando el noticiero | DXY (dólar), VIX (miedo del mercado) |
| **Sentimiento** | Un psicólogo leyendo Twitter | ¿La gente está eufórica o aterrada? |
| **On-chain** | Un detective de blockchain | Entradas/salidas de wallets, actividad en la red |
| **Orderbook** | Un trader de piso mirando la profundidad | ¿Hay más compradores o vendedores? |
| **Cross-asset** | Un estratega comparando mercados | Si SPY sube, ¿QQQ lo sigue? |
| **ADX Regime** | Un meteorólogo del mercado | ¿Está en tendencia o está planchado? |
| **ICT/SMC** | Un trader institucional | Order blocks, liquidity sweeps, smart money |

Cada uno da su opinión: **LONG**, **SHORT**, o **WAIT** — con un puntaje de 0 a 100.

---

## 2. El motor de fusión = El jefe de mesa

El **fusion engine** toma las 9 opiniones y las combina como un promedio ponderado:

```
Si el técnico dice LONG(72) y el macro dice LONG(65) y el sentimiento dice WAIT(50)
→ Fusión: "hay consenso parcial, señal LONG con confianza 50"
```

El jefe resume los datos y los pasa al decisor final: DeepSeek.

---

## 3. DeepSeek = El trader que decide

DeepSeek recibe:
- El resumen del jefe de mesa (fusión)
- Las 9 opiniones individuales de los asesores
- Las posiciones que ya tenés abiertas
- El precio actual

Y piensa:

> "OK, hay 2 capas diciendo LONG con scores decentes. El macro está neutral (no contradice). No hay posición abierta en este ticker. El riesgo es que el DXY rebote en 105. Conclusión: LONG con 70% de confianza, $30 de tamaño."

**Optimización de costo:** antes de llamar a DeepSeek, el sistema verifica:
- ¿El mercado está abierto? (R89 session filter)
- ¿La fusión tiene score suficiente? (R89 pre-filter — si score < 30 y conf < 25, ni se llama)

Esto ahorra ~$0.78/día en llamadas innecesarias.

---

## 4. Los 5 Risk Gates = Los controles de seguridad del aeropuerto

Después de que DeepSeek decide, la orden pasa por 5 filtros:

```
DeepSeek: "COMPRAR SPY, $30"
   ↓
R4 — Max Open: ¿Hay menos de 12 posiciones abiertas? → Sí, pasá.
R5 — Max Size: ¿$30 no es más del 12% del balance? → Sí, pasá.
R1 — Sector Cap: ¿No estoy concentrado en tech USA? → Sí, pasá.
R2 — Correlation: ¿No tengo ya SPY o QQQ abierto? → No duplicado. Pasá.
R3 — Effective-N: ¿Estoy diversificado en al menos 2 sectores? → Sí, pasá.
   ↓
✅ Orden ejecutada → Paper Broker
```

Orden de cascada: **R4 → R5 → R1 → R2 → R3** (del más barato al más caro computacionalmente). Si cualquiera rechaza, la orden se cancela.

---

## 5. Dual Profile = Dos personalidades de inversión

MarketAI corre dos traders en paralelo:

| | **FAST** 😎 | **NORMAL** 🧐 |
|---|---|---|
| Estilo | Agresivo, micro-trading | Conservador, paciente |
| Tamaño por trade | $30-50 | $50 |
| Stop-loss | 0.5-1.5% | 2% |
| Take-profit | 1.5-3% | 5% |
| ¿Filtra por ADX? | No (opera siempre) | Opcional |
| ¿Filtra por correlación? | No | Sí |
| ¿Horario? | 22h/día | Solo horario de mercado |
| Analogía | Un scalper que entra y sale rápido | Un inversor que espera la oportunidad perfecta |

Cada perfil tiene su propia cuenta separada de $1,000 (paper).

---

## 6. Paper Broker = Trading con dinero de mentira

Simula la ejecución real:

```
1. Resta $30 del balance (ficticio)
2. Aplica slippage (0.1%) + comisión (0.1%)
3. Guarda la posición: "SPY LONG, entraste a $752, SL a 1%, TP a 3%"
```

Cada 60 segundos revisa precios reales:
- **Stop-loss:** el precio bajó → cierra con pérdida
- **Take-profit:** el precio subió → cierra con ganancia
- **Partial TP1:** llegó a la mitad del TP → cierra 50%, sube SL a break-even
- **Time-exit:** pasaron 72h → cierra por tiempo

---

## 7. El ciclo completo — Cada 60 minutos

```
08:00 → El loop despierta
08:01 → 9 analizadores recolectan datos (yfinance, APIs)
08:02 → Fusión: "En SPY hay señal LONG con confianza 50"
08:03 → Session filter: ¿mercado abierto? → Sí
08:03 → DeepSeek (FAST): "LONG SPY, conf 70%"
08:03 → DeepSeek (NORMAL): "WAIT — no hay convergencia suficiente"
08:03 → FAST pasa 5 risk gates → ✅ OK
08:03 → Paper Broker abre posición: SPY LONG, $30
08:03 → Se guarda en DB: trades, signals, portfolio
08:03 → El loop duerme 60 minutos
09:00 → El loop despierta de nuevo...
```

---

## Diagrama completo

```
        9 ANALIZADORES          FUSIÓN           DEEPSEEK        5 GATES        BROKER
        ┌──────────┐              │                 │              │              │
 Técnico│ "LONG 72"│              │                 │              │              │
 Macro  │ "LONG 65"│──→ Jefe: ──→│ "Señal LONG,  ──→│ ¿Compro? ──→│ R1→R5 ✓ ──→│ "SPY LONG
 Sentim.│ "WAIT 50"│    promediar│  confianza 50%" │ "Sí, LONG"   │              │  $30 abierto"
        └──────────┘              │                 │              │              │
                                  │                 │              │              │
     Opiniones individuales       │  Opinión        │  Decisión    │  Filtros     │  Ejecución
                                  │  combinada      │  final       │  seguridad   │  simulada
```

---

## Archivos relacionados

- `engine/decider.py` — Prompts de DeepSeek (v3: WAIT fallback, pre-mortem modulador)
- `engine/fusion.py` — Fusión ponderada de analizadores
- `orchestrator/pipeline.py` — Ciclo principal con filtros y risk gates
- `execution/risk_gates/` — R1 a R5 en cascada
- `execution/paper_broker.py` — Simulador de ejecución
- `config.yaml` — Perfiles, intervalos, filtros, risk gates
- `orchestrator/core.py` — Loop principal y auto-detox
