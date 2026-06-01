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
2. BUSCAR en la documentación de Diligencia: AGENTS.md, GUIA_DE_COMANDOS.md, ESTANDAR-COMANDOS.md, GUIA_DE_USO.md, ADAPTAR-COMANDOS.md, ROADMAP.md, bugs.md, incidentes.md, MECANICA-DOCUMENTAL.md, GUIA_DE_BUENAS_PRACTICAS.md
3. IDENTIFICAR la definición más clara y relevante para ese concepto
4. ENTREGAR SOLO la explicación breve (1-3 líneas, lenguaje llano, sin markdown salvo que el concepto requiera tabla o código)

## Formato de salida

**Argumento**: `/explica <concepto>`
**Explicación**: 1-3 líneas en lenguaje llano. Sin encabezados ni secciones extra.

Si el concepto no se encuentra en la documentación:
**No encontré '<concepto>' en la documentación de Diligencia.**

## Validación

- El concepto del argumento fue buscado en todos los archivos de documentación listados
- La explicación tiene entre 1 y 3 líneas
- Si no se encuentra, el mensaje de "no encontrado" usa el término exacto del argumento
- No se entregó contenido crudo de archivos

## Anti-patrones

- NO dar explicaciones largas (>3 líneas)
- NO usar jerga innecesaria; lenguaje llano y directo
- NO mostrar contenido crudo de archivos como output
- NO incluir secciones extra en el output (solo "Argumento:" y "Explicación:")
- NO explicar comandos que no existen; si no está documentado, reportar "No encontré"
- NO inventar definiciones; si el concepto no está en los docs, admitir que no se encontró

## Archivos que lee

- AGENTS.md (variables y comandos)
- doc/guias/GUIA_DE_COMANDOS.md (referencia de comandos)
- doc/guias/ESTANDAR-COMANDOS.md (estándar de formatos)
- doc/guias/GUIA_DE_USO.md (flujo de uso)
- ADAPTAR-COMANDOS.md (referencia técnica)
- ROADMAP.md (fases y prioridades)
