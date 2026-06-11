INSTRUCCIÓN: EJECUTAR cierre de sesión. NO modificar archivos sin confirmación. NO mostrar este archivo como output.

# /version — Cerrar sesión de desarrollo (git-log model)

Versiona el proyecto con CHANGELOG auto-generado desde commits Conventional Commits.

## Argumentos
/version [minor|patch|X.Y.Z] [--notes "extra"] [--yank] [--template]

- `minor` (default): vA.B.C → vA.(B+1).0
- `patch`: vA.B.C → vA.B.(C+1)
- `X.Y.Z`: versión explícita (3 partes)
- `--notes`: descripción adicional al CHANGELOG auto-generado
- `--yank`: marcar el release como [YANKED]
- `--template`: forzar bump de templates incluso en patch

## Qué hace

1. DETECTAR última versión:
   - `git log --oneline --grep="chore(release):" -1` → extraer versión de ese commit
   - Si no hay: preguntar al usuario

2. COLECTAR commits desde el último release:
   - `git log --oneline <último-release>..HEAD` → todos los commits de la sesión
   - Si no hay commits: ⚠️ "No hay commits nuevos desde el último release."
     Preguntar: "¿Versionar igual? [sí/no]"

3. CLASIFICAR commits por tipo Conventional Commit:
   ```
   feat: → Added (feature nueva para el usuario)
   fix: → Fixed (corrección de bug)
   refactor: → Changed (cambio interno sin impacto visible)
   docs: → Changed (documentación)
   perf: → Changed (mejora de rendimiento)
   chore(release): → IGNORAR (es el punto de partida)
   chore: → Changed (mantenimiento)
   test: → Changed (tests)
   ```
   Para cada tipo, acumular los mensajes de commit (sin el prefijo tipo:).

4. AUTO-GENERAR entrada CHANGELOG:
   ```
   ## [vX.Y.Z] — YYYY-MM-DD

   ### Added
   - feat commit message 1
   - feat commit message 2

   ### Fixed
   - fix commit message 1
   ```
   Si `--notes` existe, agregarlo como última línea de la sección Added.

5. PRE-FLIGHT (6 checks, igual que antes):
   a. Staleness documental — LEER INDEX.md → labels vs CHANGELOG
   b. Salud — status-salud.md existe? stale?
   c. Scope /explica — faltantes en doc/guias/mecanicas/arch
   d. Template sync (solo Diligencia)
   e. Cross-refs §8 (solo Diligencia)
   f. Variables resolubles

6. MOSTRAR al usuario:
   - CHANGELOG auto-generado (para revisar/editar)
   - Resultado pre-flight
   Preguntar: "¿Aceptar CHANGELOG y versionar? [sí/no]"

7. INSERTAR entrada en CHANGELOG.md

8. Si el proyecto es Diligencia Y (minor/major o --template):
   a. Actualizar adaptar.md global (versión + migración)
   b. Actualizar DILIGENCIA.md template global
   c. Sincronizar templates doc-base

9. ACTUALIZAR INDEX.md: versión CHANGELOG + DILIGENCIA, fechas

10. `git add -A` → `git commit -m "chore(release): vX.Y.Z"` → `git tag vX.Y.Z`

11. `git status --porcelain` → DEBE estar vacío. Si no: ERROR FATAL.

12. Reportar SOLO resumen.

## Formato de salida
🔖 vA.B.C → vX.Y.Z
📄 CHANGELOG auto-generado: N items (N Added, N Fixed, N Changed)
🔍 Pre-flight: A: <N STALE> | B: <OK/⚠️> | C: <N faltantes> | D: <OK/mismatch> | E: <OK/N sin ref> | F: <OK/N rotas>
✅ Commit: chore(release): vX.Y.Z + tag
⚠️ git status --porcelain limpio: Sí

## Validación
- Último release detectado por `git log --grep="chore(release):"`
- Commits clasificados por tipo Conventional Commit
- CHANGELOG generado con categorías Added/Fixed/Changed
- Pre-flight protegido (6 checks)
- INDEX.md actualizado con nueva versión
- `git status --porcelain` vacío post-commit
- Tag creado: `git tag vX.Y.Z`

## Anti-patrones
- NO clasificar chore(release): commits como Changed (son el punto de referencia)
- NO sobrescribir CHANGELOG existente — la nueva entrada se INSERTA tras la última
- NO saltarse el paso de revisión (paso 6) — el usuario debe aprobar el CHANGELOG
- NO versionar si el pre-flight tiene alertas sin resolver
- NO omitir la creación del tag
