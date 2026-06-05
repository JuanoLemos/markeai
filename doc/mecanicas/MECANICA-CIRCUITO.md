# MECANICA-CIRCUITO.md — Circuito de Workflows Vinculantes

**Propósito:** Define cómo se encadenan los comandos de OpenCode en secuencias multi-comando gestionadas por `/circuito`.

---

## Meta-PLAN (PRO) vs BUILD (FLASH)

Todo workflow sigue esta estructura:

```
META-PLAN (DeepSeek PRO)
  → Ejecuta solo fases de PLAN (lectura + auditoría)
  → NO modifica archivos
  → Muestra tabla consolidada
  → Pide UNA SOLA confirmación

BUILD (DeepSeek FLASH)
  → Ejecuta fases de BUILD (escritura, edición, generación)
  → Actúa sobre las decisiones del META-PLAN
  → Commit final si corresponde
```

## Workflows disponibles

| Workflow | Comandos |
|---|---|
| **/version** | plan → updoc → version → commit |
| **/doctor** | plan → diligencia-check → salud → commit |
| **/updoc** | plan → updoc → salud |
