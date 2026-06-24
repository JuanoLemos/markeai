INSTRUCCIÓN: EJECUTAR las 3 fases de abajo sobre el proyecto actual. NO modificar archivos sin confirmación del usuario. NO mostrar este archivo como output.

# /doctor — Cuidado integral del proyecto

Diagnóstico y corrección de estructura, código, tracking, limpieza y deprecación en un solo flujo de 3 fases. Orquesta los comandos de cuidado sin reemplazarlos.

---

## Fase 1 — Diagnóstico (solo lectura, no modificar archivos)

### 1a — Estructura (diligencia-check A-B)
LEER AGENTS.md, ROADMAP.md, CHECKLIST.md, CHANGELOG.md, DILIGENCIA.md, `.markdownlint.json`, `.opencode/HARNESS.md` AHORA
VERIFICAR:
- Archivos core: ROADMAP.md, CHECKLIST.md, CHANGELOG.md, AGENTS.md, DILIGENCIA.md, `.markdownlint.json`
- Directorios: `doc/arch/`, `doc/guias/` (plural forzado), `.opencode/commands/`
- `$BUGS` → `doc/arch/bugs.md` si existe en AGENTS.md
- `$INCIDENTS` → `doc/arch/incidentes.md` si existe en AGENTS.md
- Cada `$VARIABLE` en AGENTS.md resuelve a archivo o directorio existente
- Variables core presentes: `$ROADMAP`, `$CHECKLIST`, `$CHANGELOG`, `$GUIAS`, `$COMMANDS_DIR`

### 1b — Código (health)
DETECTAR stack desde `.opencode/HARNESS.md` (campo Stack) o AGENTS.md (`$STACK` o `$HARNESS`)
Si stack == JS/TS:
- LEER archivo(s) JS/TS principal(es) del proyecto
- VERIFICAR paréntesis balanceados
- VERIFICAR consistencia rutas backend ↔ frontend
- EJECUTAR `node --check` sobre archivos JS/TS críticos
Si stack ≠ JS/TS: reportar "⚠️ /health no aplica (stack no JS)" y CONTINUAR

### 1c — Gaps documentales (updoc Fase C)
LEER RM, CHECKLIST, ADRs (`doc/arch/*.md`), guías (`doc/guias/*.md`), mecánicas (`doc/mecanicas/*.md`) AHORA
DETECTAR:
- Items DONE en RM que faltan en CHECKLIST → necesitan tilde
- Items en RM "Ahora" con 🟡/✅ que ya están en RM "Completado" → stale, mover
- ADRs nuevos sin registrar en AGENTS.md o CHECKLIST
- Guías/mecánicas nuevas sin registrar en AGENTS.md
- Variables en AGENTS.md que apuntan a archivos que no existen en disco
- DILIGENCIA.md sin versión o desactualizada vs /adaptar

### 1d — Temporales (limpiar)
BUSCAR patrones: `*.log`, `*.tmp`, `*.bak.*`, `temp/`, `node_modules/.cache/`, `query`, `start`, `line*.txt`, `check_*.js`, `chk.js`
Solo LISTAR — no eliminar todavía.

### 1e — Obsoletos (deprecar)
BUSCAR en raíz archivos que NO son core (no ROADMAP, CHECKLIST, CHANGELOG, AGENTS, DILIGENCIA, `.markdownlintjson`)
BUSCAR en `.opencode/commands/` comandos existentes pero NO listados en AGENTS.md
Listar hallazgos con ruta y tipo.

### 1f — Backup preventivo (diagnóstico, solo lectura)
LEER $BACKUP_KEEP de AGENTS.md (default: 5)
VERIFICAR git disponible (`git --version`)
Si git disponible:
  - EJECUTAR `git log --oneline -1` para commit actual
Si no hay git: commit = "sin git"
LEER versión desde DILIGENCIA.md (línea 1: `# Diligencia vX.Y.Z`)
CONTAR backups existentes en $BACKUPS (número de filas en la tabla)
DETECTAR qué workflow invocó al doctor (/CBP doctor, /CBP completo, /CBP updoc, standalone /doctor)
LISTAR archivos críticos que serían respaldados:
  - Core: AGENTS.md, ROADMAP.md, CHECKLIST.md, CHANGELOG.md, DILIGENCIA.md, `.markdownlint.json`
  - Guías: `doc/guias/*.md`
  - Mecánicas: `doc/mecanicas/*.md`
  - ADRs: `doc/arch/*.md`
  - Comandos: `.opencode/commands/*.md`
