# Manual de Usuario — MarketAI

## Sistema de Trading Automático con Inteligencia Artificial

---

## 1. ¿Qué es MarketAI?

MarketAI es un **robot de trading automático** que compra y vende en los mercados financieros usando Inteligencia Artificial (DeepSeek) para decidir cuándo y qué operar.

**En simple:** El sistema mira datos del mercado 24/7, analiza precios, noticias y tendencias, y decide automáticamente si comprar, vender o esperar. Todo sin que nadie tenga que mirar pantallas.

### ¿Qué mercados opera?

| Mercado | Ejemplos | ¿Qué hace? |
|---|---|---|
| **Acciones** (Stocks) | SPY, AAPL, MSFT, TSLA | Compra acciones de empresas |
| **Forex** | EUR/USD, GBP/USD | Compra/vende divisas (dólares, euros) |
| **Predicciones** (Polymarket) | Eventos políticos, deportivos | Apuesta sobre resultados de eventos |

### Modo paper vs Real

| Modo | ¿Usa plata real? | Para qué sirve |
|---|---|---|
| **Paper** (predeterminado) | ❌ No, es simulación | Probar y aprender sin riesgo |
| **Real** | ✅ Sí, con tu dinero | Solo cuando estés seguro de resultados |

> **Por defecto, MarketAI siempre arranca en modo PAPER.** Nunca pone dinero real a menos que cambies manualmente la configuración.

---

## 2. Conceptos básicos — Explicados simple

| Término | Significado | En simple |
|---|---|---|
| **LONG** | Señal de COMPRA | Esperás que el precio suba |
| **SHORT** | Señal de VENTA | Esperás que el precio baje |
| **WAIT** | Señal de ESPERA | Mejor no hacer nada hoy |
| **SL (Stop Loss)** | Límite de pérdida | Si la operación pierde X%, se cierra sola |
| **TP (Take Profit)** | Límite de ganancia | Si la operación gana X%, se cierra sola |
| **Win Rate** | % de aciertos | Cada 100 trades, cuántos ganaron vs perdieron |
| **Balance** | Dinero disponible | Lo que tenés en la cuenta |
| **Equity Curve** | Curva de resultados | Gráfico que muestra si vas ganando o perdiendo |
| **Confianza** | Seguridad de la señal | 0 = nada seguro, 100 = muy seguro |
| **Exposición** | Cuánto dinero arriesgás | % del total en operaciones abiertas |

### Ciclo de vida de una operación

```
1. MarketAI analiza el mercado → detecta oportunidad
2. Genera señal LONG o SHORT (con confianza)
3. DeepSeek IA decide si ejecutar
4. Abre la operación con SL y TP
5. Monitorea el precio
6. Cierra solo cuando:
   a) Se activa el SL (pérdida) → se corta a tiempo
   b) Se activa el TP (ganancia) → se toma ganancia
   c) Pasa demasiado tiempo → cierre por tiempo
```

---

## 3. Instalación — Primeros pasos

### Requisitos

- Windows 10/11
- Python 3.10+
- Conexión a internet estable
- API key de DeepSeek (se obtiene en deepseek.com)

### Paso a paso

```powershell
# 1. Abrir PowerShell en la carpeta del proyecto
cd C:\xampp\htdocs\MarketAI

# 2. Crear entorno virtual (solo la primera vez)
python -m venv venv

# 3. Activar entorno virtual
venv\Scripts\activate

# 4. Instalar dependencias (solo la primera vez)
pip install -r requirements.txt

# 5. Configurar API keys
copy .env.example .env
# Editar .env y poner DEEPSEEK_API_KEY=sk-tu-key-aqui

# 6. Arrancar el sistema
.\tray_app.bat
```

Después de estos pasos, aparece un icono `$` blanco en la bandeja del sistema (al lado del reloj). **MarketAI ya está corriendo.**

---

## 4. El Dashboard — Página por página

