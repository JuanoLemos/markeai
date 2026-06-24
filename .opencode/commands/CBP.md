INSTRUCCIÓN: EJECUTAR el workflow indicado. NO modificar archivos sin confirmación del usuario. NO mostrar este archivo como output.

# /CBP [full|parcial|commit|completo|updoc|doctor|version] — Orquestador de workflows vinculantes

Ejecuta secuencias multi-comando con encadenamiento controlado por el orquestador.
Cada workflow se divide en dos fases: **Meta-PLAN (razonamiento)** y **BUILD (ejecuci�n)**.

Reemplaza la sección "Próximo paso en el circuito" que existía en los comandos individuales.
El SSOT del encadenamiento es este archivo + `MECANICA-CBP.md`.

## Despacho de entrada (entry dispatch)

Cuando /CBP se invoca, EJECUTAR este algoritmo ANTES de cualquier otra acción:

0. **PRE-FLIGHT: verificar versión Diligencia**
   a. LEER `DILIGENCIA.md` línea 1 → extraer `versión_proyecto` (formato `vX.Y.Z`).
   b. LEER `~/.config/opencode/commands/adaptar.md` → extraer `versión_global` desde la tabla Versión.
   c. Si `DILIGENCIA.md` NO existe:
      ⚠️ "Proyecto no adaptado a Diligencia."
      Preguntar: "¿Ejecutar /adaptar para iniciar adaptación? [sí/no]"
      Si sí: EJECUTAR `/adaptar` Flujo A (proyecto nuevo) → volver al paso 1.
      Si no: continuar con advertencia registrada.
   d. Si `versión_proyecto < versión_global`:
      ⚠️ "Diligencia {versión_global} disponible — proyecto en {versión_proyecto}."
      LEER tabla Migración de `adaptar.md` desde versión_proyecto hasta versión_global.
      Mostrar novedades textuales de las versiones intermedias.
      Preguntar: "¿Actualizar Diligencia antes de continuar? [sí/no/saltar]"
      - sí → EJECUTAR `/adaptar` Flujo C (upgrade) → volver al paso 1.
      - no → continuar con advertencia registrada en contexto.
      - saltar → no preguntar de nuevo en esta sesión.
   e. Si `versión_proyecto == versión_global` → continuar sin interrupción.
   f. DETECTAR comandos globales pendientes de versionar (si DILIGENCIA.md existe):
      - LEER `~/.config/opencode/commands/PENDING.md` → extraer todas las entradas en la tabla
      - Si PENDING.md no existe o está vacío → continuar sin interrupción.
      - Si PENDING.md tiene entradas:
        ⚠️ "Hay [N] cambios globales sin documentar en CHANGELOG."
        Mostrar tabla: Fecha | Comando | Cambio
        Preguntar: "¿Bump versión de Diligencia y documentar cambios? [sí/no]"
        - Si sí → MARCAR en contexto: `necesita_bump = true`. Durante BUILD (cualquier camino), ejecutar:
          a. Bump en adaptar.md tabla Versión (patch)
          b. Agregar entrada en tabla Migración
          c. Actualizar DILIGENCIA.md + CHANGELOG.md + INDEX.md del proyecto
          d. LIMPIAR PENDING.md (vaciar archivo)
          e. Commit sugerido: `chore: upgrade v{anterior} → v{nueva} (cambios globales documentados)`
        - Si no → continuar con advertencia registrada en contexto (no repetir en la misma sesión).

1. **Si hay argumento explícito** (`commit`, `parcial`, `full`, `completo`, `updoc`, `doctor`, `version`):
   → Saltar al workflow correspondiente directamente. Sin detección. Sin preguntar camino.

