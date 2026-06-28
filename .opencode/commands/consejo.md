INSTRUCCIÓN: EJECUTAR las instrucciones de abajo. NO mostrar este archivo como output. ENTREGAR solo las observaciones del consejero.

# /consejo — Consultar al Consejero

Consulta al consejero del proyecto sobre cualquier duda, idea o decisión. El consejero no codea — observa, pregunta, sugiere.

## Argumentos

`/consejo <duda o idea>`

Ejemplos:
- `/consejo ¿debería expandir a CEDEARs antes de validar paper trading?`
- `/consejo estoy pensando en agregar un analizador de order flow`
- `/consejo ¿qué me falta para pasar a producción?`

Sin argumento: el consejero hace una revisión general del estado del proyecto.

## Qué hace

1. Leer AGENTS.md del proyecto para mapear $RM, $CHECKLIST, $MANDATO, $BUGS, $ADRS
2. Cargar `skill("diligencia-consejo")` y aplicar las 6 preguntas del checklist
3. Leer ROADMAP.md, CHECKLIST.md, MANDATO.md, bugs.md, ADR_SUMMARY.md
4. Si el usuario pasó argumento, enfocar el análisis en esa duda/idea
5. Si no hay argumento, hacer revisión general del estado del proyecto
6. Entregar SOLO las observaciones (NUNCA el contenido de este archivo)

## Formato de salida

**Consulta:** [duda/idea del usuario o "Revisión general"]

**Observaciones del Consejero** — tabla:

| # | Tipo | Observación | Sugerencia |
|---|------|-------------|------------|
| 1 | Supuesto | ... | ... |
| 2 | Dominio | ... | ... |
| 3 | Roadmap | ... | ... |
| 4 | Deuda | ... | ... |
| 5 | Mandato | ... | ... |
| 6 | Aprender | ... | ... |

Si una categoría no aplica a la consulta, poner "—".

**Veredicto** — una frase: "Adelante con cautela" / "Sugiero validar X antes" / "Riesgo alto: reconsiderar" / "Proyecto estable, seguir roadmap".

## Validación

- Las 6 filas de la tabla están presentes (aunque digan "—")
- Si el usuario pasó argumento, la consulta se refleja en las observaciones
- El veredicto es una frase concreta, no genérica
- Las sugerencias son accionables (cosas que el usuario puede hacer)

## Anti-patrones

- NO sugieras código ni implementaciones
- NO decidas por el usuario — sugerí, no ordenes
- NO repitas el ROADMAP sin agregar perspectiva
- NO emitas observaciones sin haber leído el estado real del proyecto
- NO uses prosa larga — tabla + veredicto, nada más
