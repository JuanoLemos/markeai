# Comandos Personalizados de OpenCode
# Versión: 1.7 | Actualizado: 2026-05-29

## Propósito

Guía de referencia rápida de todos los comandos slash disponibles para el proyecto Némesis Detective.

## Uso

Los comandos se invocan directamente en el chat de OpenCode escribiendo `/comando [argumentos]`.

---

## Sesión

| Comando | Función |
|---|---|
| `/plan [tarea]` | Planificar con DeepSeek V4 Pro, luego ejecutar BUILD tras aprobación |
| `/version [minor\|patch\|X.Y] [--notes "..."]` | Cerrar sesión: bump de versión, CHANGELOG, bitácora, commit |
| `/commit [mensaje]` | `git add -A` + commit con formato del proyecto |

## Documentación

| Comando | Función |
|---|---|
| `/updoc` | Sincronizar documentación completa: cruza CHECKLIST con los 3 RM y AGENTS.md |
| `/+guia [nombre]` | Crear guía nueva en `doc/guia/` a partir del último commit |
| `/upguia` | Actualizar guías existentes en `doc/guia/` según el último commit |
| `/+mec [nombre]` | Crear mecánica nueva en `doc/mecanicas/` a partir del último commit |
| `/upmec` | Actualizar mecánicas existentes en `doc/mecanicas/` según el último commit |

## Creación

| Comando | Función |
|---|---|
| `/+pend [nombre]` | Agregar pendiente de revisión en `doc/pendientes/` |
| `/+rm [nombre] [rm]` | Agregar ítem al roadmap de sesión en `doc/` |
| `/+rmi [nombre] [ii]` | Agregar idea al roadmap (revisable con IA) en `doc/` |

## Revisión

| Comando | Función |
|---|---|
| `/*` | Próximos 5 pasos según CHECKLIST + dependencias + ideas |
| `/*ux` | Próximos 5 pasos enfocados en UX |
| `/*ui` | Próximos 5 pasos enfocados en UI |
| `/*tx` | Próximos 5 pasos enfocados en TX |
| `/checklist` | Cruzar CHECKLIST y RMs: detecta duplicados, inconsistencias, dependencias |
| `/rm [tx\|ux\|ui]` | Revisar el Roadmap específico |
| `/estado` | Reporte rápido: últimos commits, cambios pendientes, próximos 5 pasos |

## Enfoque

| Comando | Función |
|---|---|
| `/foco [ui\|tx\|ux\|no]` | Enfocar agente: `ui`=frontend, `tx`=backend, `ux`=mecánicas, `no`=desactivar |

## Distribución

| Comando | Función |
|---|---|
| `/news [apply]` | Leer `design/report/news.txt` y distribuir items a RMs. `apply` escribe cambios. |

## Diagnóstico

| Comando | Función |
|---|---|
| `/debug [sección]` | Análisis profundo: backend/ruta, frontend/componente, DB/tabla, prompt/módulo |
| `/head SECCIÓN` | Preparar edición de sección del PeriodicoView (MASTHEAD / HEADLINE / PERFIL / PSISTATS / CRONICA / EXPEDIENTES / FUENTES / ARCHIVO) |
| `/qa "descripción"` | Registrar situación UX: crea entrada en `doc/qa/` y CHECKLIST |
| `/health` | Verificar integridad del código: paréntesis en app.js, rutas backend↔frontend, sintaxis JS |

## Operaciones

| Comando | Función |
|---|---|
| `/backup` | Backup de archivos críticos |
| `/backupall` | Backup completo del proyecto (.zip, excluye node_modules/.env/.db) |
| `/limpiar` | Eliminar archivos temporales (query, start, line*.txt, scripts/chk.js) |
| `/Tel [on\|off\|test]` | Control remoto vía Telegram. Con `/plan` envía aprobación al celular. |
| `/upclaude` | Actualizar `design/report/CLAUDE-AVANCES.md` para Claude Code |
| `/claude` | Generar informe de avances y recomendaciones de Claude |
| `/setuxi` | Aplicar cambios de Claude desde `news.txt` a `app.js` |

## Circuito Ideal

Flujo diario recomendado:

```
    1. /estado         → panorama del proyecto
    2. /*              → próximos 5 pasos priorizados
    3. /foco [área]    → cargar contexto del área
    4. /plan [tarea]   → diseñar solución (solo lectura)
    5. BUILD           → implementar cambios
    6. /commit         → checkpoint rápido
    7. /version        → cierre formal de sesión
```

Flujo de documentación (en paralelo al trabajo):

```
  /news          distribuye cambios nuevos a los RMs
  /+rm, /+pend   crea nuevos ítems en los RMs
  /+mec, /+guia  crea documentos de mecánicas/guias
  /updoc         sincroniza toda la documentación
```

Diagnóstico (cuando algo falla):

```
  /debug [sección]   → análisis profundo
  /health            → verificar integridad del código
  /checklist         → cruzar RMs y detectar duplicados
  /rm [área]         → revisar un RM específico
```

Dependencias entre archivos:

```
  CHECKLIST.md ←→ RM_TX, RM_UX, RM_UI  (se cruzan entre sí)
  AGENTS.md     → define skills y comandos activos
  /updoc        → sincroniza todos los anteriores
```

---

## Agentes y Skills

Los comandos son interpretados por el agente de OpenCode leyendo `.opencode/commands/<comando>.md`. Los skills (`skill("nombre")`) agregan documentación de referencia a la sesión.

**Skills disponibles:** `frontend-edit`, `prompt-batch`, `backup-pre-edit`, `actualizar-docs`, `nueva-mecanica`. Ver `AGENTS.md` para detalle completo.

### Comandos con argumentos

```
/debug backend/routes/game.js     → analiza esa ruta
/commit Fix autenticación         → commit con mensaje
/+mec SISTEMA_ECONOMICO           → crea mecánica
```
