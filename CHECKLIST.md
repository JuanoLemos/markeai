# MarketAI - Checklist de Implementación

## Lista de verificación para cada fase del proyecto

---

## FASE 0: Fundación

### Estructura
- [x] `C:\xampp\htdocs\MarketAI\` creado
- [x] `ROADMAP.md`, `CHECKLIST.md`, `CHANGELOG.md`, `DILIGENCIA.md` (raíz)
- [x] `doc/arch/` con metodologia.md, bugs.md, bitacora.md, reglas.md
- [x] `doc/guias/` con guia_instalacion.md, guia_configuracion.md, guia_uso.md
- [x] `doc/pendientes/` — ideas de sesión
- [x] `doc/testing/` — test logs
- [x] `skills/` — skills cargables
- [x] `tests/`

### Dependencias
- [x] Python 3.10+ instalado
- [x] `pip install -r requirements.txt` ejecutado sin errores
- [x] Cada dependencia importable
- [x] `py-clob-client` instalado para Polymarket
- [x] `python-telegram-bot` instalado

### Configuración
- [x] `config.yaml` revisado y personalizado por mercado
- [x] `.env` creado (copiar desde `.env.example`)
- [x] API keys configuradas (DeepSeek)
- [x] Token de Telegram configurado (opcional)
- [x] Polymarket API key configurada (opcional para real)

---

## FASE 1: Recolección de Datos

### Polymarket
- [x] `collector_polymarket.py` devuelve mercados activos via CLOB API
- [x] DNS bypass integrado (DoH Google DNS + monkeypatch socket)
- [x] Cache local (5 min)
- [x] Fallback si API no responde

### Yahoo Finance
- [x] `collector_yfinance.py` descarga OHLCV para Forex y Acciones
- [x] Manejo de multi-índice
- [x] Cache de 5 min
- [x] Datos fundamentales (P/E, market cap, beta, etc.)

### News
- [x] `collector_news.py` conecta NewsAPI + CryptoPanic
- [x] RSS fallback (Yahoo Finance, Google News RSS) cuando NewsAPI < 5 artículos
- [x] Rate limit protection: 1 llamada API/iteración (max 96/día)
- [x] Clasificación de sentimiento por keywords
- [x] Cache de 10 min

### Database
- [x] `database.py` crea tablas en SQLite
- [x] Esquema `trades`, `signals`, `market_data`, `strategy_performance`, `portfolio`, `motor_heartbeat`, `backtest_runs`

### Tests
- [x] `tests/test_collectors.py` pasa
- [x] Datos de todos los mercados disponibles
- [x] Database CRUD funcional

---

## FASE 2: Analizadores

### Técnico
- [x] RSI(14) calculado
- [x] MACD(12,26,9) con señal
- [x] Bollinger(20,2) con %B
- [x] EMAs(9,21,50) cruzadas detectadas
- [x] Soportes/resistencias dinámicos
- [x] Score compuesto en formato estándar

### On-Chain
- [x] Consulta de actividad via Polyscan API (Etherscan V2)
- [x] USDC transfers al exchange CLOB (>$10K)
- [x] Flujo neto de exchange calculado
- [x] Score de actividad on-chain compuesto

### Sentimiento
- [x] Clasificación bullish / bearish / neutral por keywords
- [x] Score de intensidad (0-100)
- [x] Headlines extraídas

### Order Book
- [x] Desbalance bid/ask calculado
- [x] Spread relativo
- [x] Profundidad en 5 niveles

### Fundamental
- [x] P/E ratio (trailing + forward)
- [x] Market cap
- [x] Earnings date próximo
- [x] Beta, dividend yield, price-to-book
- [x] Score fundamental compuesto

### Macro
- [x] DXY tracking
- [x] VIX nivel y tendencia
- [x] Score macro compuesto

### Cross-Asset
- [x] SPY/QQQ divergencia
- [x] USD strength patterns

### ADX Regime
- [x] Trend strength filter (ADX > 25)
- [x] Per-profile: Normal=required, Fast=optional
- [x] Score según dirección de tendencia

### ICT/SMC
- [x] Order blocks, FVG (Fair Value Gap)
- [x] Liquidity sweep detection
- [x] Score compuesto ICT (0-100)

### Tests
- [x] `tests/test_analyzers.py` pasa
- [x] Cada analyzer devuelve formato consistente
- [x] Scores en rango 0-100

---

## FASE 3: Motor de Decisión

### Fusion
- [x] Pesos configurables por capa y mercado
- [x] Score compuesto calculado
- [x] Threshold 55/45 LONG/SHORT/WAIT (configurable por perfil)
- [x] Confianza basada en consistencia entre capas
- [x] Capas con score = 50 se excluyen del cómputo

### Decider (DeepSeek)
- [x] Prompt template por mercado
- [x] DeepSeek responde JSON válido (max_tokens=4000)
- [x] Fallback WAIT si respuesta inválida

---

## FASE 4: Ejecución

### Paper Broker
- [x] Slippage configurable (0.1%)
- [x] Comisiones aplicadas (0.1%)
- [x] Balance virtual persistente en JSON
- [x] Stop-loss y take-profit automáticos
- [x] ATR trailing stop dinámico
- [x] Break-even stop (TP1 alcanzado → SL a precio de entrada)
- [x] Partial take-profit (TP1 = 50% cantidad, resto sigue)
- [x] Time-exit condicional por mercado + estado (profit/loss/stagnant)
- [x] SL/TP configurables por perfil (Normal conservador, Fast agresivo)
- [x] Log de todas las operaciones

### Executor Polymarket (Real)
- [ ] Conexión wallet Polygon (private key en .env)
- [ ] Approval de USDC automático
- [ ] `place_order()` funcional
- [x] Estructura preparada (stub)

### Executor Traditional (Real)
- [x] API Alpaca implementada (REST)
- [x] API OANDA implementada (REST)
- [ ] Keys reales configuradas en .env

---

## FASE 5: Auto-Aprendizaje

### Journal
- [x] Cada trade registrado con timestamp
- [x] Post-mortem: entrada, salida, PnL, razones
- [x] Exportable a `trade_journal.md`

### Strategy Evolver
- [x] Detecta patrones ganadores/perdedores
- [x] Sugiere ajustes a estrategias
- [ ] Skills auto-generados en `skills/`

### Backtest
- [x] Walk-forward: train/validation/test
- [x] Sharpe ratio calculado
- [x] Max drawdown histórico

---

## FASE 6: Alertas y Orquestación

### Notifier
- [x] Telegram bot conectado (requiere keys)
- [x] Discord webhook implementado (requiere URL)
- [x] Alertas de entrada/salida/error
- [ ] Resumen diario automático

### Orchestrator
- [x] Loop principal: recolección → análisis → fusión → decisión → ejecución → journal
- [x] Dual profile: Normal + Fast ejecutándose simultáneamente
- [x] Scheduling configurable (15/30/60 min)
- [x] Manejo de errores por capa
- [x] Logging a archivo
- [x] Señal de stop manual (archivo `STOP`)

---

## FASE 7: Sistema Completo

### Dashboard Web
- [x] Flask + 10 páginas (Overview, Señales, Trades, Analytics, Backtest, Config, News, Watchlist, Sandbox, Logs)
- [x] Loop control desde system tray (sin botones en dashboard)
- [x] Configuración editable desde dashboard
- [x] 6 temas visuales (Dark, Light, Bloomberg, Mint, Cyberpunk, Solarized)
- [x] Auto-refresh cada 10s
- [x] Daily Brief con resumen narrativo en español
- [x] Equity curve interactivo con selector de período (1d/7d/30d/Todo)
- [x] Risk Snapshot + Proyección & Racha
- [x] Decision Funnel widget (señales → fused → ejecutadas)
- [x] Ticker detail page (/ticker/<symbol> con chart y trades)
- [x] Filtros por mercado/decisión en Signals y Trades
- [x] API status vía orchestrator.log mod time (<60s)
- [x] sessionStorage persistencia de backtest al cambiar pestañas

### Tray App
- [x] Icono $ blanco en system tray
- [x] VBS launcher invisible (trayapp.vbs)
- [x] Menú contextual (▶ Activar, 💀 Kill Services, Reiniciar Servidor, Reiniciar Dashboard, Mostrar Dashboard)
- [x] Tooltip con PnL dual (Normal + Fast)
- [x] Auto-restart del loop si muerto >30s
- [x] Pulse dot status en icono
- [x] Get-CimInstance para restart_server

### Documentación
- [x] README.md (español)
- [x] Roadmap actualizado
- [x] Checklist actualizada
- [x] Guías de instalación, configuración, uso, motores, usuario actualizadas
- [x] Guías complementarias: COMANDOS.md, position-sizing-reference.md
- [x] Bug tracker ($BUGS) con 35 bugs enumerados, 23 resueltos
- [x] Metodología de proyecto documentada
- [x] Skills: backup-pre-edit + actualizar-docs

---

## FASE 8: Producción

### Pre-Producción
- [ ] 2 semanas de paper trading sin errores
- [ ] Win rate >55% en paper
- [ ] Sharpe >1.0 en paper
- [ ] Drawdown máximo <15%

### Producción Real
- [ ] Capital inicial: $50-100 (micro-montos)
- [ ] Position sizing: 2-5% por trade
- [ ] Stop-loss obligatorio en cada trade
- [ ] Monitoreo diario primera semana
- [ ] Backup de base de datos diario

---

## FASE R: Puesta en Marcha — Probar MarketAI

### R.0 — Entorno
- [x] Abrir PowerShell o CMD
- [x] `cd C:\xampp\htdocs\MarketAI`
- [x] `python --version` → 3.10+
- [x] `python -m venv venv` (crear entorno virtual)
- [x] `venv\Scripts\activate` (activar)
- [x] `pip install -r requirements.txt` (sin errores)

### R.1 — Configurar API Keys
- [x] `copy .env.example .env`
- [x] Editar `.env`: poner `DEEPSEEK_API_KEY=sk-...`
- [x] Verificar que `config.yaml` está en `mode: paper`

### R.2 — Verificar Dependencias
- [x] Import de yfinance, pandas, numpy, ta, yaml, dotenv OK
- [x] Import de collectors, analyzers, engine OK

### R.3 — Probar Recolección de Datos
- [x] SPY, DXY, VIX retornan precios reales
- [x] Polymarket retorna mercados activos
- [x] Resultados no son None/empty

### R.4 — Ejecutar Tests Automáticos
- [x] `python -m pytest tests/ -v` → 98/98 tests pasan

### R.5 — R.13 — Validación completa del pipeline
- [x] Paper trading, señales, DeepSeek, backtest, loop, alertas
- [x] Dashboard web, reportes, archivos generados

### Comando Único de Verificación
```powershell
cd C:\xampp\htdocs\MarketAI; venv\Scripts\activate; `
python -m pytest tests/ -v --tb=short; `
python orchestrator.py --mode once --market stocks; `
Get-Content orchestrator.log -Tail 20
```

