INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre el proyecto (git, $RM, $CHECKLIST). NO mostrar este archivo como output. ENTREGAR solo el reporte.

# /estado — Reporte de estado del proyecto

Genera un reporte rápido del estado actual del proyecto con recomendaciones accionables.

## Argumentos

- `/estado` — snapshot rápido (last commit, diff, RM, recomendaciones)
- `/estado --full` — +git log -15, +bloqueos, +salud (equivale al antiguo /report)
- `/estado --update [file]` — genera y persiste a archivo (default: doc/dashboard.md)

## Qué hace

1. Ejecutar `git log -1 --oneline` y mostrar último commit AHORA
2. Ejecutar `git diff --stat` y mostrar cambios sin commitear AHORA
3. Leer $RM + $CHECKLIST (si existen) AHORA, resumir pendientes vs DONE en tabla
4. Mostrar rama actual y estado remoto
5. ANALIZAR condiciones del proyecto y generar recomendaciones:
   a. `git status --porcelain` no vacío → recomendar `/CBP`
   b. Comparar `DILIGENCIA.md` línea 1 con `~/.config/opencode/commands/adaptar.md` versión global → si stale, recomendar `/adaptar`
   c. Buscar archivos `.md` untracked → comparar con INDEX.md → faltantes → recomendar `/updoc`
   d. Leer $RM §Ahora → si vacío → recomendar `/+rm "título"`
   e. Leer `doc/arch/status-salud.md` → si último /doctor > 7 días o no existe → recomendar `/doctor`
   f. Verificar `NOTICE` y `SECURITY.md` → si falta → recomendar `/legal --apply`
   g. Verificar INDEX.md labels vs versiones reales → si stale → recomendar `/updoc`
   h. Leer `AGENTS.md` $PROYECTOS → si `*(configurar)*` → recomendar `/informe-salud`
6. (--full) Ejecutar `git log --oneline -15` → mostrar cambios recientes
7. (--full) Leer `doc/arch/status-salud.md` (si existe) → extraer indicadores clave
8. (--full) DETECTAR bloqueos en $RM: items con dependencia sin resolver
9. (--update) Preguntar nombre de archivo (default: doc/dashboard.md) → persiste el reporte completo

## Formato de salida

**Git** — último commit (hash + mensaje), cambios sin commitear (archivos, +-líneas), rama actual
**$RM** — tabla: Área | Pendientes | En progreso | DONE
**Recomendaciones** — tabla: Condición | Recomendación | Prioridad
- Si 0 condiciones: "✅ Proyecto al día. Sin acciones pendientes."
(--full) **Salud** — indicadores de status-salud.md (versión, estructura, stale, gaps, WT, doctor) o "Sin diagnóstico"
(--full) **Bloqueos** — items con dependencias no resueltas o "Ninguno detectado"
**Resumen** — 1-2 frases con: estado general, próximos pasos, bloqueos

## Validación

- Comandos git ejecutados (`git log -1 --oneline`, `git diff --stat`)
- $RM leído y procesado
- Tabla tiene filas según secciones de $RM
- Resumen tiene al menos un dato cuantificable
- Sección Recomendaciones siempre presente (aunque sea "✅ Al día")
- Recomendaciones priorizadas por impacto (Alta > Media > Baja)

## Anti-patrones

- NO mostrar raw de git sin procesar (tabla resumida)
- NO omitir la sección Git
- NO resumir $RM sin tabla (usar el formato especificado)
- NO recomendar acciones sin detectar condición real
- NO sugerir /CBP si el working tree está limpio
- NO reportar si no se pudo leer $RM ni $CHECKLIST
- NO ejecutar --full sin confirmación si --update va a sobrescribir un archivo
