INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre los archivos del proyecto ($RM, $CHECKLIST). NO mostrar este archivo como output. ENTREGAR solo la tabla Top 5.

# /next — Próximos pasos según CHECKLIST + dependencias

Lee $RM y $CHECKLIST, identifica los próximos 5 items más relevantes para implementar, considerando dependencias y bloqueos.

## Qué hace
1. Leer $CHECKLIST AHORA (pendientes del proyecto)
2. Leer $RM AHORA (ítems PENDIENTE de todas las secciones)
3. Cruzar dependencias: items bloqueados van al final
4. Priorizar: P1 → P2 → P3
5. Entregar SOLO los 5 items más accionables en tabla:
   - ID, área, prioridad, item
   - Dependencias (si aplica)
   - Estimación (chica/mediana/grande)
   - Justificación de por qué este item es el siguiente lógico
6. Si el proyecto tiene $MANDATO y $BUGS (proyecto adaptado a Diligencia): cargar `skill("diligencia-consejo")` y agregar sección "Priorización estratégica (Consejero)" con:
   - Observaciones sobre el orden real (¿items del Top 5 dependen de fases sin completar?)
   - Deuda que bloquea (bugs abiertos, ADRs faltantes, features sin validar)
   - Recomendación concreta (qué hacer antes del Top 5)
7. Si existe $TESTING, incluir como punto final un enlace a los tests pendientes

## Formato de salida

**Top 5** — tabla con columnas: ID | Área | Prioridad | Item | Dependencias | Estimación | Justificación
**Priorización estratégica** (si proyecto adaptado) — observaciones del consejero: orden real, deuda, recomendación
**Testing** (si $TESTING existe) — enlace a tests pendientes

## Validación
- Exactamente 5 items en la tabla (o menos si $RM tiene menos)
- Cada item tiene valor en todas las columnas de la tabla
- Orden correcto: P1 antes que P2, P2 antes que P3
- No incluir items DONE en la lista
- Si $TESTING existe, la sección Testing está presente

## Anti-patrones
- NO incluir más de 5 items
- NO omitir la columna Justificación
- NO incluir items DONE
- NO ignorar dependencias (items bloqueados no van al tope)
- NO incluir items sin prioridad explícita