Para abrir el dashboard: click derecho en el icono `$` → "Mostrar Dashboard" → se abre en el navegador (http://localhost:8050).

### 4.1 Overview (Inicio)

Es la página principal. Muestra todo de un vistazo.

```
┌──────────────────────────────────────────────────────────────┐
│  Normal                         │  Fast                       │
│  Balance: $998                   │  Balance: $1,004             │
│  PnL: -$2.00 (-0.2%)           │  PnL: +$4.00 (+0.4%)        │
│  En operación: 2                │  En operación: 5             │
│  Aciertos: 1/3 (33%)           │  Aciertos: 8/12 (66%)       │
└──────────────────────────────────────────────────────────────┘

Gráfico Equity Curve: ─────────────── línea subiendo/bajando
```

**Dos columnas** (Normal y Fast) son dos formas de operar que se ejecutan al mismo tiempo (ver sección 7).

| Indicador | Qué significa |
|---|---|
| Balance | Cuánto dinero tiene virtualmente |
| PnL | Ganancia (+) o pérdida (-) total |
| En operación | Operaciones abiertas en este momento |
| Aciertos | Trades ganados / total trades |
| Equity Curve | Si la línea sube → vas ganando. Si baja → vas perdiendo |

### 4.2 Señales

Cada vez que MarketAI analiza el mercado, genera una **señal**. Esta tabla muestra las últimas.

```
┌───────┬──────────┬────────┬──────────┬──────────┐
│ Hora  │ Mercado  │ Ticker │ Decisión │ Confianza│
├───────┼──────────┼────────┼──────────┼──────────┤
│ 14:30 │ forex    │ EURUSD │ SHORT    │ 80       │
│ 14:25 │ stocks   │ AAPL   │ WAIT     │ 0        │
│ 14:20 │ forex    │ GBPUSD │ LONG     │ 65       │
└───────┴──────────┴────────┴──────────┴──────────┘
```

| Decisión | Color | Significado |
|---|---|---|
| 🟢 LONG | Verde | Señal de compra |
| 🔴 SHORT | Rojo | Señal de venta |
| 🟠 WAIT | Naranja | Esperar, no operar |
| Confianza 80/100 | — | Más alto = más seguro |

Cada fila se puede expandir (click) para ver qué detectó cada analizador.

### 4.3 Trades

Muestra el historial de operaciones abiertas y cerradas.

```
┌──────────┬────────┬────────┬───────┬────────┬────────┬────────┬──────────┐
│ Fecha   │ Mercado│ Ticker │ Señal │ Entrada│ Salida │ PnL   │ Estado   │
├──────────┼────────┼────────┼───────┼────────┼────────┼────────┼──────────┤
│ 05-19   │ stocks │ AAPL   │ LONG  │ $284   │ $287   │ +$3.00│ closed   │
│ 05-18   │ forex  │ EURUSD │ SHORT │ 1.101  │ 1.099  │ +$0.20│ closed   │
│ 05-17   │ stocks │ TSLA   │ LONG  │ $392   │ —      │ —     │ abierta  │
└──────────┴────────┴────────┴───────┴────────┴────────┴────────┴──────────┘
```

- **PnL positivo (verde)** = ganaste plata
- **PnL negativo (rojo)** = perdiste plata
- **Estado "abierta"** = todavía no se cerró

### 4.4 Analytics

Gráficos avanzados para ver patrones:

| Gráfico | Qué muestra |
|---|---|
| **Distribución de Confianza** | Cada cuánto el sistema está muy seguro vs dudoso |
| **Actividad por Capa** | Qué analizadores aportan más señales |
| **Win Rate por Hora** | A qué horas del día rinde mejor |
| **Rendimiento por Ticker** | Con qué activo (AAPL, EURUSD, etc.) se gana más |

### 4.5 Backtest

Simula cómo se habría comportado MarketAI en los últimos 90 días. Sirve para probar la configuración sin esperar.

**¿Cómo se usa?**
```
1. Click en "▶ Backtest Forex" o "▶ Backtest Stocks"
2. Esperar 30-60 segundos (el sistema analiza 90 días de datos históricos)
3. Aparece una tabla con los resultados por ticker
```

**Qué significa cada columna:**

| Columna | Significado |
|---|---|
| **Ticker** | Activo analizado |
| **Trades** | Cantidad de operaciones generadas en la simulación |
| **W/L** | Wins (ganadas) / Losses (perdidas) |
| **Win Rate** | % de aciertos sobre el total |
| **PnL** | Ganancia (+) o pérdida (-) total simulada |
| **Sharpe** | Indicador de riesgo/rentabilidad. >1 = bueno, >2 = excelente |
| **Profit Factor** | Cada $1 perdido, cuánto se ganó. >1.5 = bueno |

> El backtest **no usa DeepSeek** para ahorrar costos. Usa directamente la fusión de analizadores.

### 4.6 Config

Aquí se cambia la configuración de MarketAI. Los cambios se guardan a `config.yaml` (el archivo principal del sistema).

**Las secciones están en acordeones:** click en cada título para expandir o colapsar.

| Sección | Qué se configura |
|---|---|
| **Mercados** | Qué mercados operar (activo/inactivo), cada cuánto revisar (minutos), tamaño máximo por operación, confianza mínima |
| **Riesgo** | SL mínimo/máximo, TP mínimo/máximo, exposición total máxima, límite de pérdida diaria |
| **DeepSeek** | Modelo de IA, temperatura, tokens máximos, timeout |
| **Capas** | Peso de cada analizador en la decisión. Tres columnas: peso en polymarket, forex y stocks |

**Capas** muestra los 8 analizadores con su peso por mercado. Podés activar/desactivar cada uno con el checkbox y ajustar el peso (0.0 a 1.0) en cada mercado.

> Los cambios requieren reiniciar el loop para aplicarse. Los parámetros se escriben directamente al archivo `config.yaml`.

### 4.7 Logs

Muestra las últimas 80 líneas que MarketAI escribe mientras funciona. Se actualiza automáticamente cada 5 segundos.

```
2026-05-19 14:30:01 [INFO] Analizando EURUSD...
2026-05-19 14:30:02 [INFO] Fused: SHORT (score:45 conf:100)
2026-05-19 14:30:15 [ERROR] HTTP Error 404: No fundamentals for SPY
2026-05-19 14:30:16 [WARNING] Risk block: max_drawdown_exceeded
```

**Niveles de log:**

| Nivel | Color | Significado |
|---|---|---|
| **INFO** | Normal | Informativo. El sistema funcionando normalmente |
| **WARNING** | Amarillo | Algo no esperado, pero no crítico. Ej: límite de riesgo alcanzado |
| **ERROR** | Rojo | Algo falló. Muchos son ruido inofensivo (API temporalmente caída) |

**Botones:** "Ir arriba" e "Ir abajo" para navegar el log rápidamente.

### 4.8 Noticias

Artículos de noticias financieras con clasificación de sentimiento. Los artículos se obtienen de NewsAPI (necesita API key en `.env`).

**Filtros disponibles:**

| Filtro | Opciones |
|---|---|
| **Mercado** | Todos / Forex / Stocks / Crypto |
| **Sentimiento** | Todos / Bullish (positivo) / Bearish (negativo) / Neutral |

**Barra de mood:** arriba de todo muestra el sentimiento general del mercado:
- 🟢 **Mercado optimista** = más noticias positivas que negativas
- 🔴 **Mercado pesimista** = más noticias negativas
- 😐 **Sentimiento mixto** = equilibrado

Cada noticia tiene un indicador de sentimiento: 🟢 bullish, 🔴 bearish, ⚪ neutral. Click en el título para abrir la noticia completa en el navegador.

> Las noticias se actualizan cada vez que el loop corre. Si no ves ninguna, verificá que `NEWSAPI_KEY` esté configurada en `.env`.

### 4.9 Watchlist

Página de seguimiento de precios en vivo. Muestra los activos que MarketAI está monitoreando, con su precio actual, cambio porcentual en 24 horas, y color indicador.

```
┌──────────┬────────┬────────┬───────┐
│ Ticker   │ Mercado│ Precio │ 24h % │
├──────────┼────────┼────────┼───────┤
│ EURUSD=X │ forex  │ 1.101  │ -0.2% │
│ GBPUSD=X │ forex  │ 1.351  │ +0.1% │
│ SPY      │ stocks │ 718.07 │ +1.2% │
│ AAPL     │ stocks │ 276.84 │ -0.5% │
└──────────┴────────┴────────┴───────┘
```

- **Verde** 🟢 = el precio subió en las últimas 24 horas
- **Rojo** 🔴 = el precio bajó en las últimas 24 horas
- Los tickers corresponden a los configurados en `config.yaml` (forex pairs + stocks tickers)

La Watchlist se actualiza automáticamente cada 15 segundos con los precios en vivo de Yahoo Finance.

---

## 5. Cómo leer las señales

Cada señal que genera MarketAI tiene esta estructura:

```
MERCADO: FOREX - EURUSD
Decisión: SHORT (venta)  ← qué hacer
Confianza: 80/100        ← qué tan seguro
Precio: 1.1011            ← precio actual
Análisis usados: técnica + macro + sentimiento
```

### ¿Qué hacer con las señales?

**Nada.** MarketAI ejecuta automáticamente. No necesitás hacer nada. Las señales son solo informativas.

Si querés entender por qué decidió algo, expandí la fila en la página **Señales** y mirá el desglose por capa.

---

## 6. Los 8 analizadores — ¿Qué mira cada uno?

Son las "herramientas" que MarketAI usa para decidir. Cada una mira algo diferente:

| Analizador | Qué mira | En simple |
|---|---|---|
| **Técnico** | Gráficos de precio, RSI, MACD, medias móviles | Estudia el movimiento del precio |
| **Fundamental** | P/E ratio, dividendos, ganancias de empresas | Mira si una empresa está cara o barata |
| **Macro** | VIX (miedo), DXY (dólar), economía global | Mira el estado de la economía mundial |
| **Sentimiento** | Noticias, artículos, titulares | Mira si la gente es optimista o pesimista |
| **On-chain** | Blockchain, transfers USDC (Polymarket) | Mira movimientos de grandes billeteras |
| **Orderbook** | Órdenes de compra y venta | Mira si hay más gente comprando o vendiendo |
| **Cross-Asset** | Correlación entre activos | Mira si los mercados se mueven juntos |
| **ICT/SMC** | Patrones de precios institucionales | Técnicas de trading profesional |

Cada analizador da un puntaje (0-100) y MarketAI los combina para decidir.

---

## 7. Perfiles: Normal vs Fast

MarketAI opera **dos estrategias al mismo tiempo** para poder comparar.

| Perfil | SL (pérdida) | TP (ganancia) | Duración típica | Cuándo usarlo |
|---|---|---|---|---|
| **Normal** 🟢 | 2% | 5% | 2-5 días | Conservador, menos operaciones |
| **Fast** 🔵 | 0.5% | 1.5% | Horas | Agresivo, más operaciones |

- **Normal** intenta sacar ganancias más grandes pero espera más tiempo
- **Fast** entra y sale rápido, con ganancias chicas pero frecuentes

En el Dashboard se ven lado a lado para comparar cuál rinde mejor.

---

## 8. Operación diaria

### ¿Cada cuánto revisar?

| Frecuencia | Qué hacer |
|---|---|
| **Diario** | Ver Overview → Balance, PnL, Equity Curve |
| **Cada 2-3 días** | Revisar señales y trades cerrados |
| **Semanal** | Ver Analytics → Win rate por hora, actividad por capa |
| **Mensual** | Evaluar si vale la pena pasar a modo real |

### ¿Cómo sé que funciona bien?

| Indicador | Bueno | Regular | Malo |
|---|---|---|---|
| Win Rate | >55% | 45-55% | <45% |
| Equity Curve | Sube constantemente | Plana | Baja |
| Balance | Crece | Se mantiene | Baja |
| Sharpe | >1.0 | 0.5-1.0 | <0.5 |

### Iniciar y detener

```powershell
# Iniciar todo (loop + dashboard)
.\tray_app.bat

# Desde el tray:
#   "Mostrar Dashboard" → abre el navegador
#   "Pausar" → detiene el loop temporalmente
#   "Reanudar" → continúa el loop
#   "Detener" → para el loop
#   "Salir" → cierra todo

# Desde el dashboard:
#   Botón "▶ Iniciar Loop"
#   Botón "■ Detener"
```

---

## 9. Preguntas frecuentes

### ¿Por qué no hay operaciones?

Lo más probable es que las señales son WAIT (el sistema no detecta oportunidades claras). Es normal. MarketAI prefiere no operar a operar mal. Cuando haya movimientos en el mercado, aparecerán señales.

### ¿Está perdiendo plata? ¿Qué hago?

En paper trading, perder plata es parte del aprendizaje. MarketAI recién está aprendiendo tu configuración. Dejalo correr al menos 2 semanas y revisá la tendencia de la equity curve.

Si la curva baja consistentemente por 2 semanas, ajustá:
- Bajar `min_confidence` (para que tome más operaciones)
- Ajustar SL/TP (para darle más espacio a las operaciones)
- Cambiar pesos de capas en Config

### ¿Puedo usar dinero real?

**Solo después de validación.** Recomendamos:
1. 2+ semanas en modo paper con win rate >55%
2. Sharpe ratio >1.0
3. Equity curve en tendencia alcista
4. Empezar con $50-100 como máximo

### ¿Qué API keys necesito?

| Key | ¿Obligatoria? | Dónde conseguirla |
|---|---|---|
| **DeepSeek API** | ✅ Sí | deepseek.com |
| NewsAPI | ❌ Opcional | newsapi.org |
| Polyscan API | ❌ Opcional | polygonscan.com/apis |

### ¿Windows se duerme? ¿Se detiene el sistema?

Si la PC se suspende, MarketAI se pausa. Soluciones:
- En Windows: Configuración → Sistema → Energía → Suspensión → **Nunca**
- O mejor: ejecutar en un VPS en la nube

---

## 10. Solución de problemas rápidos

| Problema | Causa probable | Solución |
|---|---|---|
| No abre :8050 | Dashboard no iniciado | Click "Reiniciar Dashboard" en el tray |
| "possibly delisted" errores | Yahoo Finance fuera de horario | Ignorar, es normal en la noche |
| Todas las señales WAIT | Mercado tranquilo | Bajar `min_confidence` en Config |
| Balance $1,000 quieto | No se generaron operaciones | Esperar a que el mercado se mueva |
| Tray icon no responde | Pystray se colgó | `taskkill /f /im python.exe` y reiniciar |
| DeepSeek WAIT constante | API sin key o sin crédito | Verificar `.env` o recargar cuenta |
| Error de puerto 8050 ocupado | Otro dashboard ya corriendo | Matarlo desde Administrador de Tareas |

---

*MarketAI — Documentación para usuarios. Versión 1.0.*
