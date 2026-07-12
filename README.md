# MarketAI

Sistema de trading automatizado multi-capa impulsado por DeepSeek AI.

## Arquitectura

```
Datos → 9 Analizadores → Fusión → DeepSeek → Ejecución → Journal
```

3 mercados: Polymarket, Forex, Acciones. Perfiles duales: Normal + Fast.

## Inicio rápido

```powershell
venv\Scripts\activate
python orchestrator.py --mode once          # Una iteración
python orchestrator.py --mode loop          # 24/7
.\dashboard.bat                             # Dashboard web :8050
.\tray_app.bat                              # System tray (recomendado)
```

`orchestrator.py` quedó como entry-point liviano; la lógica vive en el paquete `orchestrator/` (`core.py`, `pipeline.py`, `replay.py`). Los analizadores comparten `BaseAnalyzer` (`analyzers/_base.py`) — todos heredan de ahí.

Ver `doc/guias/` para instalación, configuración y uso detallado.

## Tests

```powershell
python -m pytest tests/ -v                 # 159 tests
```

## UI / UX

Dashboard web en `localhost:8050`. Mobile-first: bottom nav 5 tabs (Inicio / Posiciones / Gates / Historial / Ajustes) en mobile, sidebar desktop en >960px. Diseño warm dark con paleta sage / terracotta / mustard. Wireframes de referencia en `doc/arch/wireframes-v2/` (cuando aplique).

Componentes clave:
- `static/style.css` — design system (Outfit + JetBrains Mono, paleta warm dark, cards con radius 16px, bottom nav fixed)
- `templates/overview.html` — 4 cards: HOY (P&L con date range + Realizado + No realizado + sparkline), Posición destacada, Gates mini (R1-R5), Equity total
- `templates/gates.html` — feed de rechazos por gate
- Banner PAPER MODE persistente, no dismissable

Endpoints principales:
- `GET /api/overview/pnl` — 3 números honestos (hoy / realizado / no_realizado) + desde + balance + equity
- `GET /api/gates/recent` — chips R1-R5 + rechazos 24h
- `GET /api/positions`, `/api/signals`, `/api/trades` — datos de operaciones

## Licencia

Uso personal. No apto para producción real sin validación previa.
