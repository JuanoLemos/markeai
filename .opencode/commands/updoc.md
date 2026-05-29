# /updoc — Actualizar documentación completa

Actualiza TODO: `doc/documentos/checklist.md`, `doc/documentos/roadmap.md`, `AGENTS.md`, y otros archivos que hayan cambiado desde la última sesión.

## Qué hace
1. Lee `git log --oneline -10` para ver qué cambió desde el último `/updoc`
2. Lee `git diff --stat` para cambios sin commitear
3. Pregunta al usuario: "¿qué items nuevos marcar como DONE y en qué archivo?"
4. Cruza `doc/documentos/checklist.md` ↔ `doc/documentos/roadmap.md`
5. Detecta:
   - Items DONE en roadmap que faltan en checklist
   - Items stale (DONE hace >1 instancia)
   - Duplicados entre archivos
   - Referencias a nombres/archivos desactualizados
6. **Compara `.opencode/commands/` con `AGENTS.md`** para detectar comandos nuevos no listados
7. Detecta nuevas guías en `doc/guias/` que falten en `AGENTS.md`
8. Reporta tabla de cambios
9. Si usuario confirma: aplica cambios a:
   - doc/documentos/checklist.md
   - doc/documentos/roadmap.md
   - doc/guias/
   - AGENTS.md
10. Sugiere commit message con los items actualizados

## Archivos que modifica
- doc/documentos/checklist.md
- doc/documentos/roadmap.md
- doc/guias/ (si hay guías nuevas)
- AGENTS.md
