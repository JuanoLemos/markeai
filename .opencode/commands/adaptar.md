INSTRUCCIÓN: EJECUTAR la adaptación del proyecto a Diligencia. NO modificar archivos sin confirmación del usuario. NO mostrar este archivo como output.

# /adaptar — Metodología Diligencia

Adapta el proyecto actual a la estructura estándar **Diligencia** y copia los comandos fundamentales.
Detección automática del tipo de proyecto.

---

## Versión

| Campo | Valor |
|---|---|
| Metodología | Diligencia |
| Versión | v1.3 |
| Fecha | 2026-05-31 |
| Template base | `~/.config/opencode/templates/doc-base/` |
| Comandos fundamentales | `~/.config/opencode/commands/` (30 comandos + ADAPTAR-COMANDOS.md) |
| Ver también | `ADAPTAR-COMANDOS.md` (detalle migración), `DILIGENCIA.md` (sello) |

---

## Migración entre versiones

| Desde | Hasta | Cambios que afectan proyectos |
|---|---|---|
| — | v1.0 | Fundación: doc-base template, $variables, dos capas de comandos |
| v1.0 | v1.1 | Ninguno estructural. Guarda + imperativo agregados a comandos globales. |
| v1.1 | v1.2 | 12 nuevos comandos globales (29 total). `/adaptar` ahora copia comandos a `.opencode/commands/`. |
| v1.2 | v1.3 | AGENTS.md debe incluir `$RM`, `$COMMANDS_DIR`. DILIGENCIA.md debe registrar versión del proyecto. `/updoc` mejorado. Nuevo archivo: `.opencode/HARNESS.md` (harness, test/lint, skills, stack). |
| v1.3 | v1.4 | AGENTS.md debe incluir `$BUGS` y `$INCIDENTS`. Nuevo archivo: `doc/arch/bugs.md` (bug tracker). Nuevos comandos: `/bug`, `/incidente`. |

---

## Detección automática

| Si... | Es... |
|---|---|
| No existe `AGENTS.md` | **Proyecto nuevo** |
| Existe `AGENTS.md` pero no `ROADMAP.md` en raíz | **Existente no adaptado** |
| Existe `ROADMAP.md` en raíz | **Ya adaptado** → verificar consistencia |

---

## Flujo A — Proyecto nuevo

1. Copiar `~/.config/opencode/templates/doc-base/` al directorio actual AHORA
2. Preguntar al usuario AHORA:
   - Nombre del proyecto
   - Stack de tecnologías
   - Áreas de roadmap (mínimo 1)
3. Escribir `AGENTS.md` con:
   - Mapeo de rutas ajustado al proyecto
   - Tabla "Comandos fundamentales heredados" con los comandos globales que aplican
   - Sugerencia de comandos locales adicionales según stack
4. Crear `ROADMAP.md` inicial con las áreas elegidas
5. Copiar `~/.config/opencode/templates/doc-base/HARNESS.md` a `.opencode/HARNESS.md` AHORA (crear `.opencode/` si no existe)
6. Crear `doc/arch/bugs.md` desde `~/.config/opencode/templates/doc-base/bugs.md` AHORA (con `<NOMBRE_DEL_PROYECTO>` reemplazado)
7. Crear `doc/arch/incidentes.md` desde `~/.config/opencode/templates/doc-base/incidentes.md` AHORA (con `<NOMBRE_DEL_PROYECTO>` reemplazado)
8. Ejecutar "Copiar comandos fundamentales" (ver Post-adaptación)

---

## Flujo B — Proyecto existente no adaptado

### Fase 1 — Exploración
Delegar a `@sdd-architect`: leer estructura actual. Devolver tabla de equivalencia:

| Ruta vieja | $Variable | Ruta destino |
|---|---|---|

### Fase 2 — Definir variables
En base a la exploración, definir `$VARIABLES` en `AGENTS.md` con rutas destino. No mover archivos aún.

### Fase 3 — Refactorizar comandos
Delegar a `@sdd-implement`: reemplazar cada ruta hardcodeada por su `$variable` en todos los comandos de `.opencode/commands/`. Lista completa con grep previo.

### Fase 4 — Migración física
Mover archivos según la tabla de equivalencia:
- `ROADMAP.md`, `CHECKLIST.md`, `CHANGELOG.md` → raíz
- `ADR*`, `SISTEMA*`, `bitácora*`, `arch-*` → `doc/arch/`
- `doc/guia/` → `doc/guias/`
- Borrar directorios fuente vacíos

