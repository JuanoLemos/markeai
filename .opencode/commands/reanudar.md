INSTRUCCIÓN: EJECUTAR continuar sesión interrumpida. NO modificar archivos sin confirmación. NO mostrar este archivo como output.

# /reanudar — Continuar sesión interrumpida

Recupera contexto tras interrupción brusca (pérdida de conexión, brutalstop, timeout de IA).
Detecta automáticamente si la sesión estaba en Plan (discusión/diseño) o Build (edición/implementación)
y permite continuar desde donde se cortó.

## Argumentos
/reanudar [plan|build]

- Sin argumentos: autodetectar modo desde el working tree y SDD artifacts, preguntar confirmación
- `plan`: forzar modo Plan (read-only, diseño, especificación)
- `build`: forzar modo Build (edición, implementación)

## Qué hace

### Paso 1 — Estado del working tree

1. `git status --porcelain` → listar archivos sucios
2. `git diff --stat` → resumen de cambios (+N -M líneas por archivo)
3. `git log --oneline -3` → últimos 3 commits
4. Si NO hay git: preguntar al usuario qué se estaba haciendo

### Paso 2 — Detectar modo

1. Si el usuario pasó `plan` o `build`: usar ese modo, saltar autodetección
2. Si no:
   - DETECTAR SDD artifacts: existe `.opencode/spec.md` o `.opencode/tasks.md` o `.opencode/design.md`?
   - Si SDD artifacts existen Y dirty files > 0 → **BUILD** (flujo SDD en ejecución)
   - Si SDD artifacts existen Y dirty files = 0 → **PLAN** (diseño interrumpido, no empezó build)
   - Si NO hay SDD artifacts Y dirty files > 0 → **BUILD** (edición directa)
   - Si NO hay SDD artifacts Y dirty files = 0 → **PLAN** (discusión, nada empezado)
3. PREGUNTAR confirmación: "Modo detectado: <Plan|Build>. ¿Correcto?"
   - Si no: preguntar "¿Plan o build?" y continuar con el modo indicado

### Paso 3 — Contexto de trabajo

1. LEER RM "Ahora" → items en progreso (si existe)
2. LEER CHANGELOG `[Unreleased]` → cambios trackeados para la versión en curso (si existe)
3. Si SDD artifacts existen:
   - LEER `.opencode/spec.md` → extraer objetivo
   - LEER `.opencode/tasks.md` → listar tareas completadas/pendientes
   - LEER `.opencode/design.md` → extraer decisiones tomadas
   - SINTETIZAR: "Flujo SDD en curso. Fase: <architect|implement|verify>. Tareas: N completadas / M pendientes."
4. Si hay archivos dirty:
   - LISTAR con diff stat: Archivo | +Líneas | -Líneas
   - Si son cambios grandes (>30 líneas total): sugerir que es buena idea commitear pronto

### Paso 4 — Continuar

1. ARMAR resumen ejecutivo:
   ```
   Modo: <Plan|Build>
   Último commit: <hash> — <mensaje>
   Dirty: N archivos (+X -Y líneas)
   RM en progreso: N items
   SDD: <detectado|no>
   ```

2. Si modo **PLAN**:
   - "Parece que estabas en modo Plan. ¿Sobre qué tema estabas discutiendo o diseñando?"
   - Si SDD artifacts: "¿Continuar flujo SDD en fase <architect>?"
   - Esperar respuesta del usuario → continuar planificación

3. Si modo **BUILD**:
   - "Archivos pendientes: A, B, C (+N -M líneas)"
   - "¿Continuar editando?"
   - Si sí:
     - Si SDD artifacts: "¿Continuar flujo SDD en fase <implement|verify>?"
     - CARGAR contexto de archivos dirty (leer + diff) y continuar edición
     - Si SDD: retomar desde la última tarea pendiente en tasks.md
   - Si no: preguntar al usuario qué hacer

## Validación

- git status y diff ejecutados correctamente
- Modo detectado (Plan/Build) antes de continuar — confirmado por usuario si hay ambigüedad
- RM "Ahora" y CHANGELOG [Unreleased] leídos si existen (tolerante a ausencia)
- SDD artifacts detectados si existen
- Archivos dirty listados con diff stat
- No se modificó ningún archivo sin confirmación explícita

## Anti-patrones

- NO modificar archivos sin confirmación del usuario
- NO asumir modo sin preguntar si hay ambigüedad (dirty files + no SDD + cambios mínimos)
- NO hacer commit automático
- NO depender de sesion.md ni archivos de journal
- NO abortar si RM, CHANGELOG o SDD artifacts no existen — continuar con lo que hay
- NO mezclar plan y build — si el usuario dice plan, no empezar a editar

## Archivos que lee

- CHANGELOG.md
- ROADMAP.md
- CHECKLIST.md
- .opencode/spec.md (si existe)
- .opencode/tasks.md (si existe)
- .opencode/design.md (si existe)
- Archivos dirty (vía git diff para contexto)
