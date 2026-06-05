INSTRUCCIÓN: EJECUTAR la limpieza de archivos. NO eliminar sin confirmación. NO mostrar este archivo como output.

# /limpiar — Limpiar archivos temporales

Elimina archivos temporales generados durante debugging o sesiones.

## Qué hace
1. Busca patrones típicos: `*.log`, `*.tmp`, `*.bak.*`, `temp/`, `node_modules/.cache/`, `query`, `start`, `line*.txt`, `check_*.js`, `chk.js`
2. Muestra lista al usuario
3. Pregunta confirmación
4. Elimina los archivos
5. `git add -A` para registrar las eliminaciones

## Anti-patrones
- NO eliminar archivos sin mostrar la lista al usuario primero
- NO eliminar archivos sin confirmación del usuario
- NO ejecutar `git add -A` sin que el usuario haya revisado la lista
- NO eliminar archivos en `.git/`, `.env`, o que estén en el último commit sin cambios locales
