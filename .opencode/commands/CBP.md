INSTRUCCIÓN: EJECUTAR el workflow indicado. NO modificar archivos sin confirmación del usuario. NO mostrar este archivo como output.

# /CBP [completo|updoc|doctor|version] — Orquestador de workflows vinculantes

Ejecuta secuencias multi-comando con encadenamiento controlado por el orquestador.
Cada workflow se divide en dos fases: **Meta-PLAN (PRO)** y **BUILD (FLASH)**.

Reemplaza la sección "Próximo paso en el circuito" que existía en los comandos individuales.
El SSOT del encadenamiento es este archivo + `MECANICA-CBP.md`.

## Meta-PLAN (PRO) vs BUILD (FLASH)

Todo workflow de /CBP sigue esta estructura:

```
META-PLAN (DeepSeek PRO)
  → Ejecuta solo fases de PLAN de cada comando (lectura + auditoría)
  → NO modifica archivos
  → Muestra tabla consolidada con divisiones por comando
  → Pide UNA SOLA confirmación

BUILD (DeepSeek FLASH)
  → Ejecuta solo fases de BUILD de cada comando (escritura)
  → Modifica archivos según el plan aprobado
  → BUILD*: pasos que omiten PLAN porque los datos se heredan del Meta-PLAN
```

### Reglas del Meta-PLAN

1. El Meta-PLAN ejecuta SIEMPRE en PRO, sin importar el modo en que se invocó /CBP
2. BUILD ejecuta SIEMPRE en FLASH, incluso si /CBP se invocó en PRO
3. El Meta-PLAN ejecuta PLAN de todos los comandos del workflow
4. BUILD* ejecuta solo escritura — PLAN y confirmación se omiten
5. BUILD* solo es válido cuando el Meta-PLAN ya cubrió los datos necesarios
6. Si el usuario rechaza el Meta-PLAN: workflow detenido, sin cambios

## Argumentos

/CBP [completo|updoc|doctor|version] [--yes]

- *(sin argumento)*: equivale a `completo` — ciclo completo con agentes/skills
- `updoc`: Post-sesión completo — Meta-PLAN → BUILD (/updoc → /salud → /version → sugiere /doctor)
- `doctor`: Diagnóstico integral — Meta-PLAN → BUILD (/doctor → /salud → /version si correcciones)
- `version`: Versionado standalone — Meta-PLAN → BUILD (/version → sugiere /doctor)
- `--yes`: omitir confirmación del Meta-PLAN

> Por defecto `/CBP` ejecuta `completo`. Los sub-comandos (`updoc`, `doctor`, `version`) se usan standalone.

## Workflows

---

### `updoc` — Post-sesión completo

1. **META-PLAN (PRO)**
   - LEER `updoc.md`, `version.md`, `doctor.md`, `salud.md` del disco
   - EJECUTAR /updoc Fases A→E+H (PLAN: auditoría INDEX, stale, gaps, cross-ref, tabla consolidada)
   - EJECUTAR /doctor Fases 1→2 (PLAN: diagnóstico estructura, código, tracking, limpieza, deprecación)
   - Calcular bump type (minor/patch) según hallazgos de /updoc
   - ARMAR tabla consolidada con divisiones por comando:

     ```
     ══════════════════════════════════════════
      /CBP updoc — META-PLAN (PRO)
     ══════════════════════════════════════════

      📋 /updoc
      ──────────
      [hallazgos Fase C + E + H]
      
      📦 /version → <minor|patch> BUILD*
      ──────────
      [archivos a modificar, bump type]
      
      🩺 /salud BUILD*
      ──────────
      [indicadores de salud: stale, gaps, estructura, WT, ADRs]
      
      🔬 /doctor
      ──────────
      [issues encontrados, correcciones pendientes]
     
     ══════════════════════════════════════════
      ¿Ejecutar BUILD completo? [Sí/No]
     ══════════════════════════════════════════
     ```

   - PREGUNTAR al usuario: "¿Ejecutar BUILD completo?"
   - SI no confirma: DETENER workflow

2. **BUILD (FLASH)**
   - /updoc Fase F (BUILD): aplicar correcciones de guías/mecánicas/ADRs, actualizar INDEX
   - /salud BUILD*: generar `doc/arch/status-salud.md`, actualizar INDEX
   - /version (BUILD*): Steps 6→8 — CHANGELOG, INDEX, DILIGENCIA, template/adaptar (solo minor/major), commit
   - /doctor Fase 3 (BUILD): aplicar correcciones si hay (solo si /doctor detectó issues en Meta-PLAN)

3. **SUGERIR /doctor**
   - Si /doctor ya se ejecutó en Meta-PLAN con 0 correcciones: workflow terminado — volver a SESSIONWORK
   - Si /doctor detectó correcciones no aplicadas: preguntar "¿Ejecutar /CBP doctor para aplicar?"

---

### `doctor` — Diagnóstico y corrección

1. **META-PLAN (PRO)**
   - LEER `doctor.md`, `version.md`, `salud.md` del disco
   - EJECUTAR /doctor Fases 1→2 (PLAN: diagnóstico estructura, código, tracking, limpieza, deprecación)
   - ARMAR tabla división única (solo /doctor + /salud)
   - PREGUNTAR: "¿Ejecutar correcciones?"
   - SI no confirma: DETENER workflow

