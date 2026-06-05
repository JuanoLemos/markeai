# Guía de Buenas Prácticas — MarketAI

**Propósito:** Convenciones y buenas prácticas para mantener la calidad del proyecto.

---

## Código

- Seguir PEP 8 para Python
- Tipado: usar type hints en funciones públicas
- Tests: pytest, mínimo 1 test por módulo
- Logging: usar módulo `logging`, no `print()`

## Documentación

- Mantener `CHANGELOG.md` actualizado
- Roadmap y Checklist sincronizados después de cada cambio significativo
- Usar `$variables` de AGENTS.md en lugar de rutas hardcodeadas

## Trading

- No modificar `orchestrator.py`, `engine/`, `execution/` sin approval de diseño
- CEDEARs operan en horario BYMA (12-19 UTC)
- Perfiles Normal y Fast tienen SL/TP independientes desde `config.yaml`
