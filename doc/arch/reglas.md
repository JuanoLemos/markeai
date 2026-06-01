# Reglas para agentes de diseño

## Archivos VITALES — NUNCA modificar

| Archivo | Razón |
|---|---|
| `orchestrator.py` | Loop de trading, ejecución, cron, replay |
| `engine/fusion.py` | Motor de fusión de capas |
| `engine/decider.py` | Decisor DeepSeek |
| `execution/paper_broker.py` | Simulación de broker |
| `execution/risk_engine.py` | Motor de riesgo (Kelly, circuit breakers) |
| `execution/entry_filters.py` | Filtros de entrada (sesión, correlación) |
| `execution/executor_polymarket.py` | Ejecutor Polymarket |
| `execution/executor_traditional.py` | Ejecutor Alpaca/OANDA |
| `learning/journal.py` | Trade journal |
| `learning/backtest.py` | Backtesting |
| `learning/strategy_evolver.py` | Auto-evolución de estrategias |
| `analyzers/` (todo el directorio) | Los 9 analizadores |
| `data/collector_yfinance.py` | Colector Yahoo Finance |
| `data/collector_polymarket.py` | Colector Polymarket |
| `data/collector_news.py` | Colector News + sentimiento |
| `data/database.py` | Base de datos SQLite |
| `alerts/notifier.py` | Telegram + Discord |
| `config.yaml` | Configuración central del sistema |
| `.env` | API keys y secretos |
| `.gitignore` | Reglas de git |

## Archivos de DISEÑO — Sí se pueden modificar

| Archivo | Scope |
|---|---|
| `templates/*.html` | HTML, estructura de páginas, gráficos, UX |
| `static/style.css` | CSS, 6 temas visuales, responsive |
| `dashboard.py` | Rutas Flask, endpoints API, lógica de UI |

## Formatos y convenciones

- **Idioma**: español (toda la UI, textos, comentarios)
- **Tema**: oscuro. 6 variantes (Dark, Light, Bloomberg, Mint, Cyberpunk, Solarized)
- **Responsive**: el dashboard debe adaptarse a escritorio y mobile
- **Gráficos**: Plotly para gráficos interactivos, SVG inline para simples
- **Tamaño**: mantener las páginas livianas (< 50 KB de HTML renderizado)

## Reportes

Todo análisis, bug encontrado, punto de vista alternativo o propuesta de diseño se escribe en:

```
doc/arch/news.txt
```

Con formato libre, pero incluyendo siempre:

```
## [Fecha] - [Tema]
Estado: [propuesto / en revisión / implementado]
Descripción: ...
Archivos afectados: [lista]
```
