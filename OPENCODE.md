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
Datos → 7 Analizadores → Fusión → DeepSeek → Ejecución → Journal
```

| Capa | Módulo | Función |
|---|---|---|
| Recolección | `data/collector_*.py` | Polymarket CLOB, Yahoo Finance, NewsAPI |
| Análisis | `analyzers/*.py` | 7 analizadores en paralelo: técnico, on-chain, sentimiento, order book, fundamental, macro, cross-asset |
| Decisión | `engine/fusion.py` + `engine/decider.py` | Pesos configurables → DeepSeek decide LONG/SHORT/WAIT |
| Ejecución | `execution/` | Paper broker (activo) + Executors reales (stubs) |
| Auto-aprendizaje | `learning/` | Journal, Strategy Evolver, Backtest |

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
| **Modelo DeepSeek** o temperatura | `config.yaml` + `guias/guia_configuracion.md` |
| **Variable de entorno** | `.env.example` + `guias/guia_configuracion.md` |
| **Analizador nuevo** | `guias/guia.md` §2 + `documentos/roadmap.md` |
| **Métrica de riesgo** | `config.yaml` + `guias/guia_uso.md` |
| **Estrategia de trading** | `strategies/master_strategy.md` |
| **Fase completada** | `documentos/roadmap.md` + `documentos/checklist.md` |
| **Decisión importante de instancia** | `informes/bitacora.md` (crear si no existe) |

### Quién edita qué (sin pedir aprobación)
- **OpenCode edita libre:** `documentos/checklist.md`, `documentos/roadmap.md`, `guias/`, `informes/`, código en `engine/`, `data/`, `analyzers/`, `execution/`, `learning/`, `alerts/`, `strategies/`, `scripts/`
- **OpenCode edita con aprobación:** Cambios a motor de decisión (`engine/decider.py`), risk management, `config.yaml` (estructura), OPENCODE.md, `documentos/metodologia.md`

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
1. **Actualizar `documentos/checklist.md`** — marcar completado como ✅ DONE
2. **Actualizar `documentos/roadmap.md`** — reflejar nuevos estados
3. **Escribir `informes/bitacora.md`** — entrada con: instancia #, qué se hizo, decisiones, próximo paso
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

**Fase 8 — Producción:** Paper trading en curso (validación 2-4 semanas).

### Pendientes P1
| ID | Qué |
|---|---|
| 8.1 | Paper trading 2-4 semanas sin errores |
| 8.2 | Micro-montos reales ($10-50) |
| 8.3 | Monitoreo diario con ajustes manuales |
| 8.4 | Estrategia madura → capital progresivo |
| 8.5 | Modo replay histórico para QA sin APIs live |

Ver `documentos/roadmap.md` para backlog completo.

---

*Mantenido por OpenCode + Juan Lemos. Cambios a este archivo requieren aprobación del usuario.*
