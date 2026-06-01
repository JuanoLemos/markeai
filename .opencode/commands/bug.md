INSTRUCCIÓN: EJECUTAR las instrucciones de abajo. NO mostrar este archivo como output. NO modificar archivos sin confirmación del usuario.

# /bug — Reportar bug en el proyecto

Registra un bug en el tracker `$BUGS` con severidad, archivo y descripción. Crea el tracker desde template si no existe.

## Argumentos

`/bug "<descripcion>" [--archivo "<ruta>"] [--severidad P1|P2|P3]`

| Argumento | Requerido | Descripción |
|---|---|---|
| `<descripcion>` | Sí | Qué ocurre, en qué condiciones |
| `--archivo` | No | Archivo o módulo afectado |
| `--severidad` | No | P1 (crítico), P2 (importante), P3 (mejora). Default: P2 |

## Qué hace

1. LEER `AGENTS.md` AHORA — buscar `$BUGS` (variable que apunta al tracker)
2. Si `$BUGS` no existe en AGENTS.md: PREGUNTAR al usuario si desea definirla como `doc/arch/bugs.md`
3. Si el archivo `$BUGS` no existe: CREARLO desde `~/.config/opencode/templates/doc-base/bugs.md` con `<NOMBRE_DEL_PROYECTO>` reemplazado AHORA
4. LEER `$BUGS` AHORA — detectar último ID (B-NN) y calcular B-NN+1
5. CREAR entrada con campos completos en la sección de severidad correspondiente (P1/P2/P3):
   - ID auto-incremental (B-01, B-02...)
   - Archivo (del argumento o *por determinar*)
   - Severidad (del argumento o P2)
   - Descripción
   - Causa: *(pendiente de análisis)*
   - Impacto: *(pendiente de evaluación)*
   - Estado: Abierto
   - Fix: —
6. ACTUALIZAR tabla Resumen en `$BUGS` (totales por severidad + abiertos)
7. AGREGAR entrada en `$CHECKLIST` AHORA (en sección "Bugs abiertos" o general)
8. AGREGAR entrada en Historial de cambios en `$BUGS`
9. Entregar SOLO: **Bug B-NN registrado en $BUGS, CHECKLIST actualizado**

## Formato de salida

**Bug registrado**: B-NN — <descripción>
**Archivo**: `<ruta>` | **Severidad**: P1/P2/P3
**Estado**: Abierto
**$BUGS actualizado**: ✅ | **$CHECKLIST actualizado**: ✅

## Validación

- Cada bug tiene ID único auto-incremental
- ID no colisiona con bugs existentes
- El tracker se creó desde template si no existía
- Resumen en bugs.md refleja el nuevo bug
- CHECKLIST tiene entrada del nuevo bug
- Historial de cambios en bugs.md actualizado

## Anti-patrones

- NO reusar IDs existentes — asignar B-NN+1
- NO modificar bugs existentes sin argumento explícito (solo crear nuevos)
- NO crear el tracker sin preguntar al usuario si `$BUGS` no está definido
- NO omitir la actualización de $CHECKLIST
- NO registrar bugs sin descripción
- NO mostrar el contenido de este archivo como output

## Archivos que lee

- `AGENTS.md` ($BUGS variable)
- `$BUGS` (tracker existente)
- `~/.config/opencode/templates/doc-base/bugs.md` (template si no existe)

## Archivos que modifica

- `$BUGS` (nueva entrada + resumen + historial)
- `$CHECKLIST` (nueva entrada de bug)
