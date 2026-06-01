# /upguia — Actualizar guía existente

Actualiza un documento de guía en `$GUIAS` con nuevo contenido o correcciones.

## Argumentos
`/upguia NOMBRE [sección]` — nombre del archivo y sección opcional

## Qué hace
1. Lee `$GUIAS/NOMBRE.md`
2. Pregunta al usuario qué sección actualizar
3. Aplica el cambio
4. Reporta diff

## Archivos que modifica
- $GUIAS/NOMBRE.md
