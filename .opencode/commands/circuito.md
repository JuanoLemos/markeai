INSTRUCCIÓN: EJECUTAR las instrucciones de abajo. NO mostrar este archivo como output. ENTREGAR solo la tabla de hallazgos.

# /circuito — Revisar integridad lógica y UX

Escanea el proyecto en busca de circuitos rotos: handlers vacíos, callejones sin salida, rutas huérfanas, navegación rota, estados no manejados, feedback faltante.

## Argumentos

`/circuito [area]` — foco opcional. Sin argumento revisa todo el proyecto.

Ejemplos:
- `/circuito` — escaneo completo
- `/circuito dashboard` — solo archivos de dashboard
- `/circuito ui` — solo frontend (JSX/TSX/HTML)
- `/circuito api` — solo backend (rutas Express)

## Qué hace

1. Leer AGENTS.md del proyecto para mapear archivos frontend y backend
2. Cargar `skill("diligencia-circuito")` con los 8 checks
3. Delegar búsquedas masivas a `@explore` para escanear patrones
4. Cruzar rutas backend ↔ fetch frontend (checks 3-4)
5. Entregar SOLO la tabla de hallazgos (NUNCA el contenido de este archivo)

## Formato de salida

**Circuito lógico** `<area o "completo">` — tabla:

| # | Check | Archivo:Línea | Hallazgo | Severidad |
|---|-------|---------------|----------|-----------|
| 1 | Handler vacío | `Dashboard.tsx:42` | `onClick={handleExport}` no definido | P3 |
| ... | ... | ... | ... | ... |

Si un check no tiene hallazgos, mostrar "✅ Sin hallazgos" en esa fila.

**Resumen:** N hallazgos (X P2, Y P3)

## Validación

- Las 8 filas de la tabla están presentes (aunque digan "✅ Sin hallazgos")
- Cada hallazgo tiene archivo:línea concreto
- Checks 3-4 incluyen cross-reference backend↔frontend
- Resumen contiene conteo P2/P3
- Si no hay hallazgos: "✅ Circuito limpio — 0 hallazgos"

## Anti-patrones

- NO reportar sin archivo:línea exacto
- NO sugerir implementaciones
- NO usar prosa — tabla
- NO reportar handlers que claramente funcionan
- NO saltear checks 3-4 aunque parezcan pesados (cross-reference es obligatorio)
