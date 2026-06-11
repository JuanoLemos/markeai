# GUIA_DE_CONTRIBUCION — Guia de contribucion v1.0

Esta guia detalla el flujo de contribucion para MarketAI. Complementa a `CONTRIBUTING.md` con informacion operativa.

## Flujo de PR

1. **Rama**: Crear desde `main` con prefijo `feat/`, `fix/`, `docs/` o `refactor/`.
2. **Commits**: Usar el formato del proyecto via `/commit`.
3. **Code review**: Cada PR requiere al menos un revisor.
4. **Tests**: Todos los tests deben pasar antes del merge.
5. **Documentacion**: Si el cambio modifica comportamiento visible (config, endpoints, parametros), actualizar las guias en `doc/guias/`.

## Code review

| Aspecto | Que revisar |
|---------|-------------|
| Funcionalidad | El cambio resuelve el problema sin romper nada |
| Estilo | Sigue las convenciones del proyecto (ver `AGENTS.md`) |
| Tests | Los tests nuevos cubren los casos borde |
| Documentacion | Las guias estan actualizadas si corresponde |
| Seguridad | No se exponen secretos ni credenciales |

## Testing

```powershell
python -m pytest tests/ -v
```

Los tests se ejecutan contra SQLite local. No requieren conexion a internet ni API keys.

## Documentacion

Las guias viven en `doc/guias/`. El comando `/updoc` sincroniza la documentacion completa. Las mecanicas de negocio estan en `doc/mecanicas/`.

## Archivos relacionados

- `CONTRIBUTING.md` — Guia resumida de contribucion
- `AGENTS.md` — Convenciones y mapeo de rutas
- `doc/guias/GUIA_ONBOARDING.md` — Primeros pasos para nuevos desarrolladores
- `doc/mecanicas/MECANICA-CALIDAD.md` — Estandar de calidad documental
