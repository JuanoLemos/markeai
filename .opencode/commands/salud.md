INSTRUCCIÓN: EJECUTAR BUILD* para generar el reporte de salud. NO ejecutar PLAN — los datos de diagnóstico deben ser heredados del comando anterior del workflow (/updoc o /doctor). NO mostrar este archivo como output.

# /salud — Reporte de salud del proyecto (BUILD* only)

Genera `doc/arch/status-salud.md` a partir de los datos de diagnóstico ya auditados por `/updoc` o `/doctor`.
Siempre ejecuta BUILD*: no tiene PLAN propio — los datos se heredan del paso anterior del workflow.

## Argumentos

/salud [--force]

Sin argumentos: genera status-salud.md con datos heredados.
`--force`: regenerar incluso si status-salud.md ya existe en esta sesión.

## Qué hace (BUILD*)

1. LEER `~/.config/opencode/templates/doc-base/status-salud.md` AHORA (template base)
2. LEER datos de diagnóstico del contexto heredado (de /updoc Fases A→E+H, /doctor Fases 1→2)
3. GENERAR `doc/arch/status-salud.md` con:

   | Sección | Fuente de datos |
   |---|---|
   | Versión actual | /updoc Fase B (CHANGELOG latest) o /version Step 1 |
   | Estructura | /doctor Fase 1a (estructura OK/❌) |
   | Docs stale | /updoc Fase C (stale count y lista) |
   | Gaps documentales | /updoc Fase E (gaps count) |
   | Cross-ref gaps | /updoc Fase H (D1-D5 count) |
   | Último /doctor | /doctor Fase 2 (resumen) o "Nunca ejecutado" |
   | Working tree | git status actual |
   | ADRs pendientes | /doctor Fase 1c (ADRs sin revisar) |
   | Template sync | /updoc D5 (template vs proyecto) |
   | Bump type | /updoc Fase E (minor/patch calculado) |

4. ACTUALIZAR INDEX.md: agregar/actualizar entrada para `doc/arch/status-salud.md` con versión actual y fecha
5. OUTPUT: "🩺 status-salud.md generado en doc/arch/ — N indicadores, X stale, Y gaps"

## Formato de salida

```
🩺 /salud — Reporte de salud generado
📄 doc/arch/status-salud.md
📊 Indicadores: 10 | Stale: N | Gaps: M | Estructura: ✅/❌
```

## Validación

- BUILD* ejecutado solo si /updoc o /doctor ejecutó PLAN previamente en el mismo workflow
- NO ejecutar standalone — siempre debe ser invocado por /CBP
- Si no hay datos de diagnóstico en el contexto: ERROR "No se detectó PLAN previo. Ejecutar /updoc o /doctor primero."
- status-salud.md actualizado en INDEX.md

## Anti-patrones

- NO ejecutar sin PLAN previo en el mismo workflow
- NO modificar datos de diagnóstico — solo reflejar el estado auditado
- NO sobreescribir status-salud.md sin cambios detectables (usar --force si se requiere regeneración)
- NO leer archivos de diagnóstico directamente — usar datos heredados del contexto

## Archivos que modifica

- `doc/arch/status-salud.md` (crear o actualizar)
- `INDEX.md` (entrada de salud)

## Archivos que lee (solo template)

- `~/.config/opencode/templates/doc-base/status-salud.md` (template base)
