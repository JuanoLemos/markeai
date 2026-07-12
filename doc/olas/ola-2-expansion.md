# Ola 2: Expansión

**Estado:** 🔄 En progreso
**Depende de:** Ola 0
**Agentes:** @trader, @sdd-implement

---

## Scope

Ampliación de cobertura de mercado y protección del sistema. Incluye ETFs amplios (IVV, EEM, IWM, XLK, XLF, GLD, TLT, VTI), fondos indexados (VFIAX, FXAIX), CEDEARs argentinos (.BA), y las 5 risk gates pre-trade (R1-R5). Pendiente: analizador fundamental con métricas ETF.

| ID | Item | Prioridad | Estado |
|----|------|-----------|--------|
| R63 | 8 ETFs + 2 index funds en config.yaml | P1 | ✅ |
| R64 | Matriz de correlación expandida en entry_filters | P1 | ✅ |
| R65 | 98 tests pasan — sin cambios a brokers/risk/fusion/decider | P1 | ✅ |
| R66 | Analizador fundamental con métricas ETF (AUM, expense ratio, YTD return) — Fase B | P2 | ⏳ |
| R67 | 7 CEDEARs .BA en config.yaml | P1 | ✅ |
| R68 | get_usd_ars_rate() en collector_yfinance | P1 | ✅ |
| R69 | Precios ARS → pseudo-USD en orchestrator | P1 | ✅ |
| R70 | BYMA session hours 12-19 UTC | P1 | ✅ |
| R71 | Correlación CEDEAR vs subyacente (0.98) | P1 | ✅ |
| R72 | _analyze_stocks() pasa 24 tickers completos | P1 | ✅ |
| R85 | Risk gates R1-R5: validate_trade gatekeeper pre-trade | P1 | ✅ |

## Entregables

- [x] 24 tickers total (7 US large cap + 8 ETFs + 2 index funds + 7 CEDEARs)
- [x] Risk gates R1-R5 en cascada (R4→R5→R1→R2→R3)
- [x] 34 tests de risk gates pasando
- [ ] Analizador fundamental ETF-aware (R66)

## Archivos relacionados

- `ROADMAP.md` — Roadmap del proyecto
- `doc/server/RISK_GATE_SPEC_v1.1.md` — Especificación de risk gates
