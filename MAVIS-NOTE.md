# Mavis — Chequeo de server (2026-07-12)

Hacé `git pull` en la notebook, ejecutá estos comandos en PowerShell y copiá TODO el resultado en un reply (commit, archivo, o lo que prefieras).

---

## 🌐 Conectividad (ESTO ES LO QUE FALTABA)

El server en `felrena` escucha en `0.0.0.0:8050` pero el **firewall de Windows está bloqueando conexiones entrantes**. Tenés que abrirlo vos en felrena (no en tu PC).

### IPs del server

| Tipo | IP |
|---|---|
| LAN (mismo router) | **192.168.1.34** |
| Tailscale | **100.120.192.43** |

### URL para conectar (desde tu PC)

```
http://192.168.1.34:8050
```

(o `http://100.120.192.43:8050` si usás Tailscale)

### ⚠️ Test que va a fallar hasta que el firewall esté abierto

En felrena, abrí PowerShell **como Administrador** y ejecutá:

```powershell
New-NetFirewallRule -DisplayName "MarketAI Dashboard (Mavis-allá)" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 8050 `
    -RemoteAddress 192.168.0.0/16,100.64.0.0/10 `
    -Action Allow `
    -Profile Any `
    -ErrorAction SilentlyContinue

Get-NetFirewallRule -DisplayName "MarketAI Dashboard (Mavis-allá)" | Format-List DisplayName,Enabled,Direction,Action
```

Eso abre el puerto 8050 a la red LAN (192.168.0.0/16) y a Tailscale (100.64.0.0/10).

### Test después de abrir firewall

Desde la otra notebook (la tuya), ejecutá:

```powershell
# LAN
Invoke-WebRequest -Uri "http://192.168.1.34:8050/api/health" -UseBasicParsing -TimeoutSec 5 | Select-Object StatusCode,Content

# Tailscale
Invoke-WebRequest -Uri "http://100.120.192.43:8050/api/health" -UseBasicParsing -TimeoutSec 5 | Select-Object StatusCode,Content
```

Si ves `StatusCode: 200` con `{"deepseek":true,...}`, estás conectado.

---

## 1. IP actual

```powershell
ipconfig | Select-String "192.168"
```

## 2. ¿Server vivo?

```powershell
curl -s http://localhost:8050/api/health
```

## 3. Procesos activos

```powershell
Get-Process python -ErrorAction SilentlyContinue | Select Id, ProcessName, StartTime
```

## 4. Posiciones abiertas

```powershell
curl -s http://localhost:8050/api/positions
```

## 5. Estado del watchdog / debug

```powershell
curl -s http://localhost:8050/api/debug
```
