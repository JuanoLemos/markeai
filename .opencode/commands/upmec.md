INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre los archivos del proyecto ($MECANICAS). NO mostrar este archivo como output. ENTREGAR solo el diff del cambio.

# /upmec — Actualizar documento existente

Actualiza un documento en $MECANICAS con contenido nuevo.

## Argumentos
/upmec NOMBRE [sección]

- NOMBRE: archivo en $MECANICAS sin extensión
- sección: sección del documento a actualizar (opcional, si se omite pregunta)

## Qué hace
1. Leer $MECANICAS/NOMBRE.md AHORA
2. Si no se especificó sección: listar secciones y preguntar cuál actualizar
3. Preguntar qué cambio aplicar (texto nuevo o modificación)
4. Aplicar el cambio con Edit tool
5. Reportar SOLO el diff del cambio aplicado

## Formato de salida
--- $MECANICAS/NOMBRE.md
+++ $MECANICAS/NOMBRE.md (editado)
<diff de las líneas cambiadas>

## Validación
- $MECANICAS/NOMBRE.md existe antes de editar
- La sección especificada existe en el documento
- El diff muestra las líneas exactas modificadas

## Anti-patrones
- NO modificar el documento sin mostrar la sección y el cambio propuesto al usuario
- NO editar fuera de la sección indicada
- NO reemplazar el archivo completo — solo la sección especificada

## Archivos que modifica
- $MECANICAS/NOMBRE.md
