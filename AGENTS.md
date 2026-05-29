# AGENTS.md — MarketAI

Este archivo se lee al inicio de cada sesión de OpenCode, junto con OPENCODE.md.
Contiene datos prácticos del proyecto que una sesión nueva no puede deducir sin leer varios archivos.
OPENCODE.md explica **cómo trabajar** (protocolo, reglas). AGENTS.md explica **qué saber** (configuración, atajos, trampas).

---

## Skills disponibles

Skills cargables con `skill("nombre")` para tareas recurrentes:

| Skill | Archivo | Cuándo cargar |
|---|---|---|
| `backup-pre-edit` | `doc/skills/backup-pre-edit.md` | Antes de editar archivos críticos — workflow backup/restore |
| `actualizar-docs` | `doc/skills/actualizar-docs.md` | Al invocar `/updoc` — sincronización documental completa |

## Comandos globales heredados

Estos comandos viven en `~/.config/opencode/commands/` y funcionan sin configuración:

| Comando | Función |
|---------|---------|
| `/debug` | Análisis profundo de sección (backend, frontend, DB, módulo) |
| `/health` | Verificar integridad del código (sintaxis, rutas) |
| `/plan` | Planificar (PLAN) → ejecutar (BUILD) tras aprobación |

## Comandos personalizados (.opencode/commands/)

| Comando | Archivo | Función |
|---|---|---|
| `/backup` | `.opencode/commands/backup.md` | Backup de archivos críticos |
| `/backupall` | `.opencode/commands/backupall.md` | Backup completo del proyecto (.zip) |
| `/checklist` | `.opencode/commands/checklist.md` | Revisar checklist + roadmap |
| `/commit` | `.opencode/commands/commit.md` | Commit con formato del proyecto (hereda global) |
| `/estado` | `.opencode/commands/estado.md` | Reporte rápido de estado del proyecto |
| `/foco` | `.opencode/commands/foco.md` | Enfocar agente en modo de trabajo (`tx\|ui\|ux`) |
| `/limpiar` | `.opencode/commands/limpiar.md` | Limpiar archivos temporales (hereda global) |
| `/next` | `.opencode/commands/next.md` | Próximos 5 pasos del roadmap |
| `/rm` | `.opencode/commands/rm.md` | Revisar roadmap |
| `/+guia` | `.opencode/commands/+guia.md` | Crear nueva guía |
| `/+rmi` | `.opencode/commands/+rmi.md` | Agregar idea al roadmap |
| `/updoc` | `.opencode/commands/updoc.md` | Actualizar documentación completa |
| `/upguia` | `.opencode/commands/upguia.md` | Actualizar guía existente |

## Mapeo de rutas para comandos

| Variable | Ruta en MarketAI |
|---|---|
| `$RM` | `doc/documentos/roadmap.md` |
| `$CHECKLIST` | `doc/documentos/checklist.md` |
| `$GUIAS_DIR` | `doc/guias/` |
| `$GUIAS_TEMPLATE` | `doc/guias/_template.md` |
| `$CRITICAL_FILES` | `config.yaml`, `.env`, `orchestrator.py`, `data/database.py`, `engine/decider.py` |

## Foco por área

- `tx` → backend: `engine/`, `analyzers/`, `data/`, `execution/`
- `ui` → frontend: `templates/`, `static/`, `dashboard.py`
- `ux` → experiencia: `doc/guias/`, `alerts/`, `strategies/`

---

## Arranque

```powershell
# Entorno virtual
venv\Scripts\activate

# Una iteración
python orchestrator.py --mode once

# Loop 24/7
python orchestrator.py --mode loop

# Dashboard web
.\dashboard.bat

# System tray
.\tray_app.bat
```

## Sin build step

Python puro. No hay compilación. Se edita y se ejecuta. El dashboard es Flask con templates HTML en `templates/` y estáticos en `static/`.

## Testing

```powershell
python -m pytest tests/ -v
```

## Base de datos (SQLite)

