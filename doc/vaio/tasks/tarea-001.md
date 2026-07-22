# Tarea 001 — Deploy prompt fixes v1.5.3

**Origen:** MAIN (PC Principal)
**Fecha:** 2026-07-21
**Prioridad:** Alta — aplicar inmediatamente

---

## Contexto

Se realizaron cambios críticos en el prompt trader y configuración del bot para corregir pérdidas. Los cambios ya están commiteados y pusheados en `main` (v1.5.3).

### Cambios incluidos

| Archivo | Cambio |
|---|---|
| `config.yaml` | `max_tokens: 300`, `temperature: 0.0`, `model: deepseek-v4-pro` |
| `engine/decider.py` | Rewrite de prompts NORMAL y FAST — WAIT es el default, exige ≥2 capas |
| `orchestrator/pipeline.py` | Pre-filtro fusión más restrictivo (score<35 OR conf<20 OR layers<2) |
| `engine/fusion.py` | Confidence cap: 1 capa→33%, 2→66%, 3+→100% |

---

## Pasos a ejecutar

### 1. Hacer pull del código

```powershell
cd C:\xampp\htdocs\MarketAI
git pull origin main
```

### 2. Verificar que los archivos cambien correctamente

```powershell
git log --oneline -3
```
Debe mostrar el commit `v1.5.3`.

### 3. Hacer deploy al bot vivo

```powershell
curl -X POST http://localhost:8050/api/deploy -H "X-Auth-Token: mavis2026marketai"
```

### 4. Verificar que el bot se reinicie

```powershell
Start-Sleep -Seconds 10
curl http://localhost:8050/api/ping
curl http://localhost:8050/api/debug | ConvertFrom-Json | Select-Object api_version, normal_balance, fast_balance, motors
```

`api_version` debe mostrar `1.5.3`.

---

## Si el deploy falla

Si `/api/deploy` no responde (server caído):

```powershell
taskkill /f /im python.exe
cd C:\xampp\htdocs\MarketAI
.\tray_watchdog.bat
Start-Sleep -Seconds 15
curl http://localhost:8050/api/ping
```

Si sigue sin responder, reportar en el resultado como ERROR.

---

## Resultado esperado

Escribir en `doc/vaio/results/resultado-001.md` con:
- `git pull` exitoso? SI/NO
- Deploy exitoso? SI/NO
- `api_version` post-deploy
- Balance de cada perfil
- Motors (deben ser 5/5)
- Errores encontrados (si los hubo)

---

**Fin de tarea.** Al completar, hacer commit + push del resultado.
