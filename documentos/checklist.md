# MarketAI - Checklist de Implementación

## Lista de verificación para cada fase del proyecto

---

## FASE 0: Fundación

### Estructura
- [ ] `C:\xampp\htdocs\MarketAI\` creado
- [ ] `documentos/` con guia.md, roadmap.md, checklist.md
- [ ] `guias/` con guia_instalacion.md, guia_configuracion.md, guia_uso.md
- [ ] `data/` con subcarpeta `cache/`
- [ ] `analyzers/` con `__init__.py`
- [ ] `engine/` con `__init__.py`
- [ ] `execution/` con `__init__.py`
- [ ] `learning/` con `__init__.py`
- [ ] `alerts/` con `__init__.py`
- [ ] `strategies/`
- [ ] `skills/`
- [ ] `tests/`

### Dependencias (ver requirements.txt)
- [ ] Python 3.10+ instalado
- [ ] `pip install -r requirements.txt` ejecutado sin errores
- [ ] Cada dependencia importable (`python -c "import yfinance; print('ok')"`)
- [ ] `py-clob-client` instalado para Polymarket
- [ ] `python-telegram-bot` instalado

### Configuración
- [ ] `config.yaml` revisado y personalizado por mercado
- [ ] `.env` creado (copiar desde `.env.example`)
- [ ] API keys configuradas (DeepSeek)
- [ ] Token de Telegram configurado (opcional)
- [ ] Polymarket API key configurada (opcional para real)

---

## FASE 1: Recolección de Datos

### Polymarket
- [ ] `collector_polymarket.py` devuelve order book de mercado
- [ ] Manejo de rate limits (max 10 req/s)
- [ ] Cache local para evitar llamadas repetidas
- [ ] Fallback si API no responde

### Yahoo Finance
- [ ] `collector_yfinance.py` descarga OHLCV para Forex
- [ ] Descarga OHLCV para Acciones
- [ ] Manejo de tickers con multi-índice
- [ ] Cache de 1 minuto para evitar descargas duplicadas

### News
- [ ] `collector_news.py` conecta NewsAPI
- [ ] Conecta CryptoPanic RSS
- [ ] Parseo de artículos a texto plano
- [ ] Filtrado por relevancia (keywords configurables)

### Database
- [ ] `database.py` crea tablas en SQLite
- [ ] Esquema `trades`: id, market, signal, entry, exit, pnl, timestamp
- [ ] Esquema `signals`: id, timestamp, market, layer_scores, decision
- [ ] Esquema `market_data`: timestamp, ticker, open, high, low, close, volume
- [ ] Esquema `strategy_performance`: strategy, win_rate, sharpe, trades_count

### Tests
- [ ] `tests/test_collectors.py` pasa
- [ ] Datos de todos los mercados disponibles
- [ ] Database CRUD funcional

---

## FASE 2: Analizadores

### Técnico
- [ ] RSI(14) calculado correctamente
- [ ] MACD(12,26,9) con señal
- [ ] Bollinger(20,2) con %B
- [ ] EMAs(9,21,50) cruzadas detectadas
- [ ] Soportes/resistencias dinámicos (rolling min/max)
- [ ] Score compuesto devuelto en formato estándar

### On-Chain
- [ ] Consulta de actividad de whales (Polyscan)
- [ ] Flujos netos de exchange
- [ ] Transacciones grandes (>$100K) detectadas
- [ ] Score de actividad on-chain

### Sentimiento
- [ ] NLP de noticias vía DeepSeek
- [ ] Clasificación: bullish / bearish / neutral
- [ ] Score de intensidad (0-100)
- [ ] Palabras clave extraídas

### Order Book
- [ ] Desbalance bid/ask calculado (bid_volume / ask_volume)
- [ ] Spread relativo
- [ ] Profundidad en 5 niveles
- [ ] Detección de spoofing (órdenes grandes canceladas rápido)

### Fundamental
- [ ] P/E ratio actual
- [ ] Market cap
- [ ] Earnings date próximo
- [ ] Volumen relativo vs promedio 20d
- [ ] Score fundamental compuesto

### Macro
- [ ] DXY tracking
- [ ] VIX nivel y tendencia
- [ ] Tasas de referencia (Fed, ECB, BOE, BOJ)
- [ ] CPI más reciente
- [ ] Score macro compuesto

### Cross-Asset
- [ ] Matriz de correlación rolling 30d
- [ ] Z-score de pares correlacionados
- [ ] Alertas de divergencia (>2σ)

### Tests
- [ ] `tests/test_analyzers.py` pasa
- [ ] Cada analyzer devuelve formato consistente
- [ ] Scores en rango 0-100

---

## FASE 3: Motor de Decisión

### Fusion
- [ ] Normalización de scores (0-100)
- [ ] Pesos configurables por capa y mercado
- [ ] Score compuesto calculado
- [ ] Confianza calculada (basada en consistencia entre capas)

### Decider (DeepSeek)
- [ ] Prompt template por mercado
- [ ] Incluye datos numéricos + scores
- [ ] DeepSeek responde JSON válido
- [ ] Validación de campos requeridos
- [ ] Fallback WAIT si respuesta inválida

### Tests
- [ ] Prompts testeados manualmente
- [ ] Respuestas JSON siempre parseables
- [ ] Decisiones coherentes en casos borde

---

## FASE 4: Ejecución

### Paper Broker
- [ ] Slippage configurable (default 0.1%)
- [ ] Comisiones aplicadas
- [ ] Fills parciales simulados
- [ ] Balance virtual persistente
- [ ] Log de todas las operaciones

### Executor Polymarket (Real)
- [ ] Conexión wallet Polygon (private key en .env)
- [ ] Approval de USDC automático
- [ ] `place_order()` funcional
- [ ] Cancelación de órdenes
- [ ] Verificación de fills

### Executor Traditional (Real)
- [ ] Estructura para Alpaca listo
- [ ] Estructura para OANDA listo
- [ ] Keys placeholder desde .env

---

## FASE 5: Auto-Aprendizaje

### Journal
- [ ] Cada trade registrado con timestamp
- [ ] Post-mortem: entrada, salida, PnL, razones
- [ ] Exportable a `trade_journal.md`

### Strategy Evolver
- [ ] OpenCode lee journal semanalmente
- [ ] Detecta patrones ganadores/perdedores
- [ ] Sugiere ajustes a `master_strategy.md`
- [ ] Skills auto-generados en `skills/`

### Backtest
- [ ] Walk-forward: train/validation/test
- [ ] Sharpe ratio calculado
- [ ] Max drawdown histórico
- [ ] Optimización de parámetros

---

## FASE 6: Alertas y Orquestación

### Notifier
- [ ] Telegram bot conectado
- [ ] Formato embed: señal, mercado, tamaño, razón
- [ ] Alertas de entrada/salida/stop-loss/take-profit
- [ ] Resumen diario automático

### Orchestrator
- [ ] Loop principal: recolección → análisis → decisión → ejecución → journal
- [ ] Scheduling configurable (15/30/60 min)
- [ ] Manejo de errores con retry
- [ ] Logging a archivo
- [ ] Señal de stop manual (archivo `STOP`)

---

## FASE 7: Producción

### Pre-Producción
- [ ] 2 semanas de paper trading sin errores
- [ ] Win rate >55% en paper
- [ ] Sharpe >1.0 en paper
- [ ] Drawdown máximo <15%
- [ ] Código revisado y limpio

### Producción Real
- [ ] Capital inicial: $50-100 (micro-montos)
- [ ] Position sizing: 2-5% por trade
- [ ] Stop-loss obligatorio en cada trade
- [ ] Monitoreo diario primera semana
- [ ] Backup de base de datos diario

### Post-Producción
- [ ] Dashboard de métricas (opcional web)
- [ ] Refinamiento continuo de estrategias
- [ ] Skills auto-generados revisados manualmente
- [ ] Nuevos mercados añadidos progresivamente

---

## Checklist Rápido Diario

- [ ] Sistema corriendo (verificar orchestrator.log)
- [ ] Trades del día revisados
- [ ] Balance actual vs ayer
- [ ] Alertas Telegram funcionando
- [ ] Journal del día OK
- [ ] Sin errores en logs

---

## Checklist Semanal

- [ ] Journal semanal revisado (trade_journal.md)
- [ ] Estrategias evaluadas y ajustadas
- [ ] Skills revisados/actualizados
- [ ] Backtest de nuevas señales
- [ ] Dependencias actualizadas (pip list --outdated)
- [ ] Base de datos respaldada

---

## FASE R: Puesta en Marcha — Probar MarketAI

Checklist paso a paso para verificar que MarketAI funciona correctamente de principio a fin.

---

### R.0 — Entorno

- [ ] Abrir PowerShell o CMD
- [ ] `cd C:\xampp\htdocs\MarketAI`
- [ ] `python --version` → 3.10+
- [ ] `python -m venv venv` (crear entorno virtual)
- [ ] `venv\Scripts\activate` (activar)
- [ ] `pip install -r requirements.txt` (sin errores)
- [ ] `pip list` verifica: `yfinance`, `pandas`, `numpy`, `ta`, `pyyaml`, `python-dotenv`, `schedule`

---

### R.1 — Configurar API Keys

- [ ] `copy .env.example .env`
- [ ] Editar `.env`: poner `DEEPSEEK_API_KEY=sk-...` (la única obligatoria)
- [ ] Editar `.env` (opcional): `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- [ ] Verificar que `config.yaml` está en `mode: paper` (por defecto OK)

