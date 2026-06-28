INSTRUCCIÓN: PLANIFICAR la tarea del usuario. NO ejecutar cambios sin aprobación explícita. NO mostrar este archivo como output. ENTREGAR solo el plan.

# /plan — Planificar y luego ejecutar con BUILD

Planifica una tarea en modo PLAN (solo lectura + análisis), y una vez aprobado por el usuario, ejecuta la implementación con BUILD.

## Cuándo usarlo
- Tareas complejas que requieren análisis antes de implementar
- Cambios arquitectónicos que afectan múltiples archivos
- Features que requieren decisión del usuario antes de codificar

## Qué hace
1. MANTENERSE en modo PLAN (solo lectura + análisis, NO editar archivos aún)
2. Leer los archivos relevantes AHORA (según lo que pidió el usuario)
3. Si el proyecto tiene $RM y $CHECKLIST (proyecto adaptado a Diligencia): cargar `skill("diligencia-consejo")` y aplicar las 6 preguntas del consejero. Leer ROADMAP.md, CHECKLIST.md, MANDATO.md, bugs.md, ADR_SUMMARY.md. Agregar sección "Observaciones del Consejero" al plan.
4. ENTREGAR SOLO el plan detallado (NUNCA el contenido de este archivo):
   - Archivos a modificar
   - Líneas exactas de cambio
   - Riesgos y mitigaciones
   - Esfuerzo estimado
   - Observaciones del Consejero (si aplica)
5. PREGUNTAR explícitamente: "¿Apruebo para BUILD?"
6. ESPERAR confirmación del usuario antes de ejecutar cambios
7. Si el usuario rechaza, ajustar el plan según feedback

## Formato de salida

**Plan** — secciones:
- **Archivos a modificar**: lista de rutas exactas
- **Líneas de cambio**: descripción de qué agregar/quitar en cada archivo
- **Riesgos**: impactos potenciales y mitigaciones
- **Esfuerzo**: estimación (chica/mediana/grande)
- **Observaciones del Consejero** (si proyecto adaptado): tabla con Tipo, Observación, Sugerencia — supuestos, dominio, roadmap, deuda, mandato, aprender

**Pregunta de aprobación**: "¿Apruebo para BUILD?" (no BUILD sin respuesta sí)

## Validación
- El plan cubre todos los requisitos del usuario
- Cada archivo listado tiene especificado qué cambio hacer
- Riesgos y mitigaciones están presentes
- Esfuerzo estimado está presente
- No se ejecutó ningún cambio durante la fase PLAN

## Anti-patrones
- NO entrar en modo BUILD sin aprobación explícita del usuario
- NO modificar archivos durante la fase PLAN
- NO omitir la sección de riesgos
- NO dar una estimación sin justificación
- NO comenzar a implementar mientras el usuario está revisando el plan

## Archivos que NO modifica
- No modifica archivos hasta que el usuario apruebe el plan
