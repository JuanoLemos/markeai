INSTRUCCIÓN: CREAR la guía indicada abajo. NO mostrar este archivo como output. ENTREGAR solo la confirmación.

# /+guia — Crear guía nueva

Crea un documento de guía en $GUIAS a partir de la plantilla ($GUIAS_TEMPLATE).

## Argumentos
`/+guia NOMBRE` — nombre del archivo y título

## Qué hace
1. Verificar que el nombre no exista ya en $GUIAS AHORA
2. Copiar la plantilla (`$GUIAS_TEMPLATE`) a `$GUIAS/NOMBRE.md`
3. Rellenar título y fecha en la nueva guía
4. Actualizar AGENTS.md si aplica
5. Entregar SOLO la confirmación: ruta ($GUIAS/NOMBRE.md), template usado, fecha

## Formato de salida

**Guía creada**: `$GUIAS/NOMBRE.md`
**Template usado**: `$GUIAS_TEMPLATE`
**AGENTS.md**: actualizado (si aplica)

## Validación
- El directorio `$GUIAS` no tenía el archivo antes (evitar duplicados)
- El template `$GUIAS_TEMPLATE` existe y fue leído
- El archivo fue creado efectivamente

## Anti-patrones
- NO crear la guía sin verificar que el nombre no exista
- NO crear sin usar la plantilla (`$GUIAS_TEMPLATE`)
- NO ignorar la actualización de AGENTS.md cuando corresponde

## Archivos que modifica
- $GUIAS/NOMBRE.md (nuevo)
- AGENTS.md (opcional)
