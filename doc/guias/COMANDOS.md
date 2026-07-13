# COMANDOS — Diligencia v2.6.6

> Referencia rapida de comandos, agentes y circuitos de calidad.

---

## CREAR (4)

| Comando | Descripcion |
|---|---|
| `/adaptar` | Adaptar proyecto a Diligencia |
| `/+rm` | Agregar item al ROADMAP |
| `/doc` | Crear/actualizar guia o mecanica |

---

## PLANIFICAR (8)

| Comando | Descripcion |
|---|---|
| `/plan` | Planificar tarea o grupo `--ola` |
| `/rm` | Top 10 tareas por prioridad |
| `/next` | Plan de ejecucion por olas |
| `/consejo` | Consultar al consejero |
| `/circuito` | Revisar integridad logica y UX |
| `/explica` | Explicar concepto |
| `/foco` | Enfocar agente en area |
| `/head` | Preparar edicion de seccion |

---

## EJECUTAR (6)

| Comando | Descripcion |
|---|---|
| `/commit` | Commit formateado `--push` |
| `/version` | Cerrar sesion: bump + doc sync |
| `/reanudar` | Recuperar sesion |
| `/estado` | Reporte rapido del proyecto |
| `/backup` | Backup `--all` zip completo |
| `/updoc` | Actualizar documentacion |

---

## REVISAR (5)

| Comando | Descripcion |
|---|---|
| `/informe-salud` | Salud de todos los proyectos |
| `/reportar` | Reportar bug o incidente |
| `/mutacion` | Absorber mutaciones externas |
| `/revision` | Revisar mutaciones del proyecto |
| `/debug` | Analisis profundo de codigo |

---

## CUIDAR (6)

| Comando | Descripcion |
|---|---|
| `/salud` | Cuidado integral (8 fases) |
| `/documentar` | Auditoria documental (24 checks) |
| `/health` | Verificar sintaxis y consistencia |
| `/diligencia-check` | Validar estructura Diligencia |
| `/deprecar` | Mover obsoleto a `.old/` |
| `/limpiar` | Eliminar temporales |

---

## AGENTES

### Razonamiento (DeepSeek V4 Pro)

| Agente | Rol | Subcomandos |
|---|---|---|
| `@consejero` | Decisiones de proyecto, trayectoria, dominio | `/consejo --explorar <url>` |
| `@sdd-architect` | Diseno de sistemas, propuestas, plan de tareas | `/plan --ola N --sub-fases` |
| `@sdd-reviewer` | Revision de codigo con contexto fresco | `git diff` + analisis |
| `@documentador` | Auditoria documental (24 checks, 6 cats) | `/documentar --legales` |

### Ejecucion (DeepSeek V4 Flash)

| Agente | Rol | Subcomandos |
|---|---|---|
| `@sdd-implement` | Aplica cambios de codigo segun plan | `edit` + `bash` |
| `@sdd-verify` | Ejecuta tests (RED -> GREEN -> REFACTOR) | `npm test`, `pytest` |
| `@circuito` | Integridad logica y UX | `/circuito [area]` |

### Especializados por dominio

| Agente | Rol | Modelo | Proyecto |
|---|---|---|---|
| `@narrador` | Prompt engineering narrativo, worldbuilding, system prompts | DeepSeek V4 Pro | Nemesis |
| `@game-designer` | Mecanicas, balance, economia, curvas de dificultad | DeepSeek V4 Pro | Nemesis, conquisitare |
| `@trader` | Estrategias de trading, gestion de riesgo, brokers | DeepSeek V4 Pro | MarketAI |
| `@cartografo` | Pipeline geoespacial, mapas reales, GIS | DeepSeek V4 Pro | conquisitare |
| `@editor-video` | Pipeline de video, composicion avatar+voz+contenido | MiniMax M3 | OpenMontage |
| `@disenador` (también cubre design systems) | CSS generativo, componentes, paletas, accesibilidad | MiniMax M3 + image-01 | BBB (unificado) |

### Multimodal

| Agente | Rol | Modelo |
|---|---|---|
| `@disenador` | Diseno UI/UX | MiniMax M3 + image-01 |

### Invocacion y sincronizacion

| Comando | Subcomandos |
|---|---|

---

## Circuitos de calidad

```
SDD:         @sdd-architect ──→ @sdd-implement ──→ @sdd-verify ──→ @sdd-reviewer
Documental:  @documentador ──→ /documentar ──→ /agentes-sync
Integridad:  @circuito ──→ /circuito [area] ──→ reporte de handlers/rutas/navegacion
```

| Circuito | Flujo | Salida |
|---|---|---|
| 🔵 SDD | architect → implement → verify → reviewer | Plan + codigo + tests + revision |
| 🟢 Paloma | agente → --new → --publish → evaluar → aplicar/archivar | Paloma en 📬/✅/🗑️ |
| 🟣 Documental | documentador → /documentar → /agentes-sync | Hallazgos + agentes actualizados |
| 🟡 Integridad | circuito → /circuito [area] | Reporte de handlers/rutas/UX |

---

## Archivos relacionados

- `GUIA_REFERENCIA_RAPIDA.md` — guia con categorias y workflows
- `GUIA_DE_COMANDOS.md` — referencia completa
- `AGENTS.md` — tabla original de comandos
- `MECANICA-TASK-ROUTER.md` — enrutador tarea → agente → modelo → API
| /ola | Sistema de oleadas multi-proyecto
           | planear <proyecto>, ejecutar <olas>, estado <olas> |
