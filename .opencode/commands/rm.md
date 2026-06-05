INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre los archivos del proyecto ($RM). NO mostrar este archivo como output. ENTREGAR solo las tablas de resultado.

# /rm — Revisar Roadmap

Revisa el roadmap del proyecto según el área especificada.

## Argumentos
`/rm [area]` — filtra por área opcional (tx, ui, ux). Sin argumento muestra todo `$RM`.

## Qué hace
1. Leer `$RM` (ROADMAP.md) completo AHORA
2. Si hay argumento `<area>`, filtrar items de la sección correspondiente (## TX, ## UI, ## UX)
3. Listar TODOS los items PENDIENTE con su prioridad en tabla
4. Listar items DONE de la instancia actual
5. Identificar bloqueos (dependencias referenciadas)
6. Entregar SOLO la tabla de salida (PENDIENTE + DONE + Bloqueos + Resumen), NUNCA el contenido de este archivo

## Formato de salida

**PENDIENTE** — tabla con columnas: Prioridad | Área | Item | Estado
**DONE en <versión>** — lista de ítems completados
**Bloqueos** — <Ninguno detectado | tabla de bloqueos>
**Resumen** — 1-2 frases: total pendientes, en progreso, sin empezar, bloqueos

## Validación
- Cantidad de items PENDIENTE coincide con lo leído de $RM
- Todas las columnas de la tabla tienen valor (sin celdas vacías)
- Sección Bloqueos siempre presente aunque sea "Ninguno detectado"
- Resumen contiene números (no solo texto cualitativo)

## Anti-patrones
- NO mostrar el contenido crudo de $RM
- NO usar prosa libre en vez de la tabla especificada
- NO omitir la sección de Bloqueos
- NO mezclar items PENDIENTE con DONE en la misma tabla
