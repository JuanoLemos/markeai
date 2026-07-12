# Ola 3: Producción

**Estado:** ⏳ Pendiente
**Depende de:** Ola 2
**Agentes:** @sdd-architect, @sdd-implement, @sdd-verify

---

## Scope

Puesta en producción real del sistema. Incluye la validación final en paper trading, migración a micro-montos reales, monitoreo diario, modo replay histórico, deploy 24/7 con Docker, y herramientas operacionales Ola 2.

| ID | Item | Prioridad | Estado |
|----|------|-----------|--------|
| R38 | Paper trading 2-4 semanas (validación) | P1 | 🔄 |
| R39 | Micro-montos reales ($10-50 por operación) | P1 | ⏳ |
| R40 | Monitoreo diario con ajustes manuales | P1 | ⏳ |
| R41 | Estrategia madura → capital progresivo | P2 | ⏳ |
| R42 | Modo replay histórico para QA sin APIs live | P2 | ⏳ |
| — | Deploy Docker: docker-compose, Dockerfile, healthcheck, deploy.bat | P1 | ✅ |
| — | Ola 2 tools: ola2_backup, ola2_daily_summary, ola2_monitor, ola2_watchdog | P2 | ✅ |
| — | Dashboard mobile redesign (warm dark, bottom nav, gates page) | P2 | ✅ |

## Pendientes

| Item | Prioridad | Depende de |
|---|---|---|
| Validar paper trading antes de micro-montos reales (R38→R39) | P1 | — |
| Notebook 24/7: configurar Docker auto-start, deploy.bat schedule | P1 | R38 |
| Replay histórico QA (R42) | P2 | R38 |
| Dashboard: Tabla `gate_rejections` en DB (en vez de parsear log) | P2 | R85 |

## Archivos relacionados

- `ROADMAP.md` — Roadmap del proyecto
- `Dockerfile` — Imagen Python 3.12
- `docker-compose.yml` — Servicios orchestrator + dashboard
- `doc/guias/GUIA_DEPLOY.md` — Guía de deploy Docker
- `scripts/ola2_*.py` — Scripts operacionales
