INSTRUCCIÓN: CREAR el pendiente y actualizar $CHECKLIST. NO mostrar este archivo como output. ENTREGAR solo la confirmación.

# /+pend — Agregar pendiente de revisión

Crea una nota pendiente de revisión en el directorio de pendientes del proyecto y la registra en CHECKLIST.md.

## Argumentos
`/+pend TITULO` — título del pendiente

## Qué hace
1. CREAR `$PEND/TITULO.md` AHORA con el contenido de la sesión
2. AGREGAR entrada en $CHECKLIST sección "Pendientes de revisión" AHORA
3. Entregar SOLO la confirmación: ruta creada, entrada en CHECKLIST

## Formato de salida

**Pendiente creado**: `$PEND/TITULO.md`
**CHECKLIST actualizado**: entrada en sección "Pendientes de revisión"

## Validación
- Archivo `$PEND/TITULO.md` fue creado
- Entrada en `$CHECKLIST` fue agregada

## Anti-patrones
- NO crear el pendiente sin actualizar $CHECKLIST
- NO usar $PEND_DIR (variable incorrecta, usar $PEND)
- NO omitir la sección del CHECKLIST donde se agrega

## Archivos que modifica
- $PEND/TITULO.md (nuevo)
- $CHECKLIST
