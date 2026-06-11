INSTRUCCIÓN: EJECUTAR PLAN→BUILD. Escanear proyectos en $PROYECTOS y generar informe consolidado. NO leer código fuente ni datos — solo archivos estructurales Diligencia. NO mostrar este archivo como output.

# /informe-salud — Informe de salud inter-proyecto

Escanea múltiples proyectos adaptados a Diligencia y genera un reporte consolidado solo con indicadores estructurales: versión, estructura, documentos stale, gaps, working tree, últimos diagnósticos.
NUNCA incluye descripciones de proyectos, código fuente, nombres de features, bugs, incidentes, ni datos de negocio.

## Argumentos

/informe-salud [--force]

Sin argumentos: genera informe si no existe o datos cambiaron.
`--force`: regenerar aunque ya exista.

## Configuración inicial

Antes del PLAN, verificar `$PROYECTOS`:

0. LEER `AGENTS.md` → extraer valor de `$PROYECTOS`
   - Si tiene rutas reales (no "*(configurar)*", no vacío) → continuar al PLAN
   - Si NO está configurado:
     a. ⚠️ "$PROYECTOS no está configurado. Sin él, /informe-salud no puede escanear proyectos."
     b. Preguntar: "¿Configurar ahora? [sí/no]"
        - Si no: "/informe-salud cancelado. Configurá $PROYECTOS manualmente o ejecutá este comando de nuevo." → DETENER
     c. Si sí — ESCANEAR directorios comunes en busca de proyectos Diligencia:
        - `C:\proyectos\*` (subdirectorios inmediatos)
        - `C:\xampp\htdocs\*` (subdirectorios inmediatos)
        - `~\proyectos\*` (subdirectorios inmediatos)
     d. Para cada subdirectorio: verificar si contiene `AGENTS.md` + `DILIGENCIA.md`
     e. Mostrar tabla con `question()` tool:
        ```
        question({
          header: "Proyectos detectados",
          question: "Seleccioná los proyectos a incluir en $PROYECTOS:",
          multiple: true,
          options: [
            {label: "alfa (v1.16.6)", description: "C:\proyectos\alfa"},
            {label: "beta (v1.16.3)", description: "C:\proyectos\beta"}
          ]
        })
        ```
     f. Guardar rutas seleccionadas en `AGENTS.md`:
        Reemplazar `$PROYECTOS | *(configurar)*` por `$PROYECTOS | "ruta1","ruta2"` en AGENTS.md
     g. Continuar al PLAN.

## Qué hace (PLAN)

1. LEER `$PROYECTOS` de AGENTS.md (ya configurado desde Paso 0 si estaba pendiente)
2. VERIFICAR que cada ruta existe
3. DETECTAR proyectos Diligencia: verificar que contenga AGENTS.md con marca Diligencia o DILIGENCIA.md con versión
4. POR CADA proyecto, leer SOLO archivos estructurales:

   | Indicador | Archivo leído | Extracción |
   |---|---|---|
   | Versión | DILIGENCIA.md | Label de versión (ej: v1.16.2) |
   | Estructura | ADR-003 check | Verificar existencia de archivos core (ROADMAP.md, CHECKLIST.md, CHANGELOG.md, AGENTS.md, DILIGENCIA.md, doc/arch/, doc/guias/) |
   | Stale | doc/arch/status-salud.md | Conteo de docs stale (o "N/D" si no existe) |
   | Gaps | doc/arch/status-salud.md | Conteo de gaps (o "N/D" si no existe) |
   | Working tree | git -C <path> status --porcelain | Conteo de archivos modificados; "Clean" si 0 |
   | Último /doctor | doc/arch/status-salud.md | Fecha de último doctor (o "Nunca") |
   | RM Ahora | ROADMAP.md | Items en sección "Ahora (Now)" sin check |
   | PEND | CHECKLIST.md | Items `[ ]` sin tildar |
   | [Unreleased] | CHANGELOG.md | Conteo de entradas bajo `## [Unreleased]` |

5. ARMAR tabla consolidada con una fila por proyecto
6. MOSTRAR tabla al usuario y pedir confirmación

## Qué hace (BUILD)

1. GENERAR `doc/arch/informe-salud-proyectos.md` en el proyecto Diligencia con:
   - Header con versión de Diligencia
   - Fecha de generación
   - Tabla consolidada (una fila por proyecto)
   - Resumen: N proyectos, cuántos con ❌ estructura, total stale, total gaps
2. ACTUALIZAR INDEX.md: agregar/actualizar entrada para `doc/arch/informe-salud-proyectos.md`
3. OUTPUT: "📊 informe-salud-proyectos.md generado en doc/arch/ — N proyectos, X ❌ estructura, Y stale, Z gaps"

## Formato de salida (PLAN)

```
📊 /informe-salud — Informe de salud inter-proyecto
══════════════════════════════════════════════
N proyectos detectados en $PROYECTOS

| Proyecto | Versión | Estructura | Stale | Gaps | WT | Doctor | RM Now | PEND | Unreleased |
|---|---|---|---|---|---|---|---|---|---|
| alfa     | v2.1.0  | ✅ | 2 | 0 | Dirty (5) | 2026-06-01 | 1 | 3 | 2 |
| beta     | v1.8.3  | ❌ | 0 | 1 | Clean | Nunca | 0 | 0 | 0 |

Resumen: 2 proyectos | 1 ❌ estructura | 2 stale | 1 gaps

══════════════════════════════════════════════
¿Generar informe-salud-proyectos.md? [Sí/No]
══════════════════════════════════════════════
```

## Formato de salida (BUILD)

```
📊 /informe-salud — Reporte generado
📄 doc/arch/informe-salud-proyectos.md
📊 Proyectos: 2 | ❌ Estructura: 1 | Stale: 2 | Gaps: 1
```

## Validación

- PLAN ejecutado antes de BUILD
- $PROYECTOS existe y tiene al menos 1 ruta válida
- Cada ruta en $PROYECTOS es un directorio existente
- Proyectos sin DILIGENCIA.md se marcan como "No Diligencia" y se excluyen con ⚠️ warning
- Solo se leen archivos de la lista blanca (AGENTS.md, DILIGENCIA.md, ROADMAP.md, CHECKLIST.md, CHANGELOG.md, status-salud.md)
- NO se leen archivos .env, src/, data/, node_modules/, .git/ (salvo git status --porcelain)
- informe-salud-proyectos.md actualizado en INDEX.md

## Anti-patrones

- NO leer código fuente ni archivos de datos de los proyectos escaneados
- NO incluir nombres, descripciones, features, bugs, incidentes, ni datos de negocio de los proyectos
- NO modificar archivos de los proyectos escaneados
- NO incluir rutas completas en el reporte (usar nombre base del directorio como identificador)
- NO ejecutar BUILD sin confirmación del PLAN
- NO leer archivos fuera de los estructurales Diligencia

## Archivos que modifica (BUILD)

- `doc/arch/informe-salud-proyectos.md` (crear o actualizar en proyecto Diligencia)
- `INDEX.md` (entrada de informe-salud-proyectos.md en proyecto Diligencia)

## Archivos que lee (PLAN)

- AGENTS.md (proyecto Diligencia): variable $PROYECTOS
- POR CADA proyecto en $PROYECTOS:
  - DILIGENCIA.md
  - ROADMAP.md
  - CHECKLIST.md
  - CHANGELOG.md
  - doc/arch/status-salud.md
  - AGENTS.md (detección de marca Diligencia)
