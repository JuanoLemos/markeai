# AGENTS.md — MarketAI

Este archivo se lee al inicio de cada sesión de OpenCode, junto con OPENCODE.md.
Contiene datos prácticos del proyecto que una sesión nueva no puede deducir sin leer varios archivos.
OPENCODE.md explica **cómo trabajar** (protocolo, reglas). AGENTS.md explica **qué saber** (configuración, atajos, trampas).

---

## Mapeo de rutas

Variables que los comandos del proyecto usan para referirse a archivos. Definidas acá para mantener un solo punto de configuración.

| Variable | Ruta estándar | Descripción |
|----------|---------------|-------------|
| $RM | `ROADMAP.md` | Roadmap del proyecto |
| $CHECKLIST | `CHECKLIST.md` | Checklist del proyecto |
| $CHANGELOG | `CHANGELOG.md` | Historial de versiones |
| $BITACORA | `doc/arch/bitacora.md` | Bitácora de sesiones |
| $BUGS | `doc/arch/bugs.md` | Bug tracker |
| $INCIDENTS | `doc/arch/incidentes.md` | Registro de incidentes |
| $GUIAS | `doc/guias/` | Directorio de guías |
| $GUIAS_TEMPLATE | `doc/guias/_template.md` | Plantilla de guía |
| $COMANDOS_FILE | `doc/guias/COMANDOS.md` | Documentación de comandos |
| $ARCH | `doc/arch/` | ADRs, sistema, informes |
| $PEND | `doc/pendientes/` | Pendientes de revisión |
| $QA | `doc/qa/` | Situaciones QA |
| $TESTING | `doc/testing/` | Testing pendiente |
| $MECANICAS | `doc/mecanicas/` | Reglas de negocio / mecánicas del proyecto |
| $MECANICAS_TEMPLATE | `doc/mecanicas/_template.md` | Plantilla de mecánica |
| $PALOMA_MAIN_PLAN | `doc/arch/palomas.md` | Plan de palomas activas |
| $BACKUPS | `data/cache/backups/` | Backups automáticos |
| $BACKUP_KEEP | `7` | Días a conservar backups |
| $SKILLS_DIR | `skills/` | Skills cargables |
| $CONFIG | `config.yaml` | Configuración central |
| $ENV | `.env` | API keys y secretos |
| $ORCHESTRATOR | `orchestrator.py` | Loop principal |
| $DASHBOARD | `dashboard.py` | Flask dashboard |
| $DATABASE | `data/database.py` | Schema SQLite |
| $DECIDER | `engine/decider.py` | Motor DeepSeek |
| $BACKUP_SCRIPT | `scripts/backup-critical.py` | Backup de críticos |
| $ENGINE_DIR | `engine/` | Fusión + decisión |
| $ANALYZERS_DIR | `analyzers/` | Analizadores de mercado |
| $DATA_DIR | `data/` | Recolectores + DB |
| $EXECUTION_DIR | `execution/` | Broker, risk, entry |
| $TEMPLATES_DIR | `templates/` | HTML templates |
| $STATIC_DIR | `static/` | CSS y assets |
| $ALERTS_DIR | `alerts/` | Notificaciones |
| $STRATEGIES_DIR | `strategies/` | Estrategias + journal |
| $LEARNING_DIR | `learning/` | Backtest + evolver |
| $SCRIPTS_DIR | `scripts/` | Scripts auxiliares |
| $TESTS_DIR | `tests/` | Tests pytest |
| $COMMANDS_DIR | `.opencode/commands/` | Comandos slash |
| $CRITICAL_FILES | `$CONFIG`, `$ENV`, `$ORCHESTRATOR`, `$DATABASE`, `$DECIDER` | Archivos críticos |

---

## Disciplina BUILD

BUILD = aplicar cambios, NO commitear. Solo /commit, /CBP y /version ejecutan git commit.
Al terminar cualquier BUILD, reportar cambios aplicados y sugerir /CBP.

---

## Skills disponibles

Skills cargables con `skill("nombre")` para tareas recurrentes:

| Skill | Archivo | Cuándo cargar |
|---|---|---|
| `backup-pre-edit` | `$SKILLS_DIR/backup-pre-edit.md` | Antes de editar archivos críticos — workflow backup/restore |
| `actualizar-docs` | `$SKILLS_DIR/actualizar-docs.md` | Al invocar `/updoc` — sincronización documental completa |

## Comandos globales heredados

Estos comandos viven en `~/.config/opencode/commands/` y funcionan sin configuración. También tienen copia local en `.opencode/commands/`:

| Comando | Función |
|---------|---------|
| `/debug` | Análisis profundo de sección (backend, frontend, DB, módulo) |
| `/health` | Verificar integridad del código (sintaxis, rutas) |
| `/plan` | Planificar (PLAN) → ejecutar (BUILD) tras aprobación |
| `/salud` | Reporte de salud del proyecto |
| `/reanudar` | Continuar sesión interrumpida |
| `/cbp` | Circuito basado en plan — orquestador multi-workflow |
| `/circuito` | Orquestador de workflows vinculantes |
| `/doctor` | Cuidado integral del proyecto |
| `/informe-salud` | Informe de salud inter-proyecto |
| `/legal` | Verificación legal del proyecto |
| `/mutacion` | Absorber mutaciones de un proyecto |
| `/pushgh` | Push a GitHub |
| `/revision` | Revisar mutaciones del proyecto |

