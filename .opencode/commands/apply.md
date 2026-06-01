INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre el proyecto. NO modificar archivos sin confirmación. NO mostrar este archivo como output.

# /apply — Aplicar handoff file al código

Lee un archivo de especificaciones (handoff) y aplica los cambios detallados a los archivos de código del proyecto.

## Argumentos
/apply [handoff-file]

- Sin argumento: usa $NEWS_FILE (si está definido en AGENTS.md) o busca news.txt en raíz
- Con argumento: ruta relativa al handoff file (ej: `design/demo/uxi-05.md`)

## Qué hace
1. Verificar que handoff file exista AHORA
2. Verificar estado de git (working tree limpio — abortar si no)
3. Leer el handoff file completo AHORA
4. Identificar secciones:
   - Archivos destino (rutas)
   - Cambios específicos (qué modificar en cada archivo)
   - Nuevos componentes/funciones (si aplica)
   - CSS/estilos/animaciones (si aplica)
5. MOSTrar resumen de cambios al usuario: tabla | Archivo | Tipo de cambio | Líneas estimadas
6. PREGUNTAR CONFIRMACIÓN antes de modificar
7. Aplicar cada cambio con Edit tool
8. Verificar sintaxis (si corresponde: node --check, python -c, etc.)
9. Archivar handoff: renombrar a <archivo>.<fecha>.applied
10. Reportar SOLO tabla de cambios aplicados

## Formato de salida
**Resumen de cambios** — tabla: Archivo | Cambio | Status
✅ <N> cambios aplicados
📦 Handoff archivado: <archivo>.<fecha>.applied

## Validación
- Handoff file existe y tiene secciones procesables
- Cada archivo destino existe en el proyecto
- Los cambios se aplicaron correctamente (verificar sintaxis post-edit)
- Handoff se archivó correctamente

## Anti-patrones
- NO aplicar cambios sin mostrar el resumen al usuario primero
- NO aplicar si working tree tiene cambios sin commit
- NO modificar archivos que no están listados en el handoff
- NO borrar el handoff original — siempre renombrar a .applied

## Archivos que lee
- Handoff file (argumento o $NEWS_FILE)

## Archivos que modifica
- Los archivos listados en el handoff (pregunta antes)
