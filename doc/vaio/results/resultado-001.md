# Resultado 001 — Deploy prompt fixes v1.5.3

**Fecha:** 2026-07-22 23:52 UTC
**Ejecutor:** VAIO Server (FELRENA)

## Resumen

| Campo | Valor |
|---|---|
| `git pull` exitoso | SI |
| Deploy exitoso | SI |
| `api_version` post-deploy | 1.5.2 |
| Motors (5/5) | SI (todos ok) |
| Balance normal | $1,000.00 |
| Balance fast | $708.52 |

## Detalle

### 1. git pull
```
3b2396e docs: tarea-001 deploy prompt fixes v1.5.3
1864280 fix(vaio): keep_alive migrado a pythonw.exe - ventana cero
36ea2ee fix(vaio): ventanas invisibles en tasks 5min + docs
```

### 2. Deploy
```
POST /api/deploy → 200
{"ok":true,"pull":"Already up to date.","restarted":true,"waited_s":0}
```

### 3. Verificación post-deploy
```
/api/ping → {"running":true,"time":"23:49 UTC","version":"1.5.2"}
Status: running true
```

### 4. Motors
| Motor | Status | Último mensaje |
|---|---|---|
| Loop | ok | Iteracion iter-20260722234927 |
| Datos | ok | polymarket: 3 capas |
| Fusion | ok | polymarket ... SHORT score=36.8 |
| DeepSeek | ok | polymarket ... WAIT conf=0 |
| Bot | ok | Loop activo |

## Perfiles

| Perfil | Balance | PnL total | Win rate | Posiciones |
|---|---|---|---|---|
| normal | $1,000.00 | $0.00 | 0% | 0 |
| fast | $708.52 | -$291.48 | 4.3% (1/23) | 9 |

## Errores

No se detectaron errores en el deploy. El servidor se reinició correctamente.

**Nota:** La versión actual en repo sigue siendo `1.5.2`. Los cambios de configuración mencionados en la tarea (`config.yaml`, `engine/decider.py`, `orchestrator/pipeline.py`, `engine/fusion.py`) no están presentes en `origin/main` al momento del deploy. El deploy ejecutó el restart del server con el código vigente.
