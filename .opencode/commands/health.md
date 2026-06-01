INSTRUCCIÓN: EJECUTAR las 3 verificaciones de abajo sobre los archivos del proyecto. NO mostrar este archivo como output. ENTREGAR solo la tabla de resultados.

# /health — Verificar integridad del código

Ejecuta 3 verificaciones rápidas de integridad del código del proyecto. Soporta proyectos JS/TS. Para otros stacks, reporta limitación y sugiere alternativa.

## Qué hace
0. **Detectar stack del proyecto** AHORA — leer `.opencode/HARNESS.md` (campo Stack) o `AGENTS.md` ($STACK o $HARNESS). Si no se detecta o no es JS: reportar "⚠️ /health solo soporta JS/TS. Usar /diligencia-check para estructura." y ABORTAR los 3 checks.
1. **Balance de paréntesis** — verificar paréntesis sin cerrar en el archivo JS principal AHORA
2. **Consistencia de rutas** — comparar rutas backend con llamadas HTTP del frontend AHORA
3. **Sintaxis JS** — ejecutar `node --check` sobre archivos JS críticos del proyecto AHORA

## Formato de salida
**Tabla de resultados** — verificación | estado (✅/❌) | detalle
**Resultado final** — "✅ Todo OK" o "❌ N errores encontrados"

## Formato de salida

**Checks** — tabla: Verificación | Estado (✅/❌) | Detalle
**Resultado final** — "✅ Todo OK" o "❌ N errores encontrados"

## Validación
- Las 3 verificaciones están presentes en la tabla
- Cada verificación tiene estado explícito (✅ o ❌)
- El resultado final coincide con la tabla (si alguna ❌, resultado es ❌)

## Anti-patrones
- NO saltear ninguna de las 3 verificaciones
- NO reportar OK sin haber ejecutado los checks reales
- NO usar caracteres de estado no estándar (solo ✅/❌)
- NO modificar archivos durante la verificación