---

## FASE 9: Mejoras Continuas

### Ejecución
- [x] ATR trailing stop dinámico
- [x] Partial take-profit (TP1 = 50%)
- [x] Break-even stop al alcanzar TP1
- [x] Conditional time-exit por mercado + estado
- [x] SL/TP configurables por perfil (Normal: 2-5%, Fast: 0.5-1.5%)
- [x] Correlación filter entre posiciones
- [x] Session hours filter (Normal: 18h/día, Fast: 22h/día)
- [x] Kelly criterion (fracción 25%)
- [x] Circuit breakers (daily loss, max drawdown)

### Analizadores
- [x] ADX Regime analyzer (trend strength)
- [x] ICT/SMC analyzer (order blocks, FVG, liquidity)
- [x] RSS fallback para news cuando NewsAPI falla

### Dashboard
- [x] Equity curve interactivo con selector de período
- [x] Daily Brief narrativo en español
- [x] Risk Snapshot (peor caso si todos los stops se ejecutan) — dual profile
- [x] Proyección & Racha
- [x] Decision Funnel (señales → fused → ejecutadas)
- [x] Página /ticker/<symbol> con drill-down
- [x] Página /news con feed + filtros
- [x] Página /watchlist con cross-signals/trades
- [x] Página /sandbox con controles manuales de debug
- [x] StatusMarketAi con heartbeat DB + Bot status
- [x] DeepSeek health check con cache (60s) + modelo desde config
- [x] Endpoint /api/debug para trazabilidad de fuentes
- [x] POST /api/debug/inject-signal para pruebas sintéticas
- [x] POST /api/debug/reset-broker para resetear perfil
- [x] POST /api/debug/motors-clear para limpiar heartbeats
- [x] 6 temas visuales con persistencia localStorage
- [x] sessionStorage persistencia en backtest

