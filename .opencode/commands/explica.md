INSTRUCCIÓN: EJECUTAR las instrucciones de abajo. NO mostrar este archivo como output. ENTREGAR SOLO la explicación breve.

# /explica — Explicación en 3 capas

Explica cualquier concepto de Diligencia en tres capas: criollo (qué es), técnico (cómo funciona), impacto (por qué importa).

## Argumentos

`/explica <concepto>`

Ejemplos:
- `/explica roadmap` — qué es el ROADMAP
- `/explica +mec` — qué hace el comando +mec
- `/explica $CHECKLIST` — qué variable es
- `/explica updoc` — flujo del comando /updoc

## Qué hace

1. LEER el concepto del argumento AHORA
2. BUSCAR en la documentación de Diligencia: AGENTS.md, GUIA_DE_COMANDOS.md, ESTANDAR-COMANDOS.md, GUIA_DE_USO.md, GUIA_DE_ADAPTACION.md, GUIA_DE_REVISION.md, ROADMAP.md, bugs.md, incidentes.md, ADR-001.md, ADR-002.md, ADR-003.md, MECANICA-CBP.md, MECANICA-DOCUMENTAL.md, MECANICA-ENFORCEMENT.md, GUIA_DE_BUENAS_PRACTICAS.md, GUIA_ECOSISTEMAS.md, GUIA_REFERENCIA_RAPIDA.md, GUIA_DE_CONTRIBUCION.md, ADR_SUMMARY.md, identidad.md, MANDATO.md, status-salud.md, README.md
3. IDENTIFICAR la información más clara
4. REDACTAR cuatro capas:

   **En criollo**: 1-2 líneas que responden "¿qué es esto y para qué sirve?" Sin jerga. Con analogías si aplica (ej: "es como una lista de compras").

   **Técnico**: 1-2 líneas con archivo, comando, formato, o dato preciso. Responde "¿cómo funciona?"

   **Impacto**: 1 línea sobre qué pasa si se usa bien o se ignora. Costo/beneficio para el proyecto.

   **Implicancia estratégica**: Si el proyecto está adaptado a Diligencia ($RM, $MANDATO), cargar `skill("diligencia-consejo")` y agregar 1 línea: ¿qué decisión de proyecto impacta entender este concepto? ¿Qué pasa si se ignora en la trayectoria del proyecto?

5. Si el concepto no tiene documentación formal pero aparece en ROADMAP.md, CHANGELOG.md o DILIGENCIA.md, inferir su propósito y marcarlo como "Idea de roadmap".

## Formato de salida

**En criollo:** [qué es, para qué sirve, en lenguaje sencillo]

**Técnico:** [archivo, comando, formato, dependencias]

**Impacto:** [costo/beneficio para el proyecto]

**Implicancia estratégica:** [qué decisión de proyecto impacta entender esto — solo si proyecto adaptado a Diligencia]

Si el concepto no se encuentra en ningún lado:
**Ese concepto no aparece en la documentación de Diligencia.**

## Validación

- Las tres capas están presentes (o justificar por qué alguna no aplica)
- "En criollo" no tiene jerga técnica (ni "comando", "variable", "dependencia", "flujo")
- "Técnico" solo aparece si el concepto tiene un archivo, comando o formato asociado
- "Impacto" es una oración clara de costo/beneficio
- No se excede de 2 líneas por capa

## Anti-patrones

- NO usar jerga en "En criollo" (palabras como "orquestador", "workflow", "binding", "meta-PLAN")
- NO omitir "Impacto" — el usuario necesita saber por qué le sirve o no
- NO mezclar las capas — cada una responde una pregunta distinta
- NO inventar definiciones si no hay base documental
- NO dar opiniones personales en "Técnico" — solo hechos

## Archivos que lee

Same as current (AGENTS.md, GUIA_DE_COMANDOS.md, etc.)