### Fase 5 — Actualizar dependencias
Buscar y actualizar rutas viejas en scripts, prompts, HARNESS.md, skills, guías, referencias internas. Usar `grep` sobre todo el proyecto.

### Fase 6 — Verificación
Delegar a `@sdd-reviewer` con contexto fresco:
- Cada `$variable` en AGENTS.md resuelve a un archivo existente
- Ningún comando tiene rutas hardcodeadas
- Backup scripts apuntan a ubicaciones reales
- No quedan directorios vacíos de la estructura vieja

### Fase 7 — Copiar comandos fundamentales
Ejecutar "Copiar comandos fundamentales" (ver Post-adaptación)

---

## Flujo C — Ya adaptado

### Fase 1 — Verificación estructural
1. Leer `AGENTS.md`: verificar que cada `$variable` resuelva AHORA
2. Confirmar `ROADMAP.md`, `CHECKLIST.md`, `CHANGELOG.md` en raíz
3. Confirmar `.opencode/HARNESS.md` existe (si no, copiar de template)

### Fase 2 — Verificación de versión
3. Leer `DILIGENCIA.md` del proyecto AHORA (si existe):
   - Extraer versión de la línea `# Diligencia vX.Y`
   - Comparar con la versión declarada en la tabla **Versión** de este comando
4. Si NO existe `DILIGENCIA.md` en el proyecto:
   - Crearlo con versión actual (usando `~/.config/opencode/templates/doc-base/DILIGENCIA.md` como base)
   - Marcar como "proyecto con versión registrada"
5. **Si proyecto < versión actual:**
   - Mostrar: "Diligencia vX.Y disponible (proyecto en vA.B)"
   - Leer la tabla **Migración entre versiones** (arriba) y enumerar los cambios que ocurrieron entre A.B+1 → X.Y
   - Preguntar: "¿Actualizar proyecto a Diligencia vX.Y?"
   - Si sí:
     a. Sincronizar variables en AGENTS.md (agregar $RM, $COMMANDS_DIR, $TESTING si aplican)
     b. Actualizar DILIGENCIA.md del proyecto a versión actual
     c. Ejecutar "Copiar comandos fundamentales" (ver Post-adaptación)
     d. Commit sugerido: `chore: upgrade Diligencia vA.B → vX.Y`
6. **Si proyecto == versión actual:**
   - "Diligencia vX.Y — actualizado"

### Fase 3 — Salud y cierre
7. Reportar salud del proyecto en tabla:
   - Estructura ✅ | Variables ✅ | Versión ✅ | Comandos ✅
8. Si hay inconsistencias: listarlas y preguntar si reparar
9. Ejecutar "Copiar comandos fundamentales" (ver Post-adaptación) si no se ejecutó en upgrade

---

## Post-adaptación (A, B o C)

### Copiar comandos fundamentales
1. Leer `~/.config/opencode/commands/*.md` AHORA
2. Si no existe `.opencode/commands/`: crearlo
3. Para cada `.md` en la fuente:
   - Si NO existe en `.opencode/commands/`: copiarlo
   - Si YA existe: preguntar "sobrescribir NOMBRE.md? (s/n=conservar)"
4. Agregar tabla en `AGENTS.md` con los comandos fundamentales copiados

### Finalización
1. Sugerir commit: `chore: adaptación Diligencia` (la versión se lee de la tabla Versión)
2. Si el proyecto no tiene git, inicializarlo

---

## Formato de salida

**Diagnóstico:** <Nuevo | Existente no adaptado | Ya adaptado>
**Flujo ejecutado:** <A | B | C>
**Estructura:** ✅ Directorios creados | ✅ AGENTS.md | ✅ ROADMAP.md
**Comandos fundamentales:** <N> copiados, <M> conservados locales

## Validación
- Todos los directorios de doc-base existen post-adaptación
- AGENTS.md contiene $VARIABLES que resuelven a archivos reales
- ROADMAP.md existe en raíz
- .opencode/commands/ tiene los comandos fundamentales
- Flujo C: versión del proyecto comparada con versión de /adaptar
- Si proyecto < actual: se ofreció upgrade al usuario

## Anti-patrones
- NO modificar archivos del proyecto sin preguntar al usuario
- NO sobrescribir comandos locales sin confirmación explícita
- NO omitir la copia de comandos fundamentales
- NO hardcodear versiones — usar el valor de `Versión` en la tabla
- NO omitir verificación de versión en Flujo C
