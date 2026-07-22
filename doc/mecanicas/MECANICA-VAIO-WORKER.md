# MECANICA-VAIO-WORKER.md — Worker autónomo 24/7 v1.0

Worker remoto que corre en la laptop VAIO (servidor 24/7 de MarketAI). Se comunica con MAIN a través de GitHub sin intervención humana.

---

## Arquitectura

```
MAIN (PC Principal)              GitHub                    WORKER (VAIO 24/7)
───────────────────              ──────                    ──────────────────
crea tarea en                    ← repo →                  git pull (cada 60s)
doc/vaio/tasks/tarea-NNN.md                                detecta tarea nueva
git push                                                   ejecuta comandos
                                                           escribe resultado en
                                                           doc/vaio/results/
                                                           git commit + push
git pull                        ← repo →                   sleep 60s → loop
lee resultado
```

---

## Canales de conexión remota

| Canal | Propósito | Requisito |
|---|---|---|
| **GitHub** | Comunicación MAIN↔WORKER (tareas y resultados) | git push/pull |
| **Cloudflare Tunnel** | Acceso a Chamber.exe (localhost:57123) desde PC Principal | `cloudflared` instalado |
| **VS Code Tunnels** | Acceso al sistema de archivos y terminal remota | VS Code + cuenta GitHub |
| **Tailscale** | Red privada (IP 100.120.192.43) — conexión directa LAN | Tailscale instalado |

---

## Tipos de tareas VAIO

| Tipo | Descripción | Ejemplo |
|---|---|---|
| **Check** | Verificar estado del bot, balance, motors | `curl localhost:8050/api/debug` |
| **Deploy** | git pull + restart del server | `curl -X POST localhost:8050/api/deploy` |
| **Recovery** | Reiniciar servicios caídos | `taskkill /f /im python.exe; tray_watchdog.bat` |
| **Script** | Ejecutar script de mantenimiento | `python scripts/backup-critical.py` |

---

## Ciclo del worker

1. **pull** — `git pull origin main`
2. **detectar** — listar `doc/vaio/tasks/*.md`, filtrar las que no tienen resultado
3. **ejecutar** — correr comandos uno por uno, capturar output
4. **reportar** — escribir `doc/vaio/results/resultado-NNN.md`
5. **push** — `git add doc/vaio/results/` + commit + `git pull --rebase` + push
6. **esperar** — 60 segundos
7. **repetir**

---

## Reglas

| # | Regla |
|---|---|
| 1 | Solo tocar `doc/vaio/` — no modificar código del proyecto |
| 2 | Solo ejecutar comandos de las tareas, no improvisar |
| 3 | Si un comando falla, reportar el error; no arreglarlo |
| 4 | Idempotente: si ya existe resultado-NNN.md, no re-ejecutar tarea-NNN.md |
| 5 | Commit seguro: `git pull --rebase` antes de push; si conflicto, abortar |
| 6 | No bloquearse: si requiere intervención manual, reportar y seguir |
| 7 | No pedir confirmación humana (modo autónomo) |

---

## Archivos relacionados

- `doc/vaio/PRONT_VAIO.md` — prompt de nacimiento para sesiones Chamber interactivas
- `doc/vaio/worker-loop.md` — prompt del sistema para worker autónomo 24/7
- `doc/vaio/README.md` — instrucciones del puente MAIN↔VAIO
- `doc/guias/GUIA_CONTROL_REMOTO.md` — guía de conexión remota
- `SERVER-NOTE.md` — instrucciones para el admin del server
