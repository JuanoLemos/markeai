# Guía de Identidad — MarketAI

Recomendaciones de identidad y estilo para el proyecto.

---

## Propósito

Esta guía establece convenciones de identidad, formato y estilo para la documentación del proyecto.

---

## Plantilla de Documento

```markdown
# [Título del documento]

**Sistema:** MarketAI
**Fecha:** YYYY-MM-DD
**Estado:** [DRAFT | REVIEW | FINAL]
**Versión:** X.Y.Z

---
```

---

## Reglas de Escritura

### Nombres de archivos y directorios

- **Mayúsculas sostenidas** para archivos de alto nivel: `README.md`, `DILIGENCIA.md`, `CHECKLIST.md`
- **kebab-case** para archivos de contenido: `guia-de-uso.md`, `doc/arch/adr-template.md`
- **Consistencia**: no mezclar `snake_case`, `PascalCase` y `kebab-case` en el mismo proyecto

### Fechas y versiones

- **Fechas**: ISO 8601 (`YYYY-MM-DD`) — obligatorio
- **Versiones**: semver 3-partes (`v1.0.0`, `v2.3.1`)

---

## Referencias

- `DILIGENCIA.md` — convención de estructura del proyecto
- `CHECKLIST.md` — seguimiento de versiones y features