- Archivo: `MarketAI.db` (creado automáticamente)
- Schema en `data/database.py` → clase `Database()`
- Tablas: `trades`, `signals`, `market_data`, `strategy_performance`, `portfolio`, `motor_heartbeat`, `backtest_runs`
- Sin migraciones. Tablas con `CREATE TABLE IF NOT EXISTS`.

## Auth

No hay autenticación. El dashboard es local (`localhost:8050`). No exponer en redes públicas sin agregar auth.

## Backup de archivos críticos (antes de editar)

```powershell
# Backup manual
Copy-Item config.yaml "config.yaml.bak_$(Get-Date -Format 'yyyyMMdd')"
# O usar /backup (copia a .bak_<fecha>/)
```

Archivos críticos: `config.yaml`, `.env`, `orchestrator.py`, `data/database.py`, `engine/decider.py`. Cargar `skill("backup-pre-edit")` para más detalle.

## Modelos de IA

- DeepSeek V4 Flash para decisiones de trading (`config.yaml` → `deepseek.model`)
- Temperatura: 0.3 (configurable en config.yaml)
- Fallback: WAIT si respuesta inválida

## Convenciones

| Prefijo | Significado |
|---|---|
| P1/P2/P3 | Prioridad: Crítico / Importante / Backlog |
| Fase-XX | Fase del roadmap (Fase-0..Fase-8, Fase-R) |
| ADR-XXX | Decisión arquitectónica documentada |
| B-XX | Bug |

## Directorios clave

| Directorio | Propósito |
|---|---|
| `engine/` | Fusión de señales + decisión DeepSeek |
| `analyzers/` | **9 analizadores** (técnico, on-chain, sentimiento, orderbook, fundamental, macro, cross-asset, ICT/SMC, ADX Regime) |
| `data/` | Recolectores + database |
| `execution/` | Paper broker, risk engine + ejecutores reales (Alpaca/OANDA) |
| `learning/` | Journal + strategy evolver + backtest + replay |
| `alerts/` | Telegram + Discord notifier |
| `strategies/` | Estrategias documentadas + trade journal |
| `doc/guias/` | Guías de instalación, configuración, uso |

| `doc/documentos/` | Roadmap, checklist, metodología, bugs |

| `doc/informes/` | Reportes, reglas para agentes IA |
| `templates/` | HTML templates del dashboard Flask (10 páginas) |
| `static/` | CSS y assets del dashboard |
| `tests/` | Tests pytest |
| `doc/skills/` | Skills cargables + ICT FVG standalone |

---

## Reglas post-edit (para agentes IA)

Después de CADA edición de >5 líneas:

1. Leer 15 líneas antes y después del sitio editado.
2. Verificar que no haya `const`/`let`/`function` duplicados en el mismo bloque `<script>`.
3. Si la edición reemplazó un bloque con declaraciones (`const`, `let`, `function`), confirmar que cada identificador nuevo sea único en ese scope.
4. Ejecutar `rg "const NOMBRE" archivo` sobre el símbolo modificado para confirmar unicidad.
5. Si se extrajo o movió código a otro archivo, verificar que no quede un identificador duplicado en el origen.

### Regla 6 — Sincronización de documentación

Si la edición modificó comportamiento visible para el usuario (config flags, endpoints, parámetros de estrategia, SL/TP, perfiles, columnas de DB, analizadores), actualizar la guía correspondiente en el mismo commit:

| Cambio | Docs a actualizar |
|---|---|
| `config.yaml` (flags, perfiles, time-exit) | `doc/guias/guia_configuracion.md` |
| `dashboard.py` (endpoints, páginas) | `doc/guias/guia_uso.md` (tabla de rutas) |
| `execution/paper_broker.py`, `risk_engine.py`, `entry_filters.py` | `doc/guias/guia_trading.md`, `doc/guias/guia_configuracion.md` |
| `analyzers/` (nuevo analyzer, cambios de peso) | `doc/guias/guia_configuracion.md` (tabla de capas) |
| `tray_app.py` | `doc/guias/guia_uso.md` (sección tray) |
| Cambio en número de tests | `README.md`, `doc/documentos/checklist.md`, `doc/documentos/roadmap.md` |

Cargar `skill("actualizar-docs")` para el checklist completo.
