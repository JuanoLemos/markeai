# Skill: backup-pre-edit — Backup antes de editar archivos críticos

## Cuándo ejecutar

Siempre antes de editar cualquiera de estos archivos:

| Archivo | Razón |
|---------|-------|
| `config.yaml` | Configuración central — romperlo detiene el sistema |
| `.env` | API keys — pérdida requiere regenerar keys |
| `orchestrator.py` | Loop principal — error rompe todo el pipeline |
| `data/database.py` | Schema SQLite — corromperlo inaccesibiliza la DB |
| `engine/decider.py` | Decisor DeepSeek — error causa decisiones erróneas |

## Comandos

```powershell
# Backup manual de archivo específico
Copy-Item config.yaml ".bak_$(Get-Date -Format 'yyyyMMdd')/config.yaml.bak"

# Backup de archivo con timestamp
$date = Get-Date -Format 'yyyyMMdd-HHmmss'
Copy-Item config.yaml "config.yaml.bak.$date"
```

Los backups se guardan en la raíz del proyecto o en `.bak_<fecha>/`.

## Restaurar

Si un edit sale mal:
```powershell
Copy-Item config.yaml.bak.20260505 config.yaml
```
