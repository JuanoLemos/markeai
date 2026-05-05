# /backupall — Backup completo del proyecto

Crea un `.zip` con todo el código fuente del proyecto, excluyendo `venv/`, `.git/`, `__pycache__/`, `.pytest_cache/`, `*.db`.

## Qué hace
1. Primero intenta con `7z` (mejor compresión)
2. Si no está disponible, intenta con `tar -czf`
3. Si no hay ni 7z ni tar, copia todos los archivos de `git ls-files` a `.bak_full_<fecha>/`
4. Reporta ruta y tamaño del backup

## Output
- Si 7z o tar: `MarketAI-backup-<fecha>.zip` en la raíz del proyecto
- Si copia manual: `.bak_full_<fecha>/`

## Diferencia con /backup
- `/backup` → respalda archivos críticos individuales (rápido, pre-edit)
- `/backupall` → respalda el proyecto completo (lento, pre-deploy o cierre de sesión)
