INSTRUCCIÓN: EJECUTAR las instrucciones de abajo. NO mostrar este archivo como output. NO modificar archivos sin confirmación del usuario.

# /incidente — Registrar incidente o crash en producción

Registra un incidente runtime (crash, error en producción, anomalía del sistema) en `$INCIDENTS` con stack trace, severidad y mitigación.

## Argumentos

`/incidente "<descripcion>" [--stack "<stack>"] [--severidad P1|P2|P3]`

| Argumento | Requerido | Descripción |
|---|---|---|
| `<descripcion>` | Sí | Qué ocurrió, cuándo, en qué entorno |
| `--stack` | No | Stack trace o log relevante (opcional) |
| `--severidad` | No | P1 (caída total), P2 (funcionalidad degradada), P3 (anomalía menor). Default: P2 |

## Qué hace

1. LEER `AGENTS.md` AHORA — buscar `$INCIDENTS` (variable que apunta al incident tracker)
2. Si `$INCIDENTS` no existe en AGENTS.md: PREGUNTAR al usuario si desea definirla como `doc/arch/incidentes.md`
3. Si el archivo `$INCIDENTS` no existe: CREARLO desde `~/.config/opencode/templates/doc-base/incidentes.md` AHORA (con `<NOMBRE_DEL_PROYECTO>` reemplazado)
4. LEER `$INCIDENTS` AHORA — detectar último ID (I-NN) y calcular I-NN+1
5. CREAR entrada con campos completos:
   - ID auto-incremental (I-01, I-02...)
   - Fecha y hora actual
   - Severidad
   - Descripción (del argumento)
   - Stack trace (del argumento o *no disponible*)
   - Causa: *(pendiente de investigación)*
   - Mitigación: *(pendiente)*
   - Estado: Abierto
6. ACTUALIZAR tabla Resumen en `$INCIDENTS`
7. AGREGAR entrada en `$CHECKLIST` AHORA
8. Entregar SOLO: **Incidente I-NN registrado**

## Formato de salida

**Incidente registrado**: I-NN — <descripción>
**Severidad**: P1/P2/P3 | **Estado**: Abierto
**$INCIDENTS actualizado**: ✅ | **$CHECKLIST actualizado**: ✅

La plantilla vive en `~/.config/opencode/templates/doc-base/incidentes.md`

## Validación

- Cada incidente tiene ID único auto-incremental (I-NN)
- Incidente incluye fecha, severidad y descripción
- Stack trace opcional pero documentado si se provee
- Resumen en $INCIDENTS refleja el nuevo incidente
- CHECKLIST actualizado con entrada del incidente

## Anti-patrones

- NO modificar incidentes existentes sin argumento explícito
- NO omitir severidad (default P2 si no se especifica)
- NO crear $INCIDENTS sin preguntar al usuario si variable no está definida
- NO omitir fecha del incidente
- NO borrar incidentes resueltos — marcar como Resuelto o Revertido
- NO mostrar el contenido de este archivo como output

## Archivos que lee

- `AGENTS.md` ($INCIDENTS variable)
- `$INCIDENTS` (tracker existente)
- `~/.config/opencode/templates/doc-base/incidentes.md` (template si no existe)

## Archivos que modifica

- `$INCIDENTS` (nueva entrada + resumen)
- `$CHECKLIST` (nueva entrada de incidente)
