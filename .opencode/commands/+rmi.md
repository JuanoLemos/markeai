# /+rmi — Agregar idea al roadmap

Guarda una idea de la sesión actual como documento en `$PEND` y agrega referencia en `$RM`.

## Argumentos
`/+rmi TITULO` — nombre del archivo

## Qué hace
1. Crea `$PEND/TITULO.md` con:
   - Contexto: 2-3 líneas de qué se trató la idea
   - Propuesta: descripción completa
   - Dependencias: sistemas que afecta
   - Relacionado con: (roadmap, guías, ADR si aplica)
2. Agrega entrada a `$RM`
3. Reporta archivo creado

## Archivos que modifica
- $PEND/TITULO.md (nuevo)
- $RM
