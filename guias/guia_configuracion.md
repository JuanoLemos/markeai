# Guía de Configuración

## MarketAI - Sistema de Trading Multi-Capa

---

## 1. Archivo `.env` - Variables de Entorno

### API Keys Obligatorias

```ini
# ── DeepSeek (motor de decisión) ──
DEEPSEEK_API_KEY=sk-tu-api-key-aqui
DEEPSEEK_MODEL=deepseek-v4-pro          # o deepseek-v4-flash para pruebas

# ── News (para sentimiento) ──
NEWSAPI_KEY=tu-newsapi-key            # https://newsapi.org
CRYPTOPANIC_KEY=tu-cryptopanic-key    # https://cryptopanic.com (opcional)
```

### API Keys Opcionales

```ini
# ── Polymarket (solo para ejecución real) ──
POLYMARKET_PRIVATE_KEY=0x...          # Private key de wallet Polygon
POLYMARKET_API_KEY=...
POLYMARKET_API_SECRET=...
POLYMARKET_API_PASSPHRASE=...

# ── Forex / Acciones (solo para ejecución real) ──
ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...
OANDA_API_KEY=...                     # https://developer.oanda.com

# ── Alertas ──
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
DISCORD_BOT_TOKEN=...                 # Opcional
```

---

## 2. Archivo `config.yaml` - Configuración Central

### Estructura completa

```yaml
# ── Mercados ──
markets:
  polymarket:
    enabled: true
    mode: paper                        # paper | real
    check_interval_min: 15
    max_position_usd: 50
    min_confidence: 60                 # Mínima confianza para operar
    max_positions_concurrent: 2
  
  forex:
    enabled: true
    pairs:
      - "EURUSD=X"
      - "GBPUSD=X"
      - "USDJPY=X"
      - "USDCAD=X"
      - "AUDUSD=X"
    mode: paper
    check_interval_min: 60
    max_position_usd: 30
  
  stocks:
    enabled: true
    tickers:
      - "SPY"
      - "QQQ"
      - "AAPL"
      - "MSFT"
      - "GOOGL"
      - "AMZN"
      - "TSLA"
    mode: paper
    check_interval_min: 60
    max_position_usd: 30

# ── Capas de Análisis - Pesos ──
layers:
  technical:
    enabled: true
    weight_polymarket: 0.25
    weight_forex: 0.35
    weight_stocks: 0.30
  
  onchain:
    enabled: true
    weight_polymarket: 0.25
    weight_forex: 0.10
    weight_stocks: 0.10
  
  sentiment:
    enabled: true
    weight_polymarket: 0.20
    weight_forex: 0.20
    weight_stocks: 0.25
  
  orderbook:
    enabled: true
    weight_polymarket: 0.30
    weight_forex: 0.00
    weight_stocks: 0.00
  
  fundamental:
    enabled: false                     # Deshabilitado por defecto
    weight_polymarket: 0.00
    weight_forex: 0.10
    weight_stocks: 0.20
  
  macro:
    enabled: true
    weight_polymarket: 0.00
    weight_forex: 0.25
    weight_stocks: 0.15

# ── Gestión de Riesgos ──
risk:
  max_position_pct: 0.05               # 5% del capital por trade
  max_daily_loss_pct: 0.10             # 10% pérdida diaria máxima
  stop_loss_atr_multiplier: 1.5        # SL = ATR * 1.5
  take_profit_atr_multiplier: 3.0      # TP1 = ATR * 3.0
  take_profit2_atr_multiplier: 5.0     # TP2 = ATR * 5.0
  correlation_threshold: 0.85          # No operar pares >0.85 correlación
  
# ── DeepSeek ──
deepseek:
  model: deepseek-v4-pro
  temperature: 0.3
  max_tokens: 500
  timeout_seconds: 30
  
# ── Alertas ──
alerts:
  telegram:
    enabled: false
    notify_on_entry: true
    notify_on_exit: true
    notify_on_error: true
    daily_summary: true
    daily_summary_time: "21:00"
  
  discord:
    enabled: false

# ── Orchestrador ──
orchestrator:
  log_level: INFO                      # DEBUG | INFO | WARNING | ERROR
  log_file: orchestrator.log
  data_cache_ttl_minutes: 5
  max_retries: 3
  retry_delay_seconds: 10
```

---

## 3. Archivo `config.yaml` - Ejemplo Mínimo

```yaml
markets:
  polymarket:
    enabled: true
    mode: paper
    check_interval_min: 15
    max_position_usd: 50
  forex:
    enabled: true
    mode: paper
  stocks:
    enabled: true
    mode: paper

layers:
  technical: { enabled: true }
  sentiment: { enabled: true }
  orderbook: { enabled: true }

risk:
  max_position_pct: 0.05
  stop_loss_atr_multiplier: 1.5
  take_profit_atr_multiplier: 3.0

deepseek:
  model: deepseek-v4-pro

orchestrator:
  log_level: INFO
```

---

## 4. Estrategias - `strategies/`

### master_strategy.md (se actualiza automáticamente)

```markdown
# Estrategia Maestra MarketAI

## Reglas Generales
- Señal LONG cuando score compuesto > 65
- Señal SHORT cuando score compuesto < 35
- WAIT entre 35-65

## Polymarket
- Entrar cuando order book imbalance > 2:1
- Salir cuando imbalance < 1.2:1 o evento resuelto
- Máximo 2 posiciones concurrentes

## Forex
- Operar en dirección del DXY (DXY↑ = USD long)
- Evitar operar 30 min antes/después de noticias macro
- Timeframes: 1h para entrada, 4h para tendencia

## Acciones
- Solo LONG en tendencia alcista (EMA50 > EMA200)
- Post-earnings: esperar 2 velas horarias antes de entrar
- Salir si VIX > 30 (volatilidad extrema)
```

---

## 5. Verificar Configuración

```python
# test_config.py
import yaml
from pathlib import Path

with open("config.yaml") as f:
    config = yaml.safe_load(f)

# Validar estructura
assert "markets" in config
assert "deepseek" in config
assert "risk" in config
assert config["markets"]["polymarket"]["enabled"] in [True, False]

print("Configuración válida ✅")
```
