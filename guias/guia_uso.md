# Guía de Uso

## MarketAI - Sistema de Trading Multi-Capa

---

## 1. Inicio Rápido

### Modo Manual (una iteración)
```bash
# Ejecutar una iteración completa del sistema
python orchestrator.py --mode once
```

### Modo Continuo (loop 24/7)
```bash
# Ejecutar en bucle según scheduling configurado
python orchestrator.py --mode loop
```

### Modo Paper Trading (por defecto)
```bash
# Siempre usar paper primero
python orchestrator.py --mode loop --paper
```

---

## 2. Uso con OpenCode

### Análisis Manual desde OpenCode

```bash
# Preguntar al sistema qué hacer en Polymarket
python analyzers/technical.py --market polymarket --ticker "will-btc-hit-100k-may-2026"
python analyzers/sentiment.py --market polymarket
python analyzers/orderbook.py --market polymarket --slug "will-btc-hit-100k-may-2026"

# O usar el task tool de OpenCode para lanzar subagentes
# task: "Ejecuta análisis técnico de SPY y devuelve RSI, MACD, Bollinger"
```

### Ver Estado Actual
```bash
# Resumen de posiciones abiertas
python -c "
from data.database import Database
db = Database()
trades = db.get_open_trades()
for t in trades: print(t)
"

# Últimas señales generadas
python -c "
from data.database import Database
db = Database()
signals = db.get_recent_signals(limit=10)
for s in signals: print(s)
"

# Balance y métricas
python -c "
from data.database import Database
db = Database()
print(db.get_portfolio_summary())
"
```

### Modificar Estrategia
```bash
# OpenCode lee el journal y sugiere mejoras
# Escribe sugerencias directamente en:
# strategies/master_strategy.md
# strategies/polymarket_rules.md
```

---

## 3. Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `python orchestrator.py --mode once` | Una iteración y termina |
| `python orchestrator.py --mode loop` | Bucle infinito según scheduling |
| `python orchestrator.py --mode once --market polymarket` | Solo Polymarket |
| `python orchestrator.py --mode loop --paper` | Paper trading forzado |
| `python orchestrator.py --backtest` | Ejecuta backtest de estrategias activas |
| `python orchestrator.py --report` | Genera reporte de performance |

---

## 4. Monitoreo

### Logs
```bash
# Ver últimas líneas del log
Get-Content orchestrator.log -Tail 50   # Windows
tail -50 orchestrator.log                # Linux/macOS

# Logs de análisis detallado
Get-Content data/cache/analysis_latest.json | python -m json.tool
```

### Alertas Telegram
Si configuraste Telegram, recibirás:
- ✅ **Entrada**: Señal + mercado + tamaño + precio
- ❌ **Salida**: PnL + duración + razón
- ⚠️ **Error**: Fallo en recolector/analizador
- 📊 **Resumen diario**: 21:00 (configurable)

### Archivos de Estado
```
data/cache/
├── analysis_latest.json    # Último análisis completo
├── polymarket_books.json   # Order books cacheados
├── forex_prices.json       # Precios forex actuales
└── stock_prices.json       # Precios acciones actuales
```

---

## 5. Gestión de Posiciones

### Ver Posiciones Abiertas
```bash
python -c "
from execution.paper_broker import PaperBroker
from data.database import Database

broker = PaperBroker()
print('Balance:', broker.get_balance())
print('Posiciones:', broker.get_positions())
"
```

### Cerrar Posición Manualmente
```bash
python -c "
from data.database import Database
db = Database()
db.close_trade(trade_id=123, exit_reason='manual', pnl=...)
"
```

### Stop Global
```bash
# Crear archivo STOP para detener el orquestador
echo "stop" > STOP
# El orquestador detectará el archivo y se detendrá al final del ciclo

# Eliminar para reanudar
Remove-Item STOP   # Windows
rm STOP            # Linux/macOS
```

---

## 6. Backtesting

```bash
# Backtest de estrategia actual sobre datos históricos
python learning/backtest.py --market polymarket --days 30
python learning/backtest.py --market forex --days 90
python learning/backtest.py --market stocks --days 90

# Con optimización de parámetros
python learning/backtest.py --optimize --market all --days 60

# Resultados guardados en:
# data/cache/backtest_results.json
```

---

## 7. Auto-Aprendizaje

### Revisar Journal
```bash
# Ver trade_journal.md
type strategies\trade_journal.md    # Windows
cat strategies/trade_journal.md     # Linux/macOS
```

### Forzar Evolución de Estrategia
```bash
# OpenCode lee el journal y actualiza la estrategia
python learning/strategy_evolver.py
# Esto genera sugerencias en strategies/master_strategy.md
```

### Skills Auto-Generados
```bash
# Ver skills disponibles
dir skills\*.md       # Windows
ls skills/*.md        # Linux/macOS
```

---

## 8. Solución de Problemas Comunes

### "No hay suficientes datos para análisis"
- Esperar a que los colectores acumulen datos (1-2 días)
- Verificar conectividad con las APIs

### "Señal WAIT constante"
- Revisar config.yaml: ¿pesos de capas muy bajos?
- Verificar que las APIs de datos respondan
- Ajustar `min_confidence` más bajo temporalmente

### "Error: API key no configurada"
- Verificar `.env` tiene las keys
- Ejecutar en modo paper (no requiere keys de exchange)
- DeepSeek API key es la única obligatoria

### "Error: rate limit excedido"
- Aumentar `check_interval_min` en config.yaml
- Los colectores tienen cache automático (5 min default)

---

## 9. Seguridad

- **Nunca** commitees `.env` al repositorio
- **Nunca** compartas private keys de wallet
- El modo paper **no** ejecuta trades reales
- El modo real requiere `mode: real` explícito en config.yaml
- Stop-loss es **obligatorio** en todas las operaciones
- Revisa `orchestrator.log` diariamente al inicio

---

## 10. Ejemplo de Sesión Típica

```bash
# 1. Iniciar sistema en paper
python orchestrator.py --mode loop --paper

# 2. (El sistema corre solo, recibe alertas en Telegram)

# 3. Revisar performance después de 1 semana
python orchestrator.py --report

# 4. Ver journal
type strategies\trade_journal.md

# 5. Ajustar estrategia si es necesario
# (OpenCode sugiere cambios basado en journal)

# 6. Cuando esté consistentemente rentable:
#    - Cambiar mode: paper → real en config.yaml
#    - Configurar API keys de exchange en .env
#    - Empezar con micro-montos ($10-50)
```
