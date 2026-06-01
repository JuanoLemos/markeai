INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre el archivo especificado. NO modificar sin confirmación. NO mostrar este archivo como output.

# /head — Preparar edición de sección en archivo

Lee una sección específica de un archivo grande y presenta el contexto necesario para editarla.

## Argumentos
/head ARCHIVO SECCIÓN

- ARCHIVO: ruta al archivo (relativa a raíz del proyecto)
- SECCIÓN: nombre de la sección (marcador ##, función, class, o bloque específico)

## Qué hace
1. Si ARCHIVO no existe: mostrar error y secciones disponibles en el proyecto
2. Buscar la sección en el archivo AHORA (grep por `## SECCIÓN`, `function SECCIÓN`, `class SECCIÓN`, `SECCIÓN` en contexto)
3. Si no encuentra: mostrar secciones disponibles y preguntar
4. Leer la sección + 10 líneas de contexto antes y después AHORA
5. Presentar diagnóstico:
   - Línea inicial/final de la sección
   - Estructura interna (sub-secciones, funciones hijas)
   - Dependencias (variables/imports que usa)
   - Funciones que llaman a esta sección
6. Preguntar al usuario qué cambio específico quiere hacer
7. Aplicar el cambio SOLO en los límites de la sección
8. Verificar sintaxis post-edit (node --check, python -c, etc.)

## Formato de salida
**Diagnóstico** — ARCHIVO (línea L-L)
  Sección: SECCIÓN
  Sub-secciones: <lista>
  Dependencias: <lista>
  Llaman desde: <lista>

**Cambio aplicado** (si se modifica)
  <diff>

## Validación
- El archivo existe en la ruta especificada
- La sección se encontró en el archivo
- El cambio se aplicó dentro de los límites de la sección
- Sintaxis verificada post-edit

## Anti-patrones
- NO editar fuera de la sección identificada (límites exactos)
- NO modificar el archivo sin mostrar el diagnóstico y el cambio propuesto
- NO asumir que la sección existe — buscarla con grep/contexto primero
- NO usar head sin argumento de archivo — especificar siempre

## Archivos que modifica
- ARCHIVO (solo la sección especificada)
