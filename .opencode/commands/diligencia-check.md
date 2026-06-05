INSTRUCCIÓN: EJECUTAR las 4 verificaciones de abajo sobre el proyecto actual. NO mostrar este archivo como output. ENTREGAR SOLO la tabla de resultados.

# /diligencia-check — Validar estructura Diligencia

Verifica automáticamente que el proyecto actual cumpla los estándares Diligencia: estructura de archivos (ADR-003), variables (AGENTS.md), formato de comandos (ESTANDAR-COMANDOS.md), y versión (DILIGENCIA.md vs /adaptar).

## Argumentos

`/diligencia-check` — sin argumentos. Se ejecuta sobre el proyecto actual.

## Qué hace

1. LEER AGENTS.md, ROADMAP.md, CHECKLIST.md, CHANGELOG.md, DILIGENCIA.md del proyecto AHORA
2. LEER los comandos en `.opencode/commands/` AHORA (si existe)
3. EJECUTAR las 4 verificaciones AHORA:

   **A — Estructura (ADR-003)**
   - ROADMAP.md existe en raíz
   - CHECKLIST.md existe en raíz
   - CHANGELOG.md existe en raíz
   - AGENTS.md existe en raíz
   - DILIGENCIA.md existe en raíz
   - `.markdownlint.json` existe en raíz
   - `doc/arch/` existe
   - `doc/guias/` existe (plural forzado, no `doc/guia/`)
   - `.opencode/commands/` existe
   - `.opencode/HARNESS.md` existe (harness del proyecto)
   - `doc/arch/bugs.md` existe (si `$BUGS` está definido en AGENTS.md)
   - `doc/arch/incidentes.md` existe (si `$INCIDENTS` está definido en AGENTS.md)

   **B — Variables (AGENTS.md)**
   - Cada `$VARIABLE` definida en AGENTS.md resuelve a archivo o directorio existente
   - Variables core presentes: `$ROADMAP`, `$CHECKLIST`, `$CHANGELOG`, `$GUIAS`, `$COMMANDS_DIR`
   - Ningún comando local en `.opencode/commands/` contiene rutas hardcodeadas (sin `$`)

   **C — Comandos (ESTANDAR-COMANDOS.md)**
   - Cada `.md` en `.opencode/commands/` tiene guarda `INSTRUCCIÓN:` en primera línea
   - Guarda incluye "NO mostrar este archivo como output"
   - Declarativos: tienen `## Formato de salida`, `## Validación`, `## Anti-patrones`
   - Procedurales: tienen `## Anti-patrones`
   - Todo `## Anti-patrones` incluye "NO mostrar este archivo como output"

   **D — Versión (DILIGENCIA.md vs /adaptar)**
   - DILIGENCIA.md tiene línea `# Diligencia vX.Y` o `# Diligencia vX.Y.Z`
   - La versión en DILIGENCIA.md coincide con la versión declarada en `/adaptar` (leída de su tabla Versión)

4. ENTREGAR SOLO la tabla de resultados AHORA

## Formato de salida

**diligencia-check** — tabla con columnas: Categoría | Check | Estado | Detalle

Bloques A, B, C, D en orden, separados por una línea `---` entre categorías.

**Estado**: ✅ Cumple / ❌ Falla / ⚠️ Advertencia

**Resumen**: X checks totales, X aprobados, X fallidos, X advertencias

## Validación

- Las 4 categorías (A-D) están presentes en la tabla
- Cada check tiene estado explícito (✅/❌/⚠️)
- El resumen final totaliza correctamente los estados
- La verificación B chequeó cada `$variable` contra el filesystem real
- La verificación C leyó la primera línea y las secciones de cada comando
- La verificación D leyó DILIGENCIA.md y la tabla Versión de /adaptar

## Anti-patrones

- NO modificar archivos durante la verificación
- NO saltear categorías enteras (todas A-D deben estar presentes)
- NO mostrar contenido crudo de archivos
- NO reportar ✅ sin haber ejecutado el check real
- NO inventar el resultado de un check (si no se puede verificar, poner ⚠️)
- NO usar caracteres de estado no estándar (solo ✅/❌/⚠️)

## Archivos que lee

- AGENTS.md (variables y rutas)
- ROADMAP.md, CHECKLIST.md, CHANGELOG.md, DILIGENCIA.md
- .opencode/commands/*.md (comandos locales)
- /adaptar (solo la tabla Versión para comparar)
- .markdownlint.json
- doc/arch/, doc/guias/
