INSTRUCCION: LEER el wave manifest. EJECUTAR las tareas segun las reglas OnFail. NO modificar archivos sin confirmacion. NO ejecutar cambios sin preguntar en modo plan.

# /ola — Sistema de oleadas de tareas

Planifica, ejecuta y monitorea oleadas de tareas multi-proyecto ejecutadas por agentes autonomos.

## Subcomandos

### planear
`/ola planear <proyecto>` — Lee el ROADMAP del proyecto y genera un wave manifest en `doc/olas/`.
Muestra la tabla de tareas propuestas para que el usuario la revise y ajuste.

1. LEER `ROADMAP.md` del proyecto — extraer items P1 P2 pendientes
2. CLASIFICAR por tipo segun MECANICA-TASK-ROUTER.md
3. GENERAR `doc/olas/<proyecto>-ola-NN.md` con formato MECANICA-OLAS
4. ASIGNAR agentes segun MECANICA-TASK-ROUTER
5. DETECTAR conflictos entre tareas (mismo archivo, mismo proyecto)
6. MOSTRAR tabla: `| ID | Tarea | Agente | Depende | OnFail |`
7. PREGUNTAR: "Aprobar manifest? [si/no/editar]"

### ejecutar
`/ola ejecutar <archivo-olas>` — Ejecuta las tareas del wave manifest.

1. LEER el archivo `.md` especificado
2. EXTRAER tabla de tareas
3. GRUPAR tareas por proyecto (respetando R1: 1 agente por proyecto)
4. EJECUTAR en oleadas:
   - Wave 1: tareas sin dependencias -> paralelo entre proyectos
   - Wave 2: tareas que dependen de Wave 1 -> secuencial
5. PARA CADA tarea:
   a. INVOCAR al agente correspondiente (@narrador, @trader, etc.)
   b. SI el agente falla: aplicar regla OnFail declarada
   c. ACTUALIZAR estado en el manifest
6. AL FINAL:
   a. RESUMEN: N tareas (G OK, R fallo, S saltadas)
   b. SI hay fallos: generar entradas en $BUGS
   c. SUGERIR /CBP si hay cambios pendientes

### estado
`/ola estado <archivo-olas>` — Muestra el progreso actual de la ola.

1. LEER el manifest
2. CONTAR: Pendientes, En progreso, OK, Fallo, Saltadas
3. MOSTRAR: `G X tareas completadas, R Y falladas, Z pendientes`

## Ejemplos
- `/ola planear nemesis` — crear manifest desde ROADMAP de Nemesis
- `/ola ejecutar nemesis-ola-01` — ejecutar la ola 01 de Nemesis
- `/ola estado nemesis-ola-01` — ver progreso

## Archivos que modifica
- `doc/olas/*.md` — estado de tareas actualizado durante ejecucion
- `doc/arch/bugs.md` — registro de fallos si los hay
