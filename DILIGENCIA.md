# Diligencia v2.7.0 — MarketAI

Sello de metodología para proyectos OpenCode.

---

## Convención

| Tipo | Ubicación |
|---|---|
| Roadmap | `ROADMAP.md` (raíz) |
| Checklist | `CHECKLIST.md` (raíz) |
| Changelog | `CHANGELOG.md` (raíz) |
| Índice | `INDEX.md` (raíz) |
| ADRs, sistema, bitácora | `doc/arch/` |
| Guías de usuario | `doc/guias/` |
| Mecánicas | `doc/mecanicas/` |
| Olas (waves) | `doc/olas/` |
| Variables de ruta | `AGENTS.md` → `Mapeo de rutas` |
| Comandos locales | `.opencode/commands/` |
| Harness | `.opencode/HARNESS.md` (test, lint, skills, stack) |
| Comandos globales | `~/.config/opencode/commands/` |

## Proyectos adaptados

| Proyecto | Fecha | Estado |
|---|---|---|
| MarketAI | 2026-07-11 | ✅ v2.7.0 |

## Historial

| Versión | Fecha | Cambios |
|---|---|---|
| v2.7.0 | 2026-07-11 | Sync v2.6.3 → v2.7.0. INDEX.md creado. $NEWS_FILE removido (huérfana). `doc/arch/palomas.md` creado. CHANGELOG [Unreleased] poblado con 5 commits post-1.4.0. |
| v2.6.3 | 2026-07-06 | Upgrade desde v1.18.1 — Comandos sincronizados (29 activos), $PALOMA_MAIN_PLAN en AGENTS.md, CHANGELOG registrado |
| v1.18.1 | 2026-06-13 | Emojis liberados, themes, BUILD guard, /mutacion, /revision |
| v1.17.2 | 2026-06-09 | GitHub readiness (LICENSE, CODE_OF_CONDUCT, CONTRIBUTING), guías/metodología nuevas |
| v1.15.0 | 2026-06-05 | Enforcement documental, /circuito, /doctor, /salud, /reanudar |
| v1.4 | 2026-05-31 | $INCIDENTS, doc/arch/incidentes.md, comandos bug/incidente |
| v1.0 | 2026-05-09 | Adaptación desde estructura legacy |

## Notas del upgrade v2.6.3 → v2.7.0

- El global Diligencia está en v2.7.0 (sistema de olas disponible via `/ola`)
- El comando `~/.config/opencode/commands/adaptar.md` está en v2.6.3 (lag vs DILIGENCIA.md global — flag para upstream, no es nuestro)
- Para MarketAI, los cambios estructurales aplicables al upgrade ya están: `INDEX.md` y `doc/arch/palomas.md` creados
- Items pendientes (R85-R88) son scope del proyecto, no de la metodología

## Archivos relacionados

- `ROADMAP.md` — Roadmap del proyecto
- `CHECKLIST.md` — Checklist de implementación
- `CHANGELOG.md` — Historial de versiones
- `AGENTS.md` — Variables de ruta y comandos
