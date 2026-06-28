INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre los archivos del proyecto ($CHECKLIST, $RM). NO mostrar este archivo como output. ENTREGAR solo la tabla de inconsistencias.

# /checklist — Revisar Checklist

Lee $CHECKLIST y $RM, identifica inconsistencias, pendientes, duplicados.

## Qué hace
1. Leer $CHECKLIST completo AHORA
2. Leer $RM (secciones de pendientes del roadmap) AHORA
3. Comparar: items PENDIENTE en $CHECKLIST vs $RM
4. Identificar duplicados entre $CHECKLIST y $RM
5. Identificar items DONE con fechas muy viejas o no reflejados en $RM
6. Si el proyecto tiene $BUGS y $ADRS (proyecto adaptado a Diligencia): cargar `skill("diligencia-consejo")`, leer bugs.md y ADR_SUMMARY.md, y agregar sección "Deuda detectada (Consejero)" con bugs abiertos, ADRs faltantes, y fases sin completar que bloquean avance.
7. Entregar SOLO la tabla: estado | archivo | item | prioridad | observación, seguida de Deuda detectada si aplica

## Formato de salida

**Inconsistencias** — tabla con columnas: Estado | Archivo | Item | Prioridad | Observación
Cada fila es una discrepancia entre $CHECKLIST y $RM.
**Deuda detectada** (si proyecto adaptado) — tabla: Tipo | Cantidad | Impacto (bugs abiertos, ADRs faltantes, fases sin completar)

## Validación
- Cada inconsistencia referencia el archivo fuente exacto
- No hay falsos positivos (items que están bien pero aparecen como problema)
- Items stale detectados correctamente (DONE con fecha >1 instancia)
- La tabla puede estar vacía si no hay inconsistencias (mostrar "✅ Sin inconsistencias")

## Anti-patrones
- NO mostrar archivos crudos en el output
- NO decir "todo OK" sin haber ejecutado el cruce $CHECKLIST ↔ $RM
- NO omitir detección de items stale
- NO reportar duplicados que no lo son (items iguales en distintas secciones no son duplicados)
