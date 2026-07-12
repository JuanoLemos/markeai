# MarketAI — Spec: 3 Reglas Duras de Risk Gate (R1 Sector Cap + R2 Correlation + R3 Effective-N)

**Versión:** 1.1 (actualizado con decisiones del usuario, 2026-07-11)
**Owner:** @trade (trading specialist, no code)
**Para:** @coder (implementación)
**Origen del patrón:** swarm-trader (zhound420) — risk manager con 11 reglas duras, todas code-enforced, aplicadas pre-trade. Reforzado por freqtrade (PairList + Protections) y ai-hedge-fund (agente Risk Manager dedicado).
**Patrón de fondo:** el risk manager es un **gate** (frena antes), no un **post-processor** (lamenta después).

---

## 0. Contexto (el problema que este spec resuelve)

El `correlation_check` actual de MarketAI se ejecuta **después** de que la orden se llenó. Eso significa: la posición entra, y después se evalúa si "era buena idea". El caso conocido: el bot llegó a abrir **11 LONG simultáneos en 3 minutos** sobre el mismo "barrio" (SPY, QQQ, AAPL, MSFT, GOOGL, AMZN, IVV, EEM, IWM, XLK, TSLA) — todos tech/mega-cap US, todos correlacionados, **un solo trade disfrazado de 11**.

**Decisión de diseño:** el `correlation_check` viejo se **FUSIONA** con R2 (Pre-Trade Correlation Gate) en un único sistema unificado. La lógica que ya tenía se incorpora dentro de R2 — no se mantiene como check paralelo, no se parchea, no se duplica. La decisión de correlación vive en un solo lugar. Las reglas son código, no prompts, y se ejecutan **antes** de mandar la orden al broker.

---

## 1. Las 3 reglas nuevas (todas pre-trade, en cascada)

### R1 — Sector/Theme Cap
- **ID interno:** `risk.gate.sector_cap`
- **Propósito:** tope agregado de exposición a un mismo sector/tema.
- **Inspiración:** swarm-trader regla 10 (max sector allocation 30%).
- **Lógica:** suma exposición del sector + candidato; si supera el cap → REJECT `SECTOR_CAP_EXCEEDED`.
- **Tabla de sectores:** `us_mega_cap_tech` (AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA) 30%, `us_broad_market` (SPY, IVV, QQQ, IWM) 30%, `us_sector_etf` 20%, `emerging_markets` 15%, `cash_equivalent` sin cap. Ticker no clasificado → 15% (conservador).

### R2 — Pre-Trade Correlation Gate
- **ID interno:** `risk.gate.correlation`
- **Inspiración:** implícita en cap por sector + Markowitz / ML4T.
- **Setup:** matriz de correlación rolling (60-90 días), precalculada con datos hasta T-1 (NO intraday, look-ahead bias).
- **Lógica:** si `max(corr) > 0.70` → REJECT `HIGH_CORRELATION_WITH_OPEN`; si hay 3+ posiciones con corr > 0.6 → REJECT `CORRELATION_CLUSTER_OVERLOAD`.

### R3 — Effective-N Position Cap
- **ID interno:** `risk.gate.effective_n`
- **Lógica:** `N_efectivo = 1 / sum(w_i^2)` (inverso Herfindahl sobre pesos). Si N_efectivo < 4 → REJECT `EFFECTIVE_N_TOO_LOW`.
- **Decisión del usuario:** GATE desde fase 1 (no observabilidad).

---

## 2. Reglas existentes pasadas de "check" a "gate"

### R4 — Max Open Positions (12)
### R5 — Max Position Size (8% del equity)

---

## 3. Pipeline integration

```
signal_generator → [R4] → [R5] → [R1] → [R2] → [R3] → broker
```

Cascada, de más barato a más caro. Si R1 rechaza, no se evalúa R2.

---

## 4. Configuración (YAML)

Ver `config.yaml` sección `risk_gates`.

---

## 5-7. Decisiones confirmadas por el usuario

1. R3 = GATE desde fase 1.
2. Tabla de sectores en YAML.
3. `correlation_check` viejo FUSIONADO con R2.
4. Sectorización MANUAL en YAML.
5. Matriz de correlación en SQLite.
6. R4=12, R5=8% confirmados.

---

## 8. Out of scope

- Rate-limit del signal generator (flaggeado, otro sprint).
- Cambios al signal generator mismo.
- Estrategias de salida.

---

**Implementado en commit `66e5627`. El código vive en `execution/risk_gates/`.**
