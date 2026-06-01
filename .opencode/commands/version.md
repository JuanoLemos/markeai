INSTRUCCIÓN: EJECUTAR cierre de sesión. NO modificar archivos sin confirmación. NO mostrar este archivo como output.

# /version — Cerrar sesión de desarrollo

Versiona el proyecto, documenta cambios, actualiza CHANGELOG, y prepara commit de cierre.

## Argumentos
/version [minor|patch|X.Y] [--notes "descripción"]

- `minor` (default): vX.Y → vX.(Y+1) — cambios visibles al usuario
- `patch`: vX.Y.Z → vX.Y.(Z+1) — fixes internos
- `X.Y`: versión explícita
- `--notes`: descripción de la sesión para CHANGELOG

## Qué hace
1. Detectar versión actual AHORA:
   - Si existe package.json: leer `"version"`
   - Si existe CHANGELOG.md: leer último tag en ## [X.Y.Z]
   - Si existe version.txt: leer contenido
   - Si ninguno existe: preguntar al usuario la versión actual
2. Calcular nueva versión según argumento
3. Mostrar: **"Versión actual: vA.B.C → vX.Y.Z"**
4. PREGUNTAR CONFIRMACIÓN antes de continuar
5. Si confirma:
   - Si existe package.json: actualizar `"version"` field
   - Si existe version.txt: sobrescribir con nueva versión
   - Agregar entrada en CHANGELOG.md con --notes
   - Ejecutar `/updoc` AHORA (sincroniza RM, CHECKLIST)
   - Escanear `git diff --name-only` para detectar archivos afectados
   - Si hay git: `git add -A && git commit -m "vX.Y.Z: <--notes>"`
6. Reportar SOLO el resumen de la sesión

## Formato de salida
🔖 vA.B.C → vX.Y.Z
📄 Archivos afectados: <N>
✅ Commit: vX.Y.Z: <descripción>

## Validación
- La versión actual se detectó correctamente de package.json, CHANGELOG.md o version.txt
- El incremento es válido: minor (0.1.0), patch (0.0.1), o X.Y explícito
- CHANGELOG.md se actualizó con entrada de la nueva versión
- /updoc se ejecutó (si $RM existe)
- El commit contiene todos los cambios de la sesión

## Anti-patrones
- NO modificar archivos sin confirmación del usuario (paso 4 obligatorio)
- NO usar versión hardcodeada — detectarla del proyecto
- NO omitir /updoc — sincronización documental necesaria
- NO versionar si working tree está limpio (preguntar al usuario)
- NO modificar archivos que no estén en la documentación del proyecto ($RM, $CHECKLIST, $CHANGELOG)

## Archivos que modifica
- package.json (si existe)
- version.txt (si existe)
- CHANGELOG.md
- $RM (vía /updoc)
- $CHECKLIST (vía /updoc)