---

### R.2 — Verificar Dependencias

- [ ] `python -c "import yfinance; print('yfinance OK')"`
- [ ] `python -c "import pandas, numpy, ta; print('analytics OK')"`
- [ ] `python -c "import yaml, dotenv; print('config OK')"`
- [ ] `python -c "from data.collector_yfinance import YFinanceCollector; print('collectors OK')"`
- [ ] `python -c "from analyzers.technical import TechnicalAnalyzer; print('analyzers OK')"`
- [ ] `python -c "from engine.fusion import FusionEngine; print('engine OK')"`

---

### R.3 — Probar Recolección de Datos

- [ ] `python -c "from data.collector_yfinance import YFinanceCollector; c=YFinanceCollector(); print('SPY:', c.get_current_price('SPY')); print('DXY:', c.get_dxy()); print('VIX:', c.get_vix())"`
- [ ] `python -c "from data.collector_polymarket import PolymarketCollector; c=PolymarketCollector(); print('Markets:', len(c.get_active_markets(5)))"`
- [ ] Verificar que los resultados NO son None/empty

---

### R.4 — Ejecutar Tests Automáticos

- [ ] `python -m pytest tests/test_collectors.py -v` → tests de colectores + database
- [ ] `python -m pytest tests/test_analyzers.py -v` → ~20 tests con datos sintéticos
- [ ] `python -m pytest tests/ -v` → todos los tests juntos
- [ ] Corregir cualquier error antes de continuar

