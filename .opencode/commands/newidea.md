# /newidea — Agregar idea al roadmap

Guarda una idea de la sesión actual como documento en `doc/informes/ideas/` y agrega referencia en `doc/documentos/roadmap.md`.

## Argumentos
`/newidea TITULO` — nombre del archivo

## Qué hace
1. Crea `doc/informes/ideas/TITULO.md` con:
   - Contexto: 2-3 líneas de qué se trató la idea
   - Propuesta: descripción completa
   - Dependencias: sistemas que afecta
   - Relacionado con: (roadmap, guías, ADR si aplica)
2. Agrega entrada a `doc/documentos/roadmap.md`
3. Reporta archivo creado

## Archivos que modifica
- doc/informes/ideas/TITULO.md (nuevo)
- doc/documentos/roadmap.md
