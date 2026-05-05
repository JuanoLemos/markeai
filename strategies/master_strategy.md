# MarketAI - Master Strategy

## Estrategia Maestra Inicial

---

### Reglas Generales
- Señal LONG cuando score compuesto > 65
- Señal SHORT cuando score compuesto < 35
- WAIT entre 35-65
- Máximo 5% del capital por operación
- Stop-loss obligatorio en todas las operaciones

### Polymarket
- Entrar cuando order book imbalance > 2:1
- Monitorear volumen 24h y actividad de whales
- Salir cuando imbalance < 1.2:1 o evento resuelto
- Máximo 2 posiciones concurrentes

### Forex
- Operar en dirección del DXY (DXY↑ = USD long)
- Evitar operar 30 min antes/después de noticias macro
- Timeframes: 1h para entrada, 4h para confirmación de tendencia

### Acciones
- Solo LONG en tendencia alcista (EMA50 > EMA200)
- Post-earnings: esperar 2 velas horarias antes de entrar
- Salir si VIX > 30

---

> Esta estrategia se auto-actualiza mediante `strategy_evolver.py`
> basado en el rendimiento histórico registrado en `trade_journal.md`
