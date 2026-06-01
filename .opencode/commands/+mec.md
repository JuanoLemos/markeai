INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre los archivos del proyecto ($MECANICAS). NO mostrar este archivo como output. ENTREGAR solo la línea de confirmación.

# /+mec — Crear documento desde template

Crea un documento en $MECANICAS a partir de la plantilla $MECANICAS_TEMPLATE.

## Argumentos
/+mec NOMBRE ["Título descriptivo"]

- NOMBRE: nombre del archivo sin extensión (ej: `SISTEMA_X`)
- "Título": título del documento (default: NOMBRE)

## Qué hace
1. Verificar que $MECANICAS_TEMPLATE existe AHORA
2. Si no existe: CREAR el template genérico antes de continuar
3. Verificar que $MECANICAS/NOMBRE.md no exista ya
4. Copiar el template a $MECANICAS/NOMBRE.md
5. Rellenar título y versión (v1.0) en el nuevo archivo
6. Preguntar si agregar entrada en AGENTS.md (en la sección de documentación/mecánicas)
7. Reportar SOLO: `✅ +mec: NOMBRE.md creado en $MECANICAS`

## Formato de salida
✅ +mec: NOMBRE.md creado en $MECANICAS

## Validación
- $MECANICAS_TEMPLATE existe (lo crea si no)
- $MECANICAS/NOMBRE.md no existía antes de la copia
- El archivo nuevo contiene título y versión rellenados

## Anti-patrones
- NO crear el archivo sin verificar que el nombre es único
- NO omitir la pregunta de actualizar AGENTS.md
- NO usar contenido hardcodeado — siempre usar el template

## Archivos que modifica
- $MECANICAS/NOMBRE.md (nuevo)
- $MECANICAS_TEMPLATE (solo si no existe y se crea)
- AGENTS.md (opcional)
