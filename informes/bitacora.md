# Bitácora — MarketAI

Registro cronológico de decisiones, cambios y contexto entre sesiones.

---

## Instancia 1 — 2026-05-05

### Qué se hizo
Migración de metodología OpenCode desde Nemesis Detective a MarketAI.

### Cambios aplicados
- `.opencode/` con 17 comandos slash
- `AGENTS.md` — datos prácticos del proyecto
- `OPENCODE.md` — ancla de sesión
- `documentos/metodologia.md` — taxonomía, jerarquía de cambios, ciclo de instancia
- `skills/backup-pre-edit.md` + `skills/actualizar-docs.md`
- `scripts/backup-critical.py`
- `informes/bitacora.md` — este archivo
- `informes/ideas/` — directorio para ideas de sesión

---

## Instancia 2 — 2026-05-05/06

### Qué se hizo
Auditoría y renovación completa del dashboard (Claude Sonnet 4.6).

### Cambios aplicados
- 6 temas visuales (Light, Bloomberg, Mint, Cyberpunk, Solarized)
- Páginas nuevas: Analytics, Backtest, News, Watchlist, Ticker detail
- Equity curve interactivo con selector de período
- Daily Brief narrativo en español
- Risk Snapshot + Proyección & Racha
- Decision Funnel widget
- Filtros por mercado/decisión en Signals y Trades
- Emojis en navegación, capas, estados
- Selector de tema en Config
- Cierre de posiciones desde dashboard (POST /api/positions/<id>/close)
- Price actual + Δ% en posiciones abiertas

### Bugs documentados
- NoneType en paper_broker cuando DeepSeek devuelve null
- Forex señal SHORT descartada por zona neutra (score 47.3)
- SPY/QQQ sin fundamentals (HTTP 404 en ETFs)

---

## Instancia 3 — 2026-05-16

### Qué se hizo
Implementación de Fase R completa, dual profile, FVG/ICT, ADX regime, trailing stop, partial TP, break-even, time-exit, entry filters.

### Cambios aplicados
- `config.yaml` reescrito con `profiles: { normal, fast }`
- Dual profile en orchestrator.py: dos decisiones/iteración
- `engine/decider.py`: dual prompts (NORMAL_PROMPT / FAST_PROMPT)
- `engine/fusion.py`: threshold configurable, score=50 excluido
- `execution/paper_broker.py`: ATR trailing, partial TP (50%), break-even, time-exit por mercado+estado
- `execution/risk_engine.py`: Fractional Kelly (25%), circuit breakers, ATR position sizing
- `execution/entry_filters.py`: Session hours por perfil, correlation filter
- `analyzers/adx_regime.py`: Trend strength filter
- `analyzers/ict_smc.py`: Order blocks, FVG, liquidity sweep
- `data/collector_news.py`: RSS fallback, rate limit 1 call/iteración
- Tests: 46 → 95
- Modelo: deepseek-v4-pro → deepseek-v4-flash

---

## Instancia 4 — 2026-05-19

### Qué se hizo
Mejoras al sistema tray y dashboard.

### Cambios aplicados
- Tray menu simplificado (▶ Activar, 💀 Kill Services, Reiniciar Servidor)
- Dashboard loop buttons eliminados (control solo desde tray)
- API status via orchestrator.log mod time (<60s)
- Tooltip dual PnL (Normal + Fast)
- VBS launcher invisible (trayapp.vbs)
- Pulse dot status en tray icon

---

## Instancia 5 — 2026-05-26/27

### Qué se hizo
Refinamiento de parámetros, backtest con run_replay, documentación.

### Cambios aplicados
- Backtest redirigido a run_replay (full pipeline en vez de RSI/EMA legacy)
- Timeout backtest: 120s → 600s
- Time-exit condicional por mercado+estado
- guia_motores.md, guia_trading.md, position-sizing-reference.md actualizadas
- roadmap_mejoras.md con fases completadas

---

## Instancia 6 — 2026-05-28

### Qué se hizo
Auto-restart del loop, timeout backtest extendido, persistencia de backtest, limpieza y actualización documental completa.

### Cambios aplicados
- `tray_app.py`: auto-restart loop si muerto >30s
- `dashboard.py`: timeout backtest 120s → 900s
- `templates/backtest.html`: sessionStorage persistencia al cambiar pestañas
- Limpieza de estructura:
  - Eliminado `templates/Claude/v1/` (copias redundantes de templates)
  - Eliminado `backup_dashboard/` (conservado v2)
  - Eliminado `nppBackup/` (basura de editor)
  - Eliminado `documentos/guia.md` (solapaba con `guias/`)
  - Eliminado `strategies/master_strategy.md` (0 bytes)
  - Eliminado `informes/ideas/` (vacío)
  - Movido `guia_trading.md` y `position-sizing-reference.md` a `guias/`
- Documentación actualizada:
  - `documentos/checklist.md` — Fase 9 agregada, 95 tests, 9 páginas, dual profile
  - `documentos/roadmap.md` — 9 analizadores, Fase 9, métricas actualizadas
  - `documentos/metodologia.md` — 9 analizadores, guías actualizadas
  - `guias/guia_configuracion.md` — perfiles, time-exit, flash model
  - `guias/guia_instalacion.md` — pyarrow, RSS fallback, 95 tests
  - `guias/guia_uso.md` — 9 páginas, tray simplificado, dual profile
  - `informes/bitacora.md` — todas las instancias registradas
  - `informes/reglas.md` — 9 analizadores, 6 temas
  - `skills/actualizar-docs.md` — checklist concreto por tipo de cambio
  - `AGENTS.md` — regla post-edit para docs
  - `README.md` — 9 analizadores, 95 tests
