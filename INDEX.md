# INDEX — MarketAI

Índice de documentación crítica. Punto de entrada único para entender el proyecto.

> Convencion Diligencia v2.7.0: este archivo es requerido desde v1.7.0. Si llega a faltar,
> `/adaptar` lo regenera.

---

## Docs críticos (raíz)

| Doc | Qué hay adentro |
|---|---|
| [README.md](README.md) | Quick start, arquitectura, tests, UI/UX |
| [CHANGELOG.md](CHANGELOG.md) | Historial de versiones con formato Keep a Changelog |
| [ROADMAP.md](ROADMAP.md) | Roadmap por fases (FASE 0 → FASE 9 + A, C, D) con items y prioridades |
| [DILIGENCIA.md](DILIGENCIA.md) | Sello de metodología Diligencia (versión + historial del proyecto) |
| [AGENTS.md](AGENTS.md) | Variables de ruta, comandos heredados, arranque, testing, DB, backup |
| [CHECKLIST.md](CHECKLIST.md) | Checklist de implementación (existe, ver estado) |
| `LICENSE` | (no presente, el proyecto es de uso personal) |

## `doc/arch/` — Sistema, bitácora, ADRs, informes

| Doc | Qué hay |
|---|---|
| `bitacora.md` | Bitácora de sesiones |
| `bugs.md` | Bug tracker |
| `incidentes.md` | Registro de incidentes |
| `ADR_SUMMARY.md` | Resumen de Architecture Decision Records |
| `metodologia.md` | Notas metodológicas |
| `reglas.md` | Reglas del proyecto |
| `r80_trading_ai_repos.md` | R80 — investigación de repos AI trading (cerrado) |
| `exit_strategies_research.md` | Investigación de estrategias de salida |
| `palomas.md` | Palomas activas (placeholder) |

## `doc/guias/` — Guías de usuario

| Guía | Tema |
|---|---|
| `guia_instalacion.md` | Instalación paso a paso |
| `guia_uso.md` / `guia_usuario.md` | Uso general del bot |
| `guia_configuracion.md` | Configuración (`config.yaml`, markets, profiles, risk gates) |
| `guia_trading.md` | Cómo funciona el trading (perfiles, gates, fusion) |
| `guia_motores.md` | Los 5 motores (loop, data, fusion, deepseek, execution) |
| `guia_arquitectura_ola1.md` | Arquitectura Ola 1 (orchestrator package, BaseAnalyzer) |
| `position-sizing-reference.md` | Cálculo de position size |
| `COMANDOS.md` | Documentación de todos los comandos slash |
| `GUIA_DE_BUENAS_PRACTICAS.md` | Buenas prácticas del proyecto |
| `GUIA_DEPLOY.md` | Deploy en server (notebook) |
| `GUIA_DE_CONTRIBUCION.md` | Cómo contribuir al proyecto |
| `GUIA_DE_INFORMES.md` | Cómo generar informes |
| `GUIA_ECOSISTEMAS.md` | Ecosistema de proyectos (Diligencia + adaptados) |
| `GUIA_LEGAL.md` | Aspectos legales |
| `GUIA_MULTI_REPO.md` | Multi-repo setup |
| `GUIA_ONBOARDING.md` | Onboarding de nuevos contributors |
| `GUIA_UPDATE_DILIGENCIA.md` | Cómo actualizar la metodología Diligencia |
| `identidad.md` | Identidad del proyecto (sello) |
| `_template.md` | Plantilla para nuevas guías |

## `doc/mecanicas/` — Mecánicas / reglas de negocio

| Doc | Tema |
|---|---|
| `MANDATO.md` | Mandato del director/orquestador |
| `MECANICA-CALIDAD.md` | Estándar de calidad documental |
| `MECANICA-CIRCUITO.md` | Mecánica del circuito de trabajo |
| `MECANICA-ENFORCEMENT.md` | Enforcement de metodología |
| `MECANICA-RECOVERY.md` | Crash recovery y auto-reconciliación |
| `_template.md` | Plantilla para nuevas mecánicas |

## `doc/server/` — Operación en notebook

| Doc | Tema |
|---|---|
| `SERVER_MANDATE.md` | Mandato para la sesión Mavis-allá |
| `INCIDENTS_2026-07-11.md` | Reporte de incidente del 2026-07-11 (5 issues) |
| `RISK_GATE_SPEC_v1.1.md` | Spec de los 5 risk gates |
| `brief-ai-prompt-review.md` | Brief para revision del prompt AI (sprint 2026-07-11) |

## Skills (`skills/`)

Skills cargables con `skill("nombre")` — ver `AGENTS.md` para la lista completa.

## Comandos slash

- **Globales heredados**: viven en `~/.config/opencode/commands/` (ver `AGENTS.md § Comandos globales`)
- **Locales**: `.opencode/commands/` (proyecto) — ver `AGENTS.md § Comandos personalizados`

## Convenciones rápidas

- **Sin build step**: Python puro. Se edita y se ejecuta.
- **Tests**: `python -m pytest tests/ -v` (159 tests al dia)
- **DB**: SQLite en `data/market.db`, schema en `data/database.py` → clase `Database()`
- **No hay auth**: dashboard es local en `localhost:8050`, no exponer en redes públicas
- **Disciplina de commit**: backup → pull → push (ver `AGENTS.md § Disciplina BUILD`)

## Actualizado

Ultima actualizacion del indice: 2026-07-11 (sync Diligencia v2.6.3 → v2.7.0).

## Archivos relacionados

- `DILIGENCIA.md` — metodología aplicada
- `AGENTS.md` — variables de ruta y comandos
- `CHANGELOG.md` — qué cambió en este sync
