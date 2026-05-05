# /debug — Análisis profundo de módulo

Realiza un análisis detallado de un módulo o sección específica del proyecto.

## Argumentos
`/debug engine/decider` — análisis del motor de decisión
`/debug data/collector` — análisis de recolector de datos
`/debug execution/paper` — análisis del paper broker
`/debug dashboard` — análisis del dashboard Flask
`/debug database` — análisis de la base de datos

## Qué hace
1. Lee el/los archivos relevantes
2. Identifica estructura, entradas/salidas, dependencias
3. Lista posibles problemas o mejoras
4. Reporta en formato: archivo, línea, descripción, sugerencia
