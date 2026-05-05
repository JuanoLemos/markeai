# /backup — Backup de archivos críticos

Copia los archivos críticos del proyecto a un directorio `.bak_<fecha>/` antes de editarlos.

## Archivos críticos
1. `config.yaml` — configuración central del sistema
2. `.env` — API keys y secretos
3. `orchestrator.py` — loop principal
4. `data/database.py` — schema SQLite
5. `engine/decider.py` — motor de decisión DeepSeek

## Qué hace
1. Crea `.bak_<YYYY-MM-DD>/` en la raíz del proyecto
2. Copia los archivos críticos con timestamp
3. Reporta archivos respaldados

## Diferencia con /backupall
- `/backup` → respalda archivos críticos individuales (rápido, pre-edit)
- `/backupall` → respalda el proyecto completo (lento, pre-deploy o cierre de sesión)
