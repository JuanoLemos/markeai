INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre los archivos del proyecto. NO mostrar este archivo como output. NO modificar archivos sin confirmación del usuario.

# /updoc — Auditoría y sincronización de documentación informativa

Sincroniza guías, mecánicas, ADRs y referencias según los cambios registrados en los docs críticos.
No modifica docs críticos (CHANGELOG.md, DILIGENCIA.md, ROADMAP.md, CHECKLIST.md) — esos son dominio de /version.

## Argumentos
/updoc [--apply] [guias|mecanicas|adrs|referencias]

- Sin argumentos: auditoría completa de todos los docs informativos
- `guias|mecanicas|adrs|referencias`: auditoría dirigida a una categoría
- `--apply`: aplicar cambios automáticamente (saltar confirmación en BUILD)

## Qué hace

### Fase A — Leer catálogo (INDEX.md)

1. LEER `INDEX.md` AHORA — extraer lista de docs por categoría (Guías, Mecánicas, ADRs, Referencias)
2. Si INDEX.md NO existe:
   a. ESCANEAR filesystem: `doc/guias/*.md`, `doc/mecanicas/*.md`, `doc/arch/*.md`
   b. EXCLUIR archivos del dominio de /doctor: `bugs.md`, `incidentes.md`, `adr-template.md`
   c. CLASIFICAR por carpeta (guias → Guías, mecanicas → Mecánicas, arch → ADRs)
   d. DAR SALIDA: "INDEX.md no encontrado. Docs detectados: N guías, N mecánicas, N ADRs"
   e. PREGUNTAR: "¿Crear INDEX.md?"
   f. Si confirma: CREAR `INDEX.md` con entradas detectadas (versión = — por defecto)
3. Si se especificó una categoría (ej: `/updoc guias`): FILTRAR solo esa categoría para el resto del flujo

### Fase B — Leer docs críticos (versión de referencia)

1. LEER `CHANGELOG.md` AHORA — extraer última versión del último `## [X.Y.Z]` o `## [X.Y.Z] - YYYY-MM-DD`
2. LEER `DILIGENCIA.md` (si existe) — extraer versión del header `# Diligencia vX.Y`
3. Si no existe CHANGELOG: PREGUNTAR al usuario cuál es la versión de referencia
4. La versión de referencia = latest de CHANGELOG (o la que indique el usuario)

### Fase C — Detectar stale por comparación de labels

Para cada doc en el scope (todas las categorías no críticas o una específica):

1. LEER el archivo AHORA
2. BUSCAR label de versión en primeras 3 líneas:
   - Patrón `vX.Y.Z` o `vX.Y` (semver 3 o 2 partes)
   - Si es `vX.Y`: normalizar a `vX.Y.0` para comparación
3. COMPARAR versión del doc vs versión de referencia (CHANGELOG latest):
   - doc < ref → **STALE**
   - doc == ref → **OK**
   - doc > ref → **ADELANTADO** (posible error de label, marcar para revisión)
   - Sin label detectable → **SIN LABEL** (requiere revisión manual)
4. REGISTRAR en tabla: Archivo | Categoría | Label actual | Ref. esperada | Estado

### Fase D — Detectar gaps concretos en docs stale

Para cada doc con estado **STALE** o **SIN LABEL**:

1. LEER el doc completo AHORA
2. LEER las entradas de CHANGELOG desde la versión del doc hasta versión de referencia
   - Si el doc no tiene label: leer TODO el CHANGELOG desde su sección más antigua
3. DETECTAR gaps buscando cambios en CHANGELOG que deberían reflejarse en el doc:
   - **Comandos faltantes**: si CHANGELOG Added un comando y el doc lista comandos → verificar inclusión
   - **Conteos incorrectos**: si el doc dice "N comandos" y el número no coincide → marcar
   - **Secciones faltantes**: si CHANGELOG Added una funcionalidad y el doc tiene secciones relacionadas → verificar cobertura
   - **Referencias desactualizadas**: si el doc referencia una versión, ruta o nombre obsoleto
   - **Labels de versión internos**: si el doc menciona "vX.Y.Z" en medio del texto que no coincide
4. Si se detectaron gaps: registrar en tabla con acción sugerida
5. Si NO se detectaron gaps: marcar como **solo label stale — sin gaps de contenido** (solo necesita bump de label en INDEX.md)

