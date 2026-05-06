# Bitácora — MarketAI

Registro cronológico de decisiones, cambios y contexto entre sesiones.

---

## Instancia 1 — 2026-05-05

### Qué se hizo
Migración de metodología OpenCode desde Nemesis Detective a MarketAI.

### Cambios aplicados
- `.opencode/` con 17 comandos slash (backup, backupall, checklist, commit, debug, estado, focotx, focoui, focoux, limpiar, newguia, newidea, next, plan, rm, updoc, upguia)
- `AGENTS.md` — datos prácticos del proyecto (skills, comandos, arranque, testing, DB, backup, convenciones, directorios)
- `OPENCODE.md` — ancla de sesión (stack, arquitectura 5 capas, protocolo 5 pasos, reglas de edición, cierre de instancia)
- `documentos/metodologia.md` — metodología de proyecto (taxonomía, jerarquía de cambios, ciclo de instancia, reglas de oro)
- `skills/backup-pre-edit.md` + `skills/actualizar-docs.md` — skills operativos adaptados a MarketAI
- `scripts/backup-critical.py` — script de backup de archivos críticos
- `informes/bitacora.md` — este archivo (creado)
- `informes/ideas/` — directorio para ideas de sesión (creado)

### Archivos existentes que NO se modificaron
- `documentos/roadmap.md` — se mantiene como está (Fase 8 paper trading)
- `documentos/checklist.md` — se mantiene como está
- `informes/reglas.md` — pendiente de revisión vs nueva metodología
- `informes/news.txt` — canal de handoff Claude ↔ DeepSeek (se mantiene)
- Todo el código fuente (engine/, data/, analyzers/, etc.) — sin cambios

### Próximo paso recomendado
Probar los comandos en sesiones reales de trading. El `/backup` ahora ejecuta `scripts/backup-critical.py`.
