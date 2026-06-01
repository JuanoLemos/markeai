INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre $RM. NO mostrar este archivo como output. ENTREGAR solo la línea de confirmación.

# /+rm — Agregar ítem al roadmap

Agrega un nuevo ítem a $RM con título, prioridad y área.

## Argumentos
/+rm "TITULO" [área] [P1|P2|P3]

- TITULO: texto del ítem (usar comillas si contiene espacios)
- área: sección de $RM (ej: Core, Docs, Tools). Default: primera sección PENDIENTE.
- P1|P2|P3: prioridad. Default: P2

## Qué hace
1. Leer $RM AHORA para identificar secciones disponibles
2. Si no se especifica área, usar la primera sección con items PENDIENTE
3. Si no se especifica prioridad, usar P2
4. Si el ítem ya existe en $RM (mismo título), preguntar si es duplicado
5. Agregar el ítem a la sección destino con el formato: `| TITULO | PRIORIDAD | 🔴 Pendiente |`
6. Reportar SOLO: `✅ +rm: "TITULO" (PRIORIDAD, SECCIÓN)`

## Formato de salida
✅ +rm: "TITULO" (PRIORIDAD, SECCIÓN)

## Validación
- El ítem no existe ya con el mismo título en $RM
- La sección destino existe en $RM
- Prioridad es P1/P2/P3

## Anti-patrones
- NO agregar el ítem sin mostrarlo al usuario primero
- NO crear secciones nuevas sin preguntar
- NO modificar archivos fuera de $RM

## Archivos que modifica
- $RM