2. **Si NO hay argumento** (invocación implícita):
   a. DETECTAR cambios de esta sesión:
      - `git diff --stat HEAD` → cambios staged + unstaged
      - `git log --oneline <último chore(release):>..HEAD 2>$null; if ($?) { } else { "" }` → commits desde último release
      - Si ambos están vacíos → "No hay cambios esta sesión." DETENER.
   b. CLASIFICAR:
      - WT: `git diff --stat HEAD` → código (`src/**`) vs doc (`doc/**`, `*.md`)
      - Commits: `git log --oneline <last>..HEAD` → feat/perf = código, docs = doc, resto = dividir por scope
   c. SUMAR WT + commits. Determinar camino según §Adaptación escalativa → Árbol de decisión.
   c. Usar tool `question()` con opciones dinámicas:
      ```
      question({
        questions: [{
          header: "Camino sugerido: <commit|parcial|full>",
          question: "Detecté [N] archivos: [X] docs, [Y] código.",
          options: [
            {label: "commit (Recomendado)", description: "git add + commit + push. Sin doc sync ni versión."},
            {label: "parcial", description: "/updoc + /version patch + push. Sin agentes ni /salud."},
            {label: "full", description: "Meta-PLAN + BUILD + agentes/skills."},
            {label: "abortar", description: "Cancelar sin cambios."}
          ]
        }]
      })
      ```
      Nota: "(Recomendado)" solo en el label del camino sugerido automáticamente.
   d. Si usuario elige cualquier opción menos abortar → EJECUTAR workflow correspondiente.
   e. Si usuario elige abortar → DETENER. Sin cambios.

## Meta-PLAN (razonamiento) vs BUILD (ejecuci�n)

Todo workflow de /CBP sigue esta estructura:

```
META-PLAN (modelo de razonamiento)
  → Ejecuta solo fases de PLAN de cada comando (lectura + auditoría)
  → NO modifica archivos
  → Muestra tabla consolidada con divisiones por comando
  → Pide UNA SOLA confirmación

BUILD (modelo de ejecuci�n)
  → Ejecuta solo fases de BUILD de cada comando (escritura)
  → Modifica archivos según el plan aprobado
  → BUILD*: pasos que omiten PLAN porque los datos se heredan del Meta-PLAN
```

### Reglas del Meta-PLAN

1. El Meta-PLAN ejecuta SIEMPRE en razonamiento, sin importar el modo en que se invocó /CBP
2. BUILD ejecuta SIEMPRE en ejecuci�n, incluso si /CBP se invocó en razonamiento
3. El Meta-PLAN ejecuta PLAN de todos los comandos del workflow
4. BUILD* ejecuta solo escritura — PLAN y confirmación se omiten
5. BUILD* solo es válido cuando el Meta-PLAN ya cubrió los datos necesarios
6. Si el usuario rechaza el Meta-PLAN: workflow detenido, sin cambios

## Adaptación escalativa (camino automático)

/CBP detecta automáticamente el camino óptimo según el working tree del proyecto.
Reemplaza el comportamiento default `completo` con una decisión inteligente.

### Árbol de decisión

| Señal de entrada | Camino | Qué ejecuta |
|---|---|---|
| Solo código fuente modificado, 0 docs tocados | **commit** | `git add -A` + `/commit` + `/pushgh`. Sin doc sync ni versión ni Meta-PLAN. |
| 1-5 docs tocados, sin nuevas guías/mecánicas | **parcial** | `/updoc` Fases A→F + `/version` patch + `/pushgh`. Sin Meta-PLAN profundo, sin agentes, sin /salud, sin /doctor. |
| 5+ docs tocados, nuevas guías/mecánicas, milestones, o working tree sucio de múltiples sesiones | **full** | `/CBP completo` actual (Meta-PLAN + BUILD + agentes/skills). |

### Cómo detecta el camino

```
1. git diff --stat HEAD + git log <último-release>..HEAD → detectar cambios:
   a. Solo código (src/) + 0 docs → "commit path"
   b. 1-5 docs, sin nuevas guías/mecánicas → "parcial path"
   c. 5+ docs, nuevas guías/mecánicas, milestones → "full path"
2. Verificar milestone flag (semver minor/major vs patch)
3. Presentar camino sugerido al usuario:
   "🔍 Detecté [N] archivos modificados ([X] docs, [Y] código).
    ➡️ Camino sugerido: <commit|parcial|full>
    ¿Confirmas o quieres otro camino? [commit/parcial/full/abortar]"
4. Si usuario no especifica → aplicar camino sugerido
```

### Forzar camino explícito

| Comando | Fuerza |
|---|---|
| `/CBP commit` | Camino commit directo, sin preguntar |
| `/CBP parcial` | Camino parcial directo |
| `/CBP full` | Camino full (equivalente a `/CBP completo`) |

### Cuándo usar cada camino

