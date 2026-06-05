# Diligencia v1.15.0 — Estructura estándar de documentación

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
| MarketAI | 2026-06-05 | ✅ v1.15.0 |

## Historial

| Versión | Fecha | Cambios |
|---|---|---|
| v1.15.0 | 2026-06-05 | Upgrade desde v1.4 — Enforcement documental (check-docs, pre-commit), /circuito, /doctor, /salud, /reanudar, ADR_SUMMARY, identidad, MANDATO, GUIA_DE_BUENAS_PRACTICAS, GUIA_ECOSISTEMAS, CI/CD workflow |
| v1.4 | 2026-05-31 | $INCIDENTS, doc/arch/incidentes.md, comandos bug/incidente |
| v1.0 | 2026-05-09 | Adaptación desde estructura legacy (doc/documentos/ → raíz + doc/arch/) |
