INSTRUCCIÓN: CREAR el documento QA y actualizar $CHECKLIST. NO mostrar este archivo como output. ENTREGAR solo la confirmación.

# /qa — Reportar situación a revisar

Registra una situación específica del proyecto que querés revisar o resolver.

## Argumentos
`/qa "descripción del problema"`

## Qué hace
1. CREAR documento de QA en $QA AHORA
2. INCLUIR: situación observada, comportamiento esperado vs real, pasos para reproducir
3. AGREGAR entrada en $CHECKLIST AHORA
4. Entregar SOLO la confirmación: archivo QA creado ($QA/), todos los campos rellenos, CHECKLIST actualizado

## Formato de salida

**Documento QA creado**: `$QA/<titulo>.md`
**Campos**: situación observada, comportamiento esperado, comportamiento real, pasos para reproducir
**CHECKLIST actualizado**: entrada registrada

## Validación
- Todos los campos del QA están rellenos (situación, esperado, real, pasos)
- El documento fue creado en $QA
- Entrada en $CHECKLIST fue agregada

## Anti-patrones
- NO omitir la sección "comportamiento esperado vs real"
- NO omitir los pasos para reproducir
- NO crear el documento sin actualizar $CHECKLIST

## Archivos que modifica
- $QA/[TITULO].md (nuevo)
- $CHECKLIST
