INSTRUCCIÓN: EJECUTAR las instrucciones de abajo. NO mostrar este archivo como output. ENTREGAR SOLO la explicación breve.

# /explica — Explicación breve y sencilla

Explica de forma simple y corta cualquier concepto del sistema Diligencia: mecánicas, variables, comandos, estándares.

## Argumentos

`/explica <concepto>`

Ejemplos:
- `/explica roadmap` — qué es el ROADMAP y cómo funciona
- `/explica +mec` — qué hace el comando +mec
- `/explica $CHECKLIST` — qué variable es y qué archivo apunta
- `/explica updoc` — flujo del comando /updoc
- `/explica guarda` — qué es la guarda de ejecución
- `/explica declarativo` — diferencia entre declarativo y procedural

## Qué hace

1. LEER el concepto del argumento AHORA
2. BUSCAR en la documentación de Diligencia: AGENTS.md, GUIA_DE_COMANDOS.md, ESTANDAR-COMANDOS.md, GUIA_DE_USO.md, GUIA_DE_ADAPTACION.md, GUIA_DE_REVISION.md, ROADMAP.md, bugs.md, incidentes.md, ADR-001.md, ADR-002.md, ADR-003.md, MECANICA-CBP.md, MECANICA-DOCUMENTAL.md, GUIA_DE_BUENAS_PRACTICAS.md, GUIA_ECOSISTEMAS.md, GUIA_REFERENCIA_RAPIDA.md, ADR_SUMMARY.md, identidad.md, MANDATO.md, status-salud.md
3. IDENTIFICAR la definición más clara. Si el concepto no tiene documentación formal pero aparece en ROADMAP.md, CHANGELOG.md, o DILIGENCIA.md como ítem pendiente o planificado, inferir su propósito del contexto del proyecto (nombre, prioridad, ecosistema donde se ubica).
4. ENTREGAR SOLO la explicación breve (1-3 líneas, lenguaje llano, sin markdown salvo que el concepto requiera tabla o código)
5. SIEMPRE sugerir caminos óptimos y dependencias (1 línea extra: comandos que dependen del concepto, flujo recomendado, o docs complementarios)

## Formato de salida

**Argumento**: `/explica <concepto>`
**Explicación**: 1-3 líneas en lenguaje llano. Sin encabezados ni secciones extra.
**Sugerencias**: 1 línea con → comandos relacionados, flujo óptimo, o docs complementarios.

Si el concepto no se encuentra en ningún archivo ni en ROADMAP:
**No encontré '<concepto>' en la documentación de Diligencia.**
Si aparece como ítem de roadmap pendiente: explicar desde el contexto y marcarlo como "Idea de roadmap (P2/P3)".

## Validación

- El concepto del argumento fue buscado en todos los archivos de documentación listados
- La explicación tiene entre 1 y 3 líneas
- Las sugerencias incluyen 1 línea con → comandos relacionados, flujo óptimo, o docs complementarios
- Si no se encuentra documentación pero sí en ROADMAP: se explicó por contexto (ej: "Idea de roadmap P3: ...")
- Si no existe en ningún lado: el mensaje usa el término exacto del argumento
- No se entregó contenido crudo de archivos

## Anti-patrones

- NO dar explicaciones largas (>3 líneas + 1 sugerencia)
- NO usar jerga innecesaria; lenguaje llano y directo
- NO mostrar contenido crudo de archivos como output
- NO incluir secciones extra en el output (solo "Argumento:", "Explicación:", "Sugerencias:")
- NO explicar comandos que no existen; si no está en docs ni en ROADMAP, reportar "No encontré"
- NO inventar definiciones sin base documental. ROADMAP.md, CHANGELOG.md y DILIGENCIA.md son fuentes válidas para inferir propósito de ítems pendientes.
- NO omitir sugerencias — cada respuesta debe incluir 1 línea de caminos/dependencias

## Archivos que lee

- AGENTS.md (variables y comandos)
- doc/guias/GUIA_DE_COMANDOS.md (referencia de comandos)
- doc/guias/ESTANDAR-COMANDOS.md (estándar de formatos)
- doc/guias/GUIA_DE_USO.md (flujo de uso)
- doc/guias/GUIA_DE_ADAPTACION.md (proceso de migración)
- doc/guias/GUIA_DE_REVISION.md (auditoría del sistema)
- ADAPTAR-COMANDOS.md (referencia técnica global)
- ROADMAP.md (fases y prioridades)
- doc/arch/bugs.md (bug tracker)
- doc/arch/incidentes.md (incidentes runtime)
- doc/mecanicas/MECANICA-DOCUMENTAL.md (motor documental)
- doc/guias/GUIA_DE_BUENAS_PRACTICAS.md (hábitos y workflows)
- doc/guias/GUIA_ECOSISTEMAS.md (mapa de ecosistemas)
- doc/guias/GUIA_REFERENCIA_RAPIDA.md (referencia rápida de comandos y flujos)
