INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre los archivos del proyecto ($RM, $CHECKLIST). NO mostrar este archivo como output. ENTREGAR SOLO el reporte consolidado.

# /report — Reporte consolidado del proyecto

Genera un reporte completo del estado del proyecto a partir de $RM, $CHECKLIST y git log.

## Argumentos
- `/report` — genera y muestra el reporte
- `/report --update` — genera y actualiza el archivo de reporte del proyecto

## Qué hace
1. Leer $RM AHORA (todas las secciones PENDIENTE + DONE + Bloqueos)
2. Leer $CHECKLIST AHORA (items pendientes por prioridad)
3. Ejecutar `git log --oneline -15` AHORA para cambios recientes
4. Ejecutar `git diff --name-only` AHORA para cambios sin commit
5. Consolidar en reporte con secciones:
   - ## Resumen — estado general, total pendientes/en-progreso/bloqueados
   - ## Pendientes — items P1/P2/P3 de RM + CHECKLIST
   - ## Últimos cambios — git log (últimos 15 commits)
   - ## Working tree — archivos modificados sin commit (si hay)
   - ## Bloqueos — items bloqueados o ninguno
   - ## Recomendaciones — próximo item lógico según dependencias
6. Si `--update`: escribir a un archivo de reporte (preguntar nombre o usar default doc/reporte-proyecto.md)
7. ENTREGAR SOLO el reporte completo

## Formato de salida
## Resumen
<2-3 frases con números>

## Pendientes
| Prioridad | Items | En progreso |
|---|---|---|
| P1 | <N> | <M> |
| P2 | <N> | <M> |
| P3 | <N> | <M> |

## Últimos cambios
<git log --oneline -15>

## Working tree
<git diff --name-only o "Limpio">

## Bloqueos
<Ninguno detectado | tabla>

## Recomendaciones
<próximo item lógico>

## Validación
- Todas las secciones del reporte están presentes
- Los números de pendientes suman correctamente
- git log muestra exactamente 15 commits (o menos si el repo tiene menos)
- Bloqueos siempre presente

## Anti-patrones
- NO mostrar raw de git log sin resumir
- NO omitir sección Bloqueos
- NO incluir prosa irrelevante — solo la estructura especificada

## Archivos que lee
- $RM
- $CHECKLIST
- Repositorio git (log y diff)

## Archivos que modifica
- doc/reporte-proyecto.md (solo con --update)