### Fase E — Plan consolidado

1. ARMAR tabla: Categoría | Archivo | Label actual | Estado | Gaps | Acción sugerida
2. INCLUIR docs **OK** como contexto: ✅
3. INCLUIR docs **SIN LABEL** como ⚠️ revisión manual
4. INCLUIR docs **STALE sin gaps** como ≡ solo bump de label
5. Si la tabla solo contiene OK: ✅ "Todos los docs informativos están sincronizados con vX.Y.Z"
6. Si hay stale o sin label:
   - MOSTRAR tabla completa
   - PREGUNTAR: "¿Aplicar correcciones a los N docs pendientes?"
   - Si `--apply`: saltar pregunta, ir directo a BUILD

### Fase F — BUILD (aplicar cambios)

Para cada gap pendiente (STALE o SIN LABEL):

1. APLICAR correcciones específicas según gaps detectados en Fase D:
   - Agregar comandos faltantes en listas/secciones
   - Actualizar conteos (ej: "34 comandos" → "35 comandos")
   - Agregar secciones faltantes
   - Actualizar referencias desactualizadas
   - Si SIN LABEL sin gaps detectables: dejar contenido intacto
2. ACTUALIZAR label de versión del doc → versión de referencia (CHANGELOG latest)
   - Si el doc tenía `vX.Y` → actualizar a `vX.Y` (misma convención)
   - Si el doc no tenía label → agregar label en header como `vX.Y.Z`
3. ACTUALIZAR INDEX.md: Versión = label nuevo, Última actualización = fecha actual
4. REGISTRAR cada cambio aplicado: Archivo | Cambios

### Fase G — Git-diff (archivos sin entrada en INDEX)

1. `git log --oneline -20` AHORA para historial reciente
2. Detectar último commit versionado: `git log --grep "v[0-9]+\.[0-9]+" --oneline -1` — si no existe, usar `git log --oneline -1` (HEAD)
3. `git diff --name-only <last-version>` (si no hay `<last-version>` válido: `git log --oneline --name-only --diff-filter=M HEAD~20..HEAD | findstr "\.md$" | sort -u`) AHORA — todos los .md cambiados desde la última versión
4. FILTRAR solo archivos `.md`
5. CRUZAR con INDEX.md: ¿hay .md modificados que NO están registrados en INDEX?
6. Si sí: CLASIFICAR por carpeta destino (guia, mecanica, adr, referencia)
7. PREGUNTAR: "¿Agregar N archivos a INDEX.md?"
8. Si confirma: ESCRIBIR entradas en INDEX.md con versión = — y fecha actual

### Fase H — Integridad de referencias cruzadas (D-checks)

**D1 — Guías huérfanas en GUIA_DE_COMANDOS.md:**
- Si hay guías nuevas (detectadas en Fase A o Fase G):
  - LEER `GUIA_DE_COMANDOS.md` AHORA
  - BUSCAR lista en §8 "Guías relacionadas"
  - Si la guía nueva NO aparece listada → notificar: "Guía nueva no cross-referenciada en GUIA_DE_COMANDOS.md §8"

**D2 — Templates sin consumidor (solo si proyecto = Diligencia):**
- DETECTAR si el proyecto es Diligencia: AGENTS.md tiene `$BUGS`, `$INCIDENTS`, `$RM apunta a ROADMAP.md` + `$PROJECT_NAME = Diligencia` o DILIGENCIA.md título contiene "Diligencia"
- LEER `~/.config/opencode/templates/doc-base/` AHORA — listar todos los archivos
- BUSCAR en comandos globales (`~/.config/opencode/commands/`) y en `/adaptar` referencias al template
- Si un template no está referenciado por ningún comando ni por /adaptar → notificar: "Template <nombre> en doc-base/ sin consumidor ni referencia en /adaptar"

**D3 — Scope de /explica incompleto (solo si proyecto = Diligencia):**
- LEER `~/.config/opencode/commands/explica.md` AHORA — buscar la línea "BUSCAR en la documentación de Diligencia:"
- LISTAR todos los archivos de documentación del proyecto
- Si algún archivo de doc NO aparece en la lista de /explica → notificar: "Archivo <ruta> no incluido en scope de /explica"
- Si algún archivo listado en /explica NO existe en disco → notificar: "Archivo <ruta> referenciado en /explica no existe en disco"

