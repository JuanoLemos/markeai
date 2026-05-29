# Guía de Configuración

## MarketAI - Sistema de Trading Multi-Capa

---

## 1. Archivo `.env` - Variables de Entorno

### API Keys Obligatorias

```ini
# ── DeepSeek (motor de decisión) ──
DEEPSEEK_API_KEY=sk-tu-api-key-aqui
DEEPSEEK_MODEL=deepseek-v4-flash
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
    max_positions_concurrent: 2

  forex:
    enabled: true
    pairs: ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCAD=X", "AUDUSD=X"]
    mode: paper
    check_interval_min: 60
    max_position_usd: 30

  stocks:
    enabled: true
    tickers: ["SPY", "QQQ", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    mode: paper
    check_interval_min: 60
    max_position_usd: 30
```

### Capas de Análisis — 9 Analizadores

```yaml
layers:
  technical:    { enabled: true, weight_forex: 0.35, weight_polymarket: 0.25, weight_stocks: 0.30 }
  onchain:      { enabled: true, weight_forex: 0.10, weight_polymarket: 0.25, weight_stocks: 0.10 }
  sentiment:    { enabled: true, weight_forex: 0.20, weight_polymarket: 0.20, weight_stocks: 0.25 }
  orderbook:    { enabled: true, weight_forex: 0.00, weight_polymarket: 0.30, weight_stocks: 0.00 }
  fundamental:  { enabled: true, weight_forex: 0.10, weight_polymarket: 0.00, weight_stocks: 0.20 }
  macro:        { enabled: true, weight_forex: 0.25, weight_polymarket: 0.00, weight_stocks: 0.15 }
  cross_asset:  { enabled: true, weight_forex: 0.10, weight_polymarket: 0.00, weight_stocks: 0.10 }
  adx_regime:   { enabled: true, weight_forex: 0.10, weight_polymarket: 0.00, weight_stocks: 0.10 }
  ict_smc:      { enabled: true, weight_forex: 0.15, weight_polymarket: 0.00, weight_stocks: 0.10 }
```

### Perfiles (Normal + Fast)

Dos perfiles ejecutándose simultáneamente con parámetros independientes:

```yaml
profiles:
  normal:
    label: Normal
    sl_default: 2.0                      # Stop-loss 2%
    tp_default: 5.0                      # Take-profit 5%
    per_market:
      forex:  { min_confidence: 45 }
      polymarket: { min_confidence: 50 }
      stocks: { min_confidence: 45 }
    filters:
      correlation: true                  # Filtro de correlación
      session: true                      # Solo horas de mercado
      volatility: true                   # Filtro de volatilidad
      adx_alignment: required            # ADX obligatorio
      kelly_positive: true               # Solo si Kelly > 0
      min_confluence: 2                  # Mínimo 2 capas coincidentes

  fast:
    label: Fast
    sl_default: 0.5                      # Stop-loss 0.5%
    tp_default: 1.5                      # Take-profit 1.5%
    per_market:
      forex:  { min_confidence: 30 }
      polymarket: { min_confidence: 35 }
      stocks: { min_confidence: 30 }
    filters:
      correlation: false
      session: true                      # 22h/día en vez de 18h
      volatility: false
      adx_alignment: optional
      kelly_positive: true
      min_confluence: 1                  # Mínimo 1 capa
```

### Time-Exit (Cierre por tiempo)

```yaml
time_exit:
  default:
    base_hours: 72    loss_hours: 48    profit_hours: 120    stagnant_hours: 36
  forex:
    base_hours: 96    loss_hours: 48    profit_hours: 168    stagnant_hours: 36
  polymarket:
    base_hours: 336   loss_hours: 168   profit_hours: 504    stagnant_hours: 72
  stocks:
    base_hours: 72    loss_hours: 36    profit_hours: 120    stagnant_hours: 24
```

### Riesgo

```yaml
risk:
  max_daily_loss_pct: 0.10              # 10% pérdida diaria → se detiene
  correlation_threshold: 0.85            # Máxima correlación permitida
```

### DeepSeek

```yaml
deepseek:
  model: deepseek-v4-flash
  temperature: 0.3
  max_tokens: 4000
  timeout_seconds: 30
```

---

## 3. Ajuste de Parámetros Comunes

| Situación | Qué ajustar |
|---|---|
| Demasiados WAIT | Bajar `min_confidence` en el perfil (30-40) |
| Demasiados trades | Subir `min_confidence` (60-70) o subir `min_confluence` |
| Perfil Normal muy lento | Revisar `adx_alignment: required` (cambiarlo a optional) |
| Perfil Fast muy agresivo | Subir `sl_default` o bajar `max_position_pct` |
| Sin señales fundamental | Verificar `fundamental.enabled: true` |
| Sin señales on-chain | Verificar `POLYSCAN_API_KEY` en `.env` |
| API rate limits | Subir `check_interval_min` |
| Portfolio muy volátil | Bajar `max_position_pct` en el perfil |

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
assert 'profiles' in c
assert 'normal' in c['profiles']
assert 'fast' in c['profiles']
print('Configuración válida ✅')
"
```
