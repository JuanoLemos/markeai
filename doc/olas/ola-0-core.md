# Ola 0: Core

**Estado:** ✅ Completada
**Depende de:** —
**Agentes:** @trader, @sdd-implement

---

## Scope

Infraestructura base del sistema de trading. Incluye la fundación del proyecto, recolección de datos, 9 analizadores, motor DeepSeek, paper broker en dual profile, auto-aprendizaje, alertas, y dashboard web.

| ID | Item | Prioridad | Estado |
|----|------|-----------|--------|
| R01-R06 | Fundación: estructura, arquitectura, dependencias, .env, acceso APIs | P1 | ✅ |
| R07-R10 | Recolección: yfinance, news, Polymarket, SQLite DB | P1 | ✅ |
| R11-R19 | 9 analizadores: técnico, on-chain, sentimiento, orderbook, fundamental, macro, cross-asset, ADX, ICT/SMC | P2 | ✅ |
| R20-R21 | Motor de decisión: fusión ponderada + DeepSeek dual prompt | P1 | ✅ |
| R22-R26 | Ejecución: paper broker, risk engine, entry filters, stubs reales | P1 | ✅ |
| R27-R29 | Aprendizaje: journal, strategy evolver, backtest walk-forward | P2 | ✅ |
| R30-R31 | Alertas: Telegram, Discord, orquestador loop dual profile | P1 | ✅ |
| R32-R37 | Dashboard web: Flask + 9 páginas + 6 temas, tray app, backtest replay | P1 | ✅ |

## Entregables

- [x] 98+ tests pasando
- [x] Sistema corriendo 24/7 con loop dual profile (Normal + Fast)
- [x] Dashboard funcional en localhost:8050
- [x] System tray con tooltip, auto-restart, pulse dot
- [x] Prompts DeepSeek v1 con fallback WAIT en JSON inválido

## Archivos relacionados

- `ROADMAP.md` — Roadmap del proyecto
- `CHANGELOG.md` — Historial de versiones
