# Skill: actualizar-docs — Sincronización documental completa

## Cuándo cargar
Cuando el usuario pide `/updoc` o "actualizá los docs"

## Proceso
1. Lee `documentos/checklist.md`, `documentos/roadmap.md`
2. Identifica items DONE en roadmap que no están en checklist
3. Identifica duplicados entre checklist y roadmap
4. Identifica items stale (marcados DONE hace más de 1 instancia)
5. Reporta tabla de cambios sugeridos
6. Si el usuario confirma: aplica los cambios con `edit`

## Archivos que modifica
- documentos/checklist.md
- documentos/roadmap.md
- AGENTS.md
