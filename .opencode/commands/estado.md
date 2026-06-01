# /estado — Reporte de estado del proyecto

Genera un reporte rápido del estado actual del proyecto.

## Qué hace
1. Último commit (`git log -1 --oneline`)
2. Cambios sin commitear (`git diff --stat`)
3. Lee `$CHECKLIST` + `$RM`, resume pendientes vs DONE
4. Rama actual y estado remoto
5. Tests (`python -m pytest tests/ -v --tb=short` o último resultado conocido)
6. Reporta en formato tabla: área, estado, últimas acciones, próximo paso
