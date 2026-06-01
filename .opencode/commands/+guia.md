# /+guia — Crear nueva guía

Crea un documento de guía en `$GUIAS`.

## Argumentos
`/+guia NOMBRE` — nombre del archivo (ej: `/+guia TUTORIAL_ADVANZADO`)

## Qué hace
1. Verifica que `NOMBRE` no exista ya en `$GUIAS`
2. Crea `$GUIAS/NOMBRE.md` con estructura estándar:
   - Título
   - Secciones según el tipo de guía
3. Si existe una guía similar, la usa como referencia
4. Reporta archivo creado

## Archivos que modifica
- $GUIAS/NOMBRE.md (nuevo)
