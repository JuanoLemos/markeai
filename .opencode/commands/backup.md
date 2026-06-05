INSTRUCCIÓN: EJECUTAR backup pre-edit. NO modificar archivos originales. NO mostrar este archivo como output. ENTREGAR solo el listado de archivos respaldados.

# /backup — Backup de archivos críticos pre-edit

Respalda archivos críticos antes de editarlos, usando git stash o copia manual.

## Argumentos
/backup [archivo1 archivo2 ...]

- Sin argumentos: usa lista automática (git-tracked files modificados + AGENTS.md, ROADMAP.md, CHECKLIST.md, CHANGELOG.md)
- Con argumentos: respalda solo los archivos especificados

## Qué hace
1. Si git está disponible y working tree no está limpio:
   - `git stash push -m "backup pre-edit $(date)"` para archivos modificados
   - Reportar: "✅ backup: git stash creado"
2. Si no hay git:
   - Copiar cada archivo crítico a .old/bak_<archivo>.<fecha>
   - Si no existe .old/: preguntar si crearlo
3. Reportar SOLO la lista de archivos respaldados

## Formato de salida
✅ backup: <N> archivos respaldados
  - archivo1 → destino1
  - archivo2 → destino2

## Validación
- Los archivos respaldados existen antes de la copia
- Los destinos se crearon correctamente (stash o copia física)

## Anti-patrones
- NO ejecutar backup sin mostrar qué archivos se respaldarán
- NO sobrescribir backups existentes sin preguntar
- NO hacer git stash si el working tree está limpio

## Archivos que modifica
- .old/ (copia manual) o git stash (si hay git)
