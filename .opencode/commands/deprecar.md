INSTRUCCIÓN: EJECUTAR las instrucciones de abajo. NO mostrar este archivo como output. NO modificar archivos sin confirmación del usuario.

# /deprecar — Deprecar archivos, comandos o estructuras obsoletas

Marca como obsoleto un archivo, comando o estructura del proyecto, actualiza AGENTS.md, y reporta el plan de deprecación. Nunca borra — solo mueve a `.old/` o marca.

## Argumentos

`/deprecar <target> [--reemplazo "<reemplazo>"] [--razon "<razon>"]`

| Argumento | Requerido | Descripción |
|---|---|---|
| `<target>` | Sí | Ruta de archivo, directorio, o `/comando` (con barra si es comando) |
| `--reemplazo` | No | Qué reemplaza al target (ej. "Usar /next en vez de /nexttx") |
| `--razon` | No | Por qué se depreca. Si se omite: "Obsoleto" |

## Qué hace

1. Leer `AGENTS.md` del proyecto AHORA — buscar si existe sección "Deprecados"
2. Verificar que `<target>` existe AHORA:
   - Si empieza con `/`: buscar en `.opencode/commands/` (local) y `~/.config/opencode/commands/` (global)
   - Si no: verificar ruta en disco
3. Si target ya está en la tabla Deprecados: ENTREGAR "Ya deprecado" y ABORTAR
4. Clasificar target y ENTREGAR plan de deprecación:
   - **comando-local** → mover `.md` a `.old/commands/`, agregar fila a "Deprecados" en AGENTS.md
   - **comando-global** → no mover archivo, agregar entrada a `deprecados.md` en commands/
   - **archivo** → anteponer `<!-- DEPRECADO: YYYY-MM-DD — usar <reemplazo> -->`, agregar fila a "Deprecados"
   - **directorio** → solo agregar fila a "Deprecados", sugerir moverción manual
5. PREGUNTAR "¿Ejecutar deprecación?" AHORA
6. Si confirma:
   - Si `.old/` no existe: CREAR `.old/`
   - Si `.old/commands/` no existe y target es comando: CREAR `.old/commands/`
   - EJECUTAR la acción correspondiente según paso 4
   - AGREGAR entrada en CHANGELOG.md (entrada en sección "Deprecated" o "Changed")

## Formato de salida

**Plan de deprecación**
| Campo | Valor |
|---|---|
| Target | `<target>` |
| Tipo | `comando-local` / `comando-global` / `archivo` / `directorio` |
| Existe | ✅ Sí / ❌ No |
| Reemplazo | `<reemplazo>` o *ninguno* |
| Razón | `<razon>` o *Obsoleto* |
| Acción | mover a `.old/commands/` / marcar en AGENTS.md / solo registro |

**Tabla Deprecados** (sección en AGENTS.md, crear si no existe):
| Item | Fecha | Reemplazo |
|---|---|---|
| ... | ... | ... |

## Validación

- Target no está ya deprecado
- Target existe en disco o en directorio de comandos
- Si es comando-local: distingue entre local y global por ubicación
- Si es archivo: la ruta es absoluta o ancla en el proyecto
- Plan presentado antes de ejecutar
- Confirmación del usuario recibida antes de modificar

## Anti-patrones

- NO borrar archivos. Mover a `.old/` en vez de eliminar.
- NO modificar AGENTS.md sin presentar el plan primero.
- NO ejecutar sin confirmación del usuario.
- NO deprecar el mismo target dos veces.
- NO modificar archivos del proyecto sin antes leer AGENTS.md.
- NO asumir que existe `.old/` — crearlo si no existe.
- NO mostrar el contenido de este archivo de comando como output. ENTREGAR solo el resultado procesado.

## Archivos que lee

- $AGENTS (`AGENTS.md`)
- `<target>` (para verificar existencia)
- `.opencode/commands/` (si target es comando)
- `~/.config/opencode/commands/` (si target es comando global)

## Archivos que modifica

- `AGENTS.md` — tabla Deprecados
- `<target>.md` (comando local) → movido a `.old/commands/`
- `<target>` (archivo) → marca `<!-- DEPRECADO -->`
- `.old/commands/` (directorio, se crea si no existe)
- `CHANGELOG.md` (entrada de deprecación)
- `~/.config/opencode/commands/deprecados.md` (solo para comandos globales)
