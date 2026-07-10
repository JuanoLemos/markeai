# Guía de Arquitectura — MarketAI v1.4.0 (post-Ola 1)

**Fecha:** 2026-07-10
**Aplica a:** versión `v1.4.0` y superiores
**Audiencia:** desarrolladores y mantenedores

---

## Visión general

MarketAI v1.4.0 introduce tres cambios estructurales que conviene entender antes de tocar código:

1. **`orchestrator.py` se partió en un package** (`orchestrator/`) con responsabilidades separadas
2. **`BaseAnalyzer` introduce jerarquía** entre los 9 analizadores
3. **Sistema de recovery automático** detecta y reconcilia estados inconsistentes al boot

---

## 1. Estructura del package `orchestrator/`

```
orchestrator/
├── __init__.py      # Re-exports: MarketAIOrchestrator, load_config
├── core.py          # Clase principal, lifecycle, run_*, init_components
├── pipeline.py      # run_iteration, _process_market, _analyze_*, _get_tickers, _snapshot, check_stops_and_evolve
└── replay.py        # run_replay (backtest engine)

orchestrator.py      # Entry point: solo main() + CLI + load_config()
```

### `core.py` (10KB)
- Clase `MarketAIOrchestrator`
- `__init__` (incluye auto-recovery al boot)
- `setup_logging`, `init_components`, `_reconcile_db_with_brokers`
- `run_loop`, `run_once`, `run_backtest`, `run_report`, `run_cron`
- Métodos de 1 línea que delegan a `pipeline.py` y `replay.py`

### `pipeline.py` (19KB)
Funciones standalone que reciben `orch` como primer argumento:
- `run_iteration(orch)` — entry point de cada iteración
- `_process_market(orch, market, cfg)` — loop principal de decisión
- `_analyze_polymarket(orch, cfg)`, `_analyze_forex(orch, cfg)`, `_analyze_stocks(orch, cfg)`
- `_get_tickers(market, cfg)` — utility
- `_snapshot_portfolio(orch)`
- `check_stops_and_evolve(orch)` — corre stops, time-exit, TP, journal

### `replay.py` (7KB)
- `run_replay(orch, market, days, use_deepseek)` — backtest engine aislado

### `orchestrator.py` (raíz, 1.5KB)
Solo entry point. No contiene lógica de trading.

---

## 2. Jerarquía `BaseAnalyzer`

```
analyzers/
├── _base.py         # BaseAnalyzer: empty_result(), ensure_cols(data, fill_volume=False)
├── _utils.py        # silent_import() — para smartmoneyconcepts
├── technical.py     # TechnicalAnalyzer(BaseAnalyzer)
├── fundamental.py   # FundamentalAnalyzer(BaseAnalyzer)
├── macro.py         # MacroAnalyzer(BaseAnalyzer)
├── sentiment.py     # SentimentAnalyzer(BaseAnalyzer)
├── onchain.py       # OnChainAnalyzer(BaseAnalyzer)
├── orderbook.py     # OrderBookAnalyzer(BaseAnalyzer)
├── cross_asset.py   # CrossAssetAnalyzer(BaseAnalyzer)
├── ict_smc.py       # ICTAnalyzer(BaseAnalyzer)
└── adx_regime.py    # ADXRegimeAnalyzer(BaseAnalyzer)
```

### Métodos heredados
- `self.empty_result()` → `{"signal": "WAIT", "score": 50, "reasoning": "insufficient_data", "details": {}}`
- `self.ensure_cols(data, fill_volume=False)` → normaliza columnas a lowercase, opcionalmente llena `volume=0` si falta

### Beneficios
- Si queremos cambiar el formato de "no data" para todos los analyzers, se cambia **una sola vez** en `BaseAnalyzer`
- Tests parametrizados verifican los 9 analyzers con un solo set de aserciones

---

## 3. Sistema de recovery automático

### El problema
Antes de Ola 1, cuando el orchestrator moría abruptamente, las posiciones en memoria del `PaperBroker` se perdían. Al reiniciar, el broker cargaba solo lo que estaba en su JSON (`pb_normal.json`, `pb_fast.json`). Las posiciones "huérfanas" (en DB pero no en JSON) se convertían en zombies que nadie cerraba.

**Evidencia histórica:** 32 trades del 27-29 de mayo de 2026 quedaron `status='open'` en DB porque el sistema cayó el 01/06 y nunca reconcilió.

### La solución
`MarketAIOrchestrator._reconcile_db_with_brokers()` se ejecuta al final de `__init__`:

1. Lee todos los trades con `status='open'` de la DB
2. Recolecta todos los `position_id` conocidos de los JSON de los brokers
3. Si un trade está en DB pero no en ningún JSON → lo marca como `lost_recovery` (closed, pnl=NULL, exit_reason='lost_recovery')

### Schema migration
La columna `position_id` se agregó al schema de `trades`. Un ALTER defensivo en `Database._init_db` agrega la columna a DBs que no la tenían:

```python
cols = [r[1] for r in conn.execute("PRAGMA table_info(trades)").fetchall()]
if "position_id" not in cols:
    conn.execute("ALTER TABLE trades ADD COLUMN position_id TEXT")
```

---

## 4. Logging

- `orchestrator.log` — todo (INFO+)
- `orchestrator.err.log` — solo ERROR+ (separado desde Ola 1)
- `request_id` por iteración: `iter-YYYYMMDDHHMMSS-XXXXXX`, loggeado al inicio de cada iteración

---

## 5. Bugs cerrados en Ola 1

Ver `doc/arch/bugs.md` y `CHANGELOG.md`. Resumen:

- **3 nuevos críticos** (B-N1, B-N2, B-N3): crash recovery, drift JSON↔DB, current_prices para ambos brokers
- **6 P2**: SL/TP defaults, correlation threshold, fused por ticker, API errors, JS api helper, sys.exit
- **6 P3**: refactor analyzers (BaseAnalyzer, _utils), tests con tmp_path, tests analyzers, tests integración

**Total: 15 bugs cerrados en Ola 1.** Sistema pasa de 95 tests a 143.

---

## Cómo contribuir al package

Si necesitás modificar el comportamiento de iteración:
- **Lógica de decisión** → `orchestrator/pipeline.py`
- **Lógica de backtest** → `orchestrator/replay.py`
- **Lifecycle / init** → `orchestrator/core.py`
- **CLI** → `orchestrator.py` (raíz)

Si necesitás modificar comportamiento de un analyzer:
- **Lógica específica** → `analyzers/<nombre>.py` (subclase de `BaseAnalyzer`)
- **Lógica compartida** → `analyzers/_base.py` o `analyzers/_utils.py`

Tests van en `tests/test_*.py`. Usar `tmp_path` para todo lo que escribe a disco (nunca `data/cache/`).
