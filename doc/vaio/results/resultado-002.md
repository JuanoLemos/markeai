# Resultado 002 — Re-deploy: prompt fixes ahora en main

**Fecha:** 2026-07-23 00:15 UTC
**Ejecutor:** VAIO Server (FELRENA)

## Resumen

| Campo | Valor |
|---|---|
| `git pull` exitoso | SI |
| Deploy exitoso | SI |
| `api_version` post-deploy | 1.5.2 (config.yaml line:1) |
| Git tag | v1.5.4 |
| Motors (5/5) | SI (todos ok) |
| Balance normal | $1,000.00 |
| Balance fast | $1,000.00 |
| Posiciones abiertas | 0 |

## Detalle

### 1. git pull
```
64c7c23 chore(release): v1.5.4 — prompt rewrite + model pro + fusion confidence cap
d61ab53 docs: tarea-002 re-deploy prompt fixes now in main
942e73d fix(trader): prompt rewrite WAIT=default + fusion confidence cap + model pro + cost reduction
```

### 2. Deploy
```
POST /api/deploy → 200
{"ok":true,"pull":"Already up to date.","restarted":true,"waited_s":0}
```

### 3. Verificación post-deploy
```
/api/ping → {"running":true,"time":"00:07 UTC","version":"1.5.2"}
Status: running true
```

### 4. Config
Los cambios de prompt ya están en `config.yaml`:
- `max_tokens: 300` ✓
- `model: deepseek-v4-pro` ✓
- `temperature: 0.0` ✓

### 5. Motors
| Motor | Status | Último mensaje |
|---|---|---|
| Loop | ok | Iteracion iter-20260723001207 |
| Datos | ok | forex: 6 capas |
| Fusion | ok | forex EURUSD=X: WAIT score=49.5 |
| DeepSeek | ok | polymarket ... WAIT conf=0 |
| Bot | ok | Loop activo |

### 6. Perfiles (post-reset)

| Perfil | Balance | PnL total | Win rate | Posiciones |
|---|---|---|---|---|
| normal | $1,000.00 | $0.00 | 0% | 0 |
| fast | $1,000.00 | $0.00 | 0% | 0 |

## Errores

Ninguno. El server se reinició correctamente y el nuevo prompt conservador (WAIT=default, ≥2 capas, deepseek-v4-pro, temperature=0.0) está activo.

**Nota:** El `api_version` devuelve `1.5.2` porque la clave `version:` en `config.yaml:1` no fue actualizada al hacer el tag v1.5.4. La app corre el código de v1.5.4.
