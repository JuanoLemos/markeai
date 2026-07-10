# MECANICA-RECOVERY — Auto-reconciliación DB ↔ Brokers

**Fecha:** 2026-07-10
**Tipo:** Mecánica de integridad
**Aplica a:** versión `v1.4.0` y superiores

---

## Definición

Al arrancar el `MarketAIOrchestrator`, se ejecuta automáticamente `_reconcile_db_with_brokers()`. Esta mecánica detecta trades en la DB que el broker ya no tiene en memoria y los marca como `lost_recovery` para que no contaminen las métricas.

## Cuándo corre

- En el `__init__` de `MarketAIOrchestrator`
- Después de cargar todos los componentes
- Antes de la primera iteración
- En cada `python orchestrator.py --mode once|loop|cron|replay`

## Lógica

1. Lee todos los trades con `status='open'` de la DB (`db.get_open_trades()`)
2. Para cada `PaperBroker` (normal + fast), recolecta los `position_id` que tiene en memoria
3. Calcula la diferencia: trades en DB que NO están en ningún JSON
4. Si hay diferencias, marca cada uno con `db.mark_lost_recovery(trade_id, timestamp)`:
   - `status = 'closed'`
   - `exit_reason = 'lost_recovery'`
   - `pnl_usd = NULL`
   - `pnl_pct = NULL`
   - `exit_time = ISO timestamp`
5. Loggea `WARNING: B-N2: Reconciled N stale open trades as 'lost_recovery'`

## Por qué importa

**Antes de esta mecánica:** un crash del orchestrator dejaba trades "zombie" en DB que el sistema nunca cerraba. Las métricas (win rate, PnL, drawdown) se contaminaban con posiciones abiertas de hace semanas/meses que ya no tenían precio.

**Después:** al siguiente boot, esas posiciones desaparecen del cálculo de "trades abiertos" pero quedan registradas en DB con `exit_reason='lost_recovery'` para auditoría. El usuario puede distinguirlas en queries:
```sql
SELECT * FROM trades WHERE exit_reason='lost_recovery';
```

## Tests

`tests/test_ola1_fixes.py` cubre:
- `test_b_n2_mark_lost_recovery_method` — método funciona
- `test_b_n2_reconcile_closes_orphan_open_trades` — borra huérfanos
- `test_b_n2_reconcile_keeps_valid_open_trades` — NO borra válidos
- `test_b_n2_column_alter_for_existing_db` — ALTER defensivo para DBs viejas

## Limitaciones

- Solo funciona para trades que tienen `position_id` registrado. Trades muy viejos (pre-Ola 1) sin `position_id` no se reconcilian — quedan como `open` hasta que el sistema los encuentre y cierre por time_exit.
- Si el broker NO se inicializa correctamente (ej: error de conexión a disk), el `_reconcile` también puede fallar. Está envuelto en try/except, no rompe el boot.
