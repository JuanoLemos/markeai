# Diligencia v1.18.1 — Estructura estándar de documentación

Sello de metodología para proyectos OpenCode.

---

## Qué es

Diligencia es una convención de estructura de documentación para proyectos OpenCode.
Define dónde vive cada tipo de archivo, cómo se nombran las variables de ruta, y cómo se organizan los comandos.

## Convención

| Tipo | Ubicación |
|---|---|
| Roadmap | `ROADMAP.md` (raíz) |
| Checklist | `CHECKLIST.md` (raíz) |
| Changelog | `CHANGELOG.md` (raíz) |
| ADRs, sistema, bitácora | `doc/arch/` |
| Guías de usuario | `doc/guias/` (incluye `ESTANDAR-COMANDOS.md`) |
| Mecánicas del juego | `doc/mecanicas/` |
| Variables de ruta | `AGENTS.md` → `Mapeo de rutas` |
| Comandos locales | `.opencode/commands/` |
| Harness | `.opencode/HARNESS.md` (test, lint, skills, stack) |
| Comandos globales | `~/.config/opencode/commands/` |

## Proyectos adaptados

| Proyecto | Fecha | Estado |
|---|---|---|
| MarketAI | 2026-06-13 | ✅ v1.18.1 |

## Historial

| Versión | Fecha | Cambios |
|---|---|---|
| v1.18.1 | 2026-06-13 | Upgrade desde v1.17.2 — Emojis liberados (política visual), themes sincronizados (naranja/verde/celeste), BUILD guard en AGENTS.md, instrucción BUILD en opencode.jsonc |
| v1.17.2 | 2026-06-09 | Upgrade desde v1.15.0 — GitHub readiness (LICENSE, CODE_OF_CONDUCT, CONTRIBUTING), GUIA_ONBOARDING, GUIA_DE_INFORMES, GUIA_LEGAL, GUIA_MULTI_REPO, GUIA_UPDATE_DILIGENCIA, MECANICA-CALIDAD, MECANICA-ENFORCEMENT, NOTICE, SECURITY.md, Provider-agnostic docs, /CBP escalativo, Meta-PLAN 4 workers, /version git-log, $BACKUPS/$BACKUP_KEEP/$MECANICAS_TEMPLATE/$NEWS_FILE |
| v1.15.0 | 2026-06-05 | Upgrade desde v1.4 — Enforcement documental (check-docs, pre-commit), /circuito, /doctor, /salud, /reanudar, ADR_SUMMARY, identidad, MANDATO, GUIA_DE_BUENAS_PRACTICAS, GUIA_ECOSISTEMAS, CI/CD workflow |
| v1.4 | 2026-05-31 | $INCIDENTS, doc/arch/incidentes.md, comandos bug/incidente |
| v1.0 | 2026-05-09 | Adaptación desde estructura legacy (doc/documentos/ → raíz + doc/arch/) |

## Archivos relacionados

- `ROADMAP.md` — Roadmap del proyecto
- `CHECKLIST.md` — Checklist de implementación
- `CHANGELOG.md` — Historial de versiones
- `AGENTS.md` — Variables de ruta y comandos
