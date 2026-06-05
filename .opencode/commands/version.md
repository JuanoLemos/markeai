INSTRUCCIÓN: EJECUTAR cierre de sesión. NO modificar archivos sin confirmación. NO mostrar este archivo como output.

# /version — Cerrar sesión de desarrollo

Versiona el proyecto, documenta cambios, actualiza CHANGELOG, y prepara commit de cierre.

## Argumentos
/version [minor|patch|X.Y.Z] [--notes "descripción"] [--yank] [--template]

- `minor` (default): vA.B.C → vA.(B+1).0 — cambios visibles al usuario
- `patch`: vA.B.C → vA.B.(C+1) — fixes internos (usar cuando /doctor actuó con correcciones)
- `X.Y.Z`: versión explícita (3 partes)
- `--notes`: descripción de la sesión para CHANGELOG
- `--yank`: marcar el release como [YANKED] (retirado)
- `--template`: forzar bump de adaptar.md y template DILIGENCIA.md incluso en patch (default: solo minor/major)

## Qué hace
1. Detectar versión actual AHORA:
   - Si existe package.json: leer `"version"`
   - Si existe CHANGELOG.md: leer último tag en ## [X.Y.Z]
   - Si existe version.txt: leer contenido
   - Si ninguno existe: preguntar al usuario la versión actual
2. Calcular nueva versión según argumento
   - Autodetección post-/doctor:
     - Si `[Unreleased]` en CHANGELOG.md contiene `/doctor` en sección "Changed"
     - Y el usuario no especificó `minor|patch|X.Y.Z` explícitamente
     - → Sugerir `patch` en lugar de `minor` (correcciones de /doctor son fixes internos)
3. Mostrar: **"Versión actual: vA.B.C → vX.Y.Z"**
4. PRE-FLIGHT — Verificación integral antes de versionar (6 checks):
   a. **Staleness documental** — LEER INDEX.md AHORA, extraer labels de Guías y Mecánicas. COMPARAR cada label contra CHANGELOG latest. REPORTAR tabla: Archivo | Label actual | Estado (STALE | OK | SIN LABEL | ADELANTADO). REPORTAR conteo total por estado.
   b. **Salud del proyecto** — BUSCAR `doc/arch/status-salud.md` AHORA. Si existe: leer conteo de STALE/CORREGIDOS/OK. Si no existe: marcar ⚠️ "status-salud.md no encontrado — ejecutar /salud".
   c. **Scope de /explica** — LEER `~/.config/opencode/commands/explica.md` AHORA, extraer lista de archivos en scope. LISTAR archivos reales en `doc/guias/*.md`, `doc/mecanicas/*.md`, `doc/arch/*.md` (excluyendo bugs.md, incidentes.md, adr-template.md, ADR-*.md). DETECTAR faltantes (en proyecto no en scope) y sobrantes (en scope no en proyecto). REPORTAR N faltantes | N sobrantes.
   d. **Template sync** (solo si proyecto = Diligencia) — LEER template DILIGENCIA.md línea 1 (template_version). LEER proyecto DILIGENCIA.md línea 1 (proyecto_version). LEER adaptar.md versión (adaptar_version). COMPARAR. REPORTAR mismatch si los hay.
   e. **Cross-refs §8** (solo si proyecto = Diligencia) — LEER GUIA_DE_COMANDOS.md §8 AHORA. LISTAR guías nuevas en `doc/guias/` no listadas en §8. REPORTAR guías sin cross-ref.
   f. **Variables resolubles** — LEER AGENTS.md AHORA, extraer `$VARIABLES`. Verificar que cada ruta resuelva. REPORTAR variables rotas.
5. Consolidar resultados del pre-flight:
   a. ARMAR tabla unificada: Check | Estado | Detalle
   b. Si 0 alertas → "✅ Pre-flight limpio" (continuar directamente)
   c. Si 1+ alertas → MOSTRAR tabla + ABORTAR. "⚠️ /version requiere proyecto limpio. Ejecutar `/CBP updoc` para resolver pendientes documentales antes de versionar."
6. PREGUNTAR CONFIRMACIÓN antes de continuar
7. Si confirma: aplicar bump de versión
   - Si existe package.json: actualizar `"version"` field
   - Si existe version.txt: sobrescribir con nueva versión
   - Agregar entrada en CHANGELOG.md con --notes (categorías: Added, Changed, Deprecated, Removed, Fixed, Security)
   - Si existe [Unreleased]: mover sus items a la nueva entrada y dejar [Unreleased] vacío
   - Si --yank: formatear entrada como `## [X.Y.Z] - YYYY-MM-DD [YANKED]`
