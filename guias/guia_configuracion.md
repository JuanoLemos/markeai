# Guía de Configuración

## MarketAI - Sistema de Trading Multi-Capa

---

## 1. Archivo `.env` - Variables de Entorno

### API Keys Obligatorias

```ini
# ── DeepSeek (motor de decisión) ──
DEEPSEEK_API_KEY=sk-tu-api-key-aqui
DEEPSEEK_MODEL=deepseek-v4-pro
```

### API Keys Opcionales

```ini
# ── News (para sentimiento vía NewsAPI) ──
NEWSAPI_KEY=tu-newsapi-key              # https://newsapi.org
CRYPTOPANIC_KEY=tu-cryptopanic-key      # https://cryptopanic.com

# ── Polyscan (para on-chain analyzer) ──
POLYSCAN_API_KEY=tu-key-polygonscan     # https://polygonscan.com/apis

# ── Polymarket (solo para ejecución real) ──
POLYMARKET_PRIVATE_KEY=0x...
POLYMARKET_API_KEY=...
POLYMARKET_API_SECRET=...
POLYMARKET_API_PASSPHRASE=...

# ── Forex / Acciones (solo para ejecución real) ──
ALPACA_API_KEY=...                      # https://alpaca.markets
ALPACA_SECRET_KEY=...
OANDA_API_KEY=...                       # https://developer.oanda.com

# ── Alertas ──
TELEGRAM_BOT_TOKEN=...                  # https://t.me/BotFather
TELEGRAM_CHAT_ID=...                    # https://t.me/userinfobot
DISCORD_WEBHOOK_URL=...                 # Canal → Integraciones → Webhooks
```

---

## 2. Archivo `config.yaml` - Configuración Central

### Mercados

```yaml
markets:
  polymarket:
    enabled: true
    mode: paper                          # paper | real
    check_interval_min: 15
    max_position_usd: 50
    min_confidence: 40
    max_positions_concurrent: 2

  forex:
    enabled: true
    pairs: ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCAD=X", "AUDUSD=X"]
    mode: paper
    check_interval_min: 60
    max_position_usd: 30
    min_confidence: 35

  stocks:
    enabled: true
    tickers: ["SPY", "QQQ", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    mode: paper
    check_interval_min: 60
    max_position_usd: 30
    min_confidence: 40
```

### Capas de Análisis - Pesos

```yaml
layers:
  technical:    { enabled: true, weight_polymarket: 0.25, weight_forex: 0.35, weight_stocks: 0.30 }
  onchain:      { enabled: true, weight_polymarket: 0.25, weight_forex: 0.10, weight_stocks: 0.10 }
  sentiment:    { enabled: true, weight_polymarket: 0.20, weight_forex: 0.20, weight_stocks: 0.25 }
  orderbook:    { enabled: true, weight_polymarket: 0.30, weight_forex: 0.00, weight_stocks: 0.00 }
  fundamental:  { enabled: true, weight_polymarket: 0.00, weight_forex: 0.10, weight_stocks: 0.20 }
  cross_asset:  { enabled: true, weight_polymarket: 0.00, weight_forex: 0.10, weight_stocks: 0.10 }
  macro:        { enabled: true, weight_polymarket: 0.00, weight_forex: 0.25, weight_stocks: 0.15 }
```

### Riesgo

```yaml
risk:
  max_position_pct: 0.05                 # 5% del capital por trade
  max_daily_loss_pct: 0.10              # 10% pérdida diaria máxima, se detiene
  stop_loss_atr_multiplier: 1.5
  take_profit_atr_multiplier: 3.0
  take_profit2_atr_multiplier: 5.0
  correlation_threshold: 0.85
```

### DeepSeek

```yaml
deepseek:
  model: deepseek-v4-pro
  temperature: 0.3
  max_tokens: 4000                       # Necesario para modelos de razonamiento
  timeout_seconds: 30
```

### Alertas

```yaml
alerts:
  telegram:
    enabled: false
    notify_on_entry: true
    notify_on_exit: true
    notify_on_error: true
    daily_summary: true
    daily_summary_time: "21:00"
  discord:
    enabled: false                       # Requiere DISCORD_WEBHOOK_URL en .env
```

### Orchestrador

```yaml
orchestrator:
  log_level: INFO
  log_file: orchestrator.log
  data_cache_ttl_minutes: 5
  max_retries: 3
  retry_delay_seconds: 10
```

---

## 3. Ajuste de Parámetros Comunes

| Situación | Qué ajustar |
|---|---|
| Demasiados WAIT | Bajar `min_confidence` (35-40) |
| Demasiados trades | Subir `min_confidence` (60-70) |
| Sin señales fundamental | Verificar `fundamental.enabled: true` |
| Sin señales on-chain | Verificar `POLYSCAN_API_KEY` en `.env` |
| API rate limits | Subir `check_interval_min` |
| Portfolio muy volátil | Bajar `max_position_pct` |

---

## 4. Verificar Configuración

```bash
python -c "
import yaml
with open('config.yaml', encoding='utf-8') as f:
    c = yaml.safe_load(f)
assert 'markets' in c
assert 'deepseek' in c
assert 'risk' in c
print('Configuración válida ✅')
"
```
