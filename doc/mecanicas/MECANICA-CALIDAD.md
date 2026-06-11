# MECANICA-CALIDAD — Estandar de calidad documental v1.0

Estandares de formato para toda la documentacion de MarketAI.

## Estructura de headers

- H1: Debe coincidir con el nombre del archivo (ej: `# GUIA_ONBOARDING — ...`).
- H2: Separadores de secciones principales.
- H3: Subsecciones solo cuando sea necesario.

## Fechas

Todas las fechas en formato ISO 8601: `YYYY-MM-DD`. Ejemplo: `2026-06-10`.

## Referencias cruzadas

Las referencias a otros archivos usan rutas relativas desde la raiz del proyecto:

```markdown
Ver `doc/guias/GUIA_ONBOARDING.md` para mas detalles.
```

## Tablas

Las tablas deben estar alineadas y usar el formato estandar de Markdown:

```markdown
| Columna A | Columna B |
|-----------|-----------|
| Valor 1   | Valor 2   |
```

## Archivos relacionados

Seccion obligatoria al final de cada documento. Lista los archivos del proyecto que se relacionan con el contenido del documento, con ruta y descripcion breve.

## Cuanto documentar

| Tipo de cambio | Documentacion requerida |
|----------------|------------------------|
| Bug fix simple | Actualizar `doc/arch/bugs.md` |
| Nueva funcionalidad | Guia correspondiente en `doc/guias/` |
| Cambio de config | `doc/guias/guia_configuracion.md` |
| Nueva mecanica | Archivo en `doc/mecanicas/` |
| Decision arquitectonica | ADR en `doc/arch/` |

## Archivos relacionados

- `doc/mecanicas/MECANICA-ENFORCEMENT.md` — Control de enforcement
- `AGENTS.md` — Reglas post-edit y sincronizacion
