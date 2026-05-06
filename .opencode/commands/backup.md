# /backup — Backup de archivos críticos

Ejecuta `scripts/backup-critical.py` para respaldar los archivos críticos del proyecto antes de editarlos.

## Archivos críticos
1. `config.yaml` — configuración central del sistema
2. `.env` — API keys y secretos
3. `orchestrator.py` — loop principal
4. `data/database.py` — schema SQLite
5. `engine/decider.py` — motor de decisión DeepSeek

## Qué hace
1. Ejecuta `python scripts/backup-critical.py`
2. Crea `.bak_<YYYY-MM-DD>/` en la raíz del proyecto
3. Copia archivos con timestamp
4. Reporta archivos respaldados

## Diferencia con /backupall
- `/backup` → respalda archivos críticos individuales (rápido, pre-edit)
- `/backupall` → respalda el proyecto completo (lento, pre-deploy o cierre de sesión)
