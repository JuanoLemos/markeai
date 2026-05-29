# /+guia — Crear nueva guía

Crea un documento de guía en `doc/guias/`.

## Argumentos
`/+guia NOMBRE` — nombre del archivo (ej: `/+guia TUTORIAL_ADVANZADO`)

## Qué hace
1. Verifica que `NOMBRE` no exista ya en `doc/guias/`
2. Crea `doc/guias/NOMBRE.md` con estructura estándar:
   - Título
   - Secciones según el tipo de guía
3. Si existe una guía similar, la usa como referencia
4. Reporta archivo creado

## Archivos que modifica
- doc/guias/NOMBRE.md (nuevo)
