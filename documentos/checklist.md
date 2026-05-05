# MarketAI - Checklist de Implementación

## Lista de verificación para cada fase del proyecto

---

## FASE 0: Fundación

### Estructura
- [x] `C:\xampp\htdocs\MarketAI\` creado
- [x] `documentos/` con guia.md, roadmap.md, checklist.md
- [x] `guias/` con guia_instalacion.md, guia_configuracion.md, guia_uso.md
- [x] `data/` con subcarpeta `cache/`
- [x] `analyzers/` con `__init__.py`
- [x] `engine/` con `__init__.py`
- [x] `execution/` con `__init__.py`
- [x] `learning/` con `__init__.py`
- [x] `alerts/` con `__init__.py`
- [x] `strategies/`
- [x] `skills/`
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
- [ ] Token de Telegram configurado (opcional)
- [ ] Polymarket API key configurada (opcional para real)

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
- [x] `collector_news.py` conecta NewsAPI
- [x] Clasificación de sentimiento por keywords
- [x] Cache de 10 min

### Database
- [x] `database.py` crea tablas en SQLite
- [x] Esquema `trades`, `signals`, `market_data`, `strategy_performance`, `portfolio`

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

### Tests
- [x] `tests/test_analyzers.py` pasa
- [x] Cada analyzer devuelve formato consistente
- [x] Scores en rango 0-100

---

## FASE 3: Motor de Decisión

### Fusion
- [x] Pesos configurables por capa y mercado
- [x] Score compuesto calculado
- [x] Confianza basada en consistencia entre capas

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
- [x] Sugiere ajustes a `master_strategy.md`
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
- [x] Loop principal: recolección → análisis → decisión → ejecución → journal
- [x] Scheduling configurable (15/30/60 min)
- [x] Manejo de errores por capa
- [x] Logging a archivo
- [x] Señal de stop manual (archivo `STOP`)

---

## FASE 7: Sistema Completo

### Dashboard Web
- [x] Flask + 5 páginas (Overview, Señales, Trades, Config, Logs)
- [x] Control start/stop loop desde UI
- [x] Configuración editable desde dashboard
- [x] Tema oscuro (4 colores)
- [x] Auto-refresh cada 10s

### Tray App
- [x] Icono $ blanco en system tray
- [x] Minimizar ventana al cerrar
- [x] Menú contextual (Show Dashboard, Pause, Resume, Stop, Exit)
- [x] Tooltip con estado del loop

### Documentación
- [x] README.md (español)
- [x] Roadmap actualizado
- [x] Checklist actualizada
- [x] Guías de instalación, configuración, uso actualizadas

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
- [x] `python -m pytest tests/ -v` → 46/46 tests pasan

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