## Comandos personalizados (.opencode/commands/)

| Comando | Archivo | Función |
|---|---|---|
| `/+guia` | `+guia.md` | Crear nueva guía |
| `/+mec` | `+mec.md` | Crear nueva mecánica en `doc/mecanicas/` |
| `/+pend` | `+pend.md` | Agregar pendiente de revisión en `doc/pendientes/` |
| `/+rm` | `+rm.md` | Agregar ítem al roadmap |
| `/+rmi` | `+rmi.md` | Agregar idea al roadmap |
| `/adaptar` | `adaptar.md` | Adaptar proyecto a metodología Diligencia |
| `/apply` | `apply.md` | Aplicar cambios de diseño aprobados |
| `/backup` | `backup.md` | Backup de archivos críticos |
| `/backupall` | `backupall.md` | Backup completo del proyecto (.zip) |
| `/bug` | `bug.md` | Registrar bug en `doc/arch/bugs.md` |
| `/checklist` | `checklist.md` | Revisar checklist + roadmap |
| `/commit` | `commit.md` | Commit con formato del proyecto (hereda global) |
| `/deprecar` | `deprecar.md` | Marcar funcionalidad como deprecada |
| `/diligencia-check` | `diligencia-check.md` | Verificar integridad Diligencia |
| `/estado` | `estado.md` | Reporte rápido de estado del proyecto |
| `/explica` | `explica.md` | Explicar sección de código |
| `/foco` | `foco.md` | Enfocar agente en modo de trabajo (`tx\|ui\|ux`) |
| `/head` | `head.md` | Preparar edición de sección PeriodicoView |
| `/incidente` | `incidente.md` | Registrar incidente en `doc/arch/incidentes.md` |
| `/limpiar` | `limpiar.md` | Limpiar archivos temporales (hereda global) |
| `/news` | `news.md` | Leer y distribuir items de `news.txt` |
| `/next` | `next.md` | Próximos 5 pasos del roadmap |
| `/notify` | `notify.md` | Enviar notificación vía Telegram/Slack |
| `/qa` | `qa.md` | Registrar situación UX |
| `/report` | `report.md` | Generar reporte de avances |
| `/rm` | `rm.md` | Revisar roadmap |
| `/updoc` | `updoc.md` | Actualizar documentación completa |
| `/upguia` | `upguia.md` | Actualizar guía existente |
| `/upmec` | `upmec.md` | Actualizar mecánicas existentes |
| `/version` | `version.md` | Cerrar sesión con bump de versión |

## Foco por área

- `tx` → backend: `$ENGINE_DIR`, `$ANALYZERS_DIR`, `$DATA_DIR`, `$EXECUTION_DIR`
- `ui` → frontend: `$TEMPLATES_DIR`, `$STATIC_DIR`, `$DASHBOARD`
- `ux` → experiencia: `$GUIAS`, `$ALERTS_DIR`, `$STRATEGIES_DIR`

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

Archivos críticos: `$CRITICAL_FILES`. Cargar `skill("backup-pre-edit")` para más detalle.

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
| `$ENGINE_DIR` | Fusión de señales + decisión DeepSeek |
| `$ANALYZERS_DIR` | **9 analizadores** (técnico, on-chain, sentimiento, orderbook, fundamental, macro, cross-asset, ICT/SMC, ADX Regime) |
| `$DATA_DIR` | Recolectores + database |
| `$EXECUTION_DIR` | Paper broker, risk engine + ejecutores reales (Alpaca/OANDA) |
| `$LEARNING_DIR` | Journal + strategy evolver + backtest + replay |
| `$ALERTS_DIR` | Telegram + Discord notifier |
| `$STRATEGIES_DIR` | Estrategias documentadas + trade journal |
| `$GUIAS` | Guías de instalación, configuración, uso |
| `$ARCH` | ADRs, metodología, bugs, bitácora, reglas, reportes |
| `$IDEAS_DIR` | Ideas de sesión pendientes |
| `$TEMPLATES_DIR` | HTML templates del dashboard Flask (10 páginas) |
| `$STATIC_DIR` | CSS y assets del dashboard |
| `$TESTS_DIR` | Tests pytest |
| `$SKILLS_DIR` | Skills cargables + ICT FVG standalone |

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
|---|---|---|
| `$CONFIG` (flags, perfiles, time-exit) | `$GUIAS/guia_configuracion.md` |
| `$DASHBOARD` (endpoints, páginas) | `$GUIAS/guia_uso.md` (tabla de rutas) |
| `$EXECUTION_DIR/paper_broker.py`, `risk_engine.py`, `entry_filters.py` | `$GUIAS/guia_trading.md`, `$GUIAS/guia_configuracion.md` |
| `$ANALYZERS_DIR` (nuevo analyzer, cambios de peso) | `$GUIAS/guia_configuracion.md` (tabla de capas) |
| `tray_app.py` | `$GUIAS/guia_uso.md` (sección tray) |
| Cambio en número de tests | `README.md`, `$CHECKLIST`, `$RM` |

Cargar `skill("actualizar-docs")` para el checklist completo.

## Archivos relacionados

- `DILIGENCIA.md` — Sello de metodología
- `ROADMAP.md` — Roadmap del proyecto
- `CHECKLIST.md` — Checklist de implementación
- `CHANGELOG.md` — Historial de versiones

---

## SELLO DILIGENCIA

Proyecto adaptado a Diligencia v2.7.0.