---

### R.5 — Primera Iteración (Paper Trading)

- [ ] `python orchestrator.py --mode once --market stocks`
- [ ] Leer el log: `Get-Content orchestrator.log -Tail 30`
- [ ] Verificar que se creó la base de datos: `dir data\market.db`
- [ ] Verificar que se crearon señales: `python -c "from data.database import Database; db=Database(); print('Signals:', db.get_recent_signals(5))"`
- [ ] Verificar el journal: `type strategies\trade_journal.md`

---

### R.6 — Iterar los 3 Mercados

- [ ] `python orchestrator.py --mode once`
- [ ] Debe ejecutar: Polymarket → Forex → Acciones
- [ ] Revisar log por señales generadas
- [ ] Si no hay señal, verificar el archivo de estado: `type data\cache\paper_broker_state.json`

---

### R.7 — Verificar Decisión DeepSeek

- [ ] Si hay `DEEPSEEK_API_KEY` real:
  - [ ] Ver en el log la línea: `DeepSeek decision: LONG/SHORT (conf:70)`
  - [ ] Verificar trade registrado en paper broker
  - [ ] Verificar que apareció en `strategies/trade_journal.md`
- [ ] Si NO hay API key:
  - [ ] Verificar log: debe decir `DeepSeek: WAIT (reasoning: no_api_key)`
  - [ ] El sistema sigue funcionando, solo no toma decisiones automáticas

