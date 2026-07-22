# MarketAI — Worker autónomo

> **Modo autónomo activo.** El worker corre 24/7 sin intervención humana.
> Loop: pull → detectar tareas → ejecutar → reportar → push → esperar 60s → repetir.

La PC principal y la máquina remota se comunican a través de este repositorio en GitHub.

## Cómo funciona

```
MAIN                             GitHub                    WORKER (24/7)
────                             ──────                    ─────────────
crea tarea en                    ← repo →                  git pull (cada 60s)
doc/vaio/tasks/tarea-NNN.md                                detecta tarea nueva
git push                                                   ejecuta comandos
                                                           escribe resultado en
                                                           doc/vaio/results/
                                                           git commit + push
git pull                        ← repo →                   sleep 60s → loop
lee resultado                                              

Sin intervención humana en la máquina remota.
```

## Para MAIN

### Crear tarea
Escribir el archivo `.md` con los comandos en `doc/vaio/tasks/` → commit → push.
El worker la detecta en el próximo ciclo (~60 segundos).

### Leer resultado
```bash
git pull
cat doc/vaio/results/resultado-NNN.md
```

## Para el Worker

Leer `doc/vaio/worker-loop.md` — prompt completo del worker autónomo.

### Ciclo de trabajo
```
LOOP:
  git pull
  detectar tareas sin resultado
  ejecutar → commit resultado → push
  sleep 60s
```

## Reglas

- Solo tocar `doc/vaio/` — no modificar código del proyecto
- Solo ejecutar comandos de las tareas, no improvisar
- Si un comando falla, reportar el error, no arreglarlo
- Idempotente: si ya existe resultado-NNN.md, no re-ejecutar tarea-NNN.md

## Archivos relacionados
- `doc/vaio/PRONT_VAIO.md` — prompt de nacimiento para sesiones Chamber interactivas
- `doc/vaio/worker-loop.md` — prompt del sistema para el worker autónomo 24/7
- `doc/mecanicas/MECANICA-VAIO-WORKER.md` — patrón documentado
- `GUIA_CONTROL_REMOTO.md` — acceso directo vía túneles (complemento)
