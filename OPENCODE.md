# MARKETAI — OPENCODE.md

**Proyecto:** Sistema de trading automatizado multi-capa impulsado por DeepSeek AI.
**Estado:** Fase 8 — Paper trading en validación.
**Última actualización:** 2026-05-05
**Mercados:** Polymarket, Forex, Acciones — 3 modos: paper / real

> Este archivo es el ancla de cada sesión. OpenCode lo lee automáticamente al entrar al proyecto.

---

## 1. STACK ACTUAL

| Capa | Tecnología | Notas |
|---|---|---|
| Lenguaje | Python 3.10+ | Sin build step |
| Dashboard | Flask + Plotly | Puerto 8050, localhost |
| Decisión IA | DeepSeek V4 Pro | Prompt engineering + JSON parsing |
| Base de datos | SQLite | `data/database.py` — schema automático |
| Trading | Paper (simulado) → Real | Paper broker con slippage 0.1% |
| Alertas | Telegram / Discord | Opcional vía webhooks |
| Estado | Pre-producción | Validación paper trading 2-4 semanas |

---

## 2. ARQUITECTURA (5 Capas)

```
Datos → 8 Analizadores → Fusión → DeepSeek → Ejecución → Journal

| Capa | Módulo | Función |
|---|---|---|
| Recolección | `data/collector_*.py` | Polymarket CLOB, Yahoo Finance, NewsAPI |
| Análisis | `analyzers/*.py` | **8 analizadores** en paralelo: técnico, on-chain, sentimiento, order book, fundamental, macro, cross-asset, ICT/SMC |
| Decisión | `engine/fusion.py` + `engine/decider.py` | Pesos configurables → DeepSeek decide LONG/SHORT/WAIT (sistema de doble prompt con reglas de riesgo) |
| Riesgo | `execution/risk_engine.py` | Kelly fraccional (25%), ATR position sizing adaptativo, circuit breakers |
| Ejecución | `execution/paper_broker.py` + `executor_*.py` | Paper broker (activo) + Executors reales (Alpaca/OANDA API listas) |
| Auto-aprendizaje | `learning/` | Journal, Strategy Evolver, Backtest, Replay mode |

---

## 3. PROTOCOLO DE TRABAJO (5 pasos)

```
1. IDEA       → Usuario propone (feature, fix, refactor, idea)
2. EXPLORAR   → OpenCode lee archivos relevantes y entiende el estado actual
3. REVISAR    → OpenCode propone: qué cambiaría, dónde impacta, alternativas
4. APROBAR    → Usuario dice SÍ / NO / CAMBIOS. Sin aprobación explícita, no se actúa
5. ACTUAR     → OpenCode implementa y actualiza los archivos correspondientes
```

**Regla de oro:** Cambios de arquitectura o motor de decisión → revisar ADR primero. Bugfixes menores → actuar y documentar después.

---

## 4. CÓMO RESPONDO (dos modos)

### Modo EXPLICAR (cuando pedís ideas, opciones, análisis)
Disparadores: "¿qué pensás?", "opciones para…", "explicame…", "comparame…", "ideas de…"

Formato:
- **Listar/agrupar** las opciones disponibles
- **Pros y contras** de cada una
- **Sumar opciones** que el usuario no haya considerado, si las veo
- **No actuar** hasta aprobación

### Modo ACTUAR (cuando aprobás, decís "hacelo", "ejecutá", o pedís edición directa)
Disparadores: "ok", "sí", "hacelo", "implementá", "editá", "arreglá X"

Formato:
- Ejecutar los cambios
- **Resumen breve de lo realizado** en <4 líneas, estructura: qué cambió, pro/con, implicancia
- Mencionar próximo paso o decisión pendiente, si la hay

---

## 5. REGLAS DE EDICIÓN DE ARCHIVOS

### Mapeo cambio → archivo a actualizar

| Cuando cambia… | Actualizar también |
|---|---|
| **Modelo DeepSeek** o temperatura | `config.yaml` + `doc/guias/guia_configuracion.md` |
| **Variable de entorno** | `.env.example` + `doc/guias/guia_configuracion.md` |
| **Analizador nuevo** | `doc/guias/guia_configuracion.md` + `doc/documentos/roadmap.md` |
| **Métrica de riesgo** | `config.yaml` + `doc/guias/guia_uso.md` |
| **Fase completada** | `doc/documentos/roadmap.md` + `doc/documentos/checklist.md` |
| **Decisión importante de instancia** | `doc/informes/bitacora.md` (crear si no existe) |

### Quién edita qué (sin pedir aprobación)
- **OpenCode edita libre:** `doc/documentos/checklist.md`, `doc/documentos/roadmap.md`, `doc/guias/`, `doc/informes/`, código en `engine/`, `data/`, `analyzers/`, `execution/`, `learning/`, `alerts/`, `strategies/`, `scripts/`
- **OpenCode edita con aprobación:** Cambios a motor de decisión (`engine/decider.py`), risk management, `config.yaml` (estructura), OPENCODE.md, `doc/documentos/metodologia.md`

### Cuándo NO editar
- No tocar archivos en `nppBackup/` (histórico)
- No editar `.db` directamente (usar `data/database.py`)
- No reescribir `.env` (API keys)

---

## 6. CONVENCIONES RÁPIDAS

| Símbolo | Significado |
|---|---|
| **P1 / P2 / P3** | Crítico / Importante / Backlog |
| **✅ / 🟡 / 🔴** | Completado / En curso / Pendiente |
| **ADR-XXX** | Decisión formalizada |
| **Fase-XX** | Fase del roadmap |
| **B-XX** | Bug |

---

## 7. REGLAS DE ARCHIVADO

| Disparador | Acción |
|---|---|
| El archivo está marcado **"DEPRECADO"** | Mover a `nppBackup/` |
| El archivo describe una decisión ya implementada (cambio histórico) | Archivar — el código actual es la verdad |
| Carpeta queda vacía tras archivar | Eliminar la carpeta |

---

## 8. REGLA DE CIERRE DE INSTANCIA

### Pasos obligatorios antes de cerrar
1. **Actualizar `doc/documentos/checklist.md`** — marcar completado como ✅ DONE
2. **Actualizar `doc/documentos/roadmap.md`** — reflejar nuevos estados
3. **Escribir `doc/informes/bitacora.md`** — entrada con: instancia #, qué se hizo, decisiones, próximo paso
4. **Nombrar el próximo paso**

### Formato resumen de cierre
```
CIERRE INSTANCIA XX — [Fecha]
✅ Completado: [lista 1-3 items]
📋 Próximo: [qué viene] (modelo recomendado: Flash/Pro)
📁 Docs actualizados: [lista archivos]
```

---

## 9. ESTADO ACTUAL

**Fase 8 — Producción:** Paper trading en curso (validación). Dashboard web corriendo en `:8050`.

### Completado en esta versión
| Feature | Estado |
|---|---|
| Dashboard web (Flask, 6 páginas, responsive) | ✅ |
| Tray app (icono $ en system tray, loop sin ventana) | ✅ |
| 8 analizadores (técnico, on-chain, sentimiento, orderbook, fundamental, macro, cross-asset, ICT/SMC) | ✅ |
| Risk Engine (Kelly, ATR stops, circuit breakers) | ✅ |
| DeepSeek decider (doble prompt, reglas de riesgo) | ✅ |
| On-chain analyzer (Polyscan API) | ✅ |
| Fundamental analyzer (P/E, market cap, beta, earnings) | ✅ |
| Discord notifier (webhook) | ✅ |
| Modo cron (daily/weekly/hourly + schtasks) | ✅ |
| Modo replay (walk-forward histórico) | ✅ |
| Skills auto-generados (strategy_evolver escribe a skills/) | ✅ |
| Portfolio snapshots + equity curve | ✅ |
| Documentación (README, roadmap, checklist, 3 guías) | ✅ |
| Paper trading 24/7 | 🔄 Corriendo |

### Pendientes P1
| ID | Qué |
|---|---|
| 8.1 | Paper trading 2-4 semanas sin errores |
| 8.2 | Micro-montos reales ($10-50) |
| 8.3 | Monitoreo diario con ajustes manuales |

Ver `doc/documentos/roadmap.md` para backlog completo.

---

*Mantenido por OpenCode + Juan Lemos. Cambios a este archivo requieren aprobación del usuario.*