### Tray App
- [x] Auto-restart del loop si muerto >30s
- [x] Dual PnL en tooltip
- [x] Menú simplificado (Activar / Kill Services / Reiniciar)
- [x] Pulse dot status

### Otros
- [x] Backtest redirigido a run_replay (full pipeline)
- [x] Timeout backtest: 120s → 900s
- [x] NewsAPI rate limit: 1 llamada/iteración + RSS fallback
- [x] API status via orchestrator.log mod time
- [x] Dual profile: Normal + Fast simultáneos
- [x] Python 3.14.0, yfinance 1.3.0, pystray 0.19.5
- [x] CHANGELOG.md en raíz
- [x] prune_signals() para retención configurable (90d)
- [x] Tabla backtest_runs con snapshot de config

---

## FASE A: Expansión de tickers (ETFs + Index Funds)

| Ítem | Estado | Descripción |
|------|--------|-------------|
| A.1 | ✅ | 8 ETFs + 2 index funds en config.yaml |
| A.2 | ✅ | Matriz de correlación expandida en entry_filters.py |
| A.3 | ✅ | Tests existentes pasan (98/98) |

---

## FASE C: CEDEARs Argentina (BYMA)

| Ítem | Estado | Descripción |
|------|--------|-------------|
| C.1 | ✅ | 7 CEDEARs .BA en config.yaml |
| C.2 | ✅ | get_usd_ars_rate() en collector_yfinance |
| C.3 | ✅ | Precios ARS → pseudo-USD en orchestrator |
| C.4 | ✅ | BYMA session hours (12-19 UTC) en entry_filters.py |
| C.5 | ✅ | Correlación CEDEAR vs subyacente (0.98) bloquea duplicados |
| C.6 | ✅ | market_data cubre todos los 24 tickers |

---

## FASE D: Diligencia — Salud estructural del proyecto

**Objetivo: Mantener integridad de la estructura Diligencia durante y después de adaptaciones.**

| Ítem | Estado | Descripción |
|------|--------|-------------|
| D.1 | ✅ | `$variables` en AGENTS.md resuelven a paths existentes |
| D.2 | ✅ | Comandos usan `$variables` sin paths hardcodeados |
| D.3 | Pendiente | OPENCODE.md y metodologia.md reflejan estructura real |
| D.4 | Pendiente | Ciclos de instancia ejecutables con estructura actual |
| D.5 | ✅ | No quedan directorios legacy con contenido residual |
| D.6 | ✅ | DILIGENCIA.md coincide con estructura real del proyecto |
| D.7 | Pendiente | Dependencias entre archivos de autoridad verificadas |
