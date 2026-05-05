# /plan — Planificar con DeepSeek V4 Pro y luego ejecutar con BUILD

Planifica una tarea usando el modelo DeepSeek V4 Pro (modo PLAN), y una vez aprobado por el usuario, ejecuta la implementación con BUILD.

## Cuándo usarlo
- Tareas complejas que requieren análisis antes de implementar
- Cambios arquitectónicos que afectan múltiples archivos
- Features que requieren decisión del usuario antes de codificar

## Qué hace
1. Cambia a modo PLAN (lectura + análisis, sin editar archivos)
2. Lee los archivos relevantes (según se indique)
3. Propone plan detallado con:
   - Archivos a modificar
   - Líneas exactas de cambio
   - Riesgos y mitigaciones
   - Esfuerzo estimado
4. Pregunta: "¿Apruebo para BUILD?"
5. Si el usuario confirma → ejecuta los cambios (modo BUILD)
6. Si el usuario rechaza → ajusta el plan

## Archivos que NO modifica
- No modifica archivos hasta que el usuario apruebe el plan