8. Si el proyecto es Diligencia Y (bump minor O major O --template activo):
   a. ACTUALIZAR OBLIGATORIAMENTE `~/.config/opencode/commands/adaptar.md` (versión en tabla Versión + entrada de migración para el nuevo bump)
   b. ACTUALIZAR OBLIGATORIAMENTE `~/.config/opencode/templates/doc-base/DILIGENCIA.md` (header + historial con la nueva versión)
   c. Sincronizar `~/.config/opencode/templates/doc-base/` completa: comparar archivos en C:\xampp\htdocs\Diligencia\ contra los templates. Si hay cambios de contenido (estructura, secciones, placeholders), propagarlos al template preservando [Nombre del Sistema] y otros marcadores. Verificar que ningún template tenga versiones hardcodeadas en headers. Archivos típicos: ADR_SUMMARY.md, identidad.md, MANDATO.md, adr-template.md, CHECKLIST.md.
   d. Informar al usuario de los archivos globales modificados
   e. NO omitir este paso — la propagación al template global es requisito obligatorio de todo BUILD de Diligencia
   Si es patch sin --template: saltar — el template no requiere bump por fixes internos de comandos.
9. Actualizar INDEX.md: Versión de CHANGELOG.md = vX.Y.Z, Versión de DILIGENCIA.md = vX.Y.Z, Última actualización de todos los docs críticos = fecha actual (YYYY-MM-DD)
10. Ejecutar `/commit chore(release): vX.Y.Z — <--notes> --auto`
    - Si falla: DETENER. Reportar error. NO declarar sesión cerrada.
11. `git status --porcelain` → DEBE estar vacío
    - Si no: ERROR FATAL. No cerrar sesión.
12. Reportar SOLO el resumen de la sesión

## Formato de salida
🔖 vA.B.C → vX.Y.Z
🔍 Pre-flight: A: <N STALE> | B: <N STALE> | C: <N faltantes+N sobrantes> | D: <OK/mismatch> | E: <OK/N sin ref> | F: <OK/N rotas>
📄 Archivos afectados: <N>
✅ Commit: chore(release): vX.Y.Z — <descripción>
⚠️ git status --porcelain limpio: Sí
⛔ [YANKED]: Sí/No

## Validación
- Los 6 checks de pre-flight se ejecutaron (paso 4a-f)
- Si hubo alertas en pre-flight, /version se abortó y redirigió a `/CBP updoc`
- La versión actual se detectó correctamente de package.json, CHANGELOG.md o version.txt
- El incremento es válido: minor (A.B+1.0), patch (A.B.C+1), o X.Y.Z explícito
- CHANGELOG.md se actualizó con entrada de la nueva versión (categorías: Added, Changed, Deprecated, Removed, Fixed, Security)
- Si existe [Unreleased], sus items se migraron a la nueva entrada
- Si --yank: CHANGELOG tiene formato `[X.Y.Z] - YYYY-MM-DD [YANKED]`
- INDEX.md actualizado: versión de CHANGELOG.md y DILIGENCIA.md, fecha de todos los docs críticos
- /commit --auto se ejecutó con formato Convencional Commits
- `git status --porcelain` está vacío (cero archivos huérfanos)

## Anti-patrones
- NO saltarse pre-flight — los 6 checks (paso 4a-f) son obligatorios; d/e pueden omitirse solo si proyecto ≠ Diligencia
- Si pre-flight tiene 1+ alertas: ABORTAR y sugerir `/CBP updoc`. NO ofrecer "forzar versionado".
- NO modificar archivos sin confirmación del usuario (paso 6 obligatorio)
- NO usar versión hardcodeada — detectarla del proyecto
- NO hacer commit manual — delegar a /commit para validación Conventional Commits
- NO versionar si working tree está limpio (preguntar al usuario)
- NO modificar archivos que no estén en la documentación del proyecto (CHANGELOG.md, DILIGENCIA.md, INDEX.md)
- NO declarar sesión cerrada si el commit falló o quedan archivos sin commit

## Archivos que modifica
- package.json (si existe)
- version.txt (si existe)
- CHANGELOG.md
- INDEX.md
- DILIGENCIA.md (del proyecto)
- `~/.config/opencode/commands/adaptar.md` (solo si proyecto = Diligencia, solo minor/major o --template)
- `~/.config/opencode/templates/doc-base/DILIGENCIA.md` (solo si proyecto = Diligencia, solo minor/major o --template)

