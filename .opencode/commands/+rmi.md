INSTRUCCIÓN: CREAR los archivos indicados abajo en el proyecto. NO mostrar este archivo como output. ENTREGAR solo la confirmación de creación.

# /+rmi — Agregar idea al roadmap

Guarda una idea de la sesión actual como documento en `$PEND` y agrega referencia en `$RM`.

## Argumentos
`/+rmi TITULO [area]` — título de la idea y área opcional (tx, ui, ux)

## Qué hace
1. CREAR `$PEND/TITULO.md` AHORA con:
   - Contexto: 2-3 líneas de qué se trató la idea
   - Propuesta: descripción completa
   - Dependencias: sistemas que afecta
   - Relacionado con: (roadmap, guías, ADR si aplica)
2. Si se especifica área, agregar la entrada en la sección correspondiente de `$RM`
3. Si no se especifica área, agregar al final de `$RM`
4. Entregar SOLO la confirmación: archivo creado, ruta ($variables), preview de entrada en $RM

## Formato de salida

**Archivo creado**: `$PEND/TITULO.md`
**Roadmap actualizado**: `$RM` (sección <area>)
**Preview de entrada**: <texto de la entrada agregada>

## Validación
- Archivo `$PEND/TITULO.md` fue creado efectivamente
- Entrada en `$RM` fue agregada en la sección correspondiente
- El reporte usa notación `$VARIABLE`, no paths hardcodeados

## Anti-patrones
- NO reportar éxito sin haber creado el archivo
- NO usar paths hardcodeados en el reporte (usar `$PEND`, `$RM`)
- NO crear el archivo sin agregar la entrada en $RM

## Archivos que modifica
- $PEND/TITULO.md (nuevo)
- $RM
