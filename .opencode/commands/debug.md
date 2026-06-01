INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre el archivo indicado por el usuario. NO mostrar este archivo como output. ENTREGAR solo la tabla de hallazgos.

# /debug — Análisis profundo de sección

Realiza un análisis detallado de una sección específica del proyecto.

## Argumentos
`/debug backend/ruta` — análisis de ruta específica
`/debug frontend/componente` — análisis de componente frontend
`/debug DB/tabla` — análisis de tabla en base de datos
`/debug modulo` — análisis de cualquier módulo del proyecto

## Qué hace
1. Leer el/los archivos relevantes AHORA (los que el usuario indicó en el argumento)
2. Identificar estructura, entradas/salidas, dependencias
3. Listar posibles problemas o mejoras en tabla
4. Entregar SOLO la tabla de hallazgos: archivo | línea | descripción | sugerencia

## Formato de salida

**Hallazgos** — tabla con columnas: Archivo | Línea | Descripción | Sugerencia
Cada fila representa un hallazgo individual.

## Validación
- Se leyó al menos el archivo target especificado en el argumento
- Cada hallazgo tiene valor en todas las 4 columnas
- La sugerencia es accionable (no genérica como "mejorar esto")
- Estructura del archivo y dependencias identificadas

## Anti-patrones
- NO mostrar contenido crudo de archivos en el output
- NO dar sugerencias genéricas ("mejorar", "optimizar") sin explicar cómo
- NO omitir la columna de línea (aunque sea estimada, siempre presente)
- NO analizar archivos que no son del proyecto