CALCULAR: "Se creará backup #<N+1> en `.old/doctor-backups/`. Pruning: se conservan últimos $BACKUP_KEEP backups."
INCLUIR en tabla consolidada de Fase 2.

---

## Fase 2 — Confirmación

ENTREGAR tabla consolidada:

| Categoría | Hallazgos | Impacto | Acción propuesta |
|---|---|---|---|
| Estructura | N ❌ estructura, N ❌ variables | Alto si estructura rota | Crear directorios/archivos, corregir variables |
| Código | N ❌ sintaxis/paréntesis/rutas | Medio a alto | Registrar bugs en $BUGS |
| Tracking | N gaps RM↔CHECKLIST, ADRs, guías | Bajo a medio | Sincronizar RM/CHECKLIST/AGENTS.md |
| Limpieza | N temporales | Bajo | /limpiar: eliminar temporales |
| Deprecación | N obsoletos | Bajo | /deprecar: mover a .old/ |

PREGUNTAR: "¿Ejecutar correcciones? (s/n)"

Si responde "s" o "si": ejecutar Backup, luego Fase 3.
Si responde "n" o "no": ENTREGAR "Sin correcciones aplicadas" y TERMINAR.

---

## Backup pre-corrección (solo si Fase 2 confirma — antes de Fase 3)

Ejecutar backup de archivos críticos antes de cualquier modificación.

1. LEER $BACKUP_KEEP de AGENTS.md (default: 5)
2. OBTENER commit actual: `git log --oneline -1` (si git disponible; si no: "sin-git")
3. LEER versión desde DILIGENCIA.md (línea 1)
4. DETECTAR workflow: /CBP doctor, /CBP completo, /CBP updoc, o standalone /doctor
5. CALCULAR número de backup: contar filas de tabla en $BACKUPS + 1
6. CREAR directorio: `.old/doctor-backups/backup-<N>-<YYYYMMDD-HHMM>/`
7. COPIAR archivos críticos al directorio de backup:
   - AGENTS.md, ROADMAP.md, CHECKLIST.md, CHANGELOG.md, DILIGENCIA.md, `.markdownlint.json`, `.opencode/HARNESS.md`
   - `doc/guias/*.md`, `doc/mecanicas/*.md`, `doc/arch/*.md`
   - `.opencode/commands/*.md`
8. AGREGAR entrada en $BACKUPS:
   ```
   | <N> | <YYYY-MM-DD HH:MM> | <commit> | <version> | <workflow> | <cantidad archivos> archivos |
   ```
9. PRUNING: si total backups en `.old/doctor-backups/` > $BACKUP_KEEP:
   - IDENTIFICAR los backups más antiguos (por número o timestamp en nombre de directorio)
   - ELIMINAR directorios de backup excedentes (los N más antiguos que sobran)
   - ELIMINAR filas correspondientes del log en $BACKUPS
   - REPORTAR: "🗑️ Pruning: eliminados <X> backups antiguos (se conservan últimos $BACKUP_KEEP)"
10. REPORTAR: "✅ Backup #<N> creado: `.old/doctor-backups/backup-<N>-<timestamp>/` (<cantidad> archivos)"

---

## Fase 3 — Correcciones (solo si el usuario confirma)

### 3a — Estructura
- Directorios faltantes (`doc/arch/`, `doc/guias/`, `.opencode/commands/`): CREAR
- Archivos core faltantes: CREAR desde `~/.config/opencode/templates/doc-base/<nombre>` si existe template
- Si `$BUGS` está definido pero no existe `doc/arch/bugs.md`: CREAR desde template `bugs.md`
- Si `$INCIDENTS` está definido pero no existe `doc/arch/incidentes.md`: CREAR desde template `incidentes.md`
- Variables huérfanas en AGENTS.md: NOTIFICAR y PREGUNTAR "¿Eliminar variable <$VAR>?" antes de tocar

### 3b — Código
Por cada ❌ concreto con archivo:línea exacta:
- Si el error es reproducible y tiene archivo definido: REGISTRAR bug en `$BUGS` (formato: ID auto B-NN, severidad P2, descripción "<archivo>:<línea> — <error>"), AGREGAR entrada a $CHECKLIST
- Si el error es ⚠️ o borroso: SALTAR (no es bug confirmado)

### 3c — Tracking
Aplicar correcciones de gaps documentales:
- Items DONE en RM que faltan en CHECKLIST → AGREGAR a CHECKLIST como `[x]`
- Items stale en RM "Ahora" (ya en "Completado") → ELIMINAR de "Ahora"
- ADRs/guías/mecánicas nuevas no registradas → AGREGAR a AGENTS.md

