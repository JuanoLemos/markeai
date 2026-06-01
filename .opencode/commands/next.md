# /next — Próximos pasos según roadmap + dependencias

Lee `$RM` y `$CHECKLIST`, identifica los próximos 5 items más relevantes para implementar, considerando dependencias y bloqueos.

## Qué hace
1. Lee `$RM` (pendientes por fase)
2. Lee `$CHECKLIST` (items pendientes)
3. Cruza dependencias: items bloqueados por fases anteriores van al final
4. Prioriza: P1 → P2 → P3
5. Devuelve los 5 items más accionables con:
   - ID, fase de origen, prioridad
   - Dependencias (si aplica)
   - Estimación (chica/mediana/grande)
   - Por qué este item es el siguiente lógico
