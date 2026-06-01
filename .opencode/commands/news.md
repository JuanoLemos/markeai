INSTRUCCIÓN: EJECUTAR las instrucciones de abajo sobre los archivos del proyecto ($NEWS_FILE, $RM). NO mostrar este archivo como output. ENTREGAR SOLO la tabla resumen.

# /news — Leer y distribuir ítems a $RM

Lee $NEWS_FILE y distribuye los ítems encontrados a las secciones correspondientes de $RM.

## Argumentos
- `/news` — solo muestra resumen (no modifica archivos)
- `/news apply` — distribuye ítems a $RM y actualiza CHECKLIST

## Qué hace
1. Leer $NEWS_FILE AHORA
2. Si $NEWS_FILE no existe o está vacío: reportar "📭 News vacío o ausente" y terminar
3. Identificar secciones en $NEWS y mapearlas a secciones de $RM
4. Si solo resumen (`/news`):
   - Mostrar tabla con columna: Sección | Ítems nuevos | Ítems aplicados previamente
5. Si apply (`/news apply`):
   - Mostrar la tabla primero
   - PREGUNTAR CONFIRMACIÓN antes de modificar archivos
   - Agregar cada ítem a su sección correspondiente en $RM
   - Si alguno ya existe en $RM: mostrar duplicado, no agregar
   - Renombrar $NEWS_FILE a $NEWS_FILE.<fecha>.applied
   - Reportar: "✅ news applied: <N> items distribuidos"

## Formato de salida
**Resumen** — tabla: Sección | Nuevos | Aplicados
(apply) **Distribuidos** — <N> items agregados a $RM

## Validación
- $NEWS_FILE debe existir para continuar
- Cada sección en $NEWS se mapea a una sección existente en $RM
- No se aplican cambios sin confirmación explícita del usuario
- El archivo .applied no se crea si el apply falló

## Anti-patrones
- NO aplicar cambios sin confirmación del usuario
- NO distribuir ítems a secciones de $RM que no existen
- NO procesar $NEWS si $NEWS_FILE no está definido en AGENTS.md
- NO borrar $NEWS_FILE — siempre renombrar a .applied

## Archivos que lee
- $NEWS_FILE

## Archivos que modifica
- $RM (solo con apply)
- $CHECKLIST (solo con apply)
- $NEWS_FILE → $NEWS_FILE.<fecha>.applied (solo con apply)
