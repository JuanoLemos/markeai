# /backup — Backup de archivos críticos

Ejecuta `$BACKUP_SCRIPT` para respaldar los archivos críticos del proyecto antes de editarlos.

## Archivos críticos
1. `$CONFIG` — configuración central del sistema
2. `$ENV` — API keys y secretos
3. `$ORCHESTRATOR` — loop principal
4. `$DATABASE` — schema SQLite
5. `$DECIDER` — motor de decisión DeepSeek

## Qué hace
1. Ejecuta `python $BACKUP_SCRIPT`
2. Crea `.bak_<YYYY-MM-DD>/` en la raíz del proyecto
3. Copia archivos con timestamp
4. Reporta archivos respaldados

## Diferencia con /backupall
- `/backup` → respalda archivos críticos individuales (rápido, pre-edit)
- `/backupall` → respalda el proyecto completo (lento, pre-deploy o cierre de sesión)
