# Ola 06: Finalización — Producción + IA 2.0

**Wave manifest** generado por `/ola planear marketai` el 2026-07-15.

---

## Pendientes cubiertos

| ID | Item | Prioridad | Ola origen | Estado actual |
|----|------|-----------|------------|---------------|
| R89 | Ahorro DeepSeek cost | P1 | Ola 2 | 🔴 Pendiente (parcial: session filter + fusion pre-filter OK) |
| R66 | ETF fundamentals | P2 | Ola 2 | ⏳ Pendiente |
| R86 | Time-exit configurable | P1 | Ola 4 | 🔴 Pendiente |
| R87 | PM bottleneck | P1 | Ola 4 | 🔴 Pendiente |
| R88 | Walk-forward validation | P2 | Ola 4 | 🔴 Pendiente |
| R38-R42 | Producción (paper trade → real) | P1/P2 | Ola 3 | 🔄 En progreso |

---

## Oleadas de ejecución

### Wave 1 — Tareas sin dependencias (paralelo)

| Tarea | ID | Agente | Archivo clave | OnFail |
|-------|----|--------|---------------|--------|
| T1 | R89 | @trader | `pipeline.py`, `config.yaml` | skip |
| T2 | R66 | @sdd-implement | `analyzers/fundamental.py` | skip |

**T1 — R89 Ahorro DeepSeek** (partially done)
- Ya implementado: session filter, fusion pre-filter, profile overnight off
- Pendiente: verificar efectividad en vivo, documentar ahorro real
- Archivo: `orchestrator/pipeline.py`

**T2 — R66 ETF fundamentals**
- Agregar métricas ETF (AUM, expense ratio, YTD return) al fundamental analyzer
- Sin esto, ETFs reciben score=50 neutro siempre
- Archivo: `analyzers/fundamental.py`

---

### Wave 2 — Dependen de Wave 1 (secuencial)

| Tarea | ID | Agente | Archivo clave | OnFail |
|-------|----|--------|---------------|--------|
| T3 | R86 | @trader | `paper_broker.py` | warn |
| T4 | R88 | @sdd-implement | `learning/backtest.py` | warn |

**T3 — R86 Time-exit configurable**
- Implementar tabla `minimal_roi` estilo Freqtrade para cierres por tiempo
- Config en `config.yaml` ya tiene sección `time_exit` lista
- Stub en `paper_broker.py` ya existe
- Archivo: `execution/paper_broker.py`

**T4 — R88 Walk-forward validation**
- Agregar purging-and-embargo al backtest
- Implementado siguiendo patrón ML4T (López de Prado)
- Archivo: `learning/backtest.py`

---

### Wave 3 — Secuencial (depende de Wave 2)

| Tarea | ID | Agente | Archivo clave | OnFail |
|-------|----|--------|---------------|--------|
| T5 | R87 | @sdd-implement | `pipeline.py`, DB | warn |

**T5 — R87 PM bottleneck**
- Crear tabla `gate_rejections` en DB (hoy parsea `orchestrator.log` con regex)
- Agregar endpoint dedicado para consultas de rechazos
- Archivos: `data/database.py`, `dashboard.py`

---

### Wave 4 — Producción (depende de R38 🔄)

| Tarea | ID | Agente | Archivo clave | OnFail |
|-------|----|--------|---------------|--------|
| T6 | R38-R42 | @trader + @sdd-verify | Múltiples | skip |

**T6 — R38-R42 Producción**
- R38: Paper trading validation (actualmente corriendo, monitorear por 2-4 semanas)
- R39: Micro-montos reales ($10-50) — solo si R38 da win rate >50%
- R40: Monitoreo diario con ajustes
- R41: Capital progresivo
- R42: Modo replay histórico
- Esta wave se ejecuta SOLO cuando R38 termine (en ~2 semanas)

---

## Resumen de ejecución

| Wave | Tareas | Tipo | Estado |
|------|--------|------|--------|
| Wave 1 | T1 (R89), T2 (R66) | Paralelo | ⏳ Pendiente |
| Wave 2 | T3 (R86), T4 (R88) | Secuencial | ⏳ Pendiente |
| Wave 3 | T5 (R87) | Secuencial | ⏳ Pendiente |
| Wave 4 | T6 (R38-R42) | Condicional (R38 🔄) | ⏳ Pendiente |

## Archivos relacionados

- `ROADMAP.md` — Roadmap del proyecto
- `doc/olas/` — Otras olas
- `analyzers/fundamental.py` — T2
- `execution/paper_broker.py` — T3
- `learning/backtest.py` — T4
- `data/database.py` — T5
