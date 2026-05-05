# /newidea — Agregar idea al roadmap

Guarda una idea de la sesión actual como documento en `informes/ideas/` y agrega referencia en `documentos/roadmap.md`.

## Argumentos
`/newidea TITULO` — nombre del archivo

## Qué hace
1. Crea `informes/ideas/TITULO.md` con:
   - Contexto: 2-3 líneas de qué se trató la idea
   - Propuesta: descripción completa
   - Dependencias: sistemas que afecta
   - Relacionado con: (roadmap, guías, ADR si aplica)
2. Agrega entrada a `documentos/roadmap.md`
3. Reporta archivo creado

## Archivos que modifica
- informes/ideas/TITULO.md (nuevo)
- documentos/roadmap.md
