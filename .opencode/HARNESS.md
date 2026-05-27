# HARNESS.md — MarketAI

Harness global: `~/.config/opencode/`
Versión: 1.0.0 | Creado: 2026-05-19

---

## Comandos del proyecto

| Tipo | Comando | Notas |
|---|---|---|
| Test | `python -m pytest tests/ -v` | pytest |
| Lint | *No configurado* | |
| Virtualenv | `venv\Scripts\activate` | Entorno virtual Python |
| Orchestrator (once) | `python orchestrator.py --mode once` | Una iteración |
| Orchestrator (loop) | `python orchestrator.py --mode loop` | Loop 24/7 |
| Dashboard | `.\dashboard.bat` | Flask en localhost:8050 |

## Documento SSOT del proyecto

Archivo principal: `AGENTS.md` (136 líneas)

## Skills locales del proyecto

| Skill | Ruta |
|---|---|
| `backup-pre-edit` | `skills/backup-pre-edit.md` |
| `actualizar-docs` | `skills/actualizar-docs.md` |

## Modelos del proyecto

| Rol | Modelo |
|---|---|
| Decisiones de trading | DeepSeek V4 Pro (`config.yaml` → `deepseek.model`) |
| Temperatura | 0.3 |

## Stack

- Python puro (sin compilación)
- Dashboard: Flask + HTML templates + Plotly
- DB: SQLite (`MarketAI.db`)
- Tests: pytest
- 8 analizadores (técnico, on-chain, sentimiento, orderbook, fundamental, macro, cross-asset, ICT/SMC)

## Convenciones

- Prefijos: P1/P2/P3 (prioridad), Fase-XX, ADR-XXX, B-XX
- Fallback: WAIT si respuesta inválida de DeepSeek

## Archivos críticos

`config.yaml`, `.env`, `orchestrator.py`, `data/database.py`, `engine/decider.py`

## Harness activo

- [x] Agentes SDD globales disponibles
- [x] Skills del harness disponibles
- [x] Post-edit verification activa
- [x] TDD (pytest disponible)
