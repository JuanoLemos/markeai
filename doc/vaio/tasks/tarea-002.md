# Tarea 002 — Re-deploy: prompt fixes ahora en main

**Origen:** MAIN (PC Principal)
**Fecha:** 2026-07-22
**Prioridad:** Alta — los fixes ya están en `main`, solo falta reiniciar el server

---

## Contexto

La tarea-001 se ejecutó pero los cambios de código no estaban en `main` en ese momento. Ahora están commiteados en `942e73d`.

### Commits a deployar

| Commit | Cambios |
|---|---|
| `942e73d` | `config.yaml`: max_tokens 4000→300, temperature 0.3→0.0, model flash→pro |
| `942e73d` | `engine/decider.py`: rewrite prompts — WAIT=default, ≥2 capas |
| `942e73d` | `engine/fusion.py`: confidence cap (1 capa=33%, 2=66%, 3+=100%) |
| `942e73d` | `orchestrator/pipeline.py`: pre-filtro layers<2 |

---

## Pasos

### 1. Pull + Deploy

```powershell
cd C:\xampp\htdocs\MarketAI
git pull origin main
curl -X POST http://localhost:8050/api/deploy -H "X-Auth-Token: mavis2026marketai"
```

### 2. Verificar

```powershell
Start-Sleep -Seconds 10
curl http://localhost:8050/api/debug | ConvertFrom-Json | Select-Object api_version, normal_balance, fast_balance
```

`api_version` debe mostrar `1.5.3`.

### 3. Verificar posiciones abiertas

```powershell
curl http://localhost:8050/api/positions
```

---

## Resultado esperado

Escribir en `doc/vaio/results/resultado-002.md` con:
- `git pull` exitoso? SI/NO
- Deploy exitoso? SI/NO
- `api_version` post-deploy
- Balance normal y fast
- Número de posiciones abiertas (deberían bajar con el nuevo prompt conservador)
- Errores

---

**Fin de tarea.**
