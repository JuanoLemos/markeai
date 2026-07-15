# Incidentes — MarketAI

**Actualizado:** 2026-07-15 | **Total:** 1 activo

---

## Resumen

| Total | P1 | P2 | P3 | Abiertos |
|---|---|---|---|---|
| 1 | 0 | 1 | 0 | 1 |

---

## Registro de incidentes

### I-01 — /ola no existe como comando standalone en v2.7.1
| Campo | Detalle |
|---|---|
| **Fecha** | 2026-07-15 02:00 |
| **Severidad** | P2 |
| **Descripción** | El changelog de Diligencia v2.7.1 anuncia "/ola: sistema de oleadas multi-proyecto con wave manifest y reglas OnFail" pero no existe archivo `ola.md` en `~/.config/opencode/commands/`. La tabla de migración v2.6.6→v2.7.1 dice "33 comandos fundamentales activos" pero solo hay 45 archivos en el directorio global y ninguno es ola.md. El comando `/ola` no se puede ejecutar desde ningún proyecto adaptado. |
| **Stack** | No aplica — es un gap documental/metodológico, no un error de código |
| **Causa** | Probablemente /ola existe como subcomando dentro de /CBP (Meta-PLAN paralelo en olas) o solo funciona en el proyecto Diligencia mismo, pero se documentó como comando standalone sin implementar el archivo |
| **Mitigación** | Reportar a Diligencia upstream para que creen `ola.md` como comando global o aclaren en la migración que es parte de /CBP |
| **Estado** | Abierto |
