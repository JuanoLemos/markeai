# Guía de Uso

## MarketAI - Sistema de Trading Multi-Capa

---

## 1. Inicio Rápido

### Lanzadores (doble clic)

| Archivo | Qué hace |
|---|---|
| `tray_app.bat` | Inicia el loop 24/7 + dashboard web minimizado a system tray (recomendado) |
| `dashboard.bat` | Inicia solo el dashboard web en `http://localhost:8050` |
| `loop.bat` | Inicia solo el loop de trading en consola |
| `cron_daily.bat` | Reporte diario manual |
| `cron_hourly.bat` | Health check manual |
| `cron_weekly.bat` | Backtest semanal |

### Modo Manual (una iteración)
```bash
venv\Scripts\activate
python orchestrator.py --mode once
```

### Modo Loop (24/7)
```bash
python orchestrator.py --mode loop
```

### Dashboard Web
```bash
python dashboard.py
# Abrir http://localhost:8050
```

### System Tray (todo en uno)
```bash
python tray_app.py
# Icono $ en la bandeja del sistema
# Click derecho: ▶ Activar, 💀 Kill Services, Reiniciar Servidor, etc.
```

---

## 2. Comandos Principales

| Comando | Descripción |
|---|---|
| `python orchestrator.py --mode once` | Una iteración (todos los mercados) |
| `python orchestrator.py --mode loop` | Loop 24/7 |
| `python orchestrator.py --mode once --market polymarket` | Solo Polymarket |
| `python orchestrator.py --mode report` | Resumen de portfolio |
| `python dashboard.py` | Dashboard web :8050 |
| `python tray_app.py` | Loop + dashboard en system tray |

---

## 3. Dashboard Web (9 páginas)

| Ruta | Página | Qué muestra |
|---|---|---|
| `/` | Overview | Balance, P&L dual (Normal/Fast), posiciones abiertas con Δ%, equity curve, Daily Brief, Risk Snapshot, Proyección |
| `/signals` | Señales | Últimas 50 señales, filtros por decisión/mercado, expansión por capas |
| `/trades` | Trades | Historial completo, filtros por estado/resultado, resumen W/L |
| `/analytics` | Analytics | Confianza, actividad por capa, win rate por hora, benchmark vs SPY/BTC/Banco |
| `/backtest` | Simulación | Backtest por mercado (Forex/Acciones), resultados agregados + por ticker |
| `/config` | Config | Editor de config.yaml en vivo, selector de tema visual |
| `/news` | Noticias | Feed de noticias con análisis de sentimiento, filtros por mercado |
| `/watchlist` | Watchlist | Cruzar señales + trades por ticker con sparkline |
| `/logs` | Logs | Tail de orchestrator.log |
| `/ticker/<symbol>` | Detalle | Drill-down por activo: chart, señales, trades |

### Temas visuales
6 temas disponibles: Dark, Light, Bloomberg, Mint, Cyberpunk, Solarized. Se cambian desde Config o desde el sidebar. Persisten en localStorage.

---

## 4. System Tray (control principal)

El tray app es el método recomendado para operar el sistema. No hay botones de start/stop en el dashboard.

| Menú | Acción |
|---|---|
| **▶ Activar** | Inicia el loop + dashboard (mata procesos previos primero) |
| **💀 Kill Services** | Detiene loop y dashboard por completo |
| **Reiniciar Servidor** | Mata y relanza el loop |
| **Reiniciar Dashboard** | Mata y relanza solo el dashboard Flask |
| **Mostrar Dashboard** | Abre http://localhost:8050 en el navegador |
| **Salir** | Cierra todo |

El tooltip del icono muestra: "BotEscucha — N: +$X.xx (+Y.YY%) F: +$Z.zz (+W.WW%)" (Normal + Fast).

El loop se reinicia automáticamente si muere por más de 30 segundos.

---

## 5. Detener el Sistema

```bash
# Opción 1: System tray
# Click derecho → 💀 Kill Services

# Opción 2: Archivo STOP
echo "stop" > STOP

# Opción 3: Consola directa
# Ctrl+C
```

---

## 6. Monitoreo

### Desde consola
```bash
# Últimas líneas del log
Get-Content orchestrator.log -Tail 50

# Resumen de portfolio
python orchestrator.py --mode report

# Posiciones abiertas
type data\cache\paper_broker_state.json
```

### Desde dashboard
Abrir `http://localhost:8050` en el navegador. Auto-refresh cada 10s.

### Alertas
Si configuraste Telegram o Discord webhook, recibirás:
- 🟢 **Entrada**: Señal + mercado + tamaño + precio
- ✅/❌ **Salida**: PnL + duración + razón
- ⚠️ **Error**: Fallo en recolector/analizador

---

## 7. Backtesting

```bash
# Desde el dashboard:
# Ir a /backtest, click en "Simular Forex" o "Simular Acciones"
# Toma ~5-15 min (usa el pipeline completo, no RSI/EMA legacy)
```

El backtest ejecuta el pipeline completo de MarketAI (run_replay): recolecta datos históricos, ejecuta los 9 analizadores, fusiona señales, consulta DeepSeek y simula trades. Los resultados persisten en sessionStorage al cambiar de pestaña.

---

## 8. Perfiles de Trading (Normal + Fast)

El sistema opera **dos perfiles simultáneamente**:

| Perfil | SL | TP | Confianza | Filtros |
|---|---|---|---|---|
| **Normal** | 2% | 5% | Alta (45-50%) | Sesión 18h, correlación, ADX, volatilidad |
| **Fast** | 0.5% | 1.5% | Baja (30-35%) | Sesión 22h, sin correlación ni volatilidad |

Cada perfil tiene su propio SL/TP, min_confidence y filtros configurados en `config.yaml` bajo `profiles`.

---

## 9. Configuración Rápida desde Dashboard

El dashboard permite editar en vivo desde `http://localhost:8050/config`:
- Activar/desactivar mercados
- Cambiar pesos de capas
- Configurar riesgo

> Los cambios se guardan a `config.yaml`. Requieren reinicio del loop para aplicarse (💀 Kill Services → ▶ Activar).

---

## 10. Cron — Tareas Automáticas

| Tarea | Archivo | Frecuencia | Qué hace |
|---|---|---|---|
| `daily` | `cron_daily.bat` | 1 vez/día | Una iteración + resumen |
| `weekly` | `cron_weekly.bat` | 1 vez/semana | Backtest completo |
| `hourly` | `cron_hourly.bat` | Cada hora | Health check del log |

### Programar en Windows Task Scheduler
```powershell
schtasks /create /tn "MarketAI-Daily" /tr "C:\xampp\htdocs\MarketAI\cron_daily.bat" /sc daily /st 21:00
```

---

## 11. Seguridad

- **Nunca** commitees `.env` al repositorio (`.gitignore` lo excluye)
- **Nunca** compartas private keys de wallet
- El modo paper **no** ejecuta trades reales
- El modo real requiere `mode: real` explícito en `config.yaml`
- DeepSeek API key es la única obligatoria para operar
- Sin API key → el sistema genera señales pero no ejecuta trades