---

### R.8 — Backtest

- [ ] `python orchestrator.py --mode backtest --market stocks`
- [ ] Verificar salida con win rate, Sharpe, profit factor
- [ ] `python orchestrator.py --mode backtest --market forex`
- [ ] Si los resultados son malos (win rate <40%), ajustar `config.yaml`

---

### R.9 — Modo Loop (24/7)

- [ ] `python orchestrator.py --mode loop --paper`
- [ ] El sistema corre según los intervalos de `config.yaml` (15 min Polymarket, 60 min Forex/Stocks)
- [ ] Detener: crear archivo `STOP` en la raíz del proyecto:
  - [ ] `echo "stop" > STOP`
  - [ ] El loop se detiene al final del ciclo actual

---

### R.10 — Alertas Telegram (Opcional)

- [ ] Crear bot con [@BotFather](https://t.me/BotFather)
- [ ] Obtener chat ID con [@userinfobot](https://t.me/userinfobot)
- [ ] Agregar `.env`: `TELEGRAM_BOT_TOKEN=...` y `TELEGRAM_CHAT_ID=...`
- [ ] En `config.yaml`: `alerts.telegram.enabled: true`
- [ ] Ejecutar `python orchestrator.py --mode once` y verificar alerta

---

### R.11 — Validación Rápida de Cada Módulo

| Comando | Qué verifica |
|---------|-------------|
| `python -c "from execution.paper_broker import PaperBroker; pb=PaperBroker(); t=pb.open_position('test','SPY','LONG',400,50,2,5); print(t); pb.close_position(t['id'],410,'tp'); print(pb.get_summary())"` | Paper broker: apertura, cierre, PnL |
| `python -c "from engine.fusion import FusionEngine; fe=FusionEngine({'layers':{'technical':{'enabled':True,'weight_polymarket':1.0}}}); print(fe.fuse({'technical':{'signal':'LONG','score':80}},'polymarket'))"` | Fusion engine con una capa |
| `python -c "from engine.decider import DeepSeekDecider; d=DeepSeekDecider(); print(d.decide('test','TICKER',{'signal':'LONG','score':65,'confidence':70},{},{}))"` | DeepSeek decider sin API key (debe devolver WAIT) |
| `python -c "from learning.backtest import Backtester; import pandas as pd, numpy as np; np.random.seed(0); d=pd.DataFrame({'close':100+np.cumsum(np.random.randn(200))}, index=pd.date_range('2026-01-01',periods=200,freq='h')); bt=Backtester(); print(bt.run('test','X',d))"` | Backtester con datos sintéticos |

---

### R.12 — Resumen de Archivos Generados

Después de la primera ejecución exitosa, deben existir:

- [ ] `data/market.db` — Base de datos SQLite con trades, señales, market_data
- [ ] `data/cache/` — Datos cacheados de colectores
- [ ] `data/cache/paper_broker_state.json` — Estado del paper broker
- [ ] `strategies/trade_journal.md` — Journal de trades ejecutados
- [ ] `orchestrator.log` — Log de operación
- [ ] `strategies/master_strategy.md` — Estrategia actual (se auto-actualiza)

---

### R.13 — Primeros Resultados Esperados

| Escenario | Resultado esperado |
|-----------|-------------------|
| Sin DeepSeek key | Sistema corre, señales se generan, pero no hay trades (todo WAIT) |
| Con DeepSeek key | Sistema decide LONG/SHORT, paper broker ejecuta, journal registra |
| Backtest | Win rate 40-60% con datos de 3 meses (depende del mercado) |
| Loop mode | Iteraciones cada 15-60 min según config |
| Alertas | Recibir notificaciones de entrada/salida en Telegram |

---

### Comando Único de Verificación Rápida

```powershell
cd C:\xampp\htdocs\MarketAI; venv\Scripts\activate; `
python -m pytest tests/ -v --tb=short; `
python orchestrator.py --mode once --market stocks; `
Get-Content orchestrator.log -Tail 20
```

Esto: corre tests → ejecuta iteración → muestra log. Si todo sale verde, MarketAI está listo.
