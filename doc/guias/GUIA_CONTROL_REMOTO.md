# GUIA_CONTROL_REMOTO.md — Conexión remota al server MarketAI v1.0

Guía para acceder al servidor MarketAI (notebook "felrena") desde cualquier ubicación, sin depender del ISP local.

---

## Métodos de conexión

| Método | Velocidad | Acceso | Requisito en server |
|---|---|---|---|
| **VS Code Tunnels** | Alta | Terminal + archivos + extensiones | VS Code + cuenta GitHub |
| **Cloudflare Tunnel** | Media | Chamber.exe (localhost:57123) + dashboard (8050) | `cloudflared` instalado |
| **Tailscale** | Alta | Red privada directa | Tailscale instalado |
| **GitHub** | Baja | Comunicación de tareas vía VAIO worker | git push/pull |

---

## VS Code Tunnels (recomendado para trabajo interactivo)

### En el server (una sola vez)

```powershell
# Instalar VS Code CLI si no existe
code tunnel --name felrena-marketai
# Seguir instrucciones de auth con GitHub
```

### Desde PC Principal

1. Abrir VS Code
2. Click en el ícono de Remote Explorer (esquina inferior izquierda)
3. "Connect to Tunnel..." → seleccionar `felrena-marketai`
4. Abrir carpeta `C:\xampp\htdocs\MarketAI`

---

## Cloudflare Tunnel (para Chamber y dashboard)

### En el server

```powershell
# Instalar cloudflared
winget install Cloudflare.cloudflared

# Crear túnel
cloudflared tunnel login
cloudflared tunnel create marketai-vaio
cloudflared tunnel route dns marketai-vaio marketai-vaio.example.com

# Configurar (~/.cloudflared/config.yml):
# tunnel: <tunnel-id>
# credentials-file: C:\Users\<user>\.cloudflared\<tunnel-id>.json
# ingress:
#   - hostname: marketai-vaio.example.com
#     service: http://localhost:57123
#   - service: http_status:404

# Ejecutar
cloudflared tunnel run marketai-vaio
```

### Desde PC Principal

- Chamber: `https://marketai-vaio.example.com`
- Dashboard: agregar ingress rule para `localhost:8050`

---

## Tailscale (red privada)

```powershell
# En el server y PC Principal
winget install tailscale
tailscale up
```

- IP Tailscale del server: `100.120.192.43`
- IP LAN: `192.168.100.4`
- Dashboard: `http://100.120.192.43:8050`
- Token auth: `mavis2026marketai` (header `X-Auth-Token`)

---

## Comunicación vía VAIO Worker (sin conexión directa)

Si ningún túnel funciona, usar el worker autónomo:

1. Escribir tarea en `doc/vaio/tasks/tarea-NNN.md`
2. `git push`
3. El worker en VAIO la detecta en ~60s y ejecuta
4. `git pull` → leer resultado en `doc/vaio/results/resultado-NNN.md`

Ver `doc/mecanicas/MECANICA-VAIO-WORKER.md` para el protocolo completo.

---

## Verificar conectividad

```powershell
# Ping básico (Tailscale)
Test-NetConnection 100.120.192.43 -Port 8050

# Via token auth
curl -H "X-Auth-Token: mavis2026marketai" http://100.120.192.43:8050/api/ping

# Deploy remoto
curl -X POST http://100.120.192.43:8050/api/deploy -H "X-Auth-Token: mavis2026marketai"
```

---

## Troubleshooting

| Problema | Causa probable | Solución |
|---|---|---|
| No responde en Tailscale IP | ISP cambió, Tailscale caído | Usar Cloudflare Tunnel o GitHub/VAIO |
| Cloudflare Tunnel caído | `cloudflared` no corriendo | Pedir al admin que ejecute `cloudflared tunnel run` |
| VS Code Tunnel caído | Server reinició sin auto-start | Configurar `code tunnel service install` |
| Ningún método funciona | Server apagado o sin internet | Usar SERVER-NOTE.md para instruir al admin |

---

## Archivos relacionados

- `doc/mecanicas/MECANICA-VAIO-WORKER.md` — patrón del worker autónomo
- `doc/vaio/README.md` — instrucciones del puente MAIN↔VAIO
- `SERVER-NOTE.md` — instrucciones para el admin local del server
- `scripts/keep_alive.ps1` — Task Scheduler watchdog del server
