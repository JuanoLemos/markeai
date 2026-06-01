# Diligencia v1.4 — Estructura estándar de documentación

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
| Guías de usuario | `doc/guias/` |
| Variables de ruta | `AGENTS.md` → `Mapeo de rutas` |
| Comandos locales | `.opencode/commands/` |
| Comandos globales | `~/.config/opencode/commands/` |

## Proyectos adaptados

| Proyecto | Fecha | Estado |
|---|---|---|
| MarketAI | 2026-05-31 | ✅ v1.4 |

## Historial

| Versión | Fecha | Cambios |
|---|---|---|
| v1.0 | 2026-05-09 | Adaptación desde estructura legacy (doc/documentos/ → raíz + doc/arch/) |
| v1.4 | 2026-05-31 | $INCIDENTS, doc/arch/incidentes.md, comandos bug/incidente |
