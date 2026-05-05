# /limpiar — Limpiar archivos temporales

Elimina archivos temporales generados durante debugging o sesiones.

## Qué hace
1. Busca: `*.pyc`, `__pycache__/`, `*.bak.*`, `orchestrator.log`, `*.tmp`, `STOP`
2. Muestra lista al usuario
3. Pregunta confirmación
4. Elimina los archivos
5. `git add -A` para registrar las eliminaciones
