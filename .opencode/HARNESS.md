# HARNESS.md — MarketAI

Harness global: `~/.config/opencode/`
Versión: 1.0.0 | Creado: 2026-07-01

---

## Comandos del proyecto

| Tipo | Comando | Notas |
|---|---|---|
| Test | *(no configurado)* | |
| Lint | *(no configurado)* | |
| Verify | *(no configurado)* | |
| Start | *(no configurado)* | |

## Documento SSOT del proyecto

Archivo principal: `AGENTS.md`

## Skills locales del proyecto

| Skill | Ruta |
|---|---|
| *(ninguna)* | |

## Stack

*(completar stack del proyecto)*

## Testing worktree *(opcional)*

- Worktree de testing: `<ruta>`
- Commit fijo: `<tag>` (detached HEAD en `<hash>`)
- Independiente: `node_modules`, `package-lock.json` propios
- Sync desde el repo principal:
  ```powershell
  cd <ruta-worktree>
  git fetch ../<repo-dev> <branch>
  git checkout <nuevo-hash>
  npm install
  ```

## Convenciones

- Idioma: español (todas las respuestas del agente deben ser en español)

*(completar convenciones específicas del proyecto)*

## Archivos críticos

*(listar archivos que requieren backup o aprobación)*

## Harness activo

- [x] Agentes SDD globales disponibles
- [ ] HARNESS.md completado
- [ ] TDD (test runner configurado)
- [ ] Post-edit verification activa

