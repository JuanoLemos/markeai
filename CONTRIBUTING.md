# CONTRIBUTING — Guia de contribucion

Gracias por tu interes en contribuir a MarketAI. Este documento describe el proceso para reportar bugs, proponer cambios y enviar pull requests.

## Como reportar bugs

1. Revisa que el bug no haya sido reportado antes en `doc/arch/bugs.md`.
2. Usa el comando `/bug` dentro de OpenCode para registrarlo automaticamente.
3. Incluye: descripcion del problema, pasos para reproducir, comportamiento esperado vs real, y logs relevantes.
4. Asigna prioridad P1 (critico), P2 (importante) o P3 (backlog).

## Como proponer cambios

1. Abre un issue describiendo el cambio propuesto y su justificacion.
2. Para cambios arquitectonicos, espera la creacion de un ADR antes de codificar.
3. Para cambios pequenos (menos de 20 lineas en 1 archivo), puedes enviar el PR directamente.
4. Para cambios grandes, sigue el flujo SDD: `@sdd-architect` -> `@sdd-implement` -> `@sdd-verify` -> `@sdd-reviewer`.

## Estilo de codigo

| Aspecto | Regla |
|---------|-------|
| Lenguaje | Python 3.10+ |
| Formato | Sin requisito estricto, seguir estilo existente |
| Nombres | `snake_case` para variables/funciones, `PascalCase` para clases |
| Imports | Estandar, terceros, locales (separados por linea) |
| Tipos | Type hints obligatorios en funciones publicas |
| Tests | pytest en `tests/`, nombrar `test_*.py` |
| Logging | Usar `logging` de Python, no `print` |

## Proceso de PR

1. Crea una rama desde `main`: `git checkout -b feat/nombre-descritivo`.
2. Asegura que todos los tests pasen: `python -m pytest tests/ -v`.
3. Verifica lint basico: no hay errores de sintaxis ni imports rotos.
4. Si el cambio modifica comportamiento visible, actualiza las guias en `doc/guias/`.
5. Envia el PR contra `main` con una descripcion clara de los cambios.
6. Un revisor del equipo hara code review antes del merge.

## Archivos relacionados

- `doc/arch/bugs.md` — Registro de bugs
- `doc/guias/GUIA_DE_CONTRIBUCION.md` — Guia extendida de contribucion
- `AGENTS.md` — Convenciones del proyecto
- `ROADMAP.md` — Roadmap y prioridades
