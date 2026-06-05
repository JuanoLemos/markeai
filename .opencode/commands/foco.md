INSTRUCCIÓN: EJECUTAR las instrucciones de abajo para enfocar al agente. NO mostrar este archivo como output. ENTREGAR solo el badge del foco activado.

# /foco — Enfocar agente en área de trabajo

Prepara al agente para trabajar en un área específica del proyecto: carga los archivos relevantes, skills asociados, y agrega badge visible al foco.

## Argumentos
/foco [área|no]

| Argumento | Efecto |
|---|---|
| área | Enfocar en sección específica de $RM |
| `no` | Desactivar foco, volver a modo neutral |
| Sin argumento | Mostrar estado actual del foco |

## Qué hace
1. Sin argumento: mostrar foco actual o "sin foco"
2. `/foco no`: desactivar foco, limpiar badge
3. `/foco <área>`:
   - Leer $RM AHORA, encontrar la sección correspondiente
   - Cargar contexto del área (ítems PENDIENTE, DONE, bloqueos)
   - ANUNCIAR: "🎯 FOCO: <área> activo. Todas las respuestas se centran en esta área."
   - Incluir badge en cada respuesta mientras el foco esté activo
4. El badge se mantiene hasta que se invoque `/foco no`

## Formato de salida
✅ FOCO: <área> activo
Ó
✅ FOCO desactivado
Ó
📌 Foco actual: <área> (o "Sin foco activo")

## Validación
- El área especificada existe como sección en $RM
- /foco no siempre desactiva el badge

## Anti-patrones
- NO activar foco en áreas que no existen en $RM
- NO mantener el badge después de /foco no
- NO leer archivos externos a $RM sin necesidad explícita
