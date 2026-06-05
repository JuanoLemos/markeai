INSTRUCCIÓN: ACTUALIZAR la guía indicada. NO modificar sin confirmación del usuario. NO mostrar este archivo como output.

# /upguia — Actualizar guía existente

Actualiza un documento de guía en $GUIAS con nuevo contenido o correcciones.

## Argumentos
`/upguia NOMBRE [sección]` — nombre del archivo y sección opcional

## Qué hace
1. Leer el documento de guía en $GUIAS AHORA
2. PREGUNTAR al usuario qué sección actualizar (esperar respuesta)
3. MOSTRAR diff del cambio propuesto al usuario
4. APLICAR el cambio solo después de confirmación del usuario
5. Entregar SOLO la confirmación: archivo, sección, líneas agregadas/quitadas

## Formato de salida

**Archivo modificado**: `$GUIAS/NOMBRE.md`
**Sección**: <sección>
**Diff**: <líneas agregadas / quitadas>

## Validación
- El usuario confirmó antes de aplicar el cambio
- El diff fue mostrado antes de aplicar
- La guía modificada existe (validar con Test-Path)

## Anti-patrones
- NO aplicar cambios sin mostrar el diff primero
- NO aplicar cambios sin confirmación del usuario
- NO modificar archivos que no estén en $GUIAS

## Archivos que modifica
- $GUIAS/NOMBRE.md (el documento de guía especificado)