**D4 — Variables huérfanas (comandos vs AGENTS.md):**
- Para comandos locales o globales que referencien al proyecto:
  - EXTRAER todas las referencias a `$VARIABLE` (patrón: `$[A-Z][A-Z_]+`)
  - LEER AGENTS.md AHORA — listar variables definidas
  - Si una `$VARIABLE` referenciada NO está definida en AGENTS.md → notificar: "<$VARIABLE> usada pero no definida en AGENTS.md"

**D5 — Template staleness (solo si proyecto = Diligencia):**
- DETECTAR si el proyecto es Diligencia: mismo criterio que D2
- LEER `~/.config/opencode/templates/doc-base/DILIGENCIA.md` línea 1 AHORA → extraer versión del header (template.minor)
- LEER `DILIGENCIA.md` del proyecto línea 1 AHORA → extraer versión del header (proyecto.minor)
- Comparar minor version (X.Y), NO full semver:
  - template.minor < proyecto.minor → **STALE**: "Template DILIGENCIA.md (vX.Y) desactualizado vs proyecto (vA.B)" → SUGERIR: "/version minor BUILD para sincronizar template"
  - template.minor == proyecto.minor → **OK** (diff en patch es esperado — los patches no bumpan el template)
  - template.minor > proyecto.minor → **ADELANTADO**: error potencial
- LEER `~/.config/opencode/commands/adaptar.md` línea 15 AHORA → extraer versión de la tabla (adaptar.minor)
- Misma comparación minor vs proyecto.minor

## Formato de salida

**Fase A — Catálogo:** N docs en INDEX (N guías, N mecánicas, N ADRs, N referencias)
**Fase B — Referencia:** CHANGELOG vX.Y.Z | DILIGENCIA vX.Y
**Fase C — Stale:** N stale | N ok | N sin label | N adelantado
**Fase D — Gaps:** N gaps detectados en N docs
**Fase E — Plan:** tabla Categoría | Archivo | Acción sugerida
**Fase F — BUILD:** N docs actualizados | N gaps corregidos | INDEX.md sincronizado
**Fase G — Git-diff:** N archivos nuevos sin entrada en INDEX
**Fase H — Cross-ref:** D1-D5: N gaps | por tipo
*(si no hay gaps)* ✅ **Todos los docs informativos sincronizados con vX.Y.Z**

## Validación

- Fase A ejecutada: INDEX.md leído como catálogo (o creado si no existía)
- Fase B ejecutada: versión de referencia obtenida de CHANGELOG (o del usuario)
- Fase C ejecutada: cada doc en scope comparado contra la referencia
- Fase D ejecutada: gaps detectados en cada doc stale o sin label
- Fase E ejecutada: plan presentado al usuario (o --apply activo)
- Fase F (si aplica): cambios aplicados solo con aprobación explícita
- Fase G ejecutada: git-diff contra último commit versionado, .md huérfanos detectados
- Fase H ejecutada: D1-D5 verificados
- NO se modificaron docs críticos (CHANGELOG, DILIGENCIA, ROADMAP, CHECKLIST)
- INDEX.md actualizado con nuevas versiones y fechas de docs modificados

## Anti-patrones

- NO modificar docs críticos (CHANGELOG.md, DILIGENCIA.md, ROADMAP.md, CHECKLIST.md) — son dominio de /version
- NO modificar archivos sin confirmación del usuario (salvo --apply en BUILD)
- NO omitir Fase G (git-diff): archivos .md sin entrada en INDEX son gaps
- NO asumir que todos los docs tienen label de versión — marcar como SIN LABEL
- NO modificar contenido de un doc si no hay gaps detectables (solo bump de label en INDEX.md)
- NO saltar detección de gaps (Fase D) solo porque el label está desactualizado

## Archivos que modifica (dependiendo de gaps detectados)

- INDEX.md (versiones y fechas de docs informativos, nuevas entradas)
- Guías en `doc/guias/*.md` (si tienen gaps de contenido)
- Mecánicas en `doc/mecanicas/*.md` (si tienen gaps de contenido)
- ADRs en `doc/arch/*.md` (solo metadata/estado si aplica)
- Documentos de referencia (si tienen gaps de contenido)
