# GUIA_MULTI_REPO — Guia multi-repositorio v1.0

## Contexto

MarketAI es actualmente un proyecto de un solo repositorio (monorepo). Esta guia documenta como se integrarian multiples repositorios en el ecosistema si se expandiera en el futuro.

## Arquitectura actual (monorepo)

```
MarketAI/
  analyzers/     -> 9 analizadores de mercado
  data/          -> Recolectores y base de datos
  engine/        -> Motor de fusion y decision
  execution/     -> Broker, riesgo, entradas
  learning/      -> Backtest, evolucion, journal
  alerts/        -> Notificaciones
  strategies/    -> Estrategias documentadas
  dashboard.py   -> Interfaz web
  orchestrator.py -> Loop principal
```

## Estrategia multi-repo (futuro)

Si se decide dividir en repos, la separacion recomendada seria:

| Repositorio | Contenido | Dependencia |
|-------------|-----------|-------------|
| `MarketAI-core` | `engine/`, `data/database.py`, `config.yaml` | Ninguna |
| `MarketAI-analyzers` | `analyzers/` | `MarketAI-core` |
| `MarketAI-execution` | `execution/` | `MarketAI-core` |
| `MarketAI-dashboard` | `dashboard.py`, `templates/`, `static/` | `MarketAI-core` |
| `MarketAI-learning` | `learning/` | `MarketAI-core` |

Cada sub-repositorio se publicaria como paquete Python instalable via pip desde GitHub.

## Archivos relacionados

- `AGENTS.md` — Mapeo de directorios del monorepo
- `doc/arch/` — ADRs sobre decisiones arquitectonicas