| Escenario | Camino recomendado |
|---|---|
| Sesión de código puro (arreglé bugs, implementé features en src/) | `commit` |
| Sesión de código + toqué 1 doc de pasada | `commit` (el doc se commitca igual) |
| Toqué varios docs, nada de código | `parcial` |
| Cierro milestone/fase (v0.3→v0.4) | `full` |
| Working tree sucio de 3+ sesiones acumuladas | `full` |
| Creé/eliminé guías o mecánicas nuevas | `parcial` o `full` |
| Quiero "ver cómo va el proyecto" | NO USAR /CBP — usar `/estado` o `/doctor` standalone |

## Meta-PLAN paralelo (ejecución en olas)

El Meta-PLAN ejecuta fases **read-only** que pueden lanzarse en paralelo.
Las olas (waves) agrupan fases independientes:

```
OLA 1 (20 fases paralelas — todas independientes)
  /updoc A (INDEX catalog)  |  /updoc B (CHANGELOG ref version)  |  /updoc G-read (git diff)
  /updoc H-D2 (templates)   |  /updoc H-D4 (variables orphans)  |  /updoc H-D5 (template stale)
  /doctor 1a (estructura)   |  /doctor 1b (código)              |  /doctor 1c (gaps doc)
  /doctor 1d (temporales)   |  /doctor 1e (obsoletos)           |  /doctor 1f (backup plan)
  /version V1 (detectar ver)|  /version V4b (salud existente)   |  /version V4c (explica scope)
  /version V4d (template)    |  /version V4e (§8 refs)           |  /version V4f (variables)
  /CBP AGT (agentes/skills)

OLA 2 (después de Ola 1 — dependen de sus resultados)
  /updoc C (stale detection) → necesita A+B
  /updoc H-D1 (guías huérfanas) → necesita A/G
  /updoc H-D3 (explica scope) → necesita A

OLA 3 (después de Ola 2 — consolidación)
  /updoc D → E (gaps → plan)
  /doctor Fase 2 (confirmación)
  /version V2→V5 (calcular, pre-flight)

OLA 4 (después de Ola 3 — confirmación final)
  Tabla consolidada
  Pregunta al usuario
```

Todas las fases en Ola 1 y Ola 2 se lanzan simultáneamente usando
el tool `task` en paralelo. Cada tarea recibe un `task_id` único
y produce su diagnóstico de vuelta al orquestador.

## Argumentos

/CBP [full|parcial|commit|completo|updoc|doctor|version] [--yes]

- *(sin argumento)*: **detección automática** del camino óptimo (commit / parcial / full) según el working tree
- `commit`: Solo commit + push. Sin doc sync, sin versión, sin Meta-PLAN.
- `parcial`: /updoc Fases A→F + /version patch + /pushgh. Sin /salud, sin /doctor, sin agentes.
- `full`: Ciclo completo con Meta-PLAN paralelo + BUILD (equivale a `completo`).
- `completo`: Alias de `full` (legacy, compatibilidad).
- `updoc`: Post-sesión completo — Meta-PLAN → BUILD (/updoc → /salud → /version → /pushgh → sugiere /doctor)
- `doctor`: Diagnóstico integral — Meta-PLAN → BUILD (/doctor → /salud → /version si correcciones → /pushgh)
- `version`: Versionado standalone — Meta-PLAN → BUILD (/version → /pushgh → sugiere /doctor)
- `--yes`: omitir confirmación del Meta-PLAN

> Sin argumento, `/CBP` detecta el camino óptimo. Los sub-comandos (`full`, `parcial`, `commit`, `updoc`, `doctor`, `version`) fuerzan un camino específico.

## Workflows

---

### `updoc` — Post-sesión completo

