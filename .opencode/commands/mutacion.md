INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre el archivo .zip recibido. NO mostrar este archivo como output. ENTREGAR SOLO el reporte de absorción.

# /mutacion — Absorber mutaciones de un proyecto

Procesa un archivo .zip enviado por un proyecto adaptado a Diligencia.
Extrae el contenido, consolida las mutaciones y actualiza el archivo de observaciones de Diligencia.

## Argumentos

/mutacion <ruta-al-zip>

## Qué hace

1. VERIFICAR que el archivo .zip existe y es accesible
2. EXTRAER a `doc/arch/mutaciones-recibidas/temp/`
3. LEER `mutaciones.md` del contenido extraído
4. MOSTRAR resumen:
   - Nombre del proyecto (del header del archivo)
   - Versión heredada
   - N de mutaciones (IDs M1, M2...)
   - Fecha de la revisión
5. PREGUNTAR: "¿Consolidar estas mutaciones en archivo de observaciones? [sí/no]"
6. Si sí:
   a. Copiar `mutaciones.md` a `doc/arch/mutaciones-recibidas/<fecha>-<proyecto>_mutaciones.md`
   b. AGREGAR observaciones a `doc/arch/mutaciones-consolidadas.md` (si no existe, crearlo)
      Formato:
      ```
      ## <fecha> — <proyecto>
      | ID | Mutación | Tipo | Dónde | Estado |
      | M1 | ... | ... | ... | Pendiente |
      ```
   c. Mover .zip a `doc/arch/mutaciones-recibidas/processed/`
   d. LIMPIAR temp
7. Reportar: "✅ N mutaciones de <proyecto> consolidadas en mutaciones-consolidadas.md"

## Formato de salida

```
📦 /mutacion — Absorber mutaciones
📁 Proyecto: X
🔖 Versión heredada: v1.17.7
📊 Mutaciones: 3 (M1, M2, M3)
✅ Consolidadas en doc/arch/mutaciones-consolidadas.md
```

## Validación

- El .zip contiene al menos un archivo mutaciones.md
- El contenido de mutaciones.md tiene formato tabla válido
- No se consolida sin confirmación del usuario
- El .zip original se mueve a processed/ (no se borra, no se elimina)
- No se sobrescriben observaciones existentes — las nuevas se agregan al archivo consolidado

## Anti-patrones

- NO procesar .zip sin mutaciones.md adentro
- NO sobrescribir el .zip original (mover a processed/)
- NO consolidar sin preguntar
- NO extraer archivos del .zip fuera de la carpeta temp
- NO ejecutar este comando en un proyecto que no sea Diligencia
