# Guía de Instalación

## MarketAI - Sistema de Trading Multi-Capa

---

## Requisitos del Sistema

| Componente | Requisito Mínimo |
|------------|------------------|
| **Python** | 3.10+ |
| **OS** | Windows 10/11, Linux, macOS |
| **RAM** | 4 GB (8 GB recomendado) |
| **Disco** | 500 MB libres |
| **Red** | Conexión a Internet estable |
| **OpenCode** | Última versión |
| **DeepSeek** | API key activa |

---

## Paso 1: Verificar Python

```bash
python --version
# Debe mostrar: Python 3.10.0 o superior
```

Si no está instalado: https://www.python.org/downloads/

---

## Paso 2: Crear Entorno Virtual (Recomendado)

```bash
# Windows
cd C:\xampp\htdocs\MarketAI
python -m venv venv
venv\Scripts\activate

# Linux/macOS
cd /ruta/a/MarketAI
python3 -m venv venv
source venv/bin/activate
```

---

## Paso 3: Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Verificar instalación
```bash
python -c "
import yfinance as yf
import pandas as pd
import numpy as np
from ta import add_all_ta_features
import schedule
print('Todas las dependencias OK')
"
```

---

## Paso 4: Configurar Variables de Entorno

```bash
# Copiar template
copy .env.example .env    # Windows
cp .env.example .env      # Linux/macOS

# Editar .env con tus keys:
# DEEPSEEK_API_KEY=sk-tu-key-aqui
# TELEGRAM_BOT_TOKEN=tu-token
# TELEGRAM_CHAT_ID=tu-chat-id
# POLYMARKET_PRIVATE_KEY=0x...  (opcional, solo para real)
# POLYMARKET_API_KEY=...        (opcional, solo para real)
# POLYMARKET_API_SECRET=...     (opcional, solo para real)
# ALPACA_API_KEY=...            (opcional, solo para real)
# ALPACA_SECRET_KEY=...         (opcional, solo para real)
```

---

## Paso 5: Configurar Mercados

Editar `config.yaml` para habilitar/deshabilitar mercados:

```yaml
markets:
  polymarket:
    enabled: true
    mode: paper               # paper | real
    check_interval_min: 15
    max_position_usd: 50
  forex:
    enabled: true
    pairs: ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCAD=X"]
    mode: paper
    check_interval_min: 60
  stocks:
    enabled: true
    tickers: ["SPY", "QQQ", "AAPL", "MSFT", "TSLA"]
    mode: paper
    check_interval_min: 60
```

---

## Paso 6: Verificar Conexión a Datos

```bash
# Probar Yahoo Finance
python -c "
import yfinance as yf
data = yf.download('SPY', period='1d', interval='1h')
print(f'Yahoo Finance OK: {len(data)} velas')
"

# Probar colectores
python -c "
from data.collector_yfinance import YFinanceCollector
c = YFinanceCollector()
data = c.get_forex_pairs()
print(f'Forex OK: {len(data)} pares')
"
```

---

## Paso 7: Verificar OpenCode

```bash
# Desde la terminal de OpenCode
# Verificar que DeepSeek responde
opencode --version
```

---

## Solución de Problemas

### Error: `ModuleNotFoundError: No module named 'yfinance'`
```bash
pip install yfinance
```

### Error: `SSL: CERTIFICATE_VERIFY_FAILED`
```bash
# Windows: instalar certificados
python -m pip install --upgrade certifi
```

### Error: Polymarket API no responde
```bash
# Verificar conectividad
curl https://clob.polymarket.com
```

### Error: `pip install` lento
```bash
pip install -r requirements.txt --timeout 120
```

---

## Verificación Final

```bash
# Ejecutar tests de colectores
python -m pytest tests/test_collectors.py -v

# Si todo pasa, el sistema está listo
echo "✅ MarketAI instalado correctamente"
```
