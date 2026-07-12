# Ola 4: IA 2.0

**Estado:** ⏳ Pendiente
**Depende de:** Ola 3
**Agentes:** @trader, @consejero, @sdd-implement

---

## Scope

Mejoras de inteligencia del motor de decisión y modelo de machine learning. Incluye la investigación de técnicas AI en repos GitHub (completada), los nuevos prompts v2 de DeepSeek (completados por MiniMax), time-exit configurable estilo Freqtrade, el cuello de botella del Portfolio Manager, y walk-forward validation.

| ID | Item | Prioridad | Estado |
|----|------|-----------|--------|
| R80 | Informe repos trading — investigación de técnicas AI en GitHub | P2 | ✅ |
| — | Prompt v2 DeepSeek: WAIT default, pre-mortem, 4 ejemplos few-shot, reasoning estructurado | P1 | ✅ |
| R86 | Time-exit configurable: minimal_roi table estilo Freqtrade | P1 | 🔴 Pendiente |
| R87 | Prevención posiciones contradictorias: single Portfolio Manager bottleneck | P1 | 🔴 Pendiente |
| R88 | Walk-forward validation con purging-and-embargo (ML4T pattern) | P2 | 🔴 Pendiente |

## Pendientes

| Item | Prioridad | Depende de |
|---|---|---|
| Time-exit configurable con tabla minimal_roi (R86) | P1 | R24 |
| PM bottleneck: tabla gate_rejections + single entry point | P1 | R22 |
| Walk-forward validation (R88) | P2 | R29 |

## Archivos relacionados

- `ROADMAP.md` — Roadmap del proyecto
- `engine/decider.py` — Prompts v2
- `execution/paper_broker.py` — Time-exit stub
- `doc/server/RISK_GATE_SPEC_v1.1.md` — Risk gate spec
- `doc/arch/r80_trading_ai_repos.md` — Informe de investigación
