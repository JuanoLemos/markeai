# GUIA_UPDATE_DILIGENCIA — Actualizacion de metodologia v1.0

Guia para actualizar la metodologia Diligencia en MarketAI.

## Que es Diligencia

Diligencia es la metodologia de gestion de proyectos que MarketAI sigue. Incluye convenciones de documentacion, flujos de trabajo, comandos slash y reglas de disciplina para agentes IA.

## Como actualizar

### Upgrade completo via `/adaptar`

```powershell
/adaptar
```

El comando `/adaptar` realiza los siguientes pasos:

1. Lee la version actual de Diligencia desde `.opencode/HARNESS.md`.
2. Descarga la ultima version desde el repositorio de Diligencia.
3. Actualiza archivos de configuracion (`.opencode/commands/`, `AGENTS.md`).
4. Crea o actualiza guias faltantes en `doc/guias/`.
5. Genera un reporte de cambios en `doc/arch/`.

### Upgrade manual

1. Clonar el repositorio de Diligencia.
2. Copiar los nuevos comandos a `.opencode/commands/`.
3. Revisar y aplicar cambios en `AGENTS.md`.
4. Ejecutar `/diligencia-check` para verificar integridad.

## Verificacion post-update

```powershell
/diligencia-check
```

Este comando verifica:
- Existencia de archivos obligatorios
- Integridad de comandos slash
- Coherencia de HARNESS.md
- Estado de checksums documentales

## Archivos relacionados

- `.opencode/HARNESS.md` — Configuracion del harness
- `AGENTS.md` — Convenciones del proyecto
- `doc/arch/` — Registro de versiones anteriores
