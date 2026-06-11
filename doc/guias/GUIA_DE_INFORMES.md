# GUIA_DE_INFORMES — Ecosistema de reportes v1.0

Descripcion de todas las capacidades de reportes en MarketAI.

## Dashboard Flask

El dashboard web (`dashboard.py`) expone las siguientes rutas:

| Ruta | Descripcion |
|------|-------------|
| `/` | Dashboard principal con resumen del portfolio |
| `/trades` | Historial de trades ejecutados |
| `/signals` | Senales generadas por el motor de decision |
| `/analyzers` | Estado y pesos de los analizadores |
| `/performance` | Metricas de rendimiento acumulado |
| `/backtest` | Resultados de backtesting |
| `/strategy` | Configuracion de estrategias activas |
| `/journal` | Trade journal detallado |
| `/config` | Configuracion actual del sistema |
| `/health` | Estado de salud del sistema |

## Endpoints de debug

Ademas del dashboard, hay endpoints de debug en `orchestrator.py`:

| Endpoint | Proposito |
|----------|-----------|
| `GET /health` | Heartbeat del motor, uptime, ultima iteracion |
| `GET /status` | Estado de cada subsistema (data, engine, execution) |

## Reportes de backtest

Los reportes se generan via `learning/backtest.py` y se persisten en SQLite (tabla `backtest_runs`). Incluyen:

- Sharpe ratio
- Max drawdown
- Win rate
- Total de trades simulados
- Profit factor
- Comparativa contra benchmark

## Reportes de sesion

El comando `/report` genera un resumen de la sesion actual con cambios, bugs y avances.

## Archivos relacionados

- `dashboard.py` — Implementacion del dashboard
- `learning/backtest.py` — Motor de backtest
- `data/database.py` — Schema SQLite (tabla `backtest_runs`)
- `doc/arch/` — Reportes historicos archivados
