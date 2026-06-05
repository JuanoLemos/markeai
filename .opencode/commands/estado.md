INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre el proyecto (git, $RM, $CHECKLIST). NO mostrar este archivo como output. ENTREGAR solo el reporte.

# /estado — Reporte de estado del proyecto

Genera un reporte rápido del estado actual del proyecto.

## Qué hace
1. Ejecutar `git log -1 --oneline` y mostrar último commit AHORA
2. Ejecutar `git diff --stat` y mostrar cambios sin commitear AHORA
3. Leer $RM + $CHECKLIST (si existen) AHORA, resumir pendientes vs DONE en tabla
4. Mostrar rama actual y estado remoto
5. Entregar SOLO el reporte en formato tabla: área | estado | últimas acciones | próximo paso

## Formato de salida

**Git** — último commit (hash + mensaje), cambios sin commitear (archivos, +-líneas), rama actual
**$RM** — tabla: Área | Pendientes | En progreso | DONE
**Resumen** — 1-2 frases con: estado general, próximos pasos, bloqueos

## Validación
- Comandos git ejecutados (`git log -1 --oneline`, `git diff --stat`)
- $RM leído y procesado
- Tabla tiene filas según secciones de $RM
- Resumen tiene al menos un dato cuantificable

## Anti-patrones
- NO mostrar raw de git sin procesar (tabla resumida)
- NO omitir la sección Git
- NO resumir $RM sin tabla (usar el formato especificado)
- NO reportar si no se pudo leer $RM ni $CHECKLIST