1. **META-PLAN (razonamiento) — Olas paralelas**

   OLA 1 — lanzar simultáneamente (20 fases):
   - /updoc Fase A: leer INDEX.md y catalogar docs
   - /updoc Fase B: detectar versión de referencia desde CHANGELOG
   - /updoc Fase G-read: git log + git diff (operaciones git)
   - /updoc H-D2: templates sin consumidor
   - /updoc H-D4: variables huérfanas en comandos
   - /updoc H-D5: DILIGENCIA.md vs template staleness
   - /doctor Fase 1a: estructura (AGENTS, RM, CHECKLIST, etc.)
   - /doctor Fase 1b: código (syntax, path consistency)
   - /doctor Fase 1c: gaps documentales (RM↔CHECKLIST, stale items)
   - /doctor Fase 1d: temporales (archivos *.{log,tmp,bak})
   - /doctor Fase 1e: obsoletos (archivos no core)
   - /doctor Fase 1f: backup preventivo ($BACKUP_KEEP, pruning)
   -/version V1: detectar versión actual
   - /version V4b: leer status-salud.md existente
   - /version V4c: scope de /explica
   - /version V4d: template sync
   - /version V4e: cross-refs §8
   - /version V4f: variables resolubles
   - /CBP AGT: detectar agentes/skills según working tree
   (recopilar resultados de cada fase)

   OLA 2 — después de Ola 1:
   - /updoc Fase C: stale detection (needs A+B)
   - /updoc H-D1: guías huérfanas (needs A/G)
   - /updoc H-D3: scope /explica incompleto (needs A)

   OLA 3 — después de Ola 2:
   - /updoc Fase D → E: gaps → plan (needs C)
   - /doctor Fase 2: tabla de confirmación (needs 1a-1f)
   - /version V2→V5: calcular bump + pre-flight (needs V1 + V4b-f)

   OLA 4 — después de Ola 3:
   - ARMAR tabla consolidada con divisiones por comando
   - Calcular bump type (minor/patch) según hallazgos de /updoc:

     ```
     ══════════════════════════════════════════
      /CBP updoc — META-PLAN (razonamiento)
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

2. **BUILD (ejecuci�n)**
   ⚠️ BUILD = aplicar cambios, NO commitear. Solo /commit, /CBP y /version ejecutan git commit.
      Al terminar: reportar "✅ BUILD completo. Ejecutar /CBP para commitear."
   - /updoc Fase F (BUILD): aplicar correcciones de guías/mecánicas/ADRs, actualizar INDEX
   - /salud BUILD*: generar `doc/arch/status-salud.md`, actualizar INDEX
   - /version (BUILD*): Steps 6→12 — CHANGELOG + commit + tag
   - /pushgh BUILD*: git push al remoto configurado en $REPO (solo si $REPO definido)
    - /doctor Fase 3 (BUILD): backup pre-corrección + aplicar correcciones si hay (solo si /doctor detectó issues en Meta-PLAN)

3. **SUGERIR /doctor**
   - Si /doctor ya se ejecutó en Meta-PLAN con 0 correcciones: workflow terminado — volver a SESSIONWORK
   - Si /doctor detectó correcciones no aplicadas: preguntar "¿Ejecutar /CBP doctor para aplicar?"

---

### `doctor` — Diagnóstico y corrección

1. **META-PLAN (razonamiento)**
   - LEER `doctor.md`, `version.md`, `salud.md` del disco
   - EJECUTAR /doctor Fases 1→2 (PLAN: diagnóstico estructura, código, tracking, limpieza, deprecación)
   - ARMAR tabla división única (solo /doctor + /salud)
   - PREGUNTAR: "¿Ejecutar correcciones?"
   - SI no confirma: DETENER workflow

2. **BUILD (ejecuci�n)**
   ⚠️ BUILD = aplicar cambios, NO commitear. Solo /commit, /CBP y /version ejecutan git commit.
   - /doctor Fase 3 (BUILD): backup pre-corrección + crear archivos, sincronizar tracking, deprecar, limpiar
   - /salud BUILD*: generar `doc/arch/status-salud.md`, actualizar INDEX
   - SI hubo correcciones: /version patch BUILD* — Steps 6→12 (CHANGELOG + commit + tag) → /pushgh BUILD*
   - SI no hubo correcciones: workflow terminado — volver a SESSIONWORK

---

### `version` — Versionado standalone (sin /updoc previo)

1. **META-PLAN (razonamiento)**
   - LEER `version.md` del disco
   - EJECUTAR /version Steps 1→5 (PLAN: detectar versión, calcular bump, confirmación)
    - Safe-path: si INDEX.md ausente o labels stale → preguntar "¿Ejecutar /CBP updoc primero?"
      Si sí → ABORTAR este workflow. EJECUTAR `/CBP updoc` completo. Al terminar, preguntar "¿Reanudar /CBP version? [sí/no]"
    - ARMAR tabla (solo /version)
    - MOSTRAR CHANGELOG auto-generado + resultado pre-flight
    - PREGUNTAR UNA SOLA VEZ: "¿Versionar con estos cambios? [sí/no]"
   - SI no confirma: DETENER workflow

2. **BUILD (ejecuci�n)**
   - /version BUILD* Steps 6→12 (CHANGELOG + commit + tag. No preguntar — ya confirmado en Meta-PLAN)
   - /pushgh BUILD*: git push al remoto configurado en $REPO (solo si $REPO definido)

3. **SUGERIR /doctor**
   - Preguntar: "¿Ejecutar diagnóstico post-versionado?"
   - SI sí: EJECUTAR workflow `doctor` (completo con Meta-PLAN + BUILD)
   - SI no: workflow terminado — volver a SESSIONWORK

---

### `commit` — Commit rápido (sin doc sync, sin versión)

Para sesiones de código puro donde ningún documento cambió.

1. **EJECUCIÓN DIRECTA** (sin Meta-PLAN)
   - EJECUTAR `/commit` (el comando authenticado valida Conventional Commits y muestra diff)
   - Si `/commit` falla: DETENER y mostrar error. NO continuar.
   - Si no hay cambios: "No hay cambios para commitear" — DETENER

2. **PUSH**
   - Si $REPO definido: `git push origin $(git branch --show-current)` (push directo post-commit, sin BUILD*)
   - Si no: "Commiteado localmente. Ejecutá `git push <remote> <branch>` manualmente."

---

### `parcial` — Sync documental ligero (sin Meta-PLAN completo)

Para sesiones donde se tocaron 1-5 docs sin nuevas guías/mecánicas.

1. **META-PLAN (ligero)**
   - /updoc Fases A→E+H (PLAN: solo auditoría — INDEX, stale, gaps, cross-refs. NO modificar archivos.)
   - /version Steps 1→5 (PLAN: detectar versión, colectar commits, pre-flight 6 checks)
   - Calcular bump: patch (por definición del workflow ligero)
   - ARMAR tabla consolidada (solo /updoc + /version)
   - PREGUNTAR UNA SOLA VEZ: "¿Ejecutar BUILD parcial? [sí/no]"
   - SI no confirma: DETENER workflow

2. **BUILD (ejecución)**
   - /updoc Fase F (BUILD: aplicar correcciones de la auditoría PLAN)
   - /version BUILD* Steps 6→12 (CHANGELOG + commit + tag + push)
   - /pushgh BUILD* git push

3. **NO SUGERIR /doctor**
   - Sin /salud, sin /doctor, sin agentes — el camino parcial es deliberadamente liviano

---

### `full` / `completo` — Ciclo completo con meta-orquestador

El meta-orquestador analiza el working tree y sugiere agentes/skills antes del BUILD documental.

1. **META-PLAN (razonamiento) — Olas paralelas**

   OLA 1 — lanzar 4 workers paralelos vía tool `task("explore", prompt)`

   Worker 1 — docs:
   ```
   task("explore", "Analizar documentación del proyecto. NO modificar archivos.
   1. LEER INDEX.md → catalogar archivos con versiones y fechas.
   2. LEER CHANGELOG.md → extraer versión semver de referencia.
    3. EJECUTAR git diff --stat --name-only <last-version> (si vacío: git log --oneline --stat <last-version>..HEAD) → listar modificados desde último release.
    4. LEER guías en doc/guias/ → ¿hay guías listadas en INDEX que no existen en disco?
   5. LEER AGENTS.md → extraer variables; buscar en INDEX referencias a esas rutas.
   6. LEER cada guía → ¿están actualizadas vs _template.md?
   Devolver findings como tabla estructurada con cada punto.")
   ```

   Worker 2 — diag:
   ```
   task("explore", "Diagnosticar el proyecto. NO modificar archivos.
   1. Estructura: ¿existen directorios estándar (doc/, doc/guias/, doc/mecanicas/, doc/arch/)?
   2. Código: ¿hay issues en src/ (simetría, imports rotos)?
   3. Gaps doc: archivos en INDEX vs archivos reales en disco.
   4. Temporales: ¿hay .tmp, node_modules/, __pycache__, *.log?
   5. Obsoletos: ¿archivos marcados deprecated en doc/arch/?
   6. Backups: LEER doc/arch/backups.md → estado y pruning.
   Devolver findings como tabla estructurada con cada punto.")
   ```

   Worker 3 — ver:
   ```
   task("explore", "Pre-flight de versionado. NO modificar archivos.
   1. LEER CHANGELOG.md → detectar versión actual (etiqueta [Unreleased] o último release).
   2. ¿Existe doc/arch/status-salud.md (salud ya generada)?
    3. EJECUTAR git diff --stat <last-version> (si vacío: git log --oneline --stat <last-version>..HEAD) → explicar bump según archivos tocados desde último release.
    4. LEER templates en $TEMPLATE_DIR → ¿existen? ¿están sincronizados?
   5. LEER doc/guias/GUIA_DE_COMANDOS.md §8 → referencias cruzadas de guías.
    6. LEER AGENTS.md → verificar variables ($ROADMAP, $CHECKLIST, etc).
    7. LEER DILIGENCIA.md línea 1 → extraer versión_proyecto. LEER adaptar.md → versión_global.
       Si proyecto < global: reportar staleness + novedades de las versiones intermedias.
    Devolver findings como tabla estructurada con cada punto.")
   ```

   Worker 4 — agt:
   ```
   task("explore", "Sugerir agentes/skills. NO modificar archivos.
    1. EJECUTAR git diff --stat <last-version> (si vacío: git log --oneline --stat <last-version>..HEAD) → contar líneas de código modificadas desde último release.
    2. LEER ROADMAP.md → ¿hay items SDD (Spec-Driven Development)?
   3. ¿Existen tests (tests/, __tests__, *.test.*)?
   4. ¿Se modificaron ADRs o archivos en doc/arch/ (cambios de arquitectura)?
   Devolver tabla:
   | Condición | Agente/Skill | Recomendado | Razón |
   ...")
   ```

   OLA 2 — SINTETIZAR resultados de OLA 1 (en orden, secuencial):
   - Stale: usar INDEX cat (W1) + ref version (W1) → docs desactualizados
   - Huérfanas: usar INDEX cat (W1) + git diff (W1) → guías creadas sin INDEX entry
   - Scope bump: usar pre-flight (W3) + git diff (W1) → confirmar bump type

   OLA 3 — CONSOLIDAR con resultados de OLA 1-2:
   - Gaps → plan de corrección (W1 + W2 findings)
   - Confirmación de diagnóstico (W2 findings)
   - Calcular bump y pre-flight final (W3 findings)

   OLA 4 — ARMAR tabla consolidada:
   - Agentes/Skills sugeridos (W4)
   - /updoc findings (W1+W2)
   - /salud: ¿ejecutar BUILD*?
    - /version bump y pre-flight (W3)
    - /doctor correcciones (W2)
    - Diligencia version: ✅ al día o ⚠️ stale (W3)
    - PREGUNTAR: "¿Ejecutar BUILD completo (incluyendo agentes sugeridos)?"
   - SI no confirma: DETENER workflow

2. **BUILD (ejecuci�n)**
   ⚠️ BUILD = aplicar cambios, NO commitear. Solo /commit, /CBP y /version ejecutan git commit.
   - Agentes aceptados: ejecutar en orden (reviewer → architect → verify)
   - /updoc Fase F (BUILD): aplicar correcciones documentales
   - /salud BUILD*: generar status-salud.md
   - /version BUILD*: Steps 6→12 (CHANGELOG + commit + tag)
   - /pushgh BUILD*: git push al remoto configurado en $REPO (solo si $REPO definido)
    - /doctor Fase 3 (BUILD): backup pre-corrección + aplicar correcciones si hay

3. **SUGERIR /CBP doctor** si /doctor detectó correcciones no aplicadas

---

## Reglas del orquestador

1. Cada paso ejecuta el comando indicado leyendo su archivo .md desde `~/.config/opencode/commands/`
2. Los pasos marcados **BUILD\*** ejecutan solo escritura — PLAN y confirmación se omiten
3. BUILD\* solo es válido cuando el Meta-PLAN ya cubrió los datos necesarios
4. El orquestador siempre muestra la tabla Meta-PLAN con divisiones por comando — no depende de los comandos individuales
5. `--yes` confirma automáticamente el Meta-PLAN (sin tabla ni pregunta)
6. Si un paso falla (commit no ejecutado, git status sucio): DETENER y reportar error
7. El Meta-PLAN ejecuta SIEMPRE en razonamiento (análisis profundo); BUILD en ejecución (ejecución rápida)
8. Los agentes/skills sugeridos en `full`/`completo` son opcionales — el usuario puede rechazarlos sin abortar el workflow
9. Las olas (Waves) del Meta-PLAN ejecutan fases read-only en paralelo usando el tool `task`
10. Fases en Ola 1/2 NO tienen dependencias entre sí — se lanzan simultáneamente
11. Fases en Ola 3/4 son secuenciales (dependen de resultados de olas anteriores)
12. Si alguna fase paralela falla, el orquestador recolecta todos los errores antes de reportarlos
13. El camino adaptativo se determina ANTES de entrar a Meta-PLAN, basado en `git diff --stat HEAD` + `git log <último-release>..HEAD` (cubre cambios staged, unstaged Y commiteados)
14. `/CBP` sin argumentos aplica el camino adaptativo; con argumento fuerza el camino indicado
15. Antes de cualquier workflow, verificar versión Diligencia del proyecto. Si stale → advertir y sugerir `/adaptar`. El usuario decide si actualizar. Si se rechaza, la advertencia queda registrada en el contexto de la sesión.
16. Si se edita un comando global (CBP.md, adaptar.md, etc.) que introduce cambios metodológicos, se DEBE inmediatamente: bump versión en adaptar.md, agregar entrada en tabla Migración, actualizar DILIGENCIA.md y CHANGELOG.md del proyecto Diligencia, y commitear para que los proyectos lo detecten vía pre-flight.
17. Solo `/commit`, `/CBP` y `/version` pueden ejecutar git commit. Ningún otro comando (incluyendo BUILD de /plan, /adaptar, /updoc standalone) debe commitear. Los cambios se acumulan en el working tree y el usuario decide cuándo commitear usando uno de los tres comandos autorizados.
18. Si un comando en BUILD encuentra un estado ambiguo (más de una acción posible, no hay un camino obvio), DEBE pausar, presentar opciones de forma simple y directa (con impacto estimado de cada una), y esperar confirmación del usuario antes de ejecutar. No se asume nada.
19. En cualquier proyecto que NO sea Diligencia, el agente DEBE pausar antes de modificar estado del repositorio (git add, commit, push, tag). Debe mostrar los cambios preparados y preguntar explícitamente: "¿Ejecutar [acción] en [nombre del proyecto]? [sí/no]". Diligencia es la única excepción: como proyecto auto-referencial, puede recibir acciones automáticas dentro del flujo acordado por el usuario.

## Validación

- Todo workflow comienza con Meta-PLAN (razonamiento), excepto workflow `doctor` que puede ejecutarse sin Meta-PLAN si es invocado desde `updoc` Step 3 (0 correcciones → directo a SESSIONWORK)
- BUILD* solo después de Meta-PLAN
- Los comandos individuales NO contienen su propio "Próximo paso en el circuito"
- /CBP es el único punto de entrada para ejecución multi-comando
- Cada comando puede ejecutarse standalone (sin /CBP) — pero no habrá handoff automático
- `/CBP` sin argumentos aplica detección adaptativa (commit/parcial/full)
- `/CBP` con argumento fuerza el camino indicado

## Anti-patrones

- NO modificar comandos individuales para que hagan handoff — el orquestador maneja el flujo
- NO ejecutar BUILD\* sin Meta-PLAN previo en el mismo workflow
- NO saltar pasos del workflow
- NO ejecutar Meta-PLAN en ejecuci�n — requiere razonamiento para análisis profundo
- NO ejecutar BUILD en razonamiento — desperdicio de tokens y latencia
- NO leer "Próximo paso en el circuito" en comandos individuales — esa información está obsoleta

## Archivos que referencian esta mecánica

- `~/.config/opencode/commands/updoc.md`
- `~/.config/opencode/commands/version.md`
- `~/.config/opencode/commands/doctor.md`
- `~/.config/opencode/commands/salud.md`
- `doc/mecanicas/MECANICA-CBP.md`
- `doc/guias/GUIA_DE_BUENAS_PRACTICAS.md` §9
