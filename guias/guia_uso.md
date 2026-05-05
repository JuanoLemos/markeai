# Guía de Uso

## MarketAI - Sistema de Trading Multi-Capa

---

## 1. Inicio Rápido

### Lanzadores (doble clic)

| Archivo | Qué hace |
|---|---|
| `loop.bat` | Inicia el loop de trading 24/7 |
| `dashboard.bat` | Inicia el dashboard web en `http://localhost:8050` |
| `tray_app.bat` | Inicia el loop minimizado a system tray (icono $) |

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

### System Tray
```bash
python tray_app.py
# Icono $ en la bandeja del sistema
# Click derecho: Show Dashboard, Pause, Resume, Stop, Exit
# Cerrar ventana → minimiza a tray
```

---

## 2. Comandos Principales

| Comando | Descripción |
|---|---|
| `python orchestrator.py --mode once` | Una iteración |
| `python orchestrator.py --mode loop` | Loop 24/7 |
| `python orchestrator.py --mode once --market polymarket` | Solo Polymarket |
| `python orchestrator.py --mode backtest` | Backtest sobre datos históricos |
| `python orchestrator.py --mode report` | Resumen de portfolio |
| `python dashboard.py` | Dashboard web :8050 |
| `python tray_app.py` | Loop en system tray |

---

## 3. Dashboard Web

### Páginas
| Ruta | Qué muestra |
|---|---|
| `/` | Balance, P&L, posiciones abiertas, últimas señales, botones Start/Stop |
| `/signals` | Últimas 50 señales generadas |
| `/trades` | Historial de trades cerrados con P&L |
| `/config` | Formulario editable de `config.yaml` |
| `/logs` | Tail de `orchestrator.log` |

### Iniciar/Detener Loop desde la UI
- Botón **▶ Iniciar Loop** → lanza `orchestrator.py --mode loop` como subproceso
- Botón **■ Detener** → crea archivo `STOP`, el loop se detiene
- Dashboard actualiza métricas automáticamente cada 10s

---

## 4. System Tray (tray_app.py)

| Acción | Comportamiento |
|---|---|
| Iniciar | `python tray_app.py` — aparece icono $ blanco en la bandeja |
| Cerrar ventana de loop | La consola se oculta, el proceso sigue corriendo en tray |
| Menú contextual | Show Dashboard, Pause Loop, Resume, Stop, Exit |
| Tooltip | Muestra balance actual y estado del loop |
| Detener desde tray | Exit → espera 5s y cierra todo |

---

## 5. Detener el Sistema

```bash
# Opción 1: Archivo STOP (funciona siempre)
echo "stop" > STOP

# Opción 2: Dashboard (si está corriendo)
# Click en "■ Detener"

# Opción 3: System tray
# Click derecho → Stop Loop

# Opción 4: Consola directa
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

## 7. Gestión de Posiciones

### Ver posiciones abiertas
```bash
python -c "from data.database import Database; db=Database(); print(db.get_open_trades())"
```

### Stop-loss automático
El paper broker revisa stops cada iteración. Configurable en `config.yaml`:
```yaml
risk:
  stop_loss_atr_multiplier: 1.5
  take_profit_atr_multiplier: 3.0
```

---

## 8. Backtesting

```bash
# Backtest por mercado
python orchestrator.py --mode backtest --market forex
python orchestrator.py --mode backtest --market stocks
```

Resultados: win rate, Sharpe ratio, profit factor, max drawdown.

---

## 9. Configuración Rápida desde Dashboard

El dashboard permite editar en vivo desde `http://localhost:8050/config`:

- Activar/desactivar mercados
- Ajustar `min_confidence` (más bajo → más señales)
- Cambiar pesos de capas
- Configurar riesgo

> Los cambios se guardan a `config.yaml`. Requieren reinicio del loop para aplicarse.

---

## 10. Seguridad

- **Nunca** commitees `.env` al repositorio (`.gitignore` lo excluye)
- **Nunca** compartas private keys de wallet
- El modo paper **no** ejecuta trades reales
- El modo real requiere `mode: real` explícito en `config.yaml`
- DeepSeek API key es la única obligatoria para operar
- Sin API key → el sistema genera señales pero no ejecuta trades
