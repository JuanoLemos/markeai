# MECANICA-ENFORCEMENT — Control de enforcement documental v1.0

Reglas para la integridad documental automatizada en MarketAI.

## Checks automatizados

El proyecto debe contar con un script `check-docs.js` (o `.ps1`) que verifique:

| Check | Descripcion |
|-------|-------------|
| Existencia | Todos los archivos obligatorios existen |
| Fechas ISO | Las fechas en documentos usan formato YYYY-MM-DD |
| Headers | Cada documento comienza con H1 matching filename |
| Archivos relacionados | Cada documento tiene seccion final "Archivos relacionados" |
| Rutas | Las referencias a archivos existen en el sistema de archivos |

## Pre-commit hooks

Usar hooks de git pre-commit para validar:

1. Cambios en `doc/` no introducen enlaces rotos.
2. Archivos Markdown no contienen caracteres no-ASCII no deseados (tipograficos).
3. No se modifican archivos criticos sin backup previo.

## CI validation

En GitHub Actions, el workflow de CI debe incluir un paso:

```yaml
- name: Check document integrity
  run: node .opencode/scripts/check-docs.js
```

## Archivos relacionados

- `doc/mecanicas/MECANICA-CALIDAD.md` — Estandar de calidad documental
- `README.md` — Configuracion de CI
- `.opencode/scripts/` — Scripts de validacion