### 3d — Limpieza
Si hay temporales listados:
- MOSTRAR lista al usuario
- PREGUNTAR "¿Eliminar archivos temporales? (s/n)"
- Si confirma: ELIMINAR cada archivo, luego `git add -A`

### 3e — Deprecación
Para cada candidato obsoleto:
- PREGUNTAR "¿Deprecar <ruta>? (s/n)"
- Si confirma: MOVER a `.old/<ruta>` (crear `.old/` si no existe), AGREGAR tabla "Deprecados" en AGENTS.md
- SOLO para archivos, no para directorios (sugerir mover manual para directorios)

### 3f — Post-corrección
- AGREGAR entrada en CHANGELOG.md en sección "Changed" o nueva entrada no versionada: "- `/doctor`: <N> correcciones aplicadas"
- Si hubo cambios en AGENTS.md o estructura: SUGERIR commit message `chore: /doctor — <N> correcciones en estructura, código, tracking`
- AUTOCIERRE: Si `/doctor` está como `🔴 Pendiente` en RM "Next" → actualizar a `✅ Hecho`. Si está `[ ]` en CHECKLIST → marcar `[x]`.
- Workflow terminado. Si hay cambios documentales en disco: ejecutar `/CBP updoc` para sync, o `/CBP version` para versionar. Si no hubo correcciones: volver a SESSIONWORK.

---

## Formato de salida

**🏥 /doctor — Cuidado integral del proyecto**
**🔍 Fase 1 — Diagnóstico:** tabla Categoría | Hallazgos | Estado (incluye 1f Backup)
**✋ Fase 2 — Confirmación:** "¿Ejecutar correcciones? (s/n)"
**💾 Backup pre-corrección:** backup #N creado en `.old/doctor-backups/`, pruning aplicado si > $BACKUP_KEEP
**🔧 Fase 3 — Correcciones aplicadas:** tabla Archivo | Cambio | Estado
**Resumen:**
- Si hubo correcciones → `✅ Alta médica — N correcciones aplicadas. Backup #N guardado.`
- Si no hubo correcciones → `👀 Sin novedades — proyecto sano`

---

## Validación
- Las 6 sub-verificaciones (1a-1f) están presentes en el diagnóstico
- /health no aborta /doctor si stack ≠ JS (reporta ⚠️ y continúa)
- No se modifican archivos sin confirmación en Fase 2
- El backup se ejecuta después de la confirmación y antes de cualquier corrección
- Pruning respeta $BACKUP_KEEP (default 5) — nunca elimina más backups de los necesarios
- Cada ❌ en Fase 1 tiene contraparte en Fase 3
- Si Fase 2 responde "no": no se ejecuta backup ni Fase 3
- Autocierre aplicado: /doctor marcado como ✅/[x] en RM/CHECKLIST si estaba pendiente


## Archivos que lee
- AGENTS.md, ROADMAP.md, CHECKLIST.md, CHANGELOG.md, DILIGENCIA.md
- `.markdownlint.json`, `.opencode/HARNESS.md`
- `doc/arch/*.md` (incluye $BACKUPS), `doc/guias/*.md`, `doc/mecanicas/*.md`
- `.opencode/commands/*.md`
- Archivos JS/TS del proyecto (solo si stack == JS)

## Archivos que modifica (solo si usuario confirma)
- `$BACKUPS` (nueva entrada de backup)
- `.old/doctor-backups/` (directorio de backups + pruning)
- `$BUGS` (nuevos bugs)
- `$INCIDENTS` (nuevos incidentes, si aplica)
- `$CHECKLIST` (nuevos items tildados)
- `$RM` (mover items de Ahora a Completado)
- `AGENTS.md` (nuevos registros de ADRs/guías, tabla Deprecados)
- `CHANGELOG.md` (entrada de correcciones)
- Archivos temporales eliminados
- Archivos movidos a `.old/`

## Anti-patrones
- NO abortar /doctor si una sub-verificación falla o no aplica — CONTINUAR con la siguiente
- NO modificar archivos sin confirmación explícita del usuario en Fase 2
- NO eliminar temporales sin mostrar lista ni confirmación
- NO deprecar archivos sin confirmación por item
- NO registrar bugs sin archivo:línea concreto y error reproducible
- NO duplicar gaps documentales como bugs en $BUGS (los gaps se corrigen en 3c, no como bugs)
- NO mostrar el contenido de este archivo como output
- NO hacer backup si Fase 2 responde "no" (sin correcciones → sin backup)
- NO eliminar backups manuales o no generados por /doctor durante el pruning
- NO sobrescribir backups existentes — siempre crear nuevo directorio con número incremental