2. **BUILD (FLASH)**
   - /doctor Fase 3 (BUILD): crear archivos, sincronizar tracking, deprecar, limpiar
   - /salud BUILD*: generar `doc/arch/status-salud.md`, actualizar INDEX
   - SI hubo correcciones: /version patch BUILD* — Steps 6→8 con bump patch, commit
   - SI no hubo correcciones: workflow terminado — volver a SESSIONWORK

---

### `version` — Versionado standalone (sin /updoc previo)

1. **META-PLAN (PRO)**
   - LEER `version.md` del disco
   - EJECUTAR /version Steps 1→5 (PLAN: detectar versión, calcular bump, confirmación)
   - Safe-path: si INDEX.md ausente o labels stale → preguntar "¿Ejecutar /CBP updoc primero?"
   - ARMAR tabla (solo /version)
   - PREGUNTAR: "¿Ejecutar BUILD?"
   - SI no confirma: DETENER workflow

2. **BUILD (FLASH)**
   - /version Steps 6→8: CHANGELOG, INDEX, DILIGENCIA, template/adaptar (solo minor/major), commit

3. **SUGERIR /doctor**
   - Preguntar: "¿Ejecutar diagnóstico post-versionado?"
   - SI sí: EJECUTAR workflow `doctor` (completo con Meta-PLAN + BUILD)
   - SI no: workflow terminado — volver a SESSIONWORK

---

### `completo` — Ciclo completo con meta-orquestador

El meta-orquestador analiza el working tree y sugiere agentes/skills antes del BUILD documental.

1. **META-PLAN (PRO)**
   - LEER todos los comandos del disco (`updoc.md`, `version.md`, `doctor.md`, `salud.md`)
   - ANALIZAR working tree (git diff, git status, modified files)
   - DETECTAR agentes/skills necesarios según el estado del proyecto:

     | Condición | Agente/Skill sugerido |
     |---|---|
     | git diff >20 líneas de código | `@sdd-reviewer` |
     | Cambios de arquitectura detectados | `@sdd-architect` |
     | Tests en el proyecto | `skill("tdd-strict")` + `@sdd-verify` |
     | ROADMAP.md con SDD items | `skill("sdd-workflow")` |

   - EJECUTAR /updoc Fases A→E+H (PLAN)
   - EJECUTAR /doctor Fases 1→2 (PLAN)
   - ARMAR tabla consolidada con divisiones:
     - Agentes/Skills sugeridos (si aplica)
     - /updoc
     - /salud
     - /version
     - /doctor
   - PREGUNTAR: "¿Ejecutar BUILD completo (incluyendo agentes sugeridos)?"
   - SI no confirma: DETENER workflow

2. **BUILD (FLASH)**
   - Agentes aceptados: ejecutar en orden (reviewer → architect → verify)
   - /updoc Fase F (BUILD): aplicar correcciones documentales
   - /salud BUILD*: generar status-salud.md
   - /version BUILD*: Steps 6→8 — CHANGELOG, INDEX, template, commit
   - /doctor Fase 3 (BUILD): aplicar correcciones si hay

3. **SUGERIR /CBP doctor** si /doctor detectó correcciones no aplicadas

---

## Reglas del orquestador

1. Cada paso ejecuta el comando indicado leyendo su archivo .md desde `~/.config/opencode/commands/`
2. Los pasos marcados **BUILD\*** ejecutan solo escritura — PLAN y confirmación se omiten
3. BUILD\* solo es válido cuando el Meta-PLAN ya cubrió los datos necesarios
4. El orquestador siempre muestra la tabla Meta-PLAN con divisiones por comando — no depende de los comandos individuales
5. `--yes` confirma automáticamente el Meta-PLAN (sin tabla ni pregunta)
6. Si un paso falla (commit no ejecutado, git status sucio): DETENER y reportar error
7. El Meta-PLAN ejecuta SIEMPRE en PRO (análisis profundo); BUILD en FLASH (ejecución rápida)
8. Los agentes/skills sugeridos en `completo` son opcionales — el usuario puede rechazarlos sin abortar el workflow

## Validación

- Todo workflow comienza con Meta-PLAN (PRO), excepto workflow `doctor` que puede ejecutarse sin Meta-PLAN si es invocado desde `updoc` Step 3 (0 correcciones → directo a SESSIONWORK)
- BUILD* solo después de Meta-PLAN
- Los comandos individuales NO contienen su propio "Próximo paso en el circuito"
- /CBP es el único punto de entrada para ejecución multi-comando
- Cada comando puede ejecutarse standalone (sin /CBP) — pero no habrá handoff automático
- `/CBP` sin argumentos equivale a `/CBP completo`

## Anti-patrones

- NO modificar comandos individuales para que hagan handoff — el orquestador maneja el flujo
- NO ejecutar BUILD\* sin Meta-PLAN previo en el mismo workflow
- NO saltar pasos del workflow
- NO ejecutar Meta-PLAN en FLASH — requiere PRO para análisis profundo
- NO ejecutar BUILD en PRO — desperdicio de tokens y latencia
- NO leer "Próximo paso en el circuito" en comandos individuales — esa información está obsoleta

## Archivos que referencian esta mecánica

- `~/.config/opencode/commands/updoc.md`
- `~/.config/opencode/commands/version.md`
- `~/.config/opencode/commands/doctor.md`
- `~/.config/opencode/commands/salud.md`
- `doc/mecanicas/MECANICA-CBP.md`
- `doc/guias/GUIA_DE_BUENAS_PRACTICAS.md` §9
